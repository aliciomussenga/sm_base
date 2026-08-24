# -*- coding: utf-8 -*-
from odoo import models, fields

class SmServiceCategory(models.Model):
    _name = 'sm.service.category'
    _description = 'Categoria de Serviço'
    _order = 'name'

    name = fields.Char(string='Nome da Categoria', required=True)
    description = fields.Text(string='Descrição')