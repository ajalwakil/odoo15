# -*- coding: utf-8 -*-
{
    'name': "Cloud360 Rights",
    'description': """This module will hide some of the buttons and menu.
                   1: Powered By Odoo
                   2: Manage Database""",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web','ksa_e_invoive','point_of_sale'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_config_setting_views_inherit.xml',
        'views/webclient_templates.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'user_access_rights/static/src/xml/base.xml',

        ],
    },
}
