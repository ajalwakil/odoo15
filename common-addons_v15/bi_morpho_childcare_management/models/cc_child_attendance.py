# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression
from odoo.tools import format_datetime


class CCChildAttendance(models.Model):
	_name = "cc.child.attendance"
	_description = "Child Attendance"
	_order = "check_in desc"


	# def _default_employee(self):
	# 	return self.env.user.partner_id.cc_child_ids.ids[0]

	child_id = fields.Many2one("res.partner", string="Child",required=True, ondelete='cascade', index=True)
	check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=True)
	check_out = fields.Datetime(string="Check Out")
	worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)

	company_id = fields.Many2one("res.company", string="Company", default=lambda s: s.env.company.id or s.env.user.company_id.id);
	user_id = fields.Many2one("res.users", string="Responsible", default=lambda s: s.env.user.id);


	def name_get(self):
		result = []
		for attendance in self:
			if not attendance.check_out:
				result.append((attendance.id, _("%(child_name)s from %(check_in)s") % {
					'child_name': attendance.child_id.name,
					'check_in': format_datetime(self.env, attendance.check_in, dt_format=False),
				}))
			else:
				result.append((attendance.id, _("%(child_name)s from %(check_in)s to %(check_out)s") % {
					'child_name': attendance.child_id.name,
					'check_in': format_datetime(self.env, attendance.check_in, dt_format=False),
					'check_out': format_datetime(self.env, attendance.check_out, dt_format=False),
				}))
		return result

	@api.depends('check_in', 'check_out')
	def _compute_worked_hours(self):
		for attendance in self:
			if attendance.check_out and attendance.check_in:
				delta = attendance.check_out - attendance.check_in
				attendance.worked_hours = delta.total_seconds() / 3600.0
			else:
				attendance.worked_hours = False

	@api.constrains('check_in', 'check_out')
	def _check_validity_check_in_check_out(self):
		for attendance in self:
			if attendance.check_in and attendance.check_out:
				if attendance.check_out < attendance.check_in:
					raise ValidationError(_('"Check Out" time cannot be earlier than "Check In" time.'))

	@api.constrains('check_in', 'check_out', 'child_id')
	def _check_validity(self):
		for attendance in self:
			last_attendance_before_check_in = self.env['cc.child.attendance'].search([
				('child_id', '=', attendance.child_id.id),
				('check_in', '<=', attendance.check_in),
				('id', '!=', attendance.id),
			], order='check_in desc', limit=1)
			if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
				raise ValidationError(_("Cannot create new attendance record for %(child_name)s, the child was already checked in on %(datetime)s") % {
					'child_name': attendance.child_id.name,
					'datetime': format_datetime(self.env, attendance.check_in, dt_format=False),
				})

			if not attendance.check_out:
				no_check_out_attendances = self.env['cc.child.attendance'].search([
					('child_id', '=', attendance.child_id.id),
					('check_out', '=', False),
					('id', '!=', attendance.id),
				], order='check_in desc', limit=1)
				if no_check_out_attendances:
					raise ValidationError(_("Cannot create new attendance record for %(child_name)s, the child hasn't checked out since %(datetime)s") % {
						'child_name': attendance.child_id.name,
						'datetime': format_datetime(self.env, no_check_out_attendances.check_in, dt_format=False),
					})
			else:
				last_attendance_before_check_out = self.env['cc.child.attendance'].search([
					('child_id', '=', attendance.child_id.id),
					('check_in', '<', attendance.check_out),
					('id', '!=', attendance.id),
				], order='check_in desc', limit=1)
				if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
					raise ValidationError(_("Cannot create new attendance record for %(child_name)s, the child was already checked in on %(datetime)s") % {
						'child_name': attendance.child_id.name,
						'datetime': format_datetime(self.env, last_attendance_before_check_out.check_in, dt_format=False),
					})

	@api.returns('self', lambda value: value.id)
	def copy(self):
		raise UserError(_('You cannot duplicate an attendance.'))
