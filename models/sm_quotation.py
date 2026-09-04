# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class SmQuotation(models.Model):
    _name = 'sm.quotation'
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
        ondelete='restrict'
    )

    request_id = fields.Many2one(
        comodel_name='sm.service.request',
        string='Solicitação de Origem',
        ondelete='set null',
        help='Solicitação que originou este orçamento'
    )

    date_quotation = fields.Date(
        string='Data do Orçamento',
        default=fields.Date.today,
        required=True
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
        required=True
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

    refuse_reasen = fields.Text(
        string='Motivo da Recusa',
        readonly=True
    )

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
        for vals in vals_list:
            # Se o nome for 'Novo' ou estiver vazio, consome a sequência do sistema
            if vals.get('name', _('Novo')) == _('Novo'):
                vals['name'] = self.env['ir.sequence'].next_by_code('sm.quotation') or _('Novo')
        return super(SmQuotation, self).create(vals_list)

    # -------------------------------------------------------------------------
    # VALIDAÇÕES TÉCNICAS (CONSTRAINTS)
    # -------------------------------------------------------------------------

    @api.constrains('date_quotation')
    def _check_date_quotation(self):
        """Impede a criação de orçamentos com dats passadas"""
        for record in self:
            if record.date_quotation and record.date_quotation < fields.Date.today():
                raise ValidationError(_("A data so prçamento não pode ser anterior à data de hoje (%s)!") % fields.Date.today())

    # -------------------------------------------------------------------------
    # MÉTODOS DE AÇÃO (TRANSIÇÃO DE ESTADOS)
    # -------------------------------------------------------------------------

    def action_send_quotation(self):
        """Altera o estado para Enviado"""
        for record in self:
            if not record.line_ids:
                raise UserError("Não é posssivel enviar um orçamento sem linhas de serviço!")
            record.state = 'sent'

    def action_approve(self):
        """Aprovar o orçamento"""
        for record in self:
            record.state = 'approved'

    # Atualizar o método action_refuse para abrir o Wizard em pop-up:
    def action_refuse(self):
        """Abre a caixa de diálogo (Wizard) para solicitar o motivo da recusa"""
        self.ensure_one()
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


    def action_draft(self):
        """Restaurar o orçamento para o estado de Rascunho"""
        for record in self:
            record.state = 'draft'