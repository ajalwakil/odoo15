# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression
from datetime import date


class CCSchool(models.Model):
    _name = "cc.school"
    _description = "School"


    @api.onchange("room_ids")
    def _get_total_intek(self):
        for rec in self:
            if len(rec.room_ids or []):
                rec.total_intek = sum(room.total_intek for room in rec.room_ids);
            else:
                rec.total_intek = 0;


    def _get_director_domain(self):
        emps = self.env["hr.employee"].search([]);
        emps = emps.filtered(lambda e: e.user_id and e.user_id.has_group("bi_morpho_childcare_management.bi_morpho_childcare_management_group_director"));
        for emp in emps:
            emp.is_staff = True;
        return "[('id','in',{})]".format(emps.ids);




    name = fields.Char(string="School Name", required=True);
    school_seq = fields.Char(string="School ID");
    director_id = fields.Many2one("hr.employee", required=True, domain=_get_director_domain);

    # Address
    street = fields.Char(string="Street", required=True);
    street1 = fields.Char(string="Street1");
    city = fields.Char(string="City");
    state_id = fields.Many2one("res.country.state", required=True);
    country_id = fields.Many2one("res.country", required=True);
    zip_code = fields.Char(string="Zip Code", required=True);

    # Contact Details
    phone = fields.Char(string="Phone", required=True);
    mobile = fields.Char(string="Mobile", required=True);
    email = fields.Char(string="email", required=True);

    # General Fields
    company_id = fields.Many2one("res.company", string="Company", default=lambda s: s.env.company.id or s.env.user.company_id.id);
    user_id = fields.Many2one("res.users", string="Responsible", default=lambda s: s.env.user.id);

    room_ids = fields.One2many("cc.room", "school_id", string="Rooms");
    parent_id = fields.Many2one("cc.school", string="Parent");
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id");
    school_fees = fields.Monetary(string="School Fees", currency_field="currency_id");
    product_id = fields.Many2one("product.product", string="Fees", domain="[('cc_product','=',True)]")
    total_intek = fields.Integer(string="Total Intek", compute="_get_total_intek");
    registration_ids = fields.One2many("cc.school.registration","school_id");

    @api.model
    def default_get(self, fields):
        res = super(CCSchool, self).default_get(fields);
        product_id = self.env["product.product"].search([('cc_product','=',True)], limit=1);
        res.update({"product_id": product_id.id, "school_fees" : product_id.lst_price,});
        return res;


    @api.model
    def create(self, vals):
        if not vals.get("school_seq",False):
            seq_date = None;
            seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.today());
            vals["school_seq"] = self.env.ref("bi_morpho_childcare_management.bi_morpho_childcare_management_school_sequence").next_by_id() or "";
        return super(CCSchool, self).create(vals);


     


class CCSchoolRegistration(models.Model):
    _name = "cc.school.registration"
    _description = "School Registration"


    child_id = fields.Many2one("res.partner", string="Child", domain="[('is_child','=',True)]", copy=False);
    school_id = fields.Many2one("cc.school", string="School", copy=False);
    room_id = fields.Many2one("cc.room", string="Room", copy=False);
    reg_date = fields.Date(string="Registration Date",required=True)
    start_date = fields.Date(string="Start Date", required=True);
    end_date = fields.Date(string="End Date");

    company_id = fields.Many2one("res.company", string="Company", default=lambda s: s.env.company.id or s.env.user.company_id.id);
    user_id = fields.Many2one("res.users", string="Company", default=lambda s: s.env.user.id);