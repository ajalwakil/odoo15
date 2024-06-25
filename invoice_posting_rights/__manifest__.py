# -*- coding: utf-8 -*-
{
    'name': "invoice_posting_rights",
    'description': """ Invoice Posting Rights """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '15.1',
    'depends': ['base','account'],
    'data': [
        # 'security/ir.model.access.csv',

        'views/invoice_posting_rights_views.xml',
        'security/security.xml',
    ],
}
