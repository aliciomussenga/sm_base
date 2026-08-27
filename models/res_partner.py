# -*- coding: utf-8 -*-
from odoo import models, fields

class ResPartner(models.Model):
    # Indica que estamos a alterar/estender o modelo nativo res.partner
    _inherit = 'res.partner'

    customer_code = fields.Char(
        string='Código de Cliente',
        copy=False,
        index=True,
        help='Código interno identificador do cliente para assistência técnica'
    )
    customer_type = fields.Selection(
        selection=[
            ('individual', 'Particular / Individual'),
            ('company', 'Empresarial / PME'),
            ('government', 'Instituição Pública / Governo')
        ],
        string='Tipo de Cliente',
        default='individual',
        help='Classificação do cliente para fins de atendimento'
    )