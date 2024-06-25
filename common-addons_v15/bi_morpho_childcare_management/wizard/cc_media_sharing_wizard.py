# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields,_
from odoo.exceptions import ValidationError,UserError
from odoo.tools.mimetypes import guess_mimetype
import mimetypes


class CCMediaSharing(models.TransientModel):
    _name = "cc.media.sharing.wizard"
    _description = "Media Sharing Wizard"      


    child_id = fields.Many2one("res.partner", string="Child", readonly=True);
    file = fields.Binary(string="Add Your Files/Media");
    url = fields.Char(string="URL");
    message = fields.Text(string="Message");
    filename = fields.Char(string="File name");
    media_type = fields.Selection([("url","URL"),("binary","File")], default="binary", required=True);


    @api.model
    def default_get(self, fields):
        res = super(CCMediaSharing, self).default_get(fields);
        res["child_id"] = self._context.get("active_id", False);
        return res;


    def share_media(self):
        name = "%s - %s"%(self.child_id.name, fields.Datetime.now());
        mimetype = None;
        mimetype = mimetypes.guess_type(self.filename)[0]
        if not mimetype:
            mimetype = guess_mimetype(self.file);
        media_vals = {
                        "name" : name,
                        "cc_media" : True,
                        "datas" : self.file,
                        "type" : self.media_type,
                        "url" : self.url,
                        "res_model" : "res.partner",
                        "res_id" : self._context.get("active_id",False),
                        "cc_message" : self.message,
                        "mimetype" : mimetype or 'application/octet-stream',
                    }
        media = self.env["ir.attachment"].sudo().create(media_vals);
        self.send_sms_notification(self.child_id);
        self.send_mail_notification(self.child_id, media);
        return media;                



    def send_sms_notification(self, child):
        res = child._message_sms_with_template(
                template_fallback=_("%s"%self.message),
                partner_ids=child.get_parent_to_send().ids,
                put_in_queue=False
            )
        return res;



    def send_mail_notification(self, child, media):
        template_id = self.env.ref("bi_morpho_childcare_management.parentmsg_alert_mail_template");
        template = self.env['mail.template'].browse(template_id.id);
        template.body_html = self.message;
        mail_id = template.send_mail(child.id,force_send=True);
        mail = self.env['mail.mail'].sudo().browse(mail_id);
        if mail.mail_message_id:
            mail.mail_message_id.attachment_ids = [(6,False,media.ids)]
            mail.mail_message_id.cc_attachment = True;
