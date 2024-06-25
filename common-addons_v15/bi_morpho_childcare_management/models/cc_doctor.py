# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression


class CCDoctor(models.Model):
	_name = "cc.doctor"
	_description = "Doctors"


	name = fields.Char(string="Name", required=True);
	phone = fields.Char(string="Contact No.", required=True);
	email = fields.Char(string="Email ID", required=True);
	degree_id = fields.Many2one("cc.staff.degree", string="Doctors Degree", required=True);

	company_id = fields.Many2one("res.company", string="Company", default=lambda s: s.env.company.id or s.env.user.company_id.id);
	user_id = fields.Many2one("res.users", string="Company", default=lambda s: s.env.user.id);
