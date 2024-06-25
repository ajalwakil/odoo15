# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from odoo.tools import format_datetime
import datetime


class CCAccountMoveInherit(models.Model):
	_inherit = "account.move"


	cc_invoice = fields.Boolean(default=False, string="Is Childcare invoice");
	cc_child_id = fields.Many2one("res.partner", string="Invoice For", domain="[('is_child','=',True)]");
	group_flag = fields.Boolean(default=True, readonly=True);


	def cc_get_portal_url(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
		self.ensure_one()
		access_url = "/my/cc/invoices/%s"%self.id;
		url = access_url + '%s?access_token=%s%s%s%s%s' % (
		    suffix if suffix else '',
		    self._portal_ensure_token(),
		    '&report_type=%s' % report_type if report_type else '',
		    '&download=true' if download else '',
		    query_string if query_string else '',
		    '#%s' % anchor if anchor else ''
		)
		return url