# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields,_
from odoo.exceptions import ValidationError,UserError


class CCParentMessegingWizard(models.TransientModel):
    _name = "cc.parentmsg.wizard"
    _description = "Emergency Alert"  


    child_ids = fields.Many2many("res.partner", "parentmsg_child_wiz_ref", string="Childs", domain="[('is_child','=',True)]", required=True);
    send_email = fields.Boolean(string="Send Email", default=True);
    send_messg = fields.Boolean(string="Send Message", default=True);
    message = fields.Text(string="Add Messege To Send", required=True);


    @api.model
    def default_get(self, fields):
        res = super(CCParentMessegingWizard, self).default_get(fields);
        childs = self._context.get("childs");
        if childs:
            res["child_ids"] = [(4,idd) for idd in childs];
        return res;



    def send_messeges(self):
        for child in self.child_ids:
            if self.send_messg:
                self.send_sms_emergency_alert(child);
            if self.send_email:
                self.send_mail_emergency_alert(child);



    def send_sms_emergency_alert(self, child):
        res = child._message_sms_with_template(
                template_fallback=_("%s"%self.message),
                partner_ids=child.get_parent_to_send().ids,
                put_in_queue=False
            )
        return res;



    def send_mail_emergency_alert(self, child):
        template_id = self.env.ref("bi_morpho_childcare_management.parentmsg_alert_mail_template");
        template = self.env['mail.template'].browse(template_id.id);
        template.body_html = self.message;
        return template.send_mail(child.id,force_send=True);
