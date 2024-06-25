# -*- coding: utf-8 -*-
{
    'name': "So Quotation Image",
    'summary': """ """,
    'description': """ """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'report/sale_order_report.xml',
    ],

}
