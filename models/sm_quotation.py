# -*- coding: utf-8 -*-
from odoo import models, fields

class SmQuotation(models.Model):
    _name = 'sm.quotation'
    _description = 'Orçamento de Serviço'
    _order = 'create_date desc'

    name = fields.Char(
        string='Número de Orçamento',
        required=True,
        copy=False,
        readonly=True,
        default='Novo'
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

    amount_total = fields.Float(
        string='Valor Total (Kz)',
        default=0.0
    )