# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    arabic_name = fields.Char('Arabic Name')
    arabic_address = fields.Text('Arabic Address')
    font = fields.Selection(selection_add=[('Noto Naskh Arabic', 'Noto Naskh Arabic'),('Tajawal', 'Tajawal')])




class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    street = fields.Char(related='company_id.street', readonly=True)
    arabic_name = fields.Char(related='company_id.arabic_name', readonly=True)
    arabic_address = fields.Text(related='company_id.arabic_address', readonly=True)
    zip = fields.Char(related='company_id.zip', readonly=True)
    state_id = fields.Many2one(related='company_id.state_id', readonly=True)

