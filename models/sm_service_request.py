# -*- coding: utf-8 -*-

from odoo import models, fields


class SmServiceRequest(models.Model):
    _name = 'sms.service.request'
    _description = 'Solicitação de Serviço'
    _order = 'create_date desc'

    name = fields.Char(
        string='Número da Solicitação',
        required=True,
        copy=True,
        readonly=True,
        defaut='Novo'
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