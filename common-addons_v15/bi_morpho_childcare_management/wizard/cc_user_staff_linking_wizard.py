# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields,_
from odoo.exceptions import ValidationError,UserError


class CCUserStaffLinkWizard(models.TransientModel):
    _name = "cc.userstafflink.wizard"
    _description = "Link Staff to User"


    def get_domain(self):
        users = self.env["res.users"].search([]);
        users = users.filtered(lambda s: s.has_group("bi_morpho_childcare_management.bi_morpho_childcare_management_group_staff"));
        return "[('id','in',{})]".format(users.ids);


    user_id = fields.Many2one("res.users", required=True, domain=get_domain);



    def link_user(self):
        active_id = self._context.get("active_id",False) or self._context.get("active_ids",[False])[0];
        if active_id and self.user_id:
            rec = self.env["hr.employee"].browse(active_id);
            rec.user_id = self.user_id.id;
            rec.work_email = self.user_id.login;