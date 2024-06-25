# -*- coding: utf-8 -*-
# Part of Aktiv Software
# See LICENSE file for full copyright & licensing details.

{
    'name': "KSA E-Invoice",
    'summary': """""",
    'description': """""",
    'author': "",
    'company': "",
    'website': "",
    'category': 'website',
    'version': '14.1.2.0.0',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'report/report_tax_invoice.xml',
        'views/templates.xml',
        'views/account_invoice_view.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        'views/res_branch_view.xml',
        'views/res_config_settings_view.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            '/ksa_e_invoive/static/src/less/fonts.css'
        ],
    }
}
