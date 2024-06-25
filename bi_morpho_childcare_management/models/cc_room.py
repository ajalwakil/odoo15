# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression
import datetime


class CCRooms(models.Model):
	_name = "cc.room"
	_description = "Classrooms"

	name = fields.Char(string="Name", required=True);
	description = fields.Text(string="Description", required=True);
	school_id = fields.Many2one("cc.school", string="School", required=True);
	total_intek = fields.Integer(string="Room Intek", required=True);
	staff_id = fields.Many2one("hr.employee", string="Class Teacher", required=True, domain="[('is_staff','=',True)]");

	enter_time = fields.Float(string="Enter Time", required=True);
	out_time = fields.Float(string="Out Time", required=True);

	activity_ids = fields.One2many("cc.room.activity","room_id", string="Room Activities");
	timetable_ids = fields.One2many("cc.room.timetable","room_id", string="Timetable");

	company_id = fields.Many2one("res.company", string="Company", default=lambda s: s.env.company.id or s.env.user.company_id.id);
	user_id = fields.Many2one("res.users", string="Company", default=lambda s: s.env.user.id);



	def _onchange_timetable_ids(self):
		for rec in self:
			days = {}
			for l in rec.timetable_ids:
				if l.day in days:
					days[l.day] += l.dur_time;
				else:
					days[l.day] = l.dur_time;
			room_total = rec.out_time - rec.enter_time;
			if not rec.out_time and not rec.enter_time:
				raise UserError(_("Enter classroom enter time and out time properly."));
			if any(days[l] > room_total for l in days.keys()):
				raise UserError(_("You can not add more time in timetable than total time of classroom for a single day"));



	@api.onchange("enter_time","out_time")
	def _time_constraint_check(self):
		for rec in self:
			if rec.enter_time and rec.out_time:
				if rec.enter_time >= rec.out_time:
					raise UserError(_("Enter time cannot be greater or equal to out time."));


	def open_calendar_for_room(self):
		self.ensure_one()
		return {
				"name" : _("ClassRoom Activies"),
				"type" : "ir.actions.act_window",
				"view_mode" : "calendar",
				"res_model" : "cc.room.activity",
				"domain" : "[('id','in',{})]".format(self.activity_ids.ids),
				"target" : "self",
			};


	def check_room_vaccancy(self):
		self.ensure_one();
		total_intek = self.total_intek;
		registrations = self.env["cc.school.registration"].sudo().search([('room_id','=', self.id)]);
		return total_intek - len(registrations or  [])


	@api.model
	def create(self, vals):
		if not vals.get("enter_time",False):
			raise UserError(_("Enter classroom enter time."));
		if not vals.get("out_time",False):
			raise UserError(_("Enter classroom out time."));
		res = super(CCRooms, self).create(vals);
		res._onchange_timetable_ids();
		return res;


	def write(self, vals):
		res = super(CCRooms, self).write(vals);
		self._onchange_timetable_ids()
		return res


	def get_all_staff(self):
		staffs = self.env["hr.employee"]
		for rec in self:
			staffs += rec.staff_id;
			for line in rec.timetable_ids:
				staffs += line.staff_id; 
		return staffs;




class CCRoomsTimeTable(models.Model):
	_name = "cc.room.timetable"
	_description = "Classrooms Timetable"


	day = fields.Selection([("0","Monday"), 
							("1","Tuesday"), 
							("2","Wednesday"),
							("3", "Thursday"),
							("4", "Friday"),
							("5", "Saturday"),
							("6", "Sunday")], default=False, required=True);
	name = fields.Char(string="Subject", required=True);
	description = fields.Text(string="Description", required=True);
	dur_time = fields.Float(string="Duration", required=True);
	room_id = fields.Many2one("cc.room");
	staff_id = fields.Many2one("hr.employee", string="Teacher", required=True, domain="[('is_staff','=',True)]");

	company_id = fields.Many2one("res.company", string="Company", default=lambda s: s.env.company.id or s.env.user.company_id.id);
	user_id = fields.Many2one("res.users", string="Responsible", default=lambda s: s.env.user.id);




