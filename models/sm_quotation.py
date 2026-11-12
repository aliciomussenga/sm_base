# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from psycopg2 import IntegrityError

class SmQuotation(models.Model):
    _name = 'sm.quotation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Orçamento de Serviço'
    _order = 'create_date desc'

    name = fields.Char(
        string='Número de Orçamento',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Novo')
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        required=True,
        ondelete='restrict',
        tracking=True,
    )

    request_id = fields.Many2one(
        comodel_name='sm.service.request',
        string='Solicitação de Origem',
        ondelete='set null',
        tracking=True,
        help='Solicitação que originou este orçamento'
    )

    date_quotation = fields.Date(
        string='Data do Orçamento',
        default=fields.Date.today,
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Rascunho'),
            ('sent', 'Enviado'),
            ('approved', 'Aprovado'),
            ('refused', 'Recusado'),
            ('cancel', 'Cancelado')
        ],
        string='Estado',
        default='draft',
        required=True,
        tracking=True,
    )

    # Campo One2many que lista as linhas do orçamento
    line_ids = fields.One2many(
        comodel_name='sm.quotation.line',
        inverse_name='quotation_id',
        string='Linhas do orçamento'
    )

    tag_ids = fields.Many2many(
        comodel_name='sm.tag',
        relation='sm_quotation_tag_rel',
        column1='quotation_id',
        column2='tag_id',
        string='Etiquetas'
    )

    amount_total = fields.Float(
        string='Valor Total (Kz)',
        default=0.0,
        compute='_compute_amount_total',
        store=True
    )

    refuse_reason = fields.Text(
        string='Motivo da Recusa',
        readonly=True
    )

    def init(self):
        self.env.cr.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS sm_quotation_request_open_unique "
            "ON sm_quotation (request_id) "
            "WHERE request_id IS NOT NULL AND state IN ('draft', 'sent')"
        )

    @api.model
    def _lock_request_ids(self, request_ids):
        request_ids = sorted(set(request_ids))
        if request_ids:
            self.env.cr.execute(
                "SELECT id FROM sm_service_request WHERE id = ANY(%s) ORDER BY id FOR UPDATE",
                [request_ids],
            )

    def _lock_for_update(self):
        records = self.sorted('id')
        if records:
            self.env.cr.execute(
                "SELECT id FROM sm_quotation WHERE id = ANY(%s) ORDER BY id FOR UPDATE",
                [records.ids],
            )
            records.invalidate_recordset(['state', 'request_id'])

    @api.model
    def _check_request_has_no_other_proposal(self, request_id, excluded_ids=()):
        domain = [
            ('request_id', '=', request_id),
            ('state', 'in', ['draft', 'sent', 'approved']),
        ]
        if excluded_ids:
            domain.append(('id', 'not in', list(excluded_ids)))
        if self.sudo().search(domain, limit=1):
            raise ValidationError(_(
                'Esta solicitação já possui um orçamento aberto ou aprovado. '
                'Recuse ou cancele a proposta anterior antes de criar outra.'
            ))

    @api.model
    def _reserve_request_ids(self, request_quotations):
        reservations = self.env['sm.quotation.guard'].sudo()
        for request_id, quotation_id in sorted(request_quotations.items()):
            try:
                with self.env.cr.savepoint():
                    reservations.create({
                        'request_id': request_id,
                        'quotation_id': quotation_id or False,
                    })
            except IntegrityError as error:
                raise ValidationError(_(
                    'Esta solicitação já possui um orçamento aberto ou aprovado.'
                )) from error

    def _release_request_reservation(self, request_id, quotation_id, excluded_ids=()):
        guards = self.env['sm.quotation.guard'].sudo()
        guard = guards.search([
            ('request_id', '=', request_id),
            ('quotation_id', '=', quotation_id),
        ], limit=1)
        if not guard:
            return
        domain = [
            ('request_id', '=', request_id),
            ('state', 'in', ['draft', 'sent', 'approved']),
            ('id', '!=', quotation_id),
        ]
        if excluded_ids:
            domain.append(('id', 'not in', list(excluded_ids)))
        surviving_quotation = self.sudo().search(domain, order='id', limit=1)
        if surviving_quotation:
            guard.write({'quotation_id': surviving_quotation.id})
        else:
            guard.unlink()

    # Adicionar o metodo de cálculo do total:
    @api.depends('line_ids.price_subtotal')
    def _compute_amount_total(self):
        for quotation in self:
            # Utiliza a função sum() do Python navegando nas linhas do One2many
            quotation.amount_total = sum(line.price_subtotal for line in quotation.line_ids)

    # -------------------------------------------------------------------------
    # SOBREPOSIÇÃO DO MÉTODO CREATE
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        proposal_counts = {}
        for vals in vals_list:
            request_id = vals.get('request_id')
            if request_id and vals.get('state', 'draft') in ('draft', 'sent', 'approved'):
                proposal_counts[request_id] = proposal_counts.get(request_id, 0) + 1
        if any(count > 1 for count in proposal_counts.values()):
            raise ValidationError(_('Não é possível criar mais de uma proposta ativa para a mesma solicitação.'))

        self._lock_request_ids(proposal_counts)
        for request_id in proposal_counts:
            self._check_request_has_no_other_proposal(request_id)
        self._reserve_request_ids({request_id: False for request_id in proposal_counts})

        for vals in vals_list:
            # Se o nome for 'Novo' ou estiver vazio, consome a sequência do sistema
            if vals.get('name', _('Novo')) == _('Novo'):
                vals['name'] = self.env['ir.sequence'].next_by_code('sm.quotation') or _('Novo')
        try:
            with self.env.cr.savepoint():
                records = super(SmQuotation, self).create(vals_list)
        except IntegrityError as error:
            if error.diag.constraint_name == 'sm_quotation_request_open_unique':
                raise ValidationError(_(
                    'Esta solicitação já possui um orçamento aberto ou aprovado.'
                )) from error
            raise
        # Atualiza a solicitação de serviço de origem para 'quoted' se estiver 'in_analysis'
        requests_in_analysis = records.request_id.filtered(lambda r: r.state == 'in_analysis')
        if requests_in_analysis:
            requests_in_analysis.write({'state': 'quoted'})
        for record in records.filtered('request_id'):
            self.env['sm.quotation.guard'].sudo().search([
                ('request_id', '=', record.request_id.id),
                ('quotation_id', '=', False),
            ], limit=1).write({'quotation_id': record.id})
        return records

    def write(self, vals):
        reservations_to_create = {}
        reservations_to_release = []
        if 'request_id' in vals or 'state' in vals:
            self._lock_for_update()
            request_ids = set(self.mapped('request_id').ids)
            if vals.get('request_id'):
                request_ids.add(vals['request_id'])
            self._lock_request_ids(request_ids)
            self.invalidate_recordset(['state', 'request_id'])

            proposal_counts = {}
            reservations_to_create = {}
            for record in self:
                old_request_id = record.request_id.id
                old_state = record.state
                request_id = vals.get('request_id', old_request_id)
                state = vals.get('state', old_state)
                old_active = old_request_id and old_state in ('draft', 'sent', 'approved')
                new_active = request_id and state in ('draft', 'sent', 'approved')
                if request_id and state in ('draft', 'sent', 'approved'):
                    proposal_counts[request_id] = proposal_counts.get(request_id, 0) + 1
                    if request_id != old_request_id or old_state not in ('draft', 'sent', 'approved'):
                        reservations_to_create[request_id] = record.id
                if old_active and (not new_active or old_request_id != request_id):
                    reservations_to_release.append((old_request_id, record.id))
            if any(count > 1 for count in proposal_counts.values()):
                raise ValidationError(_('Não é possível manter mais de uma proposta ativa para a mesma solicitação.'))
            for request_id in proposal_counts:
                self._check_request_has_no_other_proposal(request_id, self.ids)
            self._reserve_request_ids(reservations_to_create)
        result = super().write(vals)
        if reservations_to_release:
            for request_id, quotation_id in reservations_to_release:
                self._release_request_reservation(request_id, quotation_id)
        return result

    def unlink(self):
        self._lock_for_update()
        request_ids = set(self.mapped('request_id').ids)
        self._lock_request_ids(request_ids)
        for request_id in request_ids:
            guards = self.env['sm.quotation.guard'].sudo().search([('request_id', '=', request_id)])
            for guard in guards:
                if guard.quotation_id.id in self.ids:
                    self._release_request_reservation(request_id, guard.quotation_id.id, self.ids)
        return super().unlink()

    # -------------------------------------------------------------------------
    # VALIDAÇÕES TÉCNICAS (CONSTRAINTS)
    # -------------------------------------------------------------------------

    @api.constrains('date_quotation')
    def _check_date_quotation(self):
        """Impede a criação de orçamentos com datas anteriores à data de criação/registo."""
        for record in self:
            if record.date_quotation:
                reference_date = record.create_date.date() if record.create_date else fields.Date.today()
                if record.date_quotation < reference_date:
                    raise ValidationError(
                        _("A data do orçamento (%s) não pode ser anterior à data de registo (%s)!")
                        % (record.date_quotation, reference_date)
                    )

    # -------------------------------------------------------------------------
    # MÉTODOS DE AÇÃO (TRANSIÇÃO DE ESTADOS)
    # -------------------------------------------------------------------------

    def action_send_quotation(self):
        """Altera o estado para Enviado"""
        self._lock_for_update()
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Só é possível enviar orçamentos em rascunho.'))
            if not record.line_ids:
                raise UserError("Não é posssivel enviar um orçamento sem linhas de serviço!")
            record.write({'state': 'sent'})

    def action_approve(self):
        existing_order = self.env['sm.work.order']
        for rec in self:
            rec._lock_for_update()
            if rec.state not in ('draft', 'sent', 'approved'):
                raise UserError(_('Só é possível aprovar orçamentos em rascunho ou enviados.'))
            existing_order = self.env['sm.work.order'].sudo().search(
                [('quotation_id', '=', rec.id)], order='id', limit=1
            )
            if not existing_order:
                existing_order = self.env['sm.work.order'].create({
                    'quotation_id': rec.id,
                    'partner_id': rec.partner_id.id,
                    'description': f"Trabalho referente ao Orçamento {rec.name}",
                })
            if rec.state != 'approved':
                rec.write({'state': 'approved'})

        if len(self) == 1 and existing_order:
            return {
                'name': _('Ordem de Serviço'),
                'type': 'ir.actions.act_window',
                'res_model': 'sm.work.order',
                'view_mode': 'form',
                'res_id': existing_order.id,
                'target': 'current',
            }

    # Atualizar o método action_refuse para abrir o Wizard em pop-up:
    def action_refuse(self):
        """Abre a caixa de diálogo (Wizard) para solicitar o motivo da recusa"""
        self.ensure_one()
        if self.state not in ('draft', 'sent'):
            raise UserError(_('Só é possível recusar orçamentos em rascunho ou enviados.'))
        return {
            'name': _('Recusar Orçamento'),
            'type': 'ir.actions.act_window',
            'res_model': 'sm.quotation.refuse.wizard',
            'view_mode': 'form',
            'target': 'new',  # 'new' faz abrir como janela pop-up (Modal)
            'context': {
                'default_quotation_id': self.id,
            }
        }

    def action_confirm_refuse(self, reason):
        self.ensure_one()
        self._lock_for_update()
        if self.state not in ('draft', 'sent'):
            raise UserError(_('Só é possível recusar orçamentos em rascunho ou enviados.'))
        self.write({'state': 'refused', 'refuse_reason': reason})

    def action_draft(self):
        """Restaurar o orçamento para o estado de Rascunho"""
        self._lock_for_update()
        for record in self:
            if record.state != 'refused':
                raise UserError(_('Apenas orçamentos recusados podem ser restaurados para rascunho.'))
            record.write({'state': 'draft'})


class SmQuotationGuard(models.Model):
    _name = 'sm.quotation.guard'
    _description = 'Reserva de Orçamento Ativo por Solicitação'

    request_id = fields.Many2one(
        'sm.service.request',
        required=True,
        ondelete='cascade',
    )
    quotation_id = fields.Many2one(
        'sm.quotation',
        ondelete='cascade',
    )

    _sql_constraints = [
        ('request_id_uniq', 'unique(request_id)', 'An active quotation is already reserved for this request.'),
        ('quotation_id_uniq', 'unique(quotation_id)', 'A quotation can only reserve one request.'),
    ]

    def init(self):
        self.env.cr.execute("""
            INSERT INTO sm_quotation_guard
                (request_id, quotation_id, create_uid, create_date, write_uid, write_date)
            SELECT DISTINCT ON (request_id)
                request_id, id, 1, NOW(), 1, NOW()
            FROM sm_quotation
            WHERE request_id IS NOT NULL AND state IN ('draft', 'sent', 'approved')
            ORDER BY request_id, id
            ON CONFLICT (request_id) DO NOTHING
        """)