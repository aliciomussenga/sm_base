# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SmServiceRequest(models.Model):
    _name = 'sm.service.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Solicitação de Serviço'
    _order = 'create_date desc'

    name = fields.Char(
        string='Número da Solicitação',
        required=True,
        copy=True,
        readonly=True,
        default=lambda self: _('Novo'),
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        required=True,
        ondelete='restrict',
        tracking=True,
        help='Cliente que abriu a solicitação de serviço'
    )

    request_date = fields.Date(
        string='Data da solicitação',
        default=fields.Date.today,
        required=True,
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Rascunho'),
            ('in_analysis', 'Em Análise'),
            ('quoted', 'Orçamentado'),
            ('cancel', 'Cancelado')
        ],
        string='Estado',
        default='draft',
        required=True,
        tracking=True,
    )

    title = fields.Char(
        string='Título / Resumo do Problema',
        required=True
    )

    description = fields.Text(
        string='Descrição Detalhada da Necessidade'
    )

    # --- Sequência Automática no Create ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Novo') == 'Novo':
                vals['name'] = self.env['ir.sequence'].next_by_code('sm.service.request') or 'Novo'
        return super().create(vals_list)

# --- Métodos de Alteração de Estado ---
    def action_in_analysis(self):
        """Muda o estado para Em Análise."""
        records = self.sorted('id')
        if records:
            self.env.cr.execute(
                "SELECT id FROM sm_service_request WHERE id = ANY(%s) ORDER BY id FOR UPDATE",
                [records.ids],
            )
            records.invalidate_recordset(['state'])
        for rec in records:
            if rec.state != 'draft':
                raise UserError(_('Só é possível submeter solicitações em rascunho para análise.'))
            rec.write({'state': 'in_analysis'})
            self.env['sm.quotation'].create({
                'request_id': rec.id,
                'partner_id': rec.partner_id.id,
            })

    def action_cancel(self):
        """Cancela a solicitação de serviço."""
        for rec in self:
            rec.state = 'cancel'