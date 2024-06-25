# -*- coding: utf-8 -*-
{
    'name': "Purchase Fixconcept Report",
    'summary': """ """,
    'description': """ """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base','purchase','purchase_order_lines_discount'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/report.xml',
        'report/purchase_order_arabic_report.xml',
        'views/views.xml',
    ],
}
