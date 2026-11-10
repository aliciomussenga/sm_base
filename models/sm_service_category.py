# -*- coding: utf-8 -*-
from odoo import models, fields, _, api

class SmServiceCategory(models.Model):
    _name = 'sm.service.category'
    _description = 'Categoria de Serviço'
    _order = 'name'

    name = fields.Char(string='Nome da Categoria', required=True)
    description = fields.Text(string='Descrição')
    service_ids = fields.One2many('sm.service', 'category_id')
    service_count = fields.Integer(compute='_compute_service_count', store=True)

    @api.depends('service_ids')  
    def _compute_service_count(self):
        
        for rec in self:
            rec.service_count = len(rec.service_ids)

    def open_service_ids (self):
        return {
            'name': _("Related Service"),
            'type': 'ir.actions.act_window',
            'res_model': 'sm.service',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [('category_id', '=', self.id)],
            'context': {"default_category_id": self.id}
        }