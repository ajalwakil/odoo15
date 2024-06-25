# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression


class ProductProductInherit(models.Model):
	_inherit = "product.product"


	cc_product = fields.Boolean(default=False, string="Is Childcare Product");
	fees_type = fields.Selection([("1","Monthly"),("2","Yearly")], string="Fees Duration", default="1");