from odoo import fields, models, api


class Account_Move_Inherit(models.Model):
    _inherit = 'account.move'

    partner_id = fields.Many2one('res.partner', readonly=True, tracking=True,
                                 states={'draft': [('readonly', False)]},
                                 check_company=True,
                                 string='Partner', change_default=True)
    custom_partner_ids = fields.Many2many('res.partner',string='Partner ids',compute='_compute_customer')

    is_customer = fields.Boolean(string="Is Customer", compute='_compute_type_customer')
    is_vendor = fields.Boolean(string="Is Vendor",  compute='_compute_type_customer')

    @api.depends('move_type')
    def _compute_type_customer(self):
        self.is_customer = False
        if self.move_type in ('out_invoice', 'out_refund', 'out_receipt'):
            self.is_customer = True
        self.is_vendor = False
        if self.move_type in ('in_invoice', 'in_refund', 'in_receipt'):
            self.is_vendor = True

    @api.depends('is_customer', 'is_vendor')
    def _compute_customer(self):
        self.custom_partner_ids = False
        if self.is_customer:
            contacts = self.env['res.partner'].search([('is_customer', '=', True)])
            if contacts:
                self.custom_partner_ids = contacts.ids
        if self.is_vendor:
            contacts = self.env['res.partner'].search([('is_vendor', '=', True)])
            if contacts:
                self.custom_partner_ids = contacts.ids
        # else:
        #     contacts = self.env['res.partner'].search([])
        #     if contacts:
        #         self.custom_partner_ids = contacts.ids




            
    # @api.onchange('type_product')
    # def onchange_type_product(self):
    #     self.product_id = False
    #     if self.type_product == '0':
    #         products = self.env['product.product'].search([('categ_id.is_a_custom', '=', True)])
    #         return {'domain': {'product_id': [('id', 'in', products.ids)]}}
    #     # products = self.env['product.template'].search([('categ_id.is_a_custom', '=', True)])
    #     # return {'domain': {'product_template_id': [('id', 'in', products.ids)]}}
    #     # elif self.type_product == '1':
    #     #     return {'domain': {'product_template_id': [('categ_id.is_a_custom', '=', False)]}}
    #     else:
    #         return {'domain': {'product_id': []}}
