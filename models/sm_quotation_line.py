# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


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
    # Campo Calculado
    price_subtotal = fields.Float(
        string='Subtotal (Kz)',
        default=0.0,
        compute='_compute_price_subtotal',
        store=True
    )

    #Cálculo do Subtotal
    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit

    # Reatividade ao selecionar o serviço
    @api.onchange('service_id')
    def _onchange_service_id(self):
        if self.service_id:
            self.name = self.service_id.name
            self.price_unit = self.service_id.price

    # -------------------------------------------------------------------------
    # VALIDAÇÃO DAS LINHAS DO ORÇAMENTO
    # -------------------------------------------------------------------------

    @api.constrains('quantity', 'price_unit')
    def _check_quantities_and_prices(self):
        """Valida se a quantidades e o preço unitário são estritamente positivos"""
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_("A quantidade do serviço '%s' deve ser maior zero!") % line.service_id.name)
            if line.price_unit < 0:
                raise ValidationError(_("O preço unitário do serviço '%s' não pode ser negativo!") % line.service_id.name)