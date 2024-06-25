# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields,_
from odoo.exceptions import ValidationError,UserError


class CCRemoveParent(models.TransientModel):
    _name = "cc.removeparent.wizard"
    _description = "Remove Parent Wizard"      


    # For Existing
    is_create = fields.Boolean(default=True);
    parent_id = fields.Many2one("res.partner", string="Parent", domain="[('is_parent','=',True),('cc_child_id','=',False)]");

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


    @api.onchange("parent_id")
    def onchange_parent_id(self):
        if self.parent_id:
            self.name = self.parent_id.name;
            self.parent_type = self.parent_id.parent_type;
            self.gender = self.parent_id.gender;
            self.phone = self.parent_id.phone;
            self.mobile = self.parent_id.mobile;
            self.email = self.parent_id.email;


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
                        "cc_child_ids": [(6,False,active_id.ids)],
                    };
            parent = self.env["res.partner"].sudo().create(vals);
            if active_id:
                parent.cc_child_id = active_id.id;
            return parent;
        else:
            vals = {
                        "name": self.name,
                        "parent_type": self.parent_type,
                        "gender": self.gender,
                        "phone": self.phone,
                        "mobile": self.mobile,
                        "email": self.email,
                    };
            self.parent_id.write(vals);
            self.parent_id.cc_child_id = active_id.id;
            self.parent_id.cc_child_ids = [(4,active_id.id)];
        return self.parent_id;