class CCRoomsActivity(models.Model):
	_name = "cc.room.activity"
	_description = "Classrooms Activities"


	@api.onchange("start_datetime", "end_datetime")
	def _get_weekday(self):
		for rec in self:
			if rec.start_datetime and rec.end_datetime:
				if rec.start_datetime.date() == rec.end_datetime.date():
					rec.week_day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][rec.start_datetime.weekday()];
				else:
					rec.week_day = False;
			else:
				rec.week_day = False;



	@api.onchange("start_datetime", "end_datetime")
	def _validate_dates(self):
		for rec in self:
			if rec.start_datetime and rec.end_datetime:
				if rec.start_datetime.date() != rec.end_datetime.date():
					raise UserError(_("You cannot add time more than classroom's total time."));
				diff = rec.time_float_convert(rec.get_time_str_from_diff(rec.start_datetime, rec.end_datetime));
				room_time = rec.room_id.out_time - rec.room_id.enter_time;
				if rec.room_id and room_time < diff:
					raise UserError(_("You cannot add time more than classroom's total time."));


	def _get_activity_validity(self):
		for rec in self:
			if rec.is_complete:
				rec.state = 'complete';
			else:
				if (rec.start_datetime and rec.end_datetime):
					if (rec.start_datetime.date() == rec.end_datetime.date()):
						if (rec.start_datetime >= fields.Datetime.now()):
							rec.state = 'scheduled';
						else:
							rec.state = 'not_complete';
				else:
					rec.state = 'draft';


	def action_activity_completed(self):
		for rec in self:
			rec.is_complete = True;



	state = fields.Selection([('scheduled','Scheduled'),('not_complete','Not Completed'),('complete','Completed')], compute="_get_activity_validity");
	room_id = fields.Many2one("cc.room", string="Room", required=True);
	timetable_id = fields.Many2one("cc.room.timetable", string="Timetable");
	name = fields.Char(string="Activity Name", required=True);
	description = fields.Text(string="Activity Description", required=True);
	start_datetime = fields.Datetime(string="Start Date & Time", required=True);
	end_datetime = fields.Datetime(string="End Date & Time", required=True);
	week_day = fields.Char(string="Day", compute="_get_weekday");
	staff_id = fields.Many2one("hr.employee", string="Teacher", required=True, domain="[('is_staff','=',True)]");
	is_complete = fields.Boolean(string="Is Complete");

	# Streming Related Fields
	schedule_meet = fields.Boolean(string="Schedule Streming Meet");
	session_link = fields.Char(string="Streming Link");
	select_platform = fields.Selection([("google","Google Meet"),
                                        ("zoom", "Zoom Meeting")],default="google",string="Select Platform", required=True);
	lesson_plan = fields.Html(string="Lesson Plan");

	company_id = fields.Many2one("res.company", string="Company", default=lambda s: s.env.company.id or s.env.user.company_id.id);
	user_id = fields.Many2one("res.users", string="Company", default=lambda s: s.env.user.id);


	def update_lesson_plan(self):
		self.ensure_one();
		context = {
					"activity_id" : self.id,
					"name" : self.name,
					"description" : self.description,
					"start_datetime" : self.start_datetime,
					"end_datetime" : self.end_datetime,
				}
		action = self.env.ref("bi_morpho_childcare_management.cc_lesson_plan_wizard_action").sudo().read()[0];
		action["context"] = context;
		return action;


	def get_time_str_from_diff(self, date1, date2):
		diff = date2 - date1
		days, seconds = diff.days, diff.seconds
		hours, rem_hr = divmod(seconds,  3600)
		minutes, seconds = divmod(rem_hr, 60)
		return str(hours)+ ':'+ str(minutes) + ':' +str(seconds)


	def time_float_convert(self,float_val):
		vals = float_val.split(':')
		h = float(vals[0])
		m = float(vals[1])
		t1, hours = divmod(h, 24)
		t2, minutes = divmod(m, 60)
		minutes = minutes / 60.0
		hours = (24*t1) + hours
		return hours + minutes


