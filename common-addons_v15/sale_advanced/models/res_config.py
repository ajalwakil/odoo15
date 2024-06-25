# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_terms_and_conditions = fields.Text(string='Terms and Conditions')
    arabic_sale_terms_and_conditions = fields.Text(string='Arabic Terms and Conditions')


    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_parameters = self.env['ir.config_parameter'].sudo()
        config_parameters.set_param('sale_advanced.sale_terms_and_conditions', self.sale_terms_and_conditions)
        config_parameters.set_param('sale_advanced.arabic_sale_terms_and_conditions', self.arabic_sale_terms_and_conditions)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        config_parameters = self.env['ir.config_parameter'].sudo()
        sale_terms_and_conditions = config_parameters.get_param('sale_advanced.sale_terms_and_conditions')
        arabic_sale_terms_and_conditions = config_parameters.get_param('sale_advanced.arabic_sale_terms_and_conditions')

        res.update(
            sale_terms_and_conditions=sale_terms_and_conditions,
            arabic_sale_terms_and_conditions=arabic_sale_terms_and_conditions,
        )
        return res
