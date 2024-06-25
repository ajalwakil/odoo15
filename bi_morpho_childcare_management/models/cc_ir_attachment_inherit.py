# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import base64
import hashlib
import io
import itertools
import logging
import mimetypes
import os
import re
import uuid

from collections import defaultdict
from PIL import Image

from odoo import api, fields, models, tools, _
from odoo.exceptions import AccessError, ValidationError, MissingError, UserError
from odoo.tools import config, human_size, ustr, html_escape, ImageProcess, str2bool
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools import format_datetime
import datetime


class CCIrAttachmentInherit(models.Model):
	_inherit = "ir.attachment"


	cc_media = fields.Boolean(string="Childcare Media");
	cc_message = fields.Text(string="Message"); 

	@api.model
	def check(self, mode, values=None):
		if self.env.is_superuser():
			return True
		if not (self.env.is_admin() or self.env.user.has_group('base.group_user') or self.env.user.has_group('bi_morpho_childcare_management.bi_morpho_childcare_management_group_parent')):
			raise AccessError(_("Sorry, you are not allowed to access this document."))
		model_ids = defaultdict(set)            # {model_name: set(ids)}
		if self:
			self.env['ir.attachment'].flush(['res_model', 'res_id', 'create_uid', 'public', 'res_field'])
			self._cr.execute('SELECT res_model, res_id, create_uid, public, res_field FROM ir_attachment WHERE id IN %s', [tuple(self.ids)])
			for res_model, res_id, create_uid, public, res_field in self._cr.fetchall():
				if not self.env.is_system() and res_field:
					raise AccessError(_("Sorry, you are not allowed to access this document."))
				if public and mode == 'read':
					continue
				if not (res_model and res_id):
					continue
				model_ids[res_model].add(res_id)
		if values and values.get('res_model') and values.get('res_id'):
			model_ids[values['res_model']].add(values['res_id'])

		for res_model, res_ids in model_ids.items():
			if res_model not in self.env:
				continue
			if res_model == 'res.users' and len(res_ids) == 1 and self.env.uid == list(res_ids)[0]:
				continue
			records = self.env[res_model].browse(res_ids).exists()
			access_mode = 'write' if mode in ('create', 'unlink') else mode
			records.check_access_rights(access_mode)
			records.check_access_rule(access_mode)


class CCMailMessageInherit(models.Model):
	_inherit = "mail.message"

	cc_attachment = fields.Boolean(string="Childcare Media");