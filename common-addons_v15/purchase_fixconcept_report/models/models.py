# -*- coding: utf-8 -*-

from odoo import models, fields, api
from num2words import num2words


class PurchaseOrderFix(models.Model):
    _inherit = 'purchase.order'

    po_type = fields.Char(string='PO Type')
    project_name_no = fields.Char(string='Project Name and No')
    requistion_no = fields.Char(string='Requistion No')
    delivery_period = fields.Char(string='Deliver Period')
    shipping_location = fields.Text(string='Shipping To Location')
    shipping_marks = fields.Text(string='Shipping Marks')
    prepared_by = fields.Date(string='Date Prepared By')
    Approved_by = fields.Date(string='Date Approved By')


    def amount_to_text(self, credit, currency):
        convert_amount_in_words = currency.amount_to_text(credit)
        # convert_amount_in_words = convert_amount_in_words.replace(' Rupees', ' Only ')
        return convert_amount_in_words

    def amount_word(self, amount):
        language = self.partner_id.lang or 'en'
        language_id = self.env['res.lang'].search([('code', '=', 'ar_001')])
        if language_id:
            language = language_id.iso_code
        amount_str = str('{:2f}'.format(amount))
        amount_str_splt = amount_str.split('.')
        before_point_value = amount_str_splt[0]
        after_point_value = amount_str_splt[1][:2]
        before_amount_words = num2words(int(before_point_value), lang=language)
        after_amount_words = num2words(int(after_point_value), lang=language)
        amount = before_amount_words + ' ' + after_amount_words
        return amount
