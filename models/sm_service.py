from odoo import models, fields

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
        help='Identificador único do serviço (ex: SERV-001)'
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