# -*- coding: utf-8 -*-
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

from odoo import fields, models, api, _


class ResUserInherit(models.Model):
    _inherit = 'res.users'

    # @api.model_create_multi
    # def create(self, vals_list):
    #     if not self.env.user.has_group('user_access_rights.group_user_rights'):
    #         raise UserError(_("You are not allowed to create 'User' (res.user) records."))
    #     users = super(ResUserInherit, self).create(vals_list)
    #     for user in users:
    #         # if partner is global we keep it that way
    #         if user.partner_id.company_id:
    #             user.partner_id.company_id = user.company_id
    #         user.partner_id.active = user.active
    #     return users


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    @api.model
    def create(self, vals):
        if not self.env.user.has_group('user_access_rights.group_user_rights'):
            raise UserError(_("You are not allowed to create 'Company' (res.company) records."))
        if not vals.get('favicon'):
            vals['favicon'] = self._get_default_favicon()
        if not vals.get('name') or vals.get('partner_id'):
            self.clear_caches()
            return super(ResCompanyInherit, self).create(vals)
        partner = self.env['res.partner'].create({
            'name': vals['name'],
            'is_company': True,
            'image_1920': vals.get('logo'),
            'email': vals.get('email'),
            'phone': vals.get('phone'),
            'website': vals.get('website'),
            'vat': vals.get('vat'),
            'country_id': vals.get('country_id'),
        })
        # compute stored fields, for example address dependent fields
        partner.flush()
        vals['partner_id'] = partner.id
        self.clear_caches()
        company = super(ResCompanyInherit, self).create(vals)
        # The write is made on the user to set it automatically in the multi company group.
        self.env.user.write({'company_ids': [ResCompanyInherit.link(company.id)]})

        # Make sure that the selected currency is enabled
        if vals.get('currency_id'):
            currency = self.env['res.currency'].browse(vals['currency_id'])
            if not currency.active:
                currency.write({'active': True})
        return company
