from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestSmDocumentFlow(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'SM Phase 3 Test Customer'})
        cls.technician = cls.env['res.partner'].create({
            'name': 'SM Phase 3 Test Technician',
            'is_technician': True,
        })

    def _create_request(self):
        return self.env['sm.service.request'].create({
            'partner_id': self.partner.id,
            'title': 'SM Phase 3 duplicate guard test',
        })

    def _create_quotation(self, request=False):
        values = {'partner_id': self.partner.id}
        if request:
            values['request_id'] = request.id
        return self.env['sm.quotation'].create(values)

    def _has_tracking_for(self, record, field_name):
        return any(
            tracking_value.field_id.name == field_name
            for message in record.message_ids
            for tracking_value in message.tracking_value_ids
        )

    def test_only_one_open_quotation_per_request(self):
        request = self._create_request()
        self._create_quotation(request)
        with self.assertRaises(ValidationError):
            self._create_quotation(request)

    def test_analysis_creates_one_quotation_and_updates_request(self):
        request = self._create_request()
        request.action_in_analysis()
        quotations = self.env['sm.quotation'].search([('request_id', '=', request.id)])
        self.assertEqual(len(quotations), 1)
        self.assertEqual(request.state, 'quoted')
        with self.assertRaises(UserError):
            request.action_in_analysis()

    def test_refused_quotation_allows_replacement(self):
        request = self._create_request()
        quotation = self._create_quotation(request)
        quotation.action_confirm_refuse('SM Phase 3 test refusal')
        replacement = self._create_quotation(request)
        self.assertEqual(replacement.request_id, request)
        self.assertEqual(quotation.state, 'refused')

    def test_quotations_without_request_are_allowed(self):
        quotations = self.env['sm.quotation'].create([
            {'partner_id': self.partner.id},
            {'partner_id': self.partner.id},
        ])
        self.assertEqual(len(quotations), 2)

    def test_approval_is_idempotent_and_manual_duplicate_is_blocked(self):
        quotation = self._create_quotation()
        quotation.action_approve()
        orders = self.env['sm.work.order'].search([('quotation_id', '=', quotation.id)])
        self.assertEqual(len(orders), 1)
        orders.write({'state': 'done'})

        result = quotation.action_approve()
        self.assertEqual(result['res_model'], 'sm.work.order')
        self.assertEqual(result['res_id'], orders.id)
        self.assertEqual(
            self.env['sm.work.order'].search_count([('quotation_id', '=', quotation.id)]),
            1,
        )
        self.assertEqual(orders.state, 'done')

        with self.assertRaises(ValidationError):
            self.env['sm.work.order'].create({
                'quotation_id': quotation.id,
                'partner_id': self.partner.id,
                'description': 'SM Phase 3 duplicate order test',
            })

    def test_chatter_tracking_and_activity(self):
        request = self._create_request()
        self.env.cr.precommit.run()
        request.write({'state': 'in_analysis'})
        self.env.cr.precommit.run()
        self.assertTrue(self._has_tracking_for(request, 'state'))

        quotation = self._create_quotation()
        self.env.cr.precommit.run()
        quotation.write({'state': 'sent'})
        self.env.cr.precommit.run()
        self.assertTrue(self._has_tracking_for(quotation, 'state'))

        order = self.env['sm.work.order'].create({
            'partner_id': self.partner.id,
            'description': 'SM Phase 3 chatter test',
        })
        self.env.cr.precommit.run()
        order.write({'technician_id': self.technician.id})
        order.write({'state': 'in_progress'})
        self.env.cr.precommit.run()
        self.assertTrue(self._has_tracking_for(order, 'technician_id'))
        self.assertTrue(self._has_tracking_for(order, 'state'))

        order.activity_schedule(
            'mail.mail_activity_data_todo',
            summary='SM Phase 3 test activity',
        )
        self.assertEqual(order.activity_ids.mapped('summary'), ['SM Phase 3 test activity'])

    def test_chatter_does_not_bypass_document_access(self):
        request = self._create_request()
        restricted_user = self.env['res.users'].create({
            'name': 'SM Phase 3 Restricted User',
            'login': 'sm_phase3_restricted_user',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        with self.assertRaises(AccessError):
            request.with_user(restricted_user).read(['message_ids'])
