# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from typing import DefaultDict
from odoo import models, fields, api


class Qr_elements(models.Model):
    _name = 'sh.pos.config.qr.elements'
    _description = 'pos config qr elements'

    fields_id = fields.Selection(
        [('pos_reference', 'Receipt Number'), ('create_date', 'Created on'), ('write_date', 'Last Update on'), ('amount_paid', 'Amount Paid'), ('amount_return', 'Amount Change'), ('date_order', 'Date'), ('customer_vat', 'Customer VAT'), ('sh_cr_no', 'Customer CR No.'), ('price_total', 'Total Price'), ('sequence_number', 'Sequence Number'), ('amount_before_tax', 'Amount Before VAT'), ('price_included_taxt_total', 'Total Amount (Included VAT)'), ('config_id', 'Point of Sale'), ('amount_vat', 'VAT Amount'), ('partner_id', 'Customer'), ('company_name', 'Seller'), ('company_vat_no', 'Company VAT No'), ('company_cr_no', 'Company CR No')])
    label = fields.Char(string='Label')
    custom_field = fields.Many2one('pos.config', 'field')

    @api.onchange('fields_id')
    def _onchange_field(self):
        selections = self.fields_get()["fields_id"]["selection"]
        value = next((v[1] for v in selections if v[0]
                     == self.fields_id), self.fields_id)
        self.label = value


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.model
    def _default_qr_elements(self):
        return [
            (0, 0, {'fields_id': 'pos_reference', 'label': '#'}),
            (0, 0, {'fields_id': 'date_order', 'label': 'Date'}),
            (0, 0, {'fields_id': 'company_name', 'label': 'Seller'}),
            (0, 0, {'fields_id': 'customer_vat', 'label': 'Customer VAT'}),
            (0, 0, {'fields_id': 'price_included_taxt_total', 'label': 'Total Amount (Included VAT)'}),
            (0, 0, {'fields_id': 'amount_before_tax',
             'label': 'Amount Before VAT'}),
            (0, 0, {'fields_id': 'amount_vat', 'label': 'VAT Amount'}),
        ]

    display_qr_code = fields.Boolean(string='Show QR Code In Receipt')
    qr_code_setting = fields.Selection(
        [('top', 'Top'), ('bottom', 'Bottom')], string='QR Code Position', default='bottom')
    sh_display_arabic_name = fields.Boolean(
        string='Display Product Arabic Name',)
    sh_display_arabic_address = fields.Boolean(
        string='Display Arabic Address',)
    qr_code_height = fields.Integer(
        string='QR Code Size \n (Width x Height)', default=120)
    qr_code_width = fields.Integer(string='QR code Width', default=120)
    show_return_order_ref = fields.Boolean(string='Show Return Order Reference')


class Productinherit(models.Model):
    _inherit = 'product.product'

    sh_arabic_name = fields.Char(string='Custom Name')

class ProductTemplateinherit(models.Model):
    _inherit = 'product.template'

    sh_arabic_name = fields.Char(string='Custom Name', related='product_variant_ids.sh_arabic_name', readonly=False)

    @api.model
    def create(self, vals):
        res = super(ProductTemplateinherit, self).create(vals)
        if vals.get("sh_arabic_name", False):
            tags = vals.get("sh_arabic_name")
            if res and res.product_variant_id:
                res.product_variant_id.sh_arabic_name = tags

        return res



class PaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    sh_payment_method_arabic_name = fields.Char(
        string='Payment Method Arabic Name')


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    sh_arabic_name = fields.Char(string='Arabic Name')
    arabic_street = fields.Char(string='Arabic Street...')
    arabic_street2 = fields.Char(string='Arabic Street2...')
    arabic_city = fields.Char(string='Arabic City')
    arabic_zip = fields.Char(string='Arabic Zip')


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    sh_cr_no = fields.Char(string='CR No.')

