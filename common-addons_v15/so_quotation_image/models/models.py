# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order"

    show_image = fields.Boolean(string="Show Image", default=False)

