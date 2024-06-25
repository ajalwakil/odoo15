# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression


class CCSupplyChain(models.Model):
	_name = "cc.supply.chain"
	_description = "Supply Chain"


	name = fields.Char(string="Name");
	product_id = fields.Many2one("product.product", string="Product", required=True);
	product_qty = fields.Float(string="Quantity", default=1.0);
	partner_id = fields.Many2one("res.partner", string="Vendor", required=True);
	room_id = fields.Many2one("cc.room", string="Classroom", required=True);
	director_id = fields.Many2one("hr.employee", string="Director", related="room_id.school_id.director_id");
	date = fields.Date(string="Date", default=fields.Date.today());
	state = fields.Selection([("draft","Draft"),
								("in_appr","In Approval"),
								("confirm","Confirmed"),
								("cancel","Cancelled")], default="draft");

	purchase_order = fields.Many2one("purchase.order", string="Purchase Order");
	company_id = fields.Many2one("res.company", string="Company", default=lambda s: s.env.company.id or s.env.user.company_id.id);
	user_id = fields.Many2one("res.users", string="Company", default=lambda s: s.env.user.id);


	def name_get(self):
		result = []
		for rec in self:
			name = "[%s] "%rec.room_id.name + rec.product_id.name;
			result.append((rec.id, name))
		return result


	def send_for_approval(self):
		for rec in self:
			rec.state = "in_appr";


	def action_cancel(self):
		for rec in self:
			rec.state = "cancel";



	def _get_picking_type(self, company_id):
		picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
		if not picking_type:
			picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])
		return picking_type[:1]


	def action_approve(self):
		po = self.env["purchase.order"]
		pol = self.env["purchase.order.line"]
		for rec in self:
			name = "[%s] "%rec.room_id.name + rec.product_id.name;
			vals = {
					"name" : name,
					"partner_id" : rec.partner_id.id,
					'payment_term_id': rec.partner_id.with_company(rec.company_id).property_supplier_payment_term_id.id,
					"company_id" : rec.company_id.id,
					"currency_id" : rec.company_id.currency_id.id,
					"picking_type_id" : self._get_picking_type(rec.company_id.id).id,
					"cc_supply_chain_id" : rec.id,
					"user_id" : rec.env.user.id,
					"cc_po" : True,
					'origin': name,
					"date_order" : rec.date,
					"order_line" : [],
				}

			pos = po.create(vals);
			line_vals = {
							"name" : rec.product_id.name,
							"product_id" : rec.product_id.id,
							'product_uom': rec.product_id.uom_po_id.id,
							"product_qty" : rec.product_qty,
							"price_unit" : rec.product_id.standard_price,
							"display_type" : False,
							"order_id" : pos.id,
							'date_planned': rec.date,
						}

			pol.create(line_vals)
			pos.button_confirm();
			rec.purchase_order = pos.id;
			rec.state = "confirm";
			

	def open_purchase_orders(self):
		self.ensure_one();
		return {
				"type" : "ir.actions.act_window",
				"name" : _("Purchase Orders"),
				"res_model" : "purchase.order",
				"view_mode" : "tree,form",
				"domain" : "[('id','in',{})]".format(self.purchase_order.ids),
			}




class CCPurchaseInherit(models.Model):
	_inherit = "purchase.order"


	cc_supply_chain_id = fields.Many2one("cc.supply.chain", string="Childcare PO");
	cc_po = fields.Boolean(string="Childcare");
	group_flag = fields.Boolean(default=True, readonly=True);