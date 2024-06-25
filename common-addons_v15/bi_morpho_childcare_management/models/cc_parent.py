# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression
from random import randint


class CCParent(models.Model):
	_inherit = "res.partner"

	is_parent = fields.Boolean(default=False);
	group_flag = fields.Boolean(default=True, readonly=True);
	parent_type = fields.Selection([("parent","Parent"),
									("family","Family"),
									("pickup","Approved Pickup")], default=False);
	cc_parent_id = fields.Many2one("res.partner", string="Parent");
	cc_child_ids = fields.One2many("res.partner.parentchild", "res_partner_id", string="Child(s)");


	@api.onchange("cc_child_ids")
	def _cc_child_ids_depends(self):
		for rec in self:
			for child in rec.cc_child_ids:
				if rec.id not in child.parent_ids.ids:
					rec.cc_child_id = child.id;



	@api.model
	def create(self, vals):
		if vals.get("is_child",False):
			seq_date = None;
			seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.today())
			vals['child_seq_id'] = self.env.ref("bi_morpho_childcare_management.bi_morpho_childcare_management_child_sequence").next_by_id() or "";
		res = super(CCParent, self).create(vals);
		for rec in res:
			if rec.is_parent:
				group_id = self.env.ref("base.group_portal");
				if rec.parent_type == "family":
					cc_group_id = self.env.ref("bi_morpho_childcare_management.bi_morpho_childcare_management_group_family");
				elif rec.parent_type == "pickup":
					cc_group_id = self.env.ref("bi_morpho_childcare_management.bi_morpho_childcare_management_group_pickup");
				else:
					cc_group_id = self.env.ref("bi_morpho_childcare_management.bi_morpho_childcare_management_group_parent");
				values = {
							"partner_id": rec.id,
							"login": rec.email,
							"name": rec.name,
							"groups_id": [(6,False,group_id.ids + cc_group_id.ids)],
						}
				user = self.env["res.users"].sudo().create(values);
		return res;




class CCResPartnerParentChild(models.Model):
	_name = "res.partner.parentchild"
	_inherits = {"res.partner" : "res_partner_id"}
	_description = "Parent Child Relaction Line"


	cc_child_id = fields.Many2one("res.partner", string="Child", domain="[('is_child','=',True)]");
	res_partner_id = fields.Many2one("res.partner", required=True, ondelete="cascade");


	def get_childs(self):
		childs = self.env["res.partner"]
		for rec in self:
			childs += rec.cc_child_id;
		return childs;


	def get_parents(self):
		parents = self.env["res.partner"]
		for rec in self:
			parents += rec.parent_id;
		return parents;

