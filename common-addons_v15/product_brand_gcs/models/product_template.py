# -*- coding: utf-8 -*-
#!/usr/bin/python3
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    product_brand_gcs = fields.Many2one("product.brand.gcs", string="Product Brand", help="Select product brand")