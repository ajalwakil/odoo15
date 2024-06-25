# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_terms_and_conditions = fields.Text(string='Terms and Conditions')
    arabic_invoice_terms_and_conditions = fields.Text(string='Arabic Terms and Conditions')


    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_parameters = self.env['ir.config_parameter'].sudo()
        config_parameters.set_param('ksa_e_invoive.invoice_terms_and_conditions', self.invoice_terms_and_conditions)
        config_parameters.set_param('ksa_e_invoive.arabic_invoice_terms_and_conditions', self.arabic_invoice_terms_and_conditions)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        config_parameters = self.env['ir.config_parameter'].sudo()
        invoice_terms_and_conditions = config_parameters.get_param('ksa_e_invoive.invoice_terms_and_conditions')
        arabic_invoice_terms_and_conditions = config_parameters.get_param('ksa_e_invoive.arabic_invoice_terms_and_conditions')

        res.update(
            invoice_terms_and_conditions=invoice_terms_and_conditions,
            arabic_invoice_terms_and_conditions=arabic_invoice_terms_and_conditions,
        )
        return res
