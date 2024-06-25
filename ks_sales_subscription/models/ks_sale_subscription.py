# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
import logging

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_date

_logger = logging.getLogger(__name__)


class KsSaleSubscription(models.Model):
    _name = "ks.sale.subscription"
    _rec_name = 'ks_name'
    _description = "Subscription"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _ks_get_default_pricelist(self):
        return self.env['product.pricelist'].search([('currency_id', '=', self.env.user.company_id.currency_id.id)],
                                                    limit=1).id

    ks_name = fields.Char(track_visibility="always")
    ks_code = fields.Char(string="Reference", required=True, track_visibility="onchange", index=True, copy=False)
    ks_partner_id = fields.Many2one('res.partner', string='Customer', required=True, auto_join=True)
    ks_pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', default=_ks_get_default_pricelist,
                                      required=True)
    ks_currency_id = fields.Many2one('res.currency', related='ks_pricelist_id.currency_id', string='Currency',
                                     readonly=True)
    ks_company_id = fields.Many2one('res.company', string="Company",
                                    default=lambda s: s.env['res.company']._company_default_get(), required=True)
    ks_sale_id = fields.Many2one('sale.order', string='Sale')
    ks_date_start = fields.Date(string='Start Date', default=fields.Date.today, readonly=True)
    ks_buf_date = fields.Date(string='Buffer Date', readonly=True)
    ks_stage_id = fields.Many2one('ks.subscription.stage', string='Stage', index=True,
                                  default=lambda sub: sub.ks_load_default_stage(),
                                  group_expand='_ks_read_group_stage_ids', track_visibility='onchange')
    ks_end_date = fields.Date(string='End Date', track_visibility='onchange')
    ks_account_invoice_ids = fields.Many2many('account.move', 'rel_subscription_invoice', 'subscription_id',
                                              'invoice_id', string="Invoice")
    ks_reason_close_id = fields.Many2one('ks.subscription.close.reason', string="Close Reason",
                                         track_visibility='onchange')
    ks_recurring_next_date = fields.Date(string='Next Invoice', default=fields.Date.today)
    ks_user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
                                 default=lambda self: self.env.user)
    ks_sale_team_id = fields.Many2one('crm.team', 'Sales Team', change_default=True, default=False)
    ks_template_id = fields.Many2one('ks.sale.subscription.template', string='Subscription Plan', required=True,
                                     track_visibility='onchange')
    ks_recurring_rule_boundary = fields.Selection([
        ('unlimited', 'Unlimited'),
        ('limited', 'Limited')
    ], string='Duration', default='unlimited', related='ks_template_id.ks_recurring_rule_boundary')
    ks_to_renew = fields.Boolean(string='To Renew', default=False, copy=False)
    ks_invoice_count = fields.Integer(string="Invoices", compute='_ks_invoice_count')
    ks_sale_count = fields.Integer(string="sale", compute='_ks_compute_sale_count')
    ks_analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
                              default=lambda self: self.env.user)
    ks_payment_token_id = fields.Many2one('payment.token', 'Payment Token',
                                          help='If not set, the default payment token of the partner will be used.',
                                          domain="[('partner_id','=',partner_id)]", oldname='payment_method_id')

    ks_to_renew = fields.Boolean(string='Renew Subscription')
    ks_in_progress = fields.Boolean(related='ks_stage_id.ks_in_progress')
    ks_payment_mode = fields.Selection(related='ks_template_id.ks_payment_mode', readonly=False)
    ks_recurring_rule_count = fields.Integer(string="End After", default=1,
                                             related="ks_template_id.ks_recurring_rule_count")
    ks_recurring_rule_type = fields.Selection(string='Recurrence',
                                              help="Invoice automatically repeat at specified interval",
                                              related="ks_template_id.ks_recurring_rule_type", readonly=1)
    ks_recurring_interval = fields.Integer(string='Repeat Every', help="Repeat every (Days/Week/Month/Year)",
                                           related="ks_template_id.ks_recurring_interval", readonly=1)
    ks_recurring_invoice_line_ids = fields.One2many('ks.sale.subscription.line', 'ks_analytic_account_id',
                                                    string='Subscriptions Invoice Lines', copy=True)
    ks_recurring_total = fields.Float(compute='_ks_compute_subscription_total', string="Recurring Price", store=True,
                                      track_visibility='onchange')
    ks_reminder_day = fields.Integer("Invoice Reminder Days")
    ks_buffer_date = fields.Date(string="Subscription buffer date", default=fields.Date.today)
    ks_recurring_rule_type_readonly = fields.Selection(string='Recurrence',
                                                       help="Invoice automatically repeat at specified interval",
                                                       related="ks_template_id.ks_recurring_rule_type_readonly",
                                                       readonly=1)

    @api.depends('ks_recurring_invoice_line_ids', 'ks_recurring_invoice_line_ids.ks_quantity',
                 'ks_recurring_invoice_line_ids.ks_price_subtotal')
    def _ks_compute_subscription_total(self):
        for total in self:
            total.ks_recurring_total = sum(ks_line.ks_price_subtotal for ks_line in total.ks_recurring_invoice_line_ids)

    def ks_load_default_stage(self):
        ks_stage = self.env['ks.subscription.stage'].search([], order='ks_sequence', limit=1)
        return ks_stage

    @api.model
    def _ks_read_group_stage_ids(self, stages, domain, order):
        return stages.sudo().search([], order=order)

    @api.model
    def default_get(self, fields):
        ks_subscription = super(KsSaleSubscription, self).default_get(fields)
        if 'ks_code' in fields:
            ks_seq_code = self.env['ir.sequence'].next_by_code('ks.sale.subscription') or 'New'
            ks_subscription['ks_code'] = ks_seq_code
        return ks_subscription

    @api.model
    def create(self, vals):
        try:
            vals['ks_code'] = vals['ks_code']
        except KeyError:
            vals['ks_code'] = (self.env.context.get('default_ks_code') or self.env['ir.sequence'].next_by_code(
                'ks.sale.subscription') or 'New')
        if vals.get('ks_name', 'New') == 'New':
            vals['ks_name'] = vals['ks_code'] + ' - ' + self.env['res.partner'].browse(
                vals.get('ks_partner_id')).name
        ks_res = super(KsSaleSubscription, self).create(vals)
        if ks_res.ks_partner_id:
            ks_res.message_subscribe(ks_res.ks_partner_id.ids)
        return ks_res

    # @api.multi
    def write(self, vals):
        for rec in self:
            if vals.get('ks_partner_id'):
                vals['ks_name'] = rec.ks_code + ' - ' + self.env['res.partner'].browse(vals['ks_partner_id']).name
            if vals.get('ks_partner_id'):
                rec.message_subscribe([vals['ks_partner_id']])
        ks_res = super(KsSaleSubscription, self).write(vals)
        return ks_res

    def ks_create_invoice(self):
        self.ks_manually_create_invoice()
        return self.ks_open_action_subscription_invoice()

    def ks_manually_create_invoice(self):
        ks_invoices = self.env['account.move']
        current_date = datetime.date.today()

        if self.ks_recurring_next_date <= current_date and self.ks_in_progress == True and self.ks_recurring_invoice_line_ids:
            ks_sub_data = self.read(fields=['id', 'ks_company_id'])
            for ks_company_id in set(data['ks_company_id'][0] for data in ks_sub_data):
                ks_sub_ids = [s['id'] for s in ks_sub_data if s['ks_company_id'][0] == ks_company_id]
                # ks_subs = self.with_company(ks_company_id).with_context(company_id=ks_company_id).browse(ks_sub_ids)
                ks_subs = self.with_company(ks_company_id).with_context(company_id=ks_company_id).browse(ks_sub_ids)
                # context_company = dict(self.env.context, company_id=ks_company_id, with_company=ks_company_id)
                for self in ks_subs:
                    self = self[0]
                    if self.ks_template_id.ks_payment_mode in ['manual']:
                        try:
                            ks_invoice_values = self.with_context(lang=self.ks_partner_id.lang)._ks_prepare_invoice()
                            ks_new_invoice = self.env['account.move'].with_context(type='out_invoice',
                                                                                   company_id=ks_company_id). \
                                with_company(ks_company_id).create(ks_invoice_values)
                            ks_new_invoice.message_post_with_view(
                                'mail.message_origin_link',
                                values={'self': ks_new_invoice, 'origin': self},
                                subtype_id=self.env.ref('mail.mt_note').id)
                            # ks_new_invoice.with_context(context_company).compute_taxes()
                            ks_invoices += ks_new_invoice
                            next_date = self.ks_recurring_next_date or current_date
                            periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
                            invoicing_period = relativedelta(
                                **{periods[
                                       self.ks_recurring_rule_type]: self.ks_recurring_interval})
                            new_date = next_date + invoicing_period
                            self.write({'ks_recurring_next_date': new_date.strftime('%Y-%m-%d'),
                                        'ks_buffer_date': new_date.strftime('%Y-%m-%d'),
                                        'ks_reminder_day': 1,
                                        'ks_account_invoice_ids': [(4, ks_new_invoice.id)]})
                        except Exception:
                            _logger.exception('Fail to create recurring invoice for subscription %s',
                                              self.ks_code)

        return ks_invoices

    def ks_create_next_invoice(self, automatic=False):

        ks_invoices = self.env['account.move']
        current_date = datetime.date.today()

        ks_subscription = self if len(self) > 0 else self.search(
            [('ks_recurring_next_date', '<=', current_date), '|', ('ks_in_progress', '=', True),
             ('ks_to_renew', '=', True)])

        if ks_subscription:
            ks_sub_data = ks_subscription.read(fields=['id', 'ks_company_id'])
            for ks_company_id in set(data['ks_company_id'][0] for data in ks_sub_data):
                ks_sub_ids = [s['id'] for s in ks_sub_data if s['ks_company_id'][0] == ks_company_id]
                ks_subs = self.with_company(ks_company_id).with_context(company_id=ks_company_id).browse(ks_sub_ids)
                # context_company = dict(self.env.context, company_id=ks_company_id, with_company=ks_company_id)
                for ks_subscription in ks_subs:
                    ks_subscription = ks_subscription[0]

                    # invoice (only by cron)
                    if ks_subscription.ks_template_id.ks_payment_mode in ['draft_invoice', 'validate_send']:
                        try:
                            ks_invoice_values = ks_subscription.with_context(lang=ks_subscription.ks_partner_id.lang
                                                                             )._ks_prepare_invoice()
                            ks_new_invoice = self.env['account.move'].with_context(type='out_invoice',
                                                                                   company_id=ks_company_id). \
                                with_company(ks_company_id).create(ks_invoice_values)
                            ks_new_invoice.message_post_with_view(
                                'mail.message_origin_link',
                                values={'self': ks_new_invoice, 'origin': ks_subscription},
                                subtype_id=self.env.ref('mail.mt_note').id)
                            # ks_new_invoice.with_context(context_company).compute_taxes()
                            ks_invoices += ks_new_invoice
                            next_date = ks_subscription.ks_recurring_next_date or current_date
                            periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
                            invoicing_period = relativedelta(
                                **{periods[
                                       ks_subscription.ks_recurring_rule_type]: ks_subscription.ks_recurring_interval})
                            new_date = next_date + invoicing_period
                            ks_subscription.write({'ks_recurring_next_date': new_date.strftime('%Y-%m-%d'),
                                                   'ks_buffer_date': new_date.strftime('%Y-%m-%d'),
                                                   'ks_account_invoice_ids': [(4, ks_new_invoice.id)]})

                            if ks_subscription.ks_template_id.ks_payment_mode == 'validate_send':
                                ks_subscription.ks_validate_and_send_invoice(ks_new_invoice)


                        except Exception:
                            _logger.exception('Failed to create recurring invoice for subscription %s',
                                              ks_subscription.ks_code)
        return ks_invoices

    def ks_sub_set_to_renew(self):
        return self.write({'to_renew': True})

    @api.model
    def _ks_cron_create_next_invoice(self):
        return self.ks_create_next_invoice(automatic=True)

    def _ks_prepare_invoice(self):
        ks_invoice = self._ks_prepare_invoice_data()
        ks_invoice['invoice_line_ids'] = self._ks_prepare_invoice_lines(ks_invoice['fiscal_position_id'])
        return ks_invoice

    def _ks_return_invoice_data(self, ks_address, ks_journal, ks_fpos_id, sale_order, ks_company, ks_next_date,
                                ks_end_date):
        return {
            # 'account_id': self.ks_partner_id.property_account_receivable_id.id,
            'move_type': 'out_invoice',
            'partner_id': ks_address['invoice'],
            'partner_shipping_id': ks_address['delivery'],
            'currency_id': self.ks_pricelist_id.currency_id.id,
            'journal_id': ks_journal.id,
            'invoice_origin': self.ks_code,
            'fiscal_position_id': ks_fpos_id,
            'invoice_payment_term_id': sale_order.payment_term_id.id if sale_order else self.ks_partner_id.property_payment_term_id.id,
            'company_id': ks_company.id,
            'narration': _("This invoice covers the following period: %s - %s") %
                         (format_date(self.env, ks_next_date), format_date(self.env, ks_end_date)),
            'invoice_user_id': self.ks_user_id.id,
            'invoice_date': self.ks_recurring_next_date,
            'ks_sub_buffer_date': self.ks_buffer_date,
        }

    def _ks_prepare_invoice_data(self):
        self.ensure_one()

        if not self.ks_partner_id:
            raise UserError(_("Chose Customer for Subscription %s!") % self.ks_name)

        # if 'with_company' in self.env.context:
        #     ks_company = self.env['res.company'].browse(self.env.context['with_company'])
        # else:
        #     ks_company = self.ks_company_id
        #     self = self.with_context(with_company=ks_company.id, company_id=ks_company.id)

        ks_company = self.env.company or self.ks_company_id

        ks_fpos_id = self.env['account.fiscal.position'].get_fiscal_position(self.ks_partner_id.id)
        ks_journal = self.ks_template_id.ks_journal_id or self.env['account.journal'].search(
            [('type', '=', 'sale'), ('company_id', '=', ks_company.id)], limit=1)
        if not ks_journal:
            raise UserError(_('Please define a sale journal for the company "%s".') % (ks_company.name or '',))

        ks_next_date = fields.Date.from_string(self.ks_recurring_next_date)
        if not ks_next_date:
            raise UserError(_('Please define Date of Next Invoice of "%s".') % (self.ks_name,))
        ks_time_periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
        ks_end_date = ks_next_date + relativedelta(
            **{ks_time_periods[self.ks_recurring_rule_type]: self.ks_recurring_interval})
        ks_end_date = ks_end_date - relativedelta(
            days=1)  # remove 1 day as normal people thinks in term of inclusive ranges.
        ks_address = self.ks_partner_id.address_get(['delivery', 'invoice'])

        sale_order = self.env['sale.order'].search([('order_line.ks_subscription_id', 'in', self.ids)], order="id desc",
                                                   limit=1)
        ks_return_dict_data = self._ks_return_invoice_data(ks_address, ks_journal, ks_fpos_id, sale_order, ks_company,
                                                           ks_next_date, ks_end_date)
        return ks_return_dict_data
    def _ks_prepare_invoice_line(self, ks_line, ks_fiscal_position):
        ks_company = self.env.company or ks_line.ks_analytic_account_id.ks_company_id
        ks_tax_ids = ks_line.ks_product_id.taxes_id.filtered(lambda t: t.company_id == ks_company)
        if ks_fiscal_position:
            ks_tax_ids = self.env['account.fiscal.position'].browse(ks_fiscal_position).map_tax(ks_tax_ids)
        return {
            'name': ks_line.ks_name,
            # 'account_id': ks_account_id,
            'analytic_account_id': ks_line.ks_analytic_account_id.ks_analytic_account_id.id,
            'ks_subscription_id': self.id,
            'price_unit': ks_line.ks_price_unit or 0.0,
            'discount': ks_line.ks_discount,
            'quantity': ks_line.ks_quantity,
            'product_uom_id': ks_line.ks_uom_id.id,
            'product_id': ks_line.ks_product_id.id,
            'tax_ids': [(6, 0, ks_tax_ids.ids)],
            # 'analytic_tag_ids': [(6, 0, line.ks_analytic_account_id.ks_analytic_account_id.tag_ids.ids)]
        }

    def _ks_prepare_invoice_lines(self, ks_fiscal_position):
        self.ensure_one()
        ks_fiscal_position = self.env['account.fiscal.position'].browse(ks_fiscal_position)
        return [(0, 0, self._ks_prepare_invoice_line(ks_line, ks_fiscal_position)) for ks_line in
                self.ks_recurring_invoice_line_ids]

    def ks_validate_and_send_invoice(self, ks_invoice):
        self.ensure_one()
        ks_invoice.post()

    @api.depends('ks_account_invoice_ids')
    def _ks_invoice_count(self):
        for invoice_count in self:
            invoice_count.ks_invoice_count = len(invoice_count.ks_account_invoice_ids)

    def _ks_compute_sale_count(self):
        for count_sale in self:
            count_sale.ks_sale_count = len(self.env['sale.order.line'].search(
                [('ks_subscription_id', '=', count_sale.id)]).mapped('order_id'))

    def _ks_return_sales_view(self, ks_sales):
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "views": [[self.env.ref('sale.view_order_tree').id, "tree"],
                      [self.env.ref('sale.view_order_form').id, "form"],
                      [False, "kanban"], [False, "calendar"], [False, "pivot"], [False, "graph"]],
            "domain": [["id", "in", ks_sales.ids]],
            "context": {"create": False},
            "name": _("Sales Orders"),
        }

    def ks_open_sales_action(self):
        self.ensure_one()
        ks_sales = self.env['sale.order'].search([('order_line.ks_subscription_id', 'in', self.ids)])
        ks_sale_return = self._ks_return_sales_view(ks_sales)
        return ks_sale_return

    def ks_open_action_subscription_invoice(self):
        ks_invoices = self.mapped('ks_account_invoice_ids')
        ks_action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        ks_action["context"] = {"create": False}
        if len(ks_invoices) > 1:
            ks_action['domain'] = [('id', 'in', ks_invoices.ids)]
        elif len(ks_invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in ks_action:
                ks_action['views'] = form_view + [(state, view) for state, view in ks_action['views'] if view != 'form']
            else:
                ks_action['views'] = form_view
            ks_action['res_id'] = ks_invoices.ids[0]
        else:
            ks_action = {'type': 'ir.actions.act_window_close'}
        return ks_action

    @api.constrains('ks_reminder_day')
    def _ks_reminder_days(self):
        ks_diff_date = self.ks_recurring_next_date - self.ks_date_start
        if ks_diff_date.days < self.ks_reminder_day:
            raise ValidationError(_("Reminder days can not be greater then Subscription start date!. "))

    def ks_cron_subscription_close(self):
        template_id = self.env.ref('ks_sales_subscription.ks_subscription_close_email_template')
        ks_subscription = self.env['ks.sale.subscription'].search([])
        ks_current_date = datetime.date.today()
        ks_close_state = self.env.ref('ks_sales_subscription.ks_subscription_stage_closed').id
        ks_close_reason = self.env.ref('ks_sales_subscription.ks_subscription_close_reason_4').id
        for rec in ks_subscription:
            if rec.ks_end_date and rec.ks_end_date == ks_current_date and template_id:
                rec.write({'ks_stage_id': ks_close_state, 'ks_reason_close_id': ks_close_reason})
                values = template_id.generate_email(rec.id,
                                                    ['subject', 'body_html', 'email_from', 'email_to', 'partner_to',
                                                     'email_cc'])
                values['email_to'] = rec.ks_partner_id.email
                values['email_cc'] = rec.ks_user_id.email
                values['email_from'] = rec.env.user.email
                values['body_html'] = values['body_html']
                mail = self.env['mail.mail'].create(values)
                try:
                    mail.send()
                except Exception:
                    pass

    def ks_crone_next_invoice_subscription_reminder(self):
        ks_template_id = self.env.ref('ks_sales_subscription.ks_subscription_before_next_invoice_reminder')
        ks_inv_template_id = self.env.ref('ks_sales_subscription.ks_subscription_after_next_invoice_reminder')
        ks_subscription = self.env['ks.sale.subscription'].search([])
        ks_current_date = datetime.date.today()
        for rec in ks_subscription:
            ks_reminder_date = rec.ks_recurring_next_date - relativedelta(days=rec.ks_reminder_day)
            if ks_reminder_date <= ks_current_date < rec.ks_recurring_next_date and ks_template_id:
                values = ks_template_id.generate_email(rec.id,
                                                       ['subject', 'body_html', 'email_from', 'email_to', 'partner_to',
                                                        'email_cc'])
                values['email_to'] = rec.ks_partner_id.email
                values['email_cc'] = rec.ks_user_id.email
                values['email_from'] = rec.env.user.email
                values['body_html'] = values['body_html']
                mail = self.env['mail.mail'].create(values)
                try:
                    mail.send()
                except Exception:
                    pass
            if rec.ks_account_invoice_ids:
                for ks_next_invoice in rec.ks_account_invoice_ids:
                    if ks_next_invoice.invoice_date == ks_current_date and ks_next_invoice.state in ['draft',
                                                                                                     'posted'] and \
                            ks_next_invoice.payment_state in ['not_paid', 'partial']:
                        rec.ks_buf_date = ks_next_invoice.ks_sub_buffer_date
                        values = ks_inv_template_id.generate_email(rec.id,
                                                                   ['subject', 'body_html', 'email_from', 'email_to',
                                                                    'partner_to', 'email_cc'])
                        values['email_to'] = rec.ks_partner_id.email
                        values['email_cc'] = rec.ks_user_id.email
                        values['email_from'] = rec.env.user.email
                        values['body_html'] = values['body_html']
                        mail = self.env['mail.mail'].create(values)
                        try:
                            mail.send()
                        except Exception:
                            pass

    def ks_crone_due_subscription_close(self):
        ks_subscription = self.env['ks.sale.subscription'].search([])
        ks_template_id = self.env.ref('ks_sales_subscription.ks_subscription_closed_for_due_payment')
        ks_close_state = self.env.ref('ks_sales_subscription.ks_subscription_stage_closed').id
        ks_close_reason = self.env.ref('ks_sales_subscription.ks_subscription_close_reason_5').id
        ks_current_date = datetime.date.today()
        for sub in ks_subscription:
            for due_invoice in sub.ks_account_invoice_ids:
                if due_invoice.ks_sub_buffer_date == ks_current_date and due_invoice.state in ['draft', 'posted'] \
                        and due_invoice.payment_state in ['not_paid', 'partial']:
                    due_invoice.button_cancel()
                    sub.write({'ks_stage_id': ks_close_state, 'ks_reason_close_id': ks_close_reason})
                    if ks_template_id:
                        values = ks_template_id.generate_email(sub.id,
                                                               ['subject', 'body_html', 'email_from', 'email_to',
                                                                'partner_to', 'email_cc'])
                        values['email_to'] = sub.ks_partner_id.email
                        values['email_cc'] = sub.ks_user_id.email
                        values['email_from'] = sub.env.user.email
                        values['body_html'] = values['body_html']
                        mail = self.env['mail.mail'].create(values)
                        try:
                            mail.send()
                        except Exception:
                            pass

    def ks_cancel_invoice(self):
        self.ensure_one()
        return {
            'name': _('Close Reason'),
            'res_model': 'ks.subscription.close.reason.wizard',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('ks_sales_subscription.ks_subscription_reason_close_view_form').id,
            'target': 'new',
            'context': {
                'id': self.id,
            },

        }

    def _ks_subscription_renew_order(self, ks_sub_id):
        ks_res = {}
        ks_current_date = datetime.date.today()
        if ks_sub_id and self.ks_recurring_invoice_line_ids:
            ks_subscription = self.env['ks.sale.subscription'].search([('id', '=', ks_sub_id)])
        else:
            ks_subscription = self.env['ks.sale.subscription'].search([('ks_end_date', '=', ks_current_date),
                                                                       ('ks_to_renew', '=', True)])
        for subscription in ks_subscription:
            ks_line_date = []
            for ks_line in subscription.ks_recurring_invoice_line_ids:
                ks_line_date.append((0, 0, {
                    'product_id': ks_line.ks_product_id.id,
                    'name': ks_line.ks_product_id.product_tmpl_id.name,
                    'ks_subscription_id': subscription.id,
                    'product_uom': ks_line.ks_uom_id.id,
                    'product_uom_qty': ks_line.ks_quantity,
                    'price_unit': ks_line.ks_price_unit,
                    'discount': ks_line.ks_discount,
                }))
            ks_address = subscription.ks_partner_id.address_get(['delivery', 'invoice'])
            ks_sale_order = self.env['sale.order'].search([('order_line.ks_subscription_id', 'in', self.ids)],
                                                          order="id desc", limit=1)
            ks_res[subscription.id] = {
                'pricelist_id': subscription.ks_pricelist_id.id,
                'partner_id': subscription.ks_partner_id.id,
                'partner_invoice_id': ks_address['invoice'],
                'partner_shipping_id': ks_address['delivery'],
                'currency_id': subscription.ks_pricelist_id.currency_id.id,
                'ks_subscription_management': 'renew',
                'order_line': ks_line_date,
                'analytic_account_id': subscription.ks_analytic_account_id.id,
                'origin': subscription.ks_code,
                'user_id': subscription.ks_user_id.id,
                'payment_term_id': ks_sale_order.payment_term_id.id if ks_sale_order else subscription.ks_partner_id.property_payment_term_id.id,

            }
        return ks_res

    def ks_subscription_renew(self):
        ks_sub_id = self._context.get('ks_sub_id')
        if ks_sub_id:
            values = self._ks_subscription_renew_order(self.id)
        else:
            values = self._ks_subscription_renew_order(False)

        for val in values:
            ks_sale_order = self.env['sale.order'].create(values.get(val))
            ks_sale_order.order_line._compute_tax_id()
        if ks_sub_id and values:
            return {
                "type": "ir.actions.act_window",
                "res_model": "sale.order",
                "views": [[False, "form"]],
                "res_id": ks_sale_order.id,
            }

    def ks_sub_line_clean(self):
        ks_sub_lines = self.mapped('ks_recurring_invoice_line_ids')
        ks_sub_lines.unlink()
        return True

    def ks_set_stage_open(self):
        ks_search = self.env['ks.subscription.stage'].search
        for ks_sub in self:
            ks_stage = ks_search([('ks_in_progress', '=', True), ('ks_sequence', '>=', ks_sub.ks_stage_id.ks_sequence)],
                                 limit=1)
            if not ks_stage:
                ks_stage = ks_search([('ks_in_progress', '=', True)], limit=1)
            if ks_sub.ks_to_renew == True:
                ks_sub.write({'ks_to_renew': True})
            ks_sub.write({'ks_stage_id': ks_stage.id})

    def ks_increment_invoice_period(self):
        for ks_sub in self:
            today_date = fields.Date.today()
            ks_today_date = ks_sub.ks_recurring_next_date or self.default_get(['ks_recurring_next_date'])[
                'ks_recurring_next_date']
            ks_time_periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
            ks_new_invoice_date = fields.Date.from_string(ks_today_date) + relativedelta(
                **{ks_time_periods[ks_sub.ks_recurring_rule_type]: ks_sub.ks_recurring_interval})
            ks_sub.write({'ks_recurring_next_date': ks_new_invoice_date, 'ks_buffer_date': ks_new_invoice_date})
            if ks_sub.ks_recurring_rule_boundary == 'limited' and ks_sub.ks_end_date:
                ks_sub_end = ks_sub.ks_end_date or self.default_get(['ks_end_date'])['ks_end_date']
                periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
                ks_end_date = fields.Date.from_string(ks_sub_end) + relativedelta(
                    **{periods[ks_sub.ks_recurring_rule_type_readonly]: ks_sub.ks_recurring_rule_count})
                if today_date < ks_sub.ks_end_date:
                    ks_sub.write({'ks_end_date': ks_sub.ks_end_date})
                else:
                    ks_sub.write({'ks_end_date': ks_end_date})

    @api.onchange('ks_date_start', 'ks_template_id')
    def ks_onchange_end_date(self):
        if self.ks_recurring_rule_boundary == 'limited':
            ks_time_periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
            self.ks_end_date = fields.Date.from_string(self.ks_date_start) + relativedelta(**{
                ks_time_periods[
                    self.ks_recurring_rule_type_readonly]: self.ks_template_id.ks_recurring_rule_count})
        else:
            self.ks_end_date = False

    def ks_subscription_renew_email(self):
        ks_template_id = self.env.ref('ks_sales_subscription.ks_subscription_renew_email')
        for rec in self:
            if ks_template_id:
                values = ks_template_id.generate_email(rec.id,
                                                       ['subject', 'body_html', 'email_from', 'email_to', 'partner_to',
                                                        'email_cc'])
                values['email_to'] = rec.ks_partner_id.email
                values['email_cc'] = rec.ks_user_id.email
                values['email_from'] = rec.env.user.email
                values['body_html'] = values['body_html']
                mail = self.env['mail.mail'].create(values)
                try:
                    mail.send()
                except Exception:
                    pass

    def unlink(self):
        for ks_sub in self:
            if ks_sub.ks_in_progress == True:
                raise UserError(
                    _('You can not delete a subscription until in progress state. You must first cancel it.'))
        return super(KsSaleSubscription, self).unlink()


class KsSaleSubscriptionLine(models.Model):
    _name = "ks.sale.subscription.line"

    def _ks_get_default_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    ks_product_id = fields.Many2one('product.product', string='Product', required=True)
    ks_analytic_account_id = fields.Many2one('ks.sale.subscription', string='Subscription')
    ks_name = fields.Text(string='Description', required=True)
    ks_quantity = fields.Float(string='Quantity', help="Quantity that will be invoiced.", default=1.0)
    ks_uom_id = fields.Many2one('uom.uom', default=_ks_get_default_uom_id, string='Unit of Measure', required=True)
    ks_price_unit = fields.Float(string='Unit Price', required=True)
    ks_discount = fields.Float(string='Discount (%)')
    ks_price_subtotal = fields.Float(compute='_ks_compute_line_subtotal', string='Sub Total', store=True)

    @api.onchange('ks_product_id')
    def ks_onchange_product_id(self):
        if self.ks_product_id:
            self.ks_name = self.ks_product_id.name

    @api.onchange('ks_product_id', 'ks_quantity')
    def _ks_onchange_quantity_product(self):
        if not self.ks_product_id:
            self.ks_price_unit = 0.0
        else:
            if self.ks_product_id:
                self.ks_price_unit = self.ks_product_id.list_price

    @api.depends('ks_price_unit', 'ks_quantity', 'ks_discount', 'ks_analytic_account_id.ks_pricelist_id')
    def _ks_compute_line_subtotal(self):
        ks_tax = self.env['account.tax']
        for ks_sub_line in self:
            ks_price = ks_tax._fix_tax_included_price(ks_sub_line.ks_price_unit,
                                                      ks_sub_line.ks_product_id.sudo().taxes_id, ks_tax)
            ks_sub_line.ks_price_subtotal = ks_sub_line.ks_quantity * ks_price * (
                    100.0 - ks_sub_line.ks_discount) / 100.0
            if ks_sub_line.ks_analytic_account_id.ks_pricelist_id.sudo().currency_id:
                ks_sub_line.ks_price_subtotal = ks_sub_line.ks_analytic_account_id.ks_pricelist_id.sudo().currency_id.round(
                    ks_sub_line.ks_price_subtotal)


class KsSubscriptionCloseReason(models.Model):
    _name = "ks.subscription.close.reason"
    _rec_name = 'ks_name'

    ks_name = fields.Char('Name', required=True, translate=True)
    ks_sequence = fields.Integer(default=10)


class KsSubscriptionStage(models.Model):
    _name = 'ks.subscription.stage'
    _order = 'ks_sequence, id'
    _rec_name = 'ks_name'

    ks_name = fields.Char(string='Stage Name', required=True, translate=True)
    ks_sequence = fields.Integer(default=1)
    ks_in_progress = fields.Boolean(string='In Progress', default=True)


class KsAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    ks_subscription_id = fields.Many2one('ks.sale.subscription', string='Subscriptions')


class AccountMove(models.Model):
    _inherit = 'account.move'

    ks_sub_buffer_date = fields.Date(string="Subscription Buffer Date", default=lambda self: fields.Date.today(),
                                     readonly=True)
    ks_sub_amount_total = fields.Monetary(string='Subscription Amount Paid', readonly=True)


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        ks_res = super(AccountPaymentRegister, self).action_create_payments()
        ks_template_id = self.env.ref('ks_sales_subscription.ks_subscription_payment_successfully')
        records = self.env['account.move'].browse(self._context.get('active_id'))
        for rec in records:
            for invoices in rec.invoice_line_ids:
                if invoices:
                    ks_sub = invoices.filtered(lambda x: x.ks_subscription_id)
                    if ks_sub and ks_template_id:
                        rec.ks_sub_amount_total = self.amount
                        values = ks_template_id.generate_email(rec.id,
                                                               ['subject', 'body_html', 'email_from', 'email_to',
                                                                'partner_to', 'email_cc'])
                        values['email_to'] = rec.partner_id.email
                        values['email_cc'] = rec.user_id.login
                        values['email_from'] = rec.env.user.email
                        values['body_html'] = values['body_html']
                        mail = self.env['mail.mail'].sudo().create(values)
            try:
                mail.send()
            except Exception:
                pass
        return ks_res


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    # @api.multi
    def write(self, vals):
        ks_template_id = self.env.ref('ks_sales_subscription.ks_subscription_portal_payment_successfully')
        ks_res = super(PaymentTransaction, self).write(vals)
        if vals.get('state') == 'done':
            for rec in self.invoice_ids:
                for invoices in rec.invoice_line_ids:
                    if invoices:
                        ks_sub = invoices.filtered(lambda x: x.ks_subscription_id)
                        if ks_sub and ks_template_id:
                            values = ks_template_id.generate_email(rec.id,
                                                                   ['subject', 'body_html', 'email_from', 'email_to',
                                                                    'partner_to', 'email_cc'])
                            values['email_to'] = rec.partner_id.email
                            values['email_cc'] = rec.user_id.login
                            values['email_from'] = rec.env.user.email
                            values['body_html'] = values['body_html']
                            mail = self.env['mail.mail'].sudo().create(values)
                try:
                    mail.send()
                except Exception:
                    pass
        return ks_res
