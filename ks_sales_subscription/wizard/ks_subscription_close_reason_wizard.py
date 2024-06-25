# -*- coding: utf-8 -*-
from odoo import api, fields, models
import datetime


class KsSubscriptionCloseReasonWizard(models.TransientModel):
    _name = "ks.subscription.close.reason.wizard"
    _description = 'Subscription Close Reason'

    ks_reason_close_id = fields.Many2one("ks.subscription.close.reason", string="Close Reason", required=True)

    def ks_button_close(self):
        self.ensure_one()
        ks_close_state = self.env.ref('ks_sales_subscription.ks_subscription_stage_closed').id
        ks_template_id = self.env.ref('ks_sales_subscription.ks_subscription_close_customer_call')
        ks_subscription = self.env['ks.sale.subscription'].browse(self.env.context.get('active_id'))
        ks_subscription.sudo().write({'ks_stage_id': ks_close_state, 'ks_reason_close_id': self.ks_reason_close_id})
        # ks_subscription.ks_reason_close_id = self.ks_reason_close_id
        for due_invoice in ks_subscription.ks_account_invoice_ids:
            if due_invoice.state in ['draft', 'posted']:
                due_invoice.button_cancel()
        if ks_template_id:
            values = ks_template_id.generate_email(ks_subscription.id, ['subject', 'body_html', 'email_from', 'partner_to'])
            values['email_to'] = ks_subscription.ks_partner_id.email
            values['email_cc'] = ks_subscription.ks_user_id.email
            values['email_from'] = ks_subscription.env.user.email
            values['body_html'] = values['body_html']
            mail = self.env['mail.mail'].sudo().create(values)
            try:
                mail.send()
            except Exception:
                pass
