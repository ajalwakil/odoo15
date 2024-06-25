# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields,_
from odoo.exceptions import ValidationError,UserError


class CCEmergAlertWizard(models.TransientModel):
    _name = "cc.emergalert.wizard"
    _description = "Emergency Alert"  


    child_ids = fields.Many2many("res.partner", "alert_child_wiz_ref", string="Childs", domain="[('is_child','=',True)]", required=True);


    def send_alert(self):
        for child in self.child_ids:
            confm = child.emergency_alert();
