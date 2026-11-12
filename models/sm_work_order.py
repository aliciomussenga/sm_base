# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError # ← Adicionado
from psycopg2 import IntegrityError


class SmWorkOrder(models.Model):
    """ This model represents sm.work.order."""
    _name = 'sm.work.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Ordem de Serviço'
    _order = 'date_start desc, id desc'

    name = fields.Char(
        string='Número da OS',  # ← Corrigido
        required=True,
        readonly=True,
        default=lambda self: _('Novo'),
        copy=False,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        tracking=True,
        # ← Removido 'readonly' e 'states' (controlar na view XML)
    )
    quotation_id = fields.Many2one(
        'sm.quotation',
        string='Orçamento de Origem',
        readonly=True,
        ondelete='restrict',
    )
    request_id = fields.Many2one(
        'sm.service.request',
        string='Solicitação de Origem',
        readonly=True,
        related='quotation_id.request_id',  # ← Corrigido
        store=True,  # ← Corrigido
    )
    technician_id = fields.Many2one(
        'res.partner',
        string='Técnico Atribuído',
        domain="[('is_technician', '=', True)]",
        tracking=True,
        help='Apenas contactos marcados como técnicos podem ser selecionados.',
    )
    date_start = fields.Datetime(
        string='Data de Início Prevista',
        default=fields.Datetime.now,
        required=True,
        tracking=True,
    )
    date_end = fields.Datetime(
        string='Data de Conclusão',
        readonly=True,
        tracking=True,
    )
    description = fields.Text(
        string='Descrição do Trabalho a Executar',
        required=True,
    )
    technical_notes = fields.Text(
        string='Notas Técnicas / Diagnóstico de Execução'
    )
    state = fields.Selection(
        [
            ('draft', 'Pendente'),
            ('in_progress', 'Em Execução'),
            ('done', 'Concluída'),
            ('cancel', 'Cancelada'),
        ],
        string='Estado',
        default='draft',
        required=True,
        tracking=True,
    )

    @api.model
    def _lock_quotation_ids(self, quotation_ids):
        quotation_ids = sorted(set(quotation_ids))
        if quotation_ids:
            self.env.cr.execute(
                "SELECT id FROM sm_quotation WHERE id = ANY(%s) ORDER BY id FOR UPDATE",
                [quotation_ids],
            )

    @api.model
    def _check_quotations_have_no_orders(self, quotation_ids, excluded_ids=()):
        for quotation_id in quotation_ids:
            domain = [('quotation_id', '=', quotation_id)]
            if excluded_ids:
                domain.append(('id', 'not in', list(excluded_ids)))
            if self.sudo().search(domain, limit=1):
                raise ValidationError(_('Este orçamento já possui uma ordem de serviço associada.'))

    @api.model
    def _reserve_quotation_ids(self, quotation_ids):
        reservations = self.env['sm.work.order.guard'].sudo()
        for quotation_id in sorted(set(quotation_ids)):
            try:
                with self.env.cr.savepoint():
                    reservations.create({'quotation_id': quotation_id})
            except IntegrityError as error:
                raise ValidationError(
                    _('Este orçamento já possui uma ordem de serviço associada.')
                ) from error

    # --- Sequência Automática no Create ---
    @api.model_create_multi
    def create(self, vals_list):
        quotation_ids = [vals['quotation_id'] for vals in vals_list if vals.get('quotation_id')]
        if len(quotation_ids) != len(set(quotation_ids)):
            raise ValidationError(_('Não é possível criar mais de uma ordem de serviço para o mesmo orçamento.'))
        self._lock_quotation_ids(quotation_ids)
        self._check_quotations_have_no_orders(quotation_ids)
        self._reserve_quotation_ids(quotation_ids)

        for vals in vals_list:
            if vals.get('name', 'Novo') == 'Novo':
                vals['name'] = self.env['ir.sequence'].next_by_code('sm.work.order') or 'Novo'
        orders = super().create(vals_list)
        for order in orders.filtered('quotation_id'):
            self.env['sm.work.order.guard'].sudo().search(
                [('quotation_id', '=', order.quotation_id.id)], limit=1
            ).write({'order_id': order.id})
        return orders

    def write(self, vals):
        if 'quotation_id' in vals:
            quotation_ids = set(self.mapped('quotation_id').ids)
            if vals.get('quotation_id'):
                quotation_ids.add(vals['quotation_id'])
            self._lock_quotation_ids(quotation_ids)
            target_quotation_id = vals.get('quotation_id')
            if target_quotation_id and len(self) > 1:
                raise ValidationError(_('Não é possível associar várias ordens ao mesmo orçamento.'))
            previous_quotation_ids = {order.id: order.quotation_id.id for order in self}
            changed_quotation_ids = [
                target_quotation_id
                for order in self
                if target_quotation_id and previous_quotation_ids[order.id] != target_quotation_id
            ]
            if changed_quotation_ids:
                self._check_quotations_have_no_orders([target_quotation_id], self.ids)
                self._reserve_quotation_ids(changed_quotation_ids)
        result = super().write(vals)
        if 'quotation_id' in vals:
            target_quotation_id = vals.get('quotation_id')
            guards = self.env['sm.work.order.guard'].sudo()
            for order in self:
                previous_quotation_id = previous_quotation_ids[order.id]
                if previous_quotation_id and previous_quotation_id != target_quotation_id:
                    guards.search([
                        ('quotation_id', '=', previous_quotation_id),
                        ('order_id', '=', order.id),
                    ]).unlink()
                if target_quotation_id and previous_quotation_id != target_quotation_id:
                    guards.search([('quotation_id', '=', target_quotation_id)], limit=1).write({
                        'order_id': order.id,
                    })
        return result

    # --- Botões de Transição de Estado ---
    def action_start(self):
        """Inicia a execução da Ordem de Serviço."""
        for rec in self:
            if not rec.technician_id:
                raise ValidationError("É necessário atribuir um Técnico Responsável antes de iniciar a OS!")
            rec.state = 'in_progress'

    def action_complete(self):
        """Marca a Ordem de Serviço como Concluída."""
        for rec in self:
            rec.write({
                'state': 'done',
                'date_end': fields.Datetime.now(),
            })

    def action_cancel(self):
        """Cancela a Ordem de Serviço."""
        self.write({'state': 'cancel'})


class SmWorkOrderGuard(models.Model):
    _name = 'sm.work.order.guard'
    _description = 'Reserva de Ordem de Serviço por Orçamento'

    quotation_id = fields.Many2one(
        'sm.quotation',
        required=True,
        ondelete='cascade',
    )
    order_id = fields.Many2one(
        'sm.work.order',
        ondelete='cascade',
    )

    _sql_constraints = [
        ('quotation_id_uniq', 'unique(quotation_id)', 'An order is already reserved for this quotation.'),
        ('order_id_uniq', 'unique(order_id)', 'An order can only reserve one quotation.'),
    ]