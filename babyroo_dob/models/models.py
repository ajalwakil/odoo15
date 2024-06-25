# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import datetime


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    vat = fields.Char(string='National ID / Iqama', index=True,
                      help="The Tax Identification Number. Complete it if the contact is subjected to government taxes. Used in some legal statements.")
    dob = fields.Date('Date of Birth')
    kid_age = fields.Integer(string="Age", compute='_compute_age');

    @api.depends("dob")
    def _compute_age(self):
        self.kid_age = False
        for rec in self:
            rec.kid_age = relativedelta(datetime.date.today(), rec.dob).years;