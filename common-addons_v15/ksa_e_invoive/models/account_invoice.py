# -*- coding: utf-8 -*-

import datetime
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from num2words import num2words
import base64
import datetime
import struct
import uuid


class Accountmove(models.Model):
    _inherit = "account.move"

    date_of_supply = fields.Date(string="Date of Supply", copy=False)
    amount_discount = fields.Float(string="Amount Discount", compute="_compute_amount_discount", store=True,
                                   readonly=True)
    confirm_date = fields.Datetime(string="Confirm Date", copy=False)
    branch_id = fields.Many2one('res.branch')
    invoice_terms_and_conditions = fields.Text(string='Terms and Conditions')
    arabic_invoice_terms_and_conditions = fields.Text(string='Terms and Conditions')
    customer_po = fields.Char(string="Customer P.O")
    description = fields.Text(string='Invoice description')
    show_image = fields.Boolean(string="Show Image", default=False)


    @api.model
    def default_get(self, fields):
        res = super(Accountmove, self).default_get(fields)


        invoice_terms_and_conditions = self.env["ir.config_parameter"].sudo().get_param(
            "ksa_e_invoive.invoice_terms_and_conditions", False)


        arabic_invoice_terms_and_conditions = self.env["ir.config_parameter"].sudo().get_param(
            "ksa_e_invoive.arabic_invoice_terms_and_conditions", False)

        res.update({
            'invoice_terms_and_conditions': invoice_terms_and_conditions or False,
            'arabic_invoice_terms_and_conditions': arabic_invoice_terms_and_conditions or False,
                    })
        return res

    def amount_word(self, amount):
        language = self.partner_id.lang or 'ar'
        language_id = self.env['res.lang'].search([('code', '=', 'ar_001')])
        if language_id:
            language = language_id.iso_code
        amount_str = str('{:2f}'.format(amount))
        amount_str_splt = amount_str.split('.')
        before_point_value = amount_str_splt[0]
        after_point_value = amount_str_splt[1][:2]
        before_amount_words = num2words(int(before_point_value), lang=language)
        after_amount_words = num2words(int(after_point_value), lang=language)
        if after_amount_words == 'صفر':
            amount = before_amount_words + ' ريال '
        else:
            amount = before_amount_words + ' ريال ' + ' و ' + after_amount_words + ' هللة '
        return amount

    # def amount_total_words(self, amount):
    #     words_amount = self.currency_id.amount_to_text(amount)
    #     return words_amount

    def amount_total_words(self, amount):
        # Set the language to English temporarily
        self.env.context = dict(self.env.context, lang='en_US')

        # Call the method to get the amount in words
        words_amount = self.currency_id.amount_to_text(amount)

        # Reset the language to the user's preference
        self.env.context = dict(self.env.context, lang=self.env.user.lang)

        return words_amount



    def action_post(self):
        res = super(Accountmove, self).action_post()
        for move in self:
            move.confirm_date = datetime.datetime.now()
        return res



    @api.depends("invoice_line_ids.amount_discount")
    def _compute_amount_discount(self):
        self.amount_discount = round(sum(line.amount_discount for line in self.invoice_line_ids), 2)



    def qr_encoding_value(self, number, value):
        value = value.encode('UTF-8')
        number = struct.pack("B", number)
        length_encoding = struct.pack("B", len(value))

        return number + length_encoding + value

    def qrcode_info(self, vendor):
        if not self.env.company.vat:
            raise ValidationError(_("company vat is empty"))

        vendor_name = self.qr_encoding_value(1, vendor.display_name)
        vendor_vat = self.qr_encoding_value(2, vendor.vat)

        time_sa = fields.Datetime.context_timestamp(self.with_context(tz='Asia/Riyadh'),
                                                    fields.Datetime.from_string(
                                                        (self.confirm_date or self.create_date)))
        timestamp_invoice = self.qr_encoding_value(3, time_sa.isoformat())

        total = self.qr_encoding_value(4, str(self.amount_total))
        amount_tax = self.qr_encoding_value(5, str(self.currency_id.round(self.amount_tax)))

        str_to_encode = vendor_name + vendor_vat + timestamp_invoice + total + amount_tax

        return base64.b64encode(str_to_encode).decode('UTF-8')



    @api.depends("invoice_line_ids.amount_discount")
    def _compute_amount_discount(self):
        self.amount_discount = sum(line.amount_discount for line in self.invoice_line_ids)



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    amount_discount = fields.Float(string="Amount Discount", compute="_compute_amount_discount", store=True,
                                   readonly=True)
    amount_tax = fields.Float(string="Amount Tax", compute="_compute_amount_total", store=True,
                              readonly=True)

    @api.depends("price_unit", "discount", "quantity")
    def _compute_amount_discount(self):
        for line in self:
            line.amount_discount = line.discount != 0 and (line.price_unit * line.discount / 100) * line.quantity or 0

    @api.depends('price_unit', 'discount', 'tax_ids', 'quantity',
                 'product_id', 'move_id.partner_id', 'move_id.currency_id')
    def _compute_amount_total(self):
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_ids.compute_all(price, quantity=line.quantity, currency=line.currency_id,
                                             product=line.product_id, partner=line.partner_id)

            line.amount_tax = sum(t.get("amount", 0.0) for t in taxes.get("taxes", []))
            if line.move_id:
                line.amount_tax = line.move_id.currency_id.round(line.amount_tax)
