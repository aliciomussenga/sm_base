from odoo import models, fields, _
from odoo.exceptions import UserError

class SmQuotationRefuseWizard(models.TransientModel):
    _name = 'sm.quotation.refuse.wizard'
    _description = 'Assistant de Recusa de Orçamento'

    quotation_id = fields.Many2one(
        'sm.quotation',
        string='Orçameto',
        required=True,
        ondelete='cascade',
    )
    reason = fields.Text(
        string='Motivo da Recusa',
        required=True
    )

    def action_confirm_refuse(self):
        """Confirma a recusa e grava o motivo no orçamento"""
        self.ensure_one()
        if not self.reason:
            raise UserError(_("É obrigatório indeicar o motivo da recusa"))

        # Atualiza o orçamento associado
        self.quotation_id.write({
            'state': 'refused',
            'refuse_reason': self.reason,
        })