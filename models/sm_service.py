# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SmService(models.Model):
    _name = 'sm.service'
    _description = 'Serviço do Catálogo'
    _order = 'name'

    name = fields.Char(
        string='Nome do Serviço',
        required=True,
        index=True,
        help='Nome comercial do serviço oferecido'
    )

    code = fields.Char(
        string='Código Interno',
        required=True,
        copy=False,
        default='Novo',
        help='Identificador único do serviço (ex: SERV-001)'
    )

    category_id = fields.Many2one(
        comodel_name='sm.service.category',
        string='Categoria',
        required=True,
        ondelete='restrict',
        help='Categoria de enquadramento deste serviço'
    )

    active = fields.Boolean(
        string='Ativo',
        default=True,
        help='Permite ocultar o serviço sem apagar o histórico'
    )

    service_type = fields.Selection(
        selection=[
            ('hardware', 'Manutenção de Hardware'),
            ('software', 'Instalação / Configuração de Software'),
            ('network', 'Redes e Infraestrutura'),
            ('consulting', 'Consultoria Técnica')
        ],
        string='Tipo de Serviço',
        required=True,
        default='hardware'
    )

    price = fields.Float(
        string='Preço Base (Kz)',
        required=True,
        default=0.0,
        help='Preço padrão sugerido para o serviço'
    )

    execution_time = fields.Integer(
        string='Tempo Estimado (Horas)',
        default=1,
        help='Duração média estimada para execução'
    )
    description = fields.Text(
        string='Descrição Detalhada'
    )

    # --- Validações Técnicas ---
    @api.constrains('price')
    def _check_price(self):
        """Valida que o preço do serviço é estritamente superior a zero quando informado."""
        for rec in self:
            if rec.price is not False and rec.price is not None and rec.price <= 0:
                raise ValidationError(
                    _("O preço base do serviço '%s' deve ser estritamente superior a zero!")
                    % (rec.name or _('Novo Serviço'))
                )

    # --- Sequência Automática no Create ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('code') or vals.get('code') == 'Novo':
                vals['code'] = self.env['ir.sequence'].next_by_code('sm.service') or 'Novo'
        return super().create(vals_list)