# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError  # ← Adicionado


class SmWorkOrder(models.Model):
    """ This model represents sm.work.order."""
    _name = 'sm.work.order'
    _description = 'Ordem de Serviço'
    _order = 'date_start desc, id desc'

    name = fields.Char(
        string='Número da OS',  # ← Corrigido
        required=True,
        readonly=True,
        default='Novo',
        copy=False,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        # ← Removido 'readonly' e 'states' (controlar na view XML)
    )
    quotation_id = fields.Many2one(
        'sm.quotation',
        string='Orçamento de Origem',
        readonly=True,
        ondelete='restrict',
    )
    request_id = fields.Many2one(
        'sm.service.request',
        string='Solicitação de Origem',
        readonly=True,
        related='quotation_id.request_id',  # ← Corrigido
        store=True,  # ← Corrigido
    )
    user_id = fields.Many2one(
        'res.users',
        string='Técnico Responsável',
        tracking=True,
    )
    date_start = fields.Datetime(
        string='Data de Início Prevista',
        default=fields.Datetime.now,
        required=True,
    )
    date_end = fields.Datetime(
        string='Data de Conclusão',
        readonly=True,
    )
    description = fields.Text(
        string='Descrição do Trabalho a Executar',
        required=True,
    )
    technical_notes = fields.Text(
        string='Notas Técnicas / Diagnóstico de Execução'
    )
    state = fields.Selection(
        [
            ('draft', 'Pendente'),
            ('in_progress', 'Em Execução'),
            ('done', 'Concluída'),
            ('cancel', 'Cancelada'),
        ],
        string='Estado',
        default='draft',
        required=True,
        tracking=True,
    )

    # --- Sequência Automática no Create ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Novo') == 'Novo':
                vals['name'] = self.env['ir.sequence'].next_by_code('sm.work.order') or 'Novo'
        return super().create(vals_list)

    # --- Botões de Transição de Estado ---
    def action_start(self):
        """Inicia a execução da Ordem de Serviço."""
        for rec in self:
            if not rec.user_id:
                raise ValidationError("É necessário atribuir um Técnico Responsável antes de iniciar a OS!")
            rec.state = 'in_progress'

    def action_complete(self):
        """Marca a Ordem de Serviço como Concluída."""
        for rec in self:
            rec.write({
                'state': 'done',
                'date_end': fields.Datetime.now(),
            })

    def action_cancel(self):
        """Cancela a Ordem de Serviço."""
        self.write({'state': 'cancel'})