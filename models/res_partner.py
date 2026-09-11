# -*- coding: utf-8 -*-
from odoo import models, fields

class ResPartner(models.Model):
    # Indica que estamos a alterar/estender o modelo nativo res.partner
    _inherit = 'res.partner'

    is_technician = fields.Boolean(
        string='É Técnico?',
        default=False,
        help='Indica se este parceiro/contacto é um técnico prestador de serviços.',
    )
    technical_specialty = fields.Selection(
        [
            ('hardware', 'Hardware e Servidores'),
            ('network', 'Redes e Cablagem'),
            ('software', 'Sistemas e Software'),
            ('general', 'Técnico Generalista'),
        ],
        string='Especialidade Técnica',
        default='general',
    )
    certification_info = fields.Text(
        string='Certificações e Habilitações',
        help='Registo de qualificações e certificações do técnico.',
    )