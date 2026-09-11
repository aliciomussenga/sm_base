# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SmServiceRequest(models.Model):
    _name = 'sm.service.request'
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
        required=True
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
        for rec in self:
            rec.state = 'in_analysis'

    def action_cancel(self):
        """Cancela a solicitação de serviço."""
        for rec in self:
            rec.state = 'cancel'