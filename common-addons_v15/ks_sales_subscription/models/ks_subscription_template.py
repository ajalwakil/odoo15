import datetime

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class KsSubscriptionTemplate(models.Model):
    _name = "ks.sale.subscription.template"
    _rec_name = 'ks_name'
    _inherit = "mail.thread"

    ks_name = fields.Char(required=True, string='Name')
    ks_description = fields.Text(translate=True, string="Terms and Conditions")
    ks_recurring_rule_type = fields.Selection([('daily', 'Day(s)'), ('weekly', 'Week(s)'),
                                               ('monthly', 'Month(s)'), ('yearly', 'Year(s)'), ],
                                              string='Recurrence', required=True,
                                              default='monthly', track_visibility='onchange')
    ks_recurring_interval = fields.Integer(string="Repeat Every", help="Repeat every (Days/Week/Month/Year)",
                                           required=True, default=1, track_visibility='onchange')
    ks_recurring_rule_boundary = fields.Selection([
        ('unlimited', 'Unlimited'),
        ('limited', 'Limited')
    ], string='Duration', default='unlimited')
    ks_recurring_rule_count = fields.Integer(string="End After", default=1)
    active = fields.Boolean(default=True)
    ks_auto_close_limit = fields.Integer(string="Automatic closing limit", default=15,
                                         help="Number of days before a subscription gets closed when the chosen payment mode trigger automatically the payment.")

    ks_recurring_rule_type_readonly = fields.Selection(
        string="Recurrence Unit",
        related='ks_recurring_rule_type', readonly=True, track_visibility=False)
    ks_payment_mode = fields.Selection([
        ('manual', 'Manual Invoice'),
        ('draft_invoice', 'Draft invoice'),
        ('validate_send', 'Validate Invoice'),
    ], required=True, default='draft_invoice', string='Create Invoice')
    ks_product_count = fields.Integer(string='product count', compute='_ks_product_count')
    ks_subscription_count = fields.Integer(string='Subscription Count', compute='_ks_subscription_count')
    ks_journal_id = fields.Many2one('account.journal', string="Journal", domain=[('type', '=', 'sale')],
                                    company_dependent=True)
    ks_reminder_day = fields.Integer("Invoice Reminder Days", default=1)

    @api.constrains('ks_recurring_interval', 'ks_recurring_rule_count', 'ks_reminder_day', 'ks_recurring_rule_type')
    def _ks_check_recurring_interval(self):
        if self.ks_recurring_interval <= 0:
            raise ValidationError(_("The recurring interval must be positive"))
        if self.ks_recurring_rule_boundary == 'limited' and self.ks_recurring_rule_count < self.ks_recurring_interval:
            raise ValidationError(_("Limited Plan duration must be greater then Invoice generation period!."))
        if not self.ks_month_and_year_validation(self.ks_reminder_day, self.ks_recurring_interval,
                                                 self.ks_recurring_rule_type):
            periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
            invoicing_period = relativedelta(
                **{periods[
                       self.ks_recurring_rule_type]: self.ks_recurring_interval})

            if self.ks_reminder_day > invoicing_period.days and self.ks_recurring_rule_type in ['weekly', 'daily']:
                raise ValidationError(_("Reminder days can not be greater then Invoice period. "))

    def ks_month_and_year_validation(self, ks_reminder_day, ks_recurring_interval, ks_recurring_rule_type):
        if ks_recurring_rule_type == 'yearly':
            ks_month = ks_recurring_interval * 12
        elif ks_recurring_rule_type == 'monthly':
            ks_month = ks_recurring_interval
        elif ks_recurring_rule_type in ['weekly', 'daily']:
            return False
        start_date = datetime.datetime.today()
        end_date = start_date + relativedelta(months=+ks_month)
        total_days = (end_date.date() - start_date.date()).days
        if total_days > ks_reminder_day:
            return True
        else:
            raise ValidationError(_("Reminder days can not be greater then Invoice period."))

    def _ks_subscription_count(self):
        for rec in self:
            rec.ks_subscription_count = self.env['ks.sale.subscription'].search_count(
                [('ks_template_id', 'in', rec.ids),
                 ('ks_stage_id', '!=', False)]) or 0

    def _ks_product_count(self):
        for rec in self:
            rec.ks_product_count = self.env['product.template'].search_count(
                [('ks_subscription_plan_id', 'in', rec.ids)]) or 0
