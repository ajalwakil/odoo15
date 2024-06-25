# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'




    commercial_register = fields.Char(string="Commercial Register", copy=False)
    building_no = fields.Char(string="Building No", copy=False)
    district = fields.Char(string="District", copy=False)
    postal_code = fields.Char(string="Postal Code", copy=False)
    additional_no = fields.Char(string="Additional No", copy=False)
    other_id = fields.Char(string="Other ID", copy=False)



    arabic_name = fields.Char('Arabic Name')
    arabic_street = fields.Char('Arabic Street')
    arabic_zip = fields.Char('Arabic Zip',)
    arabic_city = fields.Char('Arabic City', )
    arabic_state_id = fields.Char( string='Arabic State')
    arabic_country_id = fields.Char(string='Arabic Country',store=True)
    arabic_building_no = fields.Char(string="Arabic Building No", copy=False)
    arabic_district = fields.Char(string="Arabic District", copy=False)
    arabic_postal_code = fields.Char(string="Arabic Postal Code", copy=False)
    arabic_additional_no = fields.Char(string="Arabic Additional No", copy=False)
    arabic_other_id = fields.Char(string="Arabic Other ID", copy=False)

