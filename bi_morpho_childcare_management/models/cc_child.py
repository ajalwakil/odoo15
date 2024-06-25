# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression
from dateutil.relativedelta import relativedelta
from datetime import datetime,date
from passlib.context import CryptContext
import math



class CCChild(models.Model):
	_inherit = "res.partner"


	@api.onchange("dob")
	def _onchange_dob(self):
		today = fields.Date.today();
		for rec in self:
			if rec.dob and today <= rec.dob:
				raise ValidationError(_("Birthdate cannot be greater than today's date."))


	@api.onchange("dob")
	def _get_age(self):
		today = fields.Date.today();
		for rec in self:
			if rec.dob:
				diff = relativedelta(today, rec.dob)
				rec.age_days = diff.days
				rec.age_month = diff.months
				rec.age_year = diff.years
			else:
				rec.age_days = 0
				rec.age_month = 0
				rec.age_year = 0


	is_child = fields.Boolean(default=False);
	group_flag = fields.Boolean(default=True, readonly=True);
	cc_status = fields.Selection([("draft","Draft"),("enquiry","Enquiry"),
									("in_queue","In Waiting"),
									("enroll","Enrolled")], string="Status", store=True,default="draft",copy=False)
	all_compute = fields.Integer(string="Helping Field", compute="_compute_all_fields");
	

	# Personal Info.
	gender = fields.Selection([("male", "Male"),
								("female", "Female"),
								("other", "Other")], string="Gender",default=False);
	dob = fields.Date(string="BrithDay");
	age_year = fields.Integer(compute="_get_age");
	age_month = fields.Integer(compute="_get_age");
	age_days = fields.Integer(compute="_get_age");
	allergy_ids = fields.One2many("lead.allergy", "child_id", string="Allergies");
	notes_ids = fields.Many2many("cc.note", "child_note_ref", string="Notes");
	medication_ids = fields.One2many("lead.medication", "child_id", string="Medications");
	nutrition_ids = fields.Many2many("cc.nutrition.meal", "child_nutrition_ref", string="Nutritions");
	doctor_id = fields.Many2one("cc.doctor", string="Doctor");
	pin = fields.Char(string="Pin", readonly=True, copy=False);


	# Rooms Info
	main_room_id = fields.Many2one("cc.room", string="Main Room"); 
	other_room_ids = fields.Many2many("cc.room", "child_rooms_ref", string="Additional Rooms"); 

	# School Details
	school_id = fields.Many2one(related="main_room_id.school_id", string="School");
	meal_type = fields.Selection([('veg','Vegetarian'),
									('non_veg','Non-Vegetarian'),
									('mixed','Mixed')], compute="_compute_all_fields", string="Meal Type");
	child_seq_id = fields.Char(string="Child ID", copy=False);
	staff_ids = fields.Many2many("hr.employee","child_staff_ref",string="Teachers", domain="[('is_staff','=',True)]")

	# Financial Details
	currency_id = fields.Many2one("res.currency", string="Currncy", default= lambda s: s.env.company.currency_id.id or s.env.user.company_id.currency_id.id);
	family_income = fields.Monetary(string="Family Income", default=0, currency_field="currency_id");

	# Enrollment Details
	enquiry_date = fields.Date(string="Enquiry Date");
	enroll_date = fields.Date(string="Enrollment Date");
	registration_ids = fields.One2many("cc.school.registration","child_id");

	# Alert
	eme_alert_ids = fields.One2many("cc.emergency.alert", "child_id", string="Emergency Alerts");


	# Parents Details
	cc_child_id = fields.Many2one("res.partner", string="Child", domain="[('is_child','=',True)]")
	parent_ids = fields.One2many("res.partner.parentchild", "cc_child_id");


	#Attendance realted fields
	reatt_st_date = fields.Date(string="Helper report field 1");
	reatt_end_date = fields.Date(string="Helper report field 2");


	def create(self, vals_list):
		res=super(CCChild,self).create(vals_list)	
		if res.main_room_id : 
			res.write({'registration_ids': [(0, 0, {'school_id':res.main_room_id.school_id.id,
													   'reg_date': date.today() ,
													   'start_date':date.today() ,
													   'room_id': res.main_room_id.id,
													   })]})
		return res

	

	@api.onchange("main_room_id","other_room_ids")
	def _onchange_staffs(self):
		for rec in self:
			staffs = []
			if rec.main_room_id:
				staffs += rec.main_room_id.get_all_staff().ids
			if rec.other_room_ids:
				staffs += rec.other_room_ids.get_all_staff().ids
			self.staff_ids = [(6,False,staffs)];



	def _compute_all_fields(self):
		today = fields.date.today();
		t1 = today.strftime("%Y/%m/%d")
		for rec in self:
			regis = rec.registration_ids.sudo().filtered(lambda s: str(s.end_date) >= t1);
			if len(regis or []):
				rec.cc_status = "enroll";
				rec.enroll_date = regis.reg_date;
			# else:
			#   rec.cc_status = "enquiry";
			rec.all_compute = 1;

			if rec.nutrition_ids:
				if all(nut.nutrition_type == "veg" for nut in rec.nutrition_ids):
					rec.meal_type = "veg";
				elif all(nut.nutrition_type == "non_veg" for nut in rec.nutrition_ids):
					rec.meal_type = "non_veg";
				else:
					rec.meal_type = "mixed";
			else:
				rec.meal_type = False;



	def open_add_new_parent(self):
		self.ensure_one();
		action = self.env.ref("bi_morpho_childcare_management.cc_addparent_wizard_action").sudo().read()[0]
		action["context"] = '{"is_create": True,}';
		return action;


	def open_add_exit_parent(self):
		self.ensure_one();
		action = self.env.ref("bi_morpho_childcare_management.cc_addparent_wizard_action").sudo().read()[0]
		action["context"] = '{"is_create": False,}';
		return action;


	#------------------------------------------------------------------
	# Emergency Alerts
	#------------------------------------------------------------------

	def get_parent_to_send(self, for_mail=False):
		if for_mail:
			parent_ids = "";
			for p in self.parent_ids.filtered(lambda p: p.parent_type in ("parent","family")):
				parent_ids += "%s,"%(str(p.email or ""))
			return parent_ids[:len(parent_ids) - 1];
		parent_ids = self.env["res.partner"];
		for par in self.parent_ids.filtered(lambda p: p.parent_type in ("parent","family")):
			parent_ids += par.res_partner_id;
		return parent_ids;


	def render_message_body(self, custom=False, custom_body=""):
		name = self.name;
		if self.main_room_id:
			s_contact = "%s / %s"%(self.main_room_id.school_id.mobile, self.main_room_id.school_id.phone)
			s_email = self.main_room_id.school_id.email or "";

			ct_emeg = "(%s) %s" %(self.main_room_id.staff_id.emerg_cont_type_m(), self.main_room_id.staff_id.emergency_cont); 
			ct_contact = self.main_room_id.staff_id.mobile_phone or "";
			ct_email = self.main_room_id.staff_id.work_email or "";
		else:
			s_contact = "";
			s_email = "";
			ct_emeg = "";
			ct_contact = "";
			ct_email = "";
		
		message = _("""
Emergency Alert For: %s,
\n
There is emergency situation for your child %s.
Please contact to School/Class Teacher.\n
\n

School:\n
Contact - %s\n
Email - %s
\n

Class Teacher:\n
Emergency Contact - %s\n
Contact - %s\n
Email - %s
		"""%(name, name, s_contact, s_email, ct_emeg, ct_contact, ct_email));
	
		return message;



	def send_sms_emergency_alert(self):
		res = self._message_sms_with_template(
				template_xmlid='bi_morpho_childcare_management.emergency_alert_sms_template',
				template_fallback=_("Emergency Alert: %s"%self.name),
				partner_ids=self.get_parent_to_send().ids,
				put_in_queue=False
			)
		return res;

	def send_mail_emergency_alert(self):
		template_id = self.env.ref("bi_morpho_childcare_management.emergency_alert_mail_template");
		template = self.env['mail.template'].browse(template_id.id);
		return template.send_mail(self.id,force_send=True);


	def emergency_alert(self):
		self.ensure_one();
		sms = self.send_sms_emergency_alert();
		mail = self.send_mail_emergency_alert();
		sms_id = self.env["sms.sms"].search([('mail_message_id','=',sms.id)], limit=1);
		self.env["cc.emergency.alert"].create({
												"child_id" : self.id,
												"message_id" : sms_id.id,
												"mail_id" : mail,
											})
		return [sms, mail]


	def action_enrolled(self):
		if self:
			for rec in self:
				enroll_obj = self.env['crm.lead']
				inspection_id = self.env['cc.school']
				enroll_create_obj = enroll_obj.create({
									'name': self.name,
									'c_fname':self.name,
									'c_dob': self.dob,
									'date_open':datetime.today(),
									'user_id':self.env.user.id,
									'room_id':self.main_room_id.id,
									'cc_status':'enroll',
					
							  })
			rec.cc_status='enroll'


				

				
							


	#------------------------------------------------------------------
	# Parent Messaging
	#------------------------------------------------------------------

	def action_parent_messaging(self):
		return {
				"name" : _("Message To Parent"),
				"type" : "ir.actions.act_window",
				"res_model" : "cc.parentmsg.wizard",
				"view_mode" : "form",
				"context" : {"childs" : self.ids,},
				"target" : "new",
			}



	#------------------------------------------------------------------
	# Media Sharing
	#------------------------------------------------------------------

	def share_media(self):
		self.ensure_one();
		return {
				"name" : _("Share Media"),
				"type" : "ir.actions.act_window",
				"res_model" : "cc.media.sharing.wizard",
				"view_mode" : "form",
				"target" : "new",
			}


	#------------------------------------------------------------------
	# Attendace Security
	#------------------------------------------------------------------

	def varify_pinpass(self, pinpass=None):
		if pinpass or len(pinpass) == 4:
			if CryptContext(schemes=['pbkdf2_sha512']).verify(pinpass, self.pin):
				return True;
			else:
				return False; 
		else:
			return False;



	#------------------------------------------------------------------
	# Attendace
	#------------------------------------------------------------------

	def action_get_child_attend(self):
		self.ensure_one();
		return {
			'name': _('Children Attendances'), 
			'type': 'ir.actions.act_window', 
			'domain': [('child_id','=',self.id)], 
			'res_model': 'cc.child.attendance', 
			'view_mode': 'tree,form',
		}


	def get_childs_attends(self):
		if self.reatt_st_date:
			st_date = datetime(self.reatt_st_date.year, self.reatt_st_date.month, self.reatt_st_date.day, 0,0,0);
		else:
			today = datetime.today();
			st_date = datetime(today.year, today.month, 1, 0, 0, 0)
		if self.reatt_end_date:
			en_date = datetime(self.reatt_end_date.year, self.reatt_end_date.month, self.reatt_end_date.day, 23,59,59);
		else:
			today = datetime.today();
			en_date = datetime(today.year, today.month, today.day, 23, 59, 59) + relativedelta(day=31)

		records = self.env["cc.child.attendance"].search([("child_id","=",self.id),("check_in",">=",st_date),("check_out","<=",en_date)]);
		self.reatt_st_date = False;
		self.reatt_end_date = False;
		return records;


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




	def get_childs_activities(self, dashboard=None):
		activities = self.env["cc.room.activity"];
		if dashboard:
			if self.main_room_id:
				activities += self.main_room_id.activity_ids.filtered(lambda s: s.start_datetime >= fields.Datetime.now() and s.schedule_meet);
			if self.other_room_ids:
				for rm in self.other_room_ids:
					activities += rm.activity_ids.filtered(lambda s: s.start_datetime >= fields.Datetime.now() and s.schedule_meet);
		else:
			if self.main_room_id:
				activities += self.main_room_id.activity_ids.filtered(lambda s: s.start_datetime.date() == fields.Date.today());
			if self.other_room_ids:
				for rm in self.other_room_ids:
					activities += rm.activity_ids.filtered(lambda s: s.start_datetime.date() == fields.Date.today());
		return activities;


	def get_today(self):
		return fields.Date.today();


	def _get_report_base_filename(self):
		return self.name;




class CCEmergencyAlert(models.Model):
	_name = "cc.emergency.alert"
	_description = "Emergency Alert"


	child_id = fields.Many2one("res.partner", string="Child", domain="[('is_child','=',True)]", required=True);
	message_id = fields.Many2one("sms.sms", string="Message");
	message_status = fields.Selection(related="message_id.state", string="Message Status");
	mail_id = fields.Many2one("mail.mail", string="Mail");
	mail_status = fields.Selection(related="mail_id.state", string="Mail Status");

	company_id = fields.Many2one("res.company", string="Company", default=lambda s: s.env.company.id or s.env.user.company_id.id);
	user_id = fields.Many2one("res.users", string="Company", default=lambda s: s.env.user.id);
