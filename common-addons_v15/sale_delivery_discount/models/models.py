# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"

    discount_amount = fields.Float('Discount Amount', store=True)

    @api.onchange('discount', 'product_uom_qty', 'price_unit','discount_amount')
    def onchange_discount(self):
        if self.discount:
            self.discount_amount = (self.product_uom_qty * self.price_unit * self.discount) / 100
        else:
            self.discount_amount = 0
