# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields,_
from odoo.exceptions import ValidationError,UserError


class CCWaitlistConfirmation(models.TransientModel):
    _name = "cc.waitlist.confirmation.wizard"
    _description = "Waitlist Confirmation Wizard"    


    def confirm_move_to_waitlist(self):
        active_id = self._context.get("active_id", False);
        lead = self.env["crm.lead"].browse(active_id);
        lead.in_waiting_list = True;




    