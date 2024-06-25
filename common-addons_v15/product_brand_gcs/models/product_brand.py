# -*- coding: utf-8 -*-
#!/usr/bin/python3
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging   
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError
_logger = logging.getLogger(__name__)

class ProductBrandGCS(models.Model):
    _name = "product.brand.gcs"
    _description = "Product Brand GCS"
    
    name = fields.Char("Brand Name", index=True, required=True, copy=False, help="Product brand")