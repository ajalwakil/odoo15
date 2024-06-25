# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields,_
from odoo.exceptions import ValidationError,UserError


class CCAddParent(models.TransientModel):
    _name = "cc.addparent.wizard"
    _description = "Add Parent Wizard"      


    def _get_parent_domain(self):
        active_id = self.env["res.partner"].browse(self._context.get("active_id",False));
        return "[('id','not in',{})]".format(active_id.parent_ids.ids);

    # For Existing
    is_create = fields.Boolean(default=True);
    res_parent_id = fields.Many2one("res.partner", string="Parent", domain="[('is_parent','=',True)]");
    parent_id = fields.Many2one("res.partner.parentchild", string="Parent", domain=_get_parent_domain);

    # For New
    name = fields.Char(string="Name");
    parent_type = fields.Selection([("parent","Parent"),
                                    ("family","Family"),
                                    ("pickup","Approved Pickup")], default=False, required=True);
    gender = fields.Selection([("male", "Male"),
                                ("female", "Female"),
                                ("other", "Other")], string="Gender",default=False);
    phone = fields.Char(string="Phone");
    mobile = fields.Char(string="Mobile");
    email = fields.Char(string="Email ID", required=True);


    @api.model
    def default_get(self, fields):
        res = super(CCAddParent, self).default_get(fields);
        res["is_create"] = self._context.get("is_create", False);
        return res;


    @api.onchange("res_parent_id")
    def onchange_res_parent_id(self):
        if self.res_parent_id:
            self.name = self.res_parent_id.name;
            self.parent_type = self.res_parent_id.parent_type;
            self.gender = self.res_parent_id.gender;
            self.phone = self.res_parent_id.phone;
            self.mobile = self.res_parent_id.mobile;
            self.email = self.res_parent_id.email;


    def add_parent(self):
        active_id = self.env["res.partner"].browse(self._context.get("active_id",False));
        if self.is_create:
            vals = {
                        "name": self.name,
                        "parent_type": self.parent_type,
                        "gender": self.gender,
                        "phone": self.phone,
                        "mobile": self.mobile,
                        "email": self.email,
                        "is_parent": True,
                        "cc_child_id": active_id.id,
                    };
        else:
            vals = {
                        "name": self.name,
                        "parent_type": self.parent_type,
                        "gender": self.gender,
                        "phone": self.phone,
                        "mobile": self.mobile,
                        "email": self.email,
                        "res_partner_id": self.res_parent_id.id,
                        "is_parent": True,
                        "cc_child_id": active_id.id,
                    };

        parent = self.env["res.partner.parentchild"].sudo().create(vals);
        return parent;


