# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ['mail.thread', 'sale.order']

    ks_subscription_count = fields.Integer(compute='_ks_subscription_count', string='Count')
    ks_subscription_management = fields.Selection(string='Subscription Management',
                                                  selection=[('create', 'Creation'), ('renew', 'Renewal')],
                                                  default='create')

    # getting subscription count
    def _ks_subscription_count(self):
        for ks_sub in self:
            ks_sub_count = self.env['sale.order.line'].read_group(
                [('order_id', '=', ks_sub.id), ('ks_subscription_id', '!=', False)],
                ['ks_subscription_id'], ['ks_subscription_id'])
            ks_sub.ks_subscription_count = len(ks_sub_count)

    # preparing dict value
    def _ks_get_values(self, ks_template):
        ks_prep_values = {
            'user_id': self.user_id.id,
            'ks_sale_team_id': self.team_id.id,
            'ks_pricelist_id': self.pricelist_id.id,
            'ks_template_id': ks_template.id,
            'ks_reminder_day': ks_template.ks_reminder_day,
            'ks_partner_id': self.partner_invoice_id.id,
            'ks_user_id': self.user_id.id,
            'ks_sale_id': self.id,
            'ks_date_start': fields.Date.today(),
            'ks_company_id': self.company_id.id,
        }
        return ks_prep_values

    def _ks_subscription_data_prepare(self, ks_template):
        self.ensure_one()
        ks_values = self._ks_get_values(ks_template)
        ks_stage = self.env['ks.subscription.stage'].search([('ks_in_progress', '=', True)], limit=1)
        if ks_stage:
            ks_values['ks_stage_id'] = ks_stage.id
        ks_time_periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
        ks_values['ks_recurring_next_date'] = fields.Date.to_string(relativedelta(**{ks_time_periods[
                                                                                         ks_template.ks_recurring_rule_type]: ks_template.ks_recurring_interval}) + datetime.date.today())
        ks_values['ks_buffer_date'] = fields.Date.to_string(relativedelta(**{ks_time_periods[
                                                                                 ks_template.ks_recurring_rule_type]: ks_template.ks_recurring_interval}) + datetime.date.today())
        if ks_template.ks_recurring_rule_boundary == 'limited':
            periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
            ks_values['ks_end_date'] = fields.Date.from_string(fields.Date.today()) + relativedelta(**{
                periods[ks_template.ks_recurring_rule_type_readonly]: ks_template.ks_recurring_rule_count})
        return ks_values

    def ks_open_sale_subscriptions_action(self):
        self.ensure_one()
        ks_sub = self.order_line.mapped('ks_subscription_id')
        ks_sale_action = self.env["ir.actions.actions"]._for_xml_id(
            "ks_sales_subscription.ks_sale_subscription_action_view")
        if len(ks_sub) > 1:
            ks_sale_action['domain'] = [('id', 'in', ks_sub.ids)]
        elif len(ks_sub) == 1:
            ks_sale_action['views'] = [
                (self.env.ref('ks_sales_subscription.ks_sale_subscription_form_view').id, 'form')]
            ks_sale_action['res_id'] = ks_sub.ids[0]
        else:
            ks_sale_action = {'type': 'ir.actions.act_window_close'}
        return ks_sale_action

    def _return_subscription_line(self, ks_sale_order, ks_subscription):
        return ks_sale_order.order_line.filtered(
            lambda l: l.ks_subscription_id == ks_subscription and l.product_id.ks_recurring_invoice)

    def ks_existing_subscriptions_update(self):
        ks_res = []
        for ks_sale_order in self:
            ks_subscriptions = ks_sale_order.order_line.mapped('ks_subscription_id').sudo()
            ks_res.append(ks_subscriptions.ids)
            if ks_sale_order.ks_subscription_management == 'renew':
                # ks_subscriptions.ks_sub_line_clean()
                ks_sub_lines = ks_subscriptions.mapped('ks_recurring_invoice_line_ids')
                ks_sub_lines.unlink()
                ks_subscriptions.ks_increment_invoice_period()
                ks_subscriptions.ks_set_stage_open()
            for ks_subscription in ks_subscriptions:
                ks_subscription_lines = ks_sale_order._return_subscription_line(ks_sale_order, ks_subscription)
                ks_line_values = ks_subscription_lines._ks_subscription_line_update(ks_subscription)
                ks_subscription.write({'ks_recurring_invoice_line_ids': ks_line_values})
                ks_subscription.ks_subscription_renew_email()
                # ks_template_id = ks_subscription.env.ref('ks_sales_subscription.ks_subscription_renew_email')
                # for rec in ks_subscription:
                #     if ks_template_id:
                #         values = ks_template_id.generate_email(rec.id,
                #                                                ['subject', 'body_html', 'email_from', 'email_to',
                #                                                 'partner_to', 'email_cc'])
                #         values['email_to'] = rec.ks_partner_id.email
                #         values['email_cc'] = rec.ks_user_id.email
                #         values['email_from'] = rec.env.user.email
                #         values['body_html'] = values['body_html']
                #         mail = self.env['mail.mail'].create(values)
                #         try:
                #             mail.send()
                #         except Exception:
                #             pass
        return ks_res

    def _ks_values_subscription_create(self, ks_subscription, ks_order):
        return {'self': ks_subscription, 'origin': ks_order}

    def ks_subscriptions_create(self):
        ks_res = []
        for ks_order in self:
            create_sub = self._ks_subscription_lines_split()
            for ks_template in create_sub:
                values = self._ks_subscription_data_prepare(ks_template)
                values['ks_recurring_invoice_line_ids'] = create_sub[ks_template]._ks_subscription_line_data()
                ks_subscription = self.env['ks.sale.subscription'].sudo().create(values)
                ks_res.append(ks_subscription.id)
                create_sub[ks_template].write({'ks_subscription_id': ks_subscription.id})
                ks_subscription.message_post_with_view(
                    'mail.message_origin_link', values=self._ks_values_subscription_create(ks_subscription, ks_order),
                    subtype_id=self.env.ref('mail.mt_note').id, author_id=self.env.user.partner_id.id
                )
        return ks_res

    def _return_sub_lines(self):
        return self.order_line.filtered(
            lambda
                l: not l.ks_subscription_id and l.product_id.ks_recurring_invoice and l.product_id.ks_subscription_plan_id)

    def _return_lines(self, ks_template):
        return self.order_line.filtered(lambda l: l.product_id.ks_subscription_plan_id == ks_template)

    def _ks_subscription_lines_split(self):
        self.ensure_one()
        ks_res = {}
        kd_sub_lines = self._return_sub_lines()
        ks_templates = kd_sub_lines.mapped('product_id').mapped('ks_subscription_plan_id')
        for ks_template in ks_templates:
            lines = self._return_lines(ks_template)
            ks_res[ks_template] = lines
        return ks_res

    def _create_invoices(self, grouped=False, final=False):
        ks_res = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final)
        invoices = ks_res.invoice_line_ids.filtered(lambda x: x.ks_subscription_id)
        for ks_inv in invoices:
            if ks_inv:
                ks_inv[0].ks_subscription_id.ks_account_invoice_ids = [(4, ks_inv.move_id.id)]
        return ks_res

    # @api.multi
    def _action_confirm(self):
        ks_confirm = super(SaleOrder, self)._action_confirm()
        self.ks_existing_subscriptions_update()
        self.ks_subscriptions_create()
        return ks_confirm


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    ks_subscription_id = fields.Many2one('ks.sale.subscription', 'Subscription')

    def _prepare_invoice_line(self, **optional_values):
        ks_res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        if self.ks_subscription_id:
            ks_res.update(ks_subscription_id=self.ks_subscription_id.id)
        return ks_res

    @api.model
    def create(self, vals):
        if vals.get('order_id'):
            ks_sale_order = self.env['sale.order'].browse(vals.get('order_id'))
            ks_product = self.env['product.product']
            if ks_sale_order.origin and ks_sale_order.ks_subscription_management in ['renew'] and ks_product.browse(
                    vals.get('product_id')).ks_recurring_invoice:
                vals['ks_subscription_id'] = self.env['ks.sale.subscription'].search(
                    [('ks_code', '=', ks_sale_order.origin)], limit=1).id
        return super(SaleOrderLine, self).create(vals)

    def _ks_subscription_line_data(self):
        ks_values = []
        for order_line in self:
            ks_values.append((0, False, {
                'ks_product_id': order_line.product_id.id,
                'ks_name': order_line.name,
                'ks_quantity': order_line.product_uom_qty,
                'ks_uom_id': order_line.product_uom.id,
                'ks_price_unit': order_line.price_unit,
                'ks_discount': order_line.discount,
            }))
        return ks_values

    def _ks_subscription_line_update(self, ks_subscription):
        ks_values = []
        ks_dict = {}
        for ks_order_line in self:
            ks_sub_line = self.ks_sub_line_calc(ks_subscription.ks_recurring_invoice_line_ids, ks_order_line)
            # ks_sub_line = ks_subscription.ks_recurring_invoice_line_ids.filtered(
            #     lambda l: (l.ks_product_id, l.ks_uom_id) == (ks_order_line.product_id, ks_order_line.product_uom))
            if ks_sub_line:
                if len(ks_sub_line) > 1:
                    ks_sub_line[0].copy(
                        {'ks_name': ks_order_line.display_name, 'ks_quantity': ks_order_line.product_uom_qty})
                else:
                    ks_dict.setdefault(ks_sub_line.id, ks_sub_line.ks_quantity)
                    ks_dict[ks_sub_line.id] += ks_order_line.product_uom_qty
            else:
                ks_values.append(ks_order_line._ks_subscription_line_data()[0])

        ks_values += [(1, sub_id, {'ks_quantity': ks_dict[sub_id]}) for sub_id in ks_dict]
        return ks_values

    def ks_sub_line_calc(self, ks_recurring_invoice_line_ids, ks_order_line):
        sub_line = []
        ks_sub_line = self.env['ks.sale.subscription']
        for line in ks_recurring_invoice_line_ids:
            if (line.ks_product_id, line.ks_uom_id) == (ks_order_line.product_id, ks_order_line.product_uom):
                sub_line.append(line)
        for lines in sub_line:
            ks_sub_line = lines
        return ks_sub_line
