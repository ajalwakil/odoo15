# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, fields, _
from werkzeug.exceptions import NotFound
import datetime
import base64
from odoo.http import request, route
from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request



class CCPortalAccount(CustomerPortal):


	def _cc_get_invoices_domain(self):
		partner_id = request.env.user.partner_id;
		return [('move_type', '=', 'out_invoice'),('cc_invoice','=','True'),('partner_id','=',partner_id.id)]


	@http.route(['/my/cc/invoices', '/my/cc/invoices/page/<int:page>'], type='http', auth="user", website=True)
	def cc_portal_my_invoices(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
		values = self._prepare_portal_layout_values()
		AccountInvoice = request.env['account.move']

		domain = self._cc_get_invoices_domain()

		searchbar_sortings = {
		    'date': {'label': _('Date'), 'order': 'invoice_date desc'},
		    'duedate': {'label': _('Due Date'), 'order': 'invoice_date_due desc'},
		    'name': {'label': _('Reference'), 'order': 'name desc'},
		    'state': {'label': _('Status'), 'order': 'state'},
		}
		# default sort by order
		if not sortby:
			sortby = 'date'
		order = searchbar_sortings[sortby]['order']

		if date_begin and date_end:
			domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

		# count for pager
		invoice_count = AccountInvoice.search_count(domain)
		# pager
		pager = portal_pager(
		    url="/my/invoices",
		    url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
		    total=invoice_count,
		    page=page,
		    step=self._items_per_page
		)
		# content according to pager and archive selected
		invoices = AccountInvoice.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
		request.session['my_invoices_history'] = invoices.ids[:100]

		values.update({
		    'date': date_begin,
		    'invoices': invoices,
		    'page_name': 'invoice',
		    'pager': pager,
		    'default_url': '/my/cc/invoices',
		    'searchbar_sortings': searchbar_sortings,
		    'sortby': sortby,
		    'inv' : True,
		    "title":"School Fees"
		})
		return request.render("bi_morpho_childcare_management.cc_invoice_portal_template", values)


	@http.route(['/my/cc/invoices/<int:invoice_id>'], type='http', auth="public", website=True)
	def cc_portal_my_invoice_detail(self, invoice_id, access_token=None, report_type=None, download=False, **kw):
		try:
			invoice_sudo = self._document_check_access('account.move', invoice_id, access_token)
		except (AccessError, MissingError):
			return request.redirect('/my')

		if report_type in ('html', 'pdf', 'text'):
			return self._show_report(model=invoice_sudo, report_type=report_type, report_ref='account.account_invoices', download=download)

		values = self._invoice_get_page_view_values(invoice_sudo, access_token, **kw)
		values.update({"title":"School Fees", "inv":True,})
		return request.render("bi_morpho_childcare_management.cc_portal_invoice_page", values)


