# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, fields, _
from odoo.http import request
from odoo.exceptions import ValidationError,UserError
from werkzeug.exceptions import NotFound
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
import datetime
import base64


class ChildcareManagement(http.Controller):


	@http.route(["/web/childcare"], type="http", auth="user", website=True)
	def ChildCareWebsite(self, **kw):
		user = request.env.user
		data = {"name" : user.name,"ho":True,};
		return request.render("bi_morpho_childcare_management.cc_home_portal_template",data); 


	@http.route(["/web/childcare/add"],type="http", auth="public", website=True)
	def ChildCareAddmission(self, **kw):
		data = {};
		request.session.update({"allergies":[],"medications":[], "is_submitted": False,})
		data["country"] = request.env["res.country"].sudo().search([]); 
		data["state"] = request.env["res.country.state"].sudo().search([]);
		return request.render("bi_morpho_childcare_management.cc_admission_enquiry_form_template",data); 


	@http.route(["/cc/add/allergy"], type="json", auth="public", website=True)
	def ChildCareAddAllergy(self, **kw):
		data = {};
		request.session.update({"allergies":request.session.get("allergies", []) + [{"name":kw.get("name"),"des":kw.get("des"),}],});
		return True;


	@http.route(["/cc/edit/allergy"], type="json", auth="public", website=True)
	def ChildCareEditAllergy(self, **kw):
		alg_list = request.session.get("allergies", []);
		alg_list[int(kw.get("id")) - 1].update({"name":kw.get("name"),"des":kw.get("des"),})
		request.session.update({"allergies": alg_list,});
		return True;


	@http.route(["/cc/del/allergy"], type="json", auth="public", website=True)
	def ChildCareDelAllergy(self, **kw):
		data = {};
		alg_list = request.session.get("allergies", []);
		try:
			alg_list.pop(int(kw.get("no")) - 1);
		except:
			return False;
		request.session.update({"allergies": alg_list,});
		return True;



	@http.route(["/cc/add/medication"], type="json", auth="public", website=True)
	def ChildCareAddMedication(self, **kw):
		data = {};
		request.session.update({"medications":request.session.get("medications", []) + [{"name":kw.get("name"),"des":kw.get("des"),}],});
		return True;


	@http.route(["/cc/edit/medication"], type="json", auth="public", website=True)
	def ChildCareEditMedication(self, **kw):
		medi_list = request.session.get("medications", []);
		medi_list[int(kw.get("id")) - 1].update({"name":kw.get("name"),"des":kw.get("des"),})
		request.session.update({"medications": medi_list,});
		return True;


	@http.route(["/cc/del/medication"], type="json", auth="public", website=True)
	def ChildCareDelMedication(self, **kw):
		data = {};
		medi_list = request.session.get("medications", []);
		try:
			medi_list.pop(int(kw.get("no")) - 1);
		except:
			return False;
		request.session.update({"medications": medi_list,});
		return True;





	@http.route(["/cc/add/cancel"], type="http", auth="public", website=True)
	def ChildCareAddCancel(self, **kw):
		request.session.update({"allergies":[],"medications":[], "is_submitted": False,});
		return request.redirect("/");



	@http.route(["/cc/submit/add"], type="http", methods=['POST'], auth="public", website=True)
	def ChildCareAddSubmit(self, parent_imge, child_imge, **kw):
		if request.session.get("is_submitted", False):
			return request.redirect("/");
		vals = {
					"c_fname" : kw.get("child_first_name"),
					"c_lname" : kw.get("child_last_name"),
					"c_dob" : kw.get("child_bod"),
					"c_gender" : kw.get("c_gender"),
					"allergy_ids" : [(0,0,lst) for lst in request.session.get("allergies", [])],
					"medication_ids" : [(0,0,lst) for lst in request.session.get("medications", [])],
					"description" : kw.get("reason_applying"),
					"p_name" : kw.get("parent_name"),
					"p_email" : kw.get("parent_email"),
					"p_phone" : kw.get("parent_phone", ""),
					"p_mobile" : kw.get("parent_mobile",""),
					"p_type" : kw.get("parent_type"),
					"p_gender" : kw.get("p_gender"),
					"type" : "lead",
					"name" : kw.get("parent_name"),
					"is_cc_lead" : True,
					"cc_status" : "draft",
					"street" : kw.get("street",""),
					"street2" : kw.get("street2",""),
					"city" : kw.get("city", ""),
					"zip" : kw.get("zip",""),
				}
		if kw.get("parent_country"):
			vals.update({"country_id" : int(kw.get("parent_country"))});
		if kw.get("parent_add_state"):
			vals.update({"state_id" : int(kw.get("parent_add_state"))});
		if not vals.get("name", False):
			request.session.update({"allergies":[],"medications":[]})
			data = {"stauts" : False,}
			return request.render("bi_morpho_childcare_management.cc_form_submission_status",data); 
		try:
			child_lead = request.env["crm.lead"].sudo().create(vals);
		except:
			request.session.update({"allergies":[],"medications":[]})
			data = {"stauts" : False,}
			return request.render("bi_morpho_childcare_management.cc_form_submission_status",data);
		images_vals = [];
		if child_imge.filename:
			images_vals.append({
								'name': "child_profile",
								'res_model': "crm.lead",
								'res_id': child_lead.id,
								'type': 'binary',
								'datas': base64.b64encode(child_imge.read()),
						});
		if parent_imge.filename:
			images_vals.append({
								'name': "parent_profile",
								'res_model': "crm.lead",
								'res_id': child_lead.id,
								'type': 'binary',
								'datas': base64.b64encode(parent_imge.read()),
						});

		try:
			request.env["ir.attachment"].sudo().create(images_vals);
		except:
			raise UserError(_("File is not uploaded successfully."));
		child_lead.send_form_noftication();
		request.session.update({"allergies":[],"medications":[], "is_submitted": True,});
		data = {"name" : kw.get("parent_name"),"status":True,};
		
		return request.render("bi_morpho_childcare_management.cc_form_submission_status",data); 



	@http.route(["/web/ccenquiry/confirm/<int:id>"],type="http", auth="user", website=True)
	def ChildCareEnquiryConfirm(self, **kw):
		data = {};
		data.update({
						"lead_id": kw.get("id", False),
					});
		rooms = request.env["cc.room"].sudo().search([]),
		data.update({"room_ids" : rooms,})
		return request.render("bi_morpho_childcare_management.cc_enquiry_confirm_form_template",data); 



	@http.route(["/web/ccwaitlist/confirm/<int:id>"],type="http", auth="user", website=True)
	def ChildCareWaitlistConfirm(self, **kw):
		data = {};
		lead_id = kw.get("id", False)
		try:
			lead = request.env["crm.lead"].sudo().browse(int(lead_id))
		except:
			return request.render("bi_morpho_childcare_management.cc_error_message",data); 
		if lead.move_id:
			redirect_url = lead.move_id.cc_get_portal_url();
			return request.redirect(redirect_url);
		data.update({
						"lead_id": lead_id,
						"name": lead.name,
						"waitlist": lead.in_waiting_list,
					});
		return request.render("bi_morpho_childcare_management.cc_waitlist_confirm_form_template",data); 




	@http.route(["/cc/enquiry/submit"],type="http", auth="user", website=True)
	def ChildCareEnquiryConfirmSubmit(self, **kw):
		data = {};
		waitlist = kw.get("waitlist",False);
		lead_id = kw.get("lead_id",False);
		room_id = kw.get("cc_room",False);
		joining_date = kw.get("sch_join_date",False);
		duration = kw.get("sch_period",False);
		income = kw.get("family_income",0);
		if lead_id and room_id and not waitlist:
			lead = request.env["crm.lead"].sudo().browse(int(lead_id));
			room = request.env["cc.room"].sudo().browse(int(room_id));
			lead = lead.sudo();
			lead.update({
				"room_id": room.id if room else False,
				"joining_date": joining_date,
				})
			lead.child_id.family_income = income;
			vaccancy = room.check_room_vaccancy();
			if vaccancy > 0:
				invoice = lead.prepare_invoice(period=duration);
				if invoice:
					lead.cc_status = "invoice";
				redirect_url = invoice.cc_get_portal_url();
				return request.redirect(redirect_url);
			else:
				lead.cc_status = "wait";
				data.update({"status": True, "name": lead.p_name,})
				return request.render("bi_morpho_childcare_management.cc_add_full_notification",data); 
		
		if lead_id and waitlist:
			lead = request.env["crm.lead"].sudo().browse(int(lead_id));
			room = lead.room_id;
			lead = lead.sudo();
			lead.update({
				"joining_date": joining_date,
			})

			lead.child_id.family_income = income;
			vaccancy = room.check_room_vaccancy();
			if vaccancy > 0:
				invoice = lead.prepare_invoice(period=duration);
				if invoice:
					lead.cc_status = "invoice";
				redirect_url = "/my/cc/invoices/%s?access_token=%s"%(invoice.id, request.session.get("access_token",""));
				return request.redirect(redirect_url);
			else:
				lead.cc_status = "wait";
				data.update({"status": True, "name": lead.p_name,})
				return request.render("bi_morpho_childcare_management.cc_add_full_notification",data); 

		return request.render("bi_morpho_childcare_management.cc_error_message",data); 




	

