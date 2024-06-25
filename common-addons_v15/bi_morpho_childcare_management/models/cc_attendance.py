# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from odoo.tools import format_datetime
import datetime


class CCAttendance(models.Model):
	_inherit = "hr.attendance"


	cc_attendance = fields.Boolean(string="Fitness Club Attendance");
	partner_id = fields.Many2one("res.partner", string="Member",domain="[('fc_member','=',True)]");
	group_flag = fields.Boolean(default=True,readonly=True);


	@api.depends("employee_id")
	def _related_partner(self):
		for rec in self:
			if rec.employee_id:
				rec.partner_id = rec.employee_id.user_partner_id.id \
				or rec.employee_id.user_id.partner_id.id or rec.env.user.partner_id.id;



class HrEmployeeInherit(models.Model):
	_inherit = "hr.employee"


	def _cc_attendance_action_change(self):
		self.ensure_one()
		action_date = fields.Datetime.now()

		if self.attendance_state != 'checked_in':
			vals = {
			    'employee_id': self.id,
			    'check_in': action_date,
			    'cc_attendance': True,
			    'partner_id': self.user_partner_id.id \
								or self.user_id.partner_id.id \
								or self.env.user.partner_id.id,
			}
			return self.env['hr.attendance'].create(vals)
		attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '=', False)], limit=1)
		if attendance:
			attendance.check_out = action_date
		else:
			raise exceptions.UserError(_('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
				'Your attendances have probably been modified manually by human resources.') % {'empl_name': self.sudo().name, })
		return attendance



	def _attendance_action(self, next_action):
		self.ensure_one()
		if next_action != "bi_morpho_childcare_management.cc_attendance_js_action":
			return super(HrEmployeeInherit, self)._attendance_action(next_action)

		employee = self.sudo()
		action_message = self.env["ir.actions.actions"]._for_xml_id("hr_attendance.hr_attendance_action_greeting_message")
		action_message['previous_attendance_change_date'] = employee.last_attendance_id and (employee.last_attendance_id.check_out or employee.last_attendance_id.check_in) or False
		action_message['employee_name'] = employee.name
		action_message['barcode'] = employee.barcode
		action_message['next_action'] = next_action
		action_message['hours_today'] = employee.hours_today

		if employee.user_id:
			modified_attendance = employee.with_user(employee.user_id)._cc_attendance_action_change()
		else:
			modified_attendance = employee._cc_attendance_action_change()
		action_message['attendance'] = modified_attendance.read()[0]
		action_message['total_overtime'] = employee.total_overtime
		return {'action': action_message}

		
