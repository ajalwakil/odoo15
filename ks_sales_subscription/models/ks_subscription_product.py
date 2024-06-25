# -*- coding: utf-8 -*-
from odoo import models, fields,api,_
from odoo.exceptions import ValidationError

class KsProductTemplate(models.Model):
    _inherit = "product.template"

    ks_recurring_invoice = fields.Boolean('Is Subscription Product')
    ks_subscription_plan_id = fields.Many2one('ks.sale.subscription.template', string='Subscription Plan')

    @api.constrains('type', 'detailed_type')
    def _constrains_detailed_type(self):
        type_mapping = self._detailed_type_mapping()
        for record in self:
            record.type = type_mapping.get(record.detailed_type, record.detailed_type)
            if record.type != type_mapping.get(record.detailed_type, record.detailed_type):
                raise ValidationError(_("The Type of this product doesn't match the Detailed Type"))