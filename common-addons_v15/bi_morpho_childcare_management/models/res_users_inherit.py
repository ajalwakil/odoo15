# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression
from random import randint


class ResUsersInherit(models.Model):
	_inherit = "res.users"


	def cc_has_access(self, user=None, to=None):
		if not user:
			return False;
		if user.has_group("bi_morpho_childcare_management.bi_morpho_childcare_management_group_director"):
			return True;
		f_group_id = user.has_group("bi_morpho_childcare_management.bi_morpho_childcare_management_group_family");
		p_group_id = user.has_group("bi_morpho_childcare_management.bi_morpho_childcare_management_group_pickup");
		cc_group_id = user.has_group("bi_morpho_childcare_management.bi_morpho_childcare_management_group_parent");
		if to == 'inv' and cc_group_id:
			return True;
		if to == 'pe' and (cc_group_id or f_group_id):
			return True;
		if to == 're' and (cc_group_id or f_group_id):
			return True;
		return False; 
