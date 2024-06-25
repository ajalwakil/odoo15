# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import math


class CCNutritionMeal(models.Model):
	_name = "cc.nutrition.meal"
	_description = "Nutrition Meal Configuration"

	name = fields.Char(string="Diet Name",required=True);
	cc_interval_id = fields.Many2one("cc.interval", string="Interval", required=True);
	food_line_ids = fields.One2many("cc.nutrition.line","nutrition_id",string="Nutrition Lines");
	nutrition_type = fields.Selection([('veg','Vegetarian'),
									('non_veg','Non-Vegetarian'),
									('mixed','Mixed')], default="veg", string="Nutrition Type");
	food_count = fields.Integer(string="Total Food Items", compute="onchange_food_line_ids");
	company_id = fields.Many2one("res.company", string="Company", default=lambda s: s.env.company.id or s.env.user.company_id.id);
	user_id = fields.Many2one("res.users", string="Related User", default=lambda s: s.env.user.id);


	@api.onchange("food_line_ids")
	def onchange_food_line_ids(self):
		for rec in self:
			if len(rec.food_line_ids or []):
				if all(line.nutrition_type == 'veg' for line in rec.food_line_ids):
					rec.nutrition_type = 'veg';
				if all(line.nutrition_type == 'non_veg' for line in rec.food_line_ids):
					rec.nutrition_type = 'non_veg';
				if any(line.nutrition_type == 'non_veg' for line in rec.food_line_ids)\
				 and any(line.nutrition_type == 'veg' for line in rec.food_line_ids):
					rec.nutrition_type = 'mixed';
			rec.food_count = len(rec.food_line_ids);



class CCNutritionLine(models.Model):
	_name = "cc.nutrition.line"
	_description = "Diet Configuration Line"

	name = fields.Char(string="Food Item",required=True);
	nutrition_id = fields.Many2one("cc.nutrition.meal", string="Diet");
	quantity = fields.Integer(string="Quantity");
	qty_measure = fields.Selection([("0","gm"),
									("1","Kg"),
									("2","Unit(s)"),
									("3","ml"),
									("4","Liter(s)")],default="0",required=True);
	nutrition_type = fields.Selection([('veg','Vegetarian'),
									('non_veg','Non-Vegetarian')],default="veg", string="Nutrition Type");
	company_id = fields.Many2one("res.company", string="Company", default=lambda s: s.env.company.id or s.env.user.company_id.id);
	user_id = fields.Many2one("res.users", string="Related User", default=lambda s: s.env.user.id);



class CCInterval(models.Model):
	_name = "cc.interval"
	_description = "Nutrition Interval"


	name = fields.Char(string="Interval", required=True);
	time = fields.Float(string="Time");
	company_id = fields.Many2one("res.company", string="Company", default=lambda s: s.env.company.id or s.env.user.company_id.id);
	user_id = fields.Many2one("res.users", string="Related User", default=lambda s: s.env.user.id);



	def name_get(self):
		result = [];

		for rec in self:
			name = rec.name + " [{}]".format(rec.float_time_convert(rec.time)) if rec.time else "";
			result.append((rec.id, name));
		return result;



	def float_time_convert(self,float_val):    
		factor = float_val < 0 and -1 or 1    
		val = abs(float_val)
		frst = str(factor * int(math.floor(val)))
		if len(frst) == 1:
			frst = "0" + frst;
		secd = str(int(round((val % 1) * 60)))  
		if len(secd) == 1:
			secd = "0" + secd;  

		return frst + ":" + secd