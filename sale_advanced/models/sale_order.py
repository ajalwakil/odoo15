# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import models, fields, api,_


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_terms_and_conditions = fields.Text(string='Terms and Conditions')
    arabic_sale_terms_and_conditions = fields.Text(string='Terms and Conditions')
    next_number = fields.Integer(default=1,copy=False)
    sale_reversion_id = fields.Many2one("sale.order")
    versioned = fields.Boolean(copy=False)
    sale_order_ids = fields.One2many(comodel_name="sale.order", inverse_name="sale_reversion_id",  string="Sales Orders", required=False, readonly=1)


    @api.model
    def default_get(self, fields):
        res = super(SaleOrder, self).default_get(fields)
        sale_terms_and_conditions = self.env["ir.config_parameter"].sudo().get_param(
            "sale_advanced.sale_terms_and_conditions", False)
        arabic_sale_terms_and_conditions = self.env["ir.config_parameter"].sudo().get_param(
            "sale_advanced.arabic_sale_terms_and_conditions", False)
        res.update({
            'sale_terms_and_conditions': sale_terms_and_conditions or False,
            'arabic_sale_terms_and_conditions': arabic_sale_terms_and_conditions or False,
                    })
        return res





