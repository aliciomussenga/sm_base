# -*- coding: utf-8 -*-
from odoo import models, fields

class SmQuotationLine(models.Model):
    _name = 'sm.quotation.line'
    _description = 'Linha de Orçameto de Serviço'

    # FK Obrigatório apontando para o pai (sm.quotation)
    quotation_id = fields.Many2one(
        comodel_name = 'sm.quotation',
        string='Orçamento',
        required=True,
        ondelete='cascade', # Se o orçamento for apagado, apaga as suas linhas
        index=True,
    )

    # Serviço selecionado do nosso catálogo
    service_id = fields.Many2one(
        comodel_name = 'sm.service',
        string='Serviço',
        required=True,
        ondelete='restrict'
    )

    name = fields.Text(
        string='Descrição / Detalhes Executivos',
        required=True
    )

    quantity = fields.Float(
        string='Quantidade',
        default=1.0,
        required=True
    )

    price_unit = fields.Float(
        string='Preço Unitário (Kz)',
        required=True,
        default=0.0
    )

    price_subtotal = fields.Float(
        string='Subtotal (Kz)',
        default=0.0
    )