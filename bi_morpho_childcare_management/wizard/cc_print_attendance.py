# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields
import datetime
import pytz
import math

class CCPrintAttendanceWizard(models.TransientModel):
    _name = "cc.attendance.wizard"
    _description = "School Attendance Report"

    def _get_domain_for_manager(self):
        uids = []
        for user in self.env["res.users"].search([]):
            if user.has_group("bi_fc_management_system.bi_fc_management_system_group_club_manager"):
                uids.append(user.id)
        return "[('id','in',{})]".format(uids)


    def _get_selection_list(self):
        lists = [("member","Member(s)"),("trainer","Trainer(s)")]
        if self.env.user.has_group("bi_fc_management_system.bi_fc_management_system_group_club_manager"):
            lists.append(("manager","Manager(s)"))
        return lists
        


    start_date = fields.Date('Start Date', required = True)
    end_date = fields.Date('End Date',required = True)
    attendance_of = fields.Selection(selection=[("staff","Staff's"),("child","Child's")], default="staff", string="Attendance Of");
    child_ids = fields.Many2many("res.partner","res_partner_cc_att_wizard",string="Child(s)",domain="[('is_child','=',True)]");
    staff_ids = fields.Many2many("hr.employee","hr_employee_cc_att_wizard",string="Staff(s)",domain="[('is_staff','=',True)]");



    def print_report_data(self):
        if self.attendance_of == "staff":
            att_ids = self.env['hr.attendance'].search([('cc_attendance','=',True),('employee_id','in',self.staff_ids.ids)]);
            att_ids = att_ids.filtered(lambda a: a.check_in.date() >= self.start_date and a.check_out.date() <= self.end_date);
            attendances = {};

            user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
            date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format + ' %H:%M:%S'
            
            for att in att_ids:
                check_in = att.check_in.replace(tzinfo=pytz.utc).astimezone(user_tz).strftime(date_format)
                check_out = att.check_out.replace(tzinfo=pytz.utc).astimezone(user_tz).strftime(date_format)
                if att.employee_id.id not in attendances:
                    attendances[att.employee_id.id] = (att.employee_id.user_id.name or att.employee_id.name, [{'sign_in': check_in,'sign_out': check_out,'worked_hours': self.float_time_convert(att.worked_hours),'worked_hours_flt':att.worked_hours,}])
                else:
                    attendances[att.employee_id.id][1].append({'sign_in': check_in,'sign_out': check_out,'worked_hours': self.float_time_convert(att.worked_hours),'worked_hours_flt':att.worked_hours,})

            date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format
            start_date = self.start_date.strftime(date_format)
            end_date = self.end_date.strftime(date_format)
            message = "staff(s)"
            return {
                    'start_date': start_date,
                    'end_date': end_date,
                    'records':attendances,
                    'message':message, 
                }

        if self.attendance_of == "child":
            att_ids = self.env['cc.child.attendance'].search([('child_id','in',self.child_ids.ids)]);
            att_ids = att_ids.filtered(lambda a: a.check_in.date() >= self.start_date and a.check_out.date() <= self.end_date);
            attendances = {};

            user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
            date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format + ' %H:%M:%S'
            
            for att in att_ids:
                check_in = att.check_in.replace(tzinfo=pytz.utc).astimezone(user_tz).strftime(date_format)
                check_out = att.check_out.replace(tzinfo=pytz.utc).astimezone(user_tz).strftime(date_format)
                if att.child_id.id not in attendances:
                    attendances[att.child_id.id] = (att.child_id.name, [{'sign_in': check_in,'sign_out': check_out,'worked_hours': self.float_time_convert(att.worked_hours),'worked_hours_flt':att.worked_hours,}])
                else:
                    attendances[att.child_id.id][1].append({'sign_in': check_in,'sign_out': check_out,'worked_hours': self.float_time_convert(att.worked_hours),'worked_hours_flt':att.worked_hours,})

            date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format
            start_date = self.start_date.strftime(date_format)
            end_date = self.end_date.strftime(date_format)
            message = "child(s)"
            return {
                    'start_date': start_date,
                    'end_date': end_date,
                    'records':attendances,
                    'message':message, 
                }

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


    def print_report(self):
        return self.env.ref('bi_morpho_childcare_management.cc_attendance_report').report_action(self)
