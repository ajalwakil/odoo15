# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression


class CCStaffDegree(models.Model):
	_name = "cc.staff.degree"
	_description = "Childcare Staff Degree"


	name = fields.Char(string="Title", required=True);
	level = fields.Selection([("0","Secondary"),
							("1","Graduation"),
							("2","Master")], default=False, required=True);
	description = fields.Text(string="Description");

	company_id = fields.Many2one("res.company", string="Company", default=lambda s: s.env.company.id or s.env.user.company_id.id);
	user_id = fields.Many2one("res.users", string="Company", default=lambda s: s.env.user.id);
