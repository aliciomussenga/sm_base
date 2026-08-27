# -*- coding: utf-8 -*-
from odoo import models, fields

class SmTag(models.Model):
    _name = 'sm.tag'
    _description = 'Etiqueta de Classificação'
    _order = 'name asc'

    name = fields.Char(
        string='Nome da Etiqueta',
        required=True,
        translate=True
    )

    color = fields.Integer(
        string='Índice de cor',
        help='Cor utilizada para exibição visual nos selectores (Widget Kanban/Tags)'
    )

    active = fields.Boolean(
        string='Ativo',
        default=True
    )