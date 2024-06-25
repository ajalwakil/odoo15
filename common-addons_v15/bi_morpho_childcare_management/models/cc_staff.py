# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression
import datetime
import pytz
import math


class CCStaff(models.Model):
    _inherit = "hr.employee"


    def _get_assigned_rooms(self):
        final_rooms = self.env["cc.room"]
        for rec in self:
            rooms1 = rec.env["cc.room"].search([('staff_id','=',rec.id)]);
            rec.room_ids = [(4,room) for room in rooms1.ids];
            rooms2 = rec.env["cc.room"].search([('timetable_ids.staff_id','=',rec.id)]);
            rec.teacher_room_ids = [(4,room) for room in rooms2.ids];
            final_rooms += rooms1 + rooms2;
        return final_rooms



    is_staff = fields.Boolean();
    staff_seq_id = fields.Char(string="Staff ID");
    parent_type = fields.Selection([("parent","Parent"),
                                    ("family","Family"),
                                    ("pickup","Approved Pickup")], default=False);

    emerg_cont_type = fields.Selection([("phone","Phone/Mobile"),("email","Email")],string="Emergency Contact", default="phone");
    emergency_cont = fields.Char(string="Emergency Contact");

    # Rooms Info
    room_ids = fields.Many2many("cc.room", "staff_rooms_ref", string="ClassRooms", compute="_get_assigned_rooms"); 
    teacher_room_ids = fields.Many2many("cc.room", "staff_teacher_rooms_ref", string="Teacher In Rooms", compute="_get_assigned_rooms"); 

    # Certification
    degree_id = fields.Many2one("cc.staff.degree", string="Degree");
    certificate_id = fields.Many2one("cc.staff.certificate", string="Certificates");


    @api.model
    def create(self, vals):
        res = super(CCStaff, self).create(vals);
        for rec in res:
            if rec.is_staff:
                if len(rec.staff_seq_id or []) == 0:
                    seq_date = None;
                    seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.today())
                    rec.staff_seq_id= self.env.ref("bi_morpho_childcare_management.bi_morpho_childcare_management_staff_sequence").next_by_id() or "";
                values = {
                            "name": rec.name,
                            "login": rec.work_email,
                            "email": rec.work_email,
                            "image_1920": rec.image_1920,
                        }
                user = self.env["res.users"].sudo().create(values);
                group_id = self.env.ref("bi_morpho_childcare_management.bi_morpho_childcare_management_group_staff");
                group_id.users = [(4,user.id)];
                if user:
                    rec.user_id = user.id;
                    rec.work_email = user.login;
        return res;


    @api.onchange("per_admin","per_supervisor")
    def _onchange_staff_permission(self):
        for rec in self:
            group_id = self.env.ref("bi_morpho_childcare_management.bi_morpho_childcare_management_group_director");

            

    def action_todays_activities(self):
        self.ensure_one();
        records = self.env["cc.room.activity"].search([('staff_id','=',self.id)]);
        records = records.filtered(lambda s : s.start_datetime.date() == fields.Date.today());
        recs = self.compute_activities_for_staff();
        records = records + recs if len(recs or []) else records;
        view_id = self.env.ref("bi_morpho_childcare_management.cc_room_lesson_plan_tree_view").id;
        return {
                "name" : _("My Lesson Planning"),
                "type" : "ir.actions.act_window",
                "res_model" : "cc.room.activity",
                "views" : [[view_id, 'list'],[False, 'form']],
                "view_mode" : "tree,form",
                "domain" : "[('id','in',{})]".format(records.ids),
        }

    def emerg_cont_type_m(self):
        return {"phone":"Phone/Mobile","email":"Email"}.get(self.emerg_cont_type, False);

    def compute_activities_for_staff(self):
        today = fields.Date.today();
        day = fields.Date.today().weekday();

        timetable_ids = self.env["cc.room.timetable"].search([('staff_id','=',self.id),('day','=',day)]);
        activity_ids = self.env["cc.room.activity"].search([('staff_id','=',self.id)]);
        activity_ids = activity_ids.filtered(lambda ac: ac.start_datetime.date() == today);

        tt_ids = [att.timetable_id.id for att in activity_ids if att.timetable_id];

        if len(timetable_ids or []) != len(activity_ids or []):
            vals_list = []
            for tt in timetable_ids:
                if tt.id not in tt_ids:
                    time = self.float_to_float_time(tt.room_id.enter_time).split(":");
                    dur = self.float_to_float_time(tt.dur_time).split(":");
                    start_datetime = datetime.datetime(today.year, today.month, today.day,int(time[0]),int(time[1]))
                    end_datetime = datetime.datetime(today.year, today.month, today.day,int(time[0]) + int(dur[0]) ,int(time[1]) + int(dur[1]))
                    
                    vals_list.append({
                        "room_id" : tt.room_id.id,
                        "name" : tt.name,
                        "description" : tt.description,
                        "start_datetime" : start_datetime,
                        "end_datetime" : end_datetime,
                        "staff_id" : tt.staff_id.id,
                        "timetable_id" : tt.id,
                    });

            records = self.env["cc.room.activity"].sudo().create(vals_list);
            return records;
        return False;


    def float_to_float_time(self, floatt):
        hour, minute = divmod(floatt, 1)
        minute *= 60
        return '{}:{}'.format(int(hour), int(minute))
