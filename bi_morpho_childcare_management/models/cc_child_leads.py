# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import datetime
from random import randint
from dateutil.relativedelta import relativedelta
from passlib.context import CryptContext


class CRMLeadInherit(models.Model):
    _inherit = "crm.lead"


    def _get_enquiry_id(self):
        for rec in self:
            rec.enquiry_id = rec.id;


    is_cc_lead = fields.Boolean(string="Is Childcare Lead");
    group_flag = fields.Boolean(default=True, readonly=True);
    enquiry_id = fields.Integer(string="Enquiry ID",compute="_get_enquiry_id");
    child_id = fields.Many2one("res.partner", string="Child");
    parent_id = fields.Many2one("res.partner.parentchild", string="Parent");
    room_id = fields.Many2one("cc.room", string="Classroom");
    school_id = fields.Many2one(related="room_id.school_id");
    joining_date = fields.Date(string="Joining School");
    move_id = fields.Many2one("account.move", string="Fees Invoice");
    in_waiting_list = fields.Boolean(string="In Waiting List");
    cc_status = fields.Selection([("draft","Draft"),
                                    ("confirm","Confirm"),
                                    ("wait","Waiting"),
                                    ("invoice","Invoiced"),
                                    ("enroll","Enrolled"),
                                    ], default="draft", string="Status",store=True,copy=False);
    fees_type = fields.Selection([("1","Monthly"),("2","Yearly")], string="Fees Duration", default="1");
    
    # Child Details
    c_fname = fields.Char(string="First Name");
    c_lname = fields.Char(string="Last Name");
    c_dob = fields.Date(string=" Child's BirthDate");
    c_gender = fields.Selection([("male", "Male"),
                                ("female", "Female"),
                                ("other", "Other")], string="Gender", default=False);
    allergy_ids = fields.One2many("lead.allergy", "lead_id", string="Allergies");
    medication_ids = fields.One2many("lead.medication", "lead_id", string="Medications");


    # Parent Details
    p_name = fields.Char(string="Parent");
    p_email = fields.Char(string="Email");
    p_phone = fields.Char(string="Phone");
    p_mobile = fields.Char(string="Mobile");
    p_gender = fields.Selection([("male", "Male"),
                                ("female", "Female"),
                                ("other", "Other")], string="Gender",default=False);
    p_type = fields.Selection([("parent","Parent"),
                                ("family","Family"),
                                ("pickup","Approved Pickup")], string="Parent Type", default=False);


    def send_form_noftication(self):
        self.ensure_one();
        template_id = self.env.ref("bi_morpho_childcare_management.cc_enquiry_mail_template").id;
        template = self.env['mail.template'].browse(template_id);
        template.send_mail(self.id,force_send=True);
        return True;


    def create_child(self):
        image = self.env["ir.attachment"].search([("res_id","=",self.id),("name","=","child_profile")]);
        vals = {	
                "name" : self.c_fname + " " + self.c_lname,
                "is_child" : True,
                "gender"   : self.c_gender,
                "dob"      : self.c_dob,
                "enquiry_date" : self.date_open,
                "cc_status" : "enquiry",
                "image_1920" : image.datas,
                "street" : self.street,
                "street2" : self.street2,
                "city" : self.city,
                "zip" : self.zip,
                "country_id" : self.country_id.id,
                "state_id" : self.state_id.id,
            }
        child = self.env["res.partner"].sudo().create(vals);
        for alg in self.allergy_ids:
            alg.child_id = child.id;
        for medi in self.medication_ids:
            medi.child_id = child.id;
        self.child_id = child.id;
        return child;


    def create_parent(self):
        image = self.env["ir.attachment"].search([("res_id","=",self.id),("name","=","parent_profile")]);
        vals = {	
                "name" : self.p_name,
                "is_parent" : True,
                "gender"   : self.p_gender,
                "phone"   : self.p_phone,
                "mobile"   : self.p_mobile,
                "email"   : self.p_email,
                "parent_type"   : self.p_type,
                "image_1920" : image.datas,
                "street" : self.street,
                "street2" : self.street2,
                "city" : self.city,
                "zip" : self.zip,
                "country_id" : self.country_id.id,
                "state_id" : self.state_id.id,
            }
        parent = self.env["res.partner.parentchild"].sudo().create(vals);
        self.parent_id = parent.id;
        return parent;


    def prepare_invoice(self, period=None):
        self.ensure_one();
        if period:
            self.fees_type = period;
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal();
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        model_id = self.env['ir.model'].sudo().search([('model', '=', 'account.move')])
        l10n_in_gst_treatment = self.env['ir.model.fields'].sudo().search(
            [('name', '=', 'l10n_in_gst_treatment'), ('model_id', '=', model_id.id)])
        
        invoice_vals = {
            'ref': self.name or '',
            'move_type': 'out_invoice',
            'narration': self.description,
            'currency_id': self.company_id.currency_id.id,
            'user_id': self.user_id.id,
            'invoice_user_id': self.user_id.id,
            'partner_id': self.parent_id.res_partner_id.id,
            'partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'journal_id': journal.id, 
            'invoice_origin': self.name,
            'invoice_line_ids': [(0,0,self._prepare_invoice_line(period=period))],
            'company_id': self.company_id.id,
            'cc_invoice': True,
            'cc_child_id': self.child_id.id,
        }

        if l10n_in_gst_treatment:
            invoice_vals.update({
                'l10n_in_gst_treatment': 'consumer'
            })
  
        invoice = self.env["account.move"].sudo().create(invoice_vals);
        invoice.action_post();
        self.move_id = invoice.id;
        return invoice;


    def _prepare_invoice_line(self, period=None):
        self.ensure_one()
        product_id = self.env["product.product"].search([("cc_product","=",True),("fees_type","=",period)], limit=1);
        if not product_id:
            product_id = self.env["product.product"].search([("cc_product","=",True)], limit=1);
            if not product_id:
                raise UserError(_('Please define fees product'));
        if self.room_id and self.room_id.school_id.school_fees:
            fees = self.room_id.school_id.school_fees;
        else:
            fees = product_id.lst_price;
        types = {"1" : "Monthly", "2" : "Yearly",}
        product_name = "[%s] "%product_id.default_code +  product_id.name + " (%s)"%types.get(period or product_id.fees_type,"");
        
        qty = 1
        if period and product_id.fees_type != period:
            if product_id.fees_type == "1" and period == "2":
                qty = 12;

        res = {
            'display_type': False,
            'name': product_name,
            'product_id': product_id.id,
            'product_uom_id': product_id.uom_id.id,
            'quantity': qty,
            'price_unit': fees,
            'tax_ids': [(6, 0, product_id.taxes_id.ids)],
        }
        return res


    def _cal_school_end_date(self):
        product_id = self.env["product.product"].search([("cc_product","=",True)], limit=1);
        today = self.joining_date or fields.Date.today();
        period = self.fees_type or product_id.fees_type
        if period == "1":
            enddate = today + relativedelta(months=1);
        else:
            enddate = today + relativedelta(years=1);
        return enddate;



    def _create_school_reg(self):
        today = fields.Date.today();
        regis = self.child_id.sudo().registration_ids.filtered(lambda s: s.end_date >= today);
        if regis:
            raise UserError(_("There is already registration record present for %s child."%self.child_id.name));
        vals_reg = {
                    "child_id" : self.child_id.id,
                    "room_id" : self.room_id.id,
                    "school_id" : self.room_id.school_id.id,
                    "reg_date" : fields.Date.today(),
                    "start_date" : self.joining_date or fields.Date.today(),
                    "end_date" : self._cal_school_end_date(),
                }
        self.env["cc.school.registration"].sudo().create(vals_reg);
        self.child_id.main_room_id = self.room_id.id;
        self.child_id._onchange_staffs();
        self.child_id.cc_status = "enroll";



    def send_enroll_confirmation(self):
        template_id = self.env.ref("bi_morpho_childcare_management.cc_enroll_confirm_mail_template").id;
        template = self.env['mail.template'].browse(template_id);
        template.send_mail(self.id,force_send=True);


    def get_payment_url(self, wait=False):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url');
        if wait:
            extention = "/web/login?redirect=/web/ccwaitlist/confirm/%s"%(self.id);
        else:
            extention = "/web/login?redirect=/web/ccenquiry/confirm/%s"%(self.id);
        return base_url + extention


    def get_rel_user(self):
        user = self.env["res.users"].sudo().search([('partner_id','=',self.parent_id.res_partner_id.id)], limit=1);
        pwd = randint(1000,100000000);
        pwd = user.name + str(pwd);
        pwd = pwd.replace(" ","");
        user.sudo().write({'password': pwd});
        if user:
            return [user.login, pwd];
        else:
            raise UserError(_('Please create user for %s')%(self.parent_id.name));


    def confirm_enrollment(self):
        self.ensure_one();
        rec = self;
        if rec.cc_status == "draft":
            if not rec.child_id and not rec.parent_id:
                child = rec.create_child();
                parent = rec.create_parent();
                parent.cc_child_id = child.id;
            else:
                child = rec.child_id;
                parent = rec.parent_id;
            rec.partner_id = parent.res_partner_id.id;
            rec.user_id = self.env.user.id;
            rec.company_id = self.env.company.id;
            rec.send_enroll_confirmation()
            rec.cc_status = "confirm";
        


    def set_childs_pinpass(self):
        pin = randint(0,9999);
        pin = str(pin);
        if len(pin) < 4:
            pin = "0"*(4 - len(pin)) + pin;
        self.child_id.pin = CryptContext(schemes=['pbkdf2_sha512']).encrypt(pin);
        return pin;


    def action_cancel(self):
        for rec in self:
            rec.cc_status = "cancel";


    def action_enrolled(self):
        for rec in self:
            rec.cc_status = "enroll";


    def action_confirm_payment(self):
        for rec in self:
            if rec.move_id.payment_state != "paid":
                model_id = self.env['ir.model'].sudo().search([('model', '=', 'account.move')])
                l10n_in_company_country_code = self.env['ir.model.fields'].sudo().search(
                    [('name', '=', 'l10n_in_company_country_code'), ('model_id', '=', model_id.id)])
                if l10n_in_company_country_code:
                    if rec.move_id.l10n_in_company_country_code == "IN":
                        rec.move_id.l10n_in_gst_treatment = "unregistered"
                raise UserError(_("Fees for this addmission in not paid. Can't move to enrolled."));
            else:
                template_id = self.env.ref("bi_morpho_childcare_management.cc_enroll_done_mail_template").id;
                template = self.env['mail.template'].browse(template_id);
                template.send_mail(self.id,force_send=True);
                return self.env.ref("crm.action_crm_lead2opportunity_partner").sudo().read()[0];



    def action_cc_invoice(self):
        self.ensure_one();
        action = self.env.ref("account.action_move_out_invoice_type").sudo().read()[0];
        action["domain"] = "[('move_type','=','out_invoice'),('id','in',{})]".format(self.move_id.ids);
        action["name"] = "School Fees";
        action["context"] = {'default_cc_invoice':True, 'default_move_type':'out_invoice',};
        return action;


    def action_move_waitlist(self):
        self.ensure_one();
        return {
                "name" : _("Confirmation"),
                "type" : "ir.actions.act_window",
                "res_model" : "cc.waitlist.confirmation.wizard",
                "view_mode" : "form",
                "target" : "new",
            }


    def action_confirm_waitlist(self):
        for rec in self:
            if rec.cc_status == "wait" and rec.in_waiting_list:
                if rec.room_id and rec.room_id.check_room_vaccancy() > 0:
                    template_id = self.env.ref("bi_morpho_childcare_management.cc_waitlist_confirm_mail_template").id;
                    template = self.env['mail.template'].browse(template_id);
                    template.send_mail(self.id,force_send=True);
                    rec.in_waiting_list = False; 
                    rec.cc_status = "confirm";
                else:
                    raise UserError(_("%s Room has no vaccency for new addmission."%(rec.room_id.name)));


    def redirect_lead_opportunity_view(self):
        self.ensure_one();
        if self.is_cc_lead:
            self.cc_status = "enroll";
            self._create_school_reg();
            form_id = self.env.ref("bi_morpho_childcare_management.cc_child_leads_form_view").id;
            return {
                'name': _('Enrollements'),
                'view_mode': 'form',
                'res_model': 'crm.lead',
                'domain': [('type', '=', self.type)],
                'res_id': self.id,
                'view_id': form_id,
                'type': 'ir.actions.act_window',
                'context': {'default_type': self.type}
            }
        else:
            super(CRMLeadInherit, self).redirect_lead_opportunity_view();



class LeadAllergies(models.Model):
    _name = "lead.allergy"
    _description = "Lead Allergies Line"

    lead_id = fields.Many2one("crm.lead");
    child_id = fields.Many2one("res.partner");
    name = fields.Char(string="Allergy Name");
    des = fields.Text(string="Description");

    company_id = fields.Many2one("res.company", string="Company", default=lambda s: s.env.company.id or s.env.user.company_id.id);
    user_id = fields.Many2one("res.users", string="Company", default=lambda s: s.env.user.id);




class LeadMedication(models.Model):
    _name = "lead.medication"
    _description = "Lead Medications Line"

    lead_id = fields.Many2one("crm.lead");
    child_id = fields.Many2one("res.partner");
    name = fields.Char(string="Allergy Name");
    des = fields.Text(string="Description");

    company_id = fields.Many2one("res.company", string="Company", default=lambda s: s.env.company.id or s.env.user.company_id.id);
    user_id = fields.Many2one("res.users", string="Company", default=lambda s: s.env.user.id);
