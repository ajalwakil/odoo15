# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, fields, _
from werkzeug.exceptions import NotFound
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.addons.portal.controllers.mail import PortalChatter
from odoo.http import request, route
import datetime
import re
from odoo.exceptions import AccessError, MissingError


class CCPortalChilds(CustomerPortal):


	@http.route(['/my/cc/childs'], type='http', auth="user", website=True)
	def cc_portal_my_childs(self, **kw):
		partner_id = request.env.user.partner_id;
		childs = partner_id.cc_child_ids.get_childs().sudo();
		data = {"childs" : childs,"chd":True};
		return request.render("bi_morpho_childcare_management.cc_childs_portal_template", data)


	@http.route(['/my/cc/childs/<int:child_id>'], type='http', auth="user", website=True)
	def cc_portal_my_childs_detail(self, child_id, access_token=None, report_type=None, download=False, **kw):

		child_sudo = request.env["res.partner"].sudo().browse(int(child_id));
		data = {"child" : child_sudo,"chd":True, "title":child_sudo.name,};
		return request.render("bi_morpho_childcare_management.cc_child_portal_template", data)




	@http.route(['/my/cc/childs/check'], type='http', auth="user", website=True)
	def cc_portal_my_childs_check(self, **kw):
		partner_id = request.env.user.partner_id.sudo();
		childs = partner_id.cc_child_ids.get_childs().filtered(lambda s: s.cc_status == "enroll");
		mess = "";
		if partner_id.cc_child_ids != childs:
			mess = "Your child is not enrolled yet."
		data = {	
					"title" : "Child's Check In/Out",
					"childs" : childs.sudo(),
					"chk" : True,
					"error_mess" : mess,
				};
		return request.render("bi_morpho_childcare_management.cc_child_check_in_out_template", data);



	@http.route(["/cc/chk/name"], type="json", auth="user", website=True)
	def cc_portal_my_childs_chkname(self, child_id, **kw):
		child_id = int(child_id);
		dt = fields.Datetime.today();
		dt = datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0);
		attend = request.env["cc.child.attendance"].sudo().search([("child_id","=",child_id),"|",("check_in",">=",dt),("check_out",">=",dt)]);
		attend = attend.filtered(lambda s: s.check_in and not s.check_out);
		
		if attend and attend.check_in and not attend.check_out:
			return "Out";
		else:
			return "In";


	@http.route(["/my/cc/childs/checkinout"], type="json", auth="user", website=True)
	def cc_portal_my_childs_checkinout(self, child_id, inout, pinpass, **kw):
		
		child_id = int(child_id);
		child = request.env["res.partner"].sudo().browse(child_id);
		if inout == "In":
			vals = {
						"check_in" : datetime.datetime.today(),
						"child_id" : child_id, 
				}
			if len(pinpass) == 4 and child.varify_pinpass(pinpass):
				request.env["cc.child.attendance"].sudo().create(vals);
				return {'success' : True, 'message' : 'Child check in successfully.'};
			else:
				return {'warning': _('Wrong PIN')};
		elif inout == "Out":
			dt = fields.Datetime.today();
			dt = datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0);
			attend = request.env["cc.child.attendance"].sudo().search([("child_id","=",child_id),"|",("check_in",">=",dt),("check_out","=",False)]);
			if not attend:
				return {'warning': _("Can not check out as selected child is not checked in")}
			else:
				if len(pinpass) == 4 and child.varify_pinpass(pinpass):
					attend.check_out = datetime.datetime.today();
					return {'success' : True, 'message' : 'Child check out successfully.'};
				else:
					return {'warning': _('Wrong PIN')};
		else:
			return {'warning': _('Failed to mark attendance')};




	@http.route(["/my/cc/parent/engagement"], type="http", auth="user", website=True)
	def cc_portal_parent_engagement(self, **kw):
		data = {"title" : "Parent Engagement", "pe": True,};
		partner_id = request.env.user.partner_id.sudo();
		childs = partner_id.cc_child_ids.sudo().get_childs().filtered(lambda s: s.cc_status == "enroll");
		mess = "";
		if partner_id.cc_child_ids != childs:
			mess = "Your child is not enrolled yet."
		data.update({
						"childs" : childs.sudo(),
						"error_mess" : mess,
					});
		return request.render("bi_morpho_childcare_management.cc_parent_engagement_template", data)



	@http.route(["/my/cc/child/reports"], type="http", auth="user", website=True)
	def cc_portal_child_reports(self, child_id=None, report_no=False, access_token=None, sdate="", edate="", report_type=None, download=False, **kw):
		data = {"title" : "Childs Reports", "re": True,};
		partner_id = request.env.user.partner_id.sudo();
		childs = partner_id.cc_child_ids.get_childs().filtered(lambda s: s.cc_status == "enroll");
		mess = "";
		if partner_id.cc_child_ids != childs:
			mess = "Your child is not enrolled yet."

		if child_id and report_type == 'pdf':
			child = request.env["res.partner"].sudo().browse(int(child_id));
			if report_no == '1':
				report_ref = 'bi_morpho_childcare_management.cc_activity_report';
			if report_no == '2':
				sdate = sdate.split("-");
				edate = edate.split("-");
				if len(sdate) == 3 and len(sdate[0]) == 4 and len(sdate[1]) == 2 and len(sdate[2]) == 2:
					child.reatt_st_date = fields.date(int(sdate[0]), int(sdate[1]), int(sdate[2]));
				if len(edate) == 3 and len(edate[0]) == 4 and len(edate[1]) == 2 and len(edate[2]) == 2:
					child.reatt_end_date = fields.date(int(edate[0]), int(edate[1]), int(edate[2]));
				report_ref = 'bi_morpho_childcare_management.cc_child_attendance_reports';
			if report_no == '3':
				report_ref = 'bi_morpho_childcare_management.cc_nutrition_report';
			return self._show_report(model=child, report_type=report_type, report_ref=report_ref, download=download)

		data.update({
						"childs" : childs.sudo(),
						"error_mess" : mess,
					});
		return request.render("bi_morpho_childcare_management.cc_reports_template", data)




class CCPortalChatter(PortalChatter):

	@http.route('/mail/chatter_fetch', type='json', auth='public', website=True)
	def portal_message_fetch(self, res_model, res_id, domain=False, limit=10, offset=0, **kw):
		if kw.get("is_parent"):
			Message = request.env['mail.message'].sudo()
			domain = [('cc_attachment', '=', True),
						('res_id', 'in', request.env.user.partner_id.cc_child_ids.get_childs().ids),
						('model', '=', 'res.partner'), 
						'|', ('message_type', '=', 'comment'), 
						('message_type', '=', 'email')]
			return {
				'messages': Message.search(domain, limit=limit, offset=offset).portal_message_format(),
				'message_count': Message.search_count(domain)
			}
		else:
			return super(CCPortalChatter, self).portal_message_fetch(res_model, res_id, domain=domain, limit=limit, offset=offset, kw=kw)