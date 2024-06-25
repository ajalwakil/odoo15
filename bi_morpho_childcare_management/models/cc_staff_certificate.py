# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression


class CCStaffCertificate(models.Model):
	_name = "cc.staff.certificate"
	_description = "Childcare Staff Certificate"


	name = fields.Char(string="Title", required=True);
	certificate_by = fields.Char(string="Issued By", required=True);
	description = fields.Text(string="Description");

	company_id = fields.Many2one("res.company", string="Company", default=lambda s: s.env.company.id or s.env.user.company_id.id);
	user_id = fields.Many2one("res.users", string="Company", default=lambda s: s.env.user.id);
