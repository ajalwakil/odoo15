# -*- coding: utf-8 -*-
{
    "name": "Separate Customer Vendor ",
    "summary": """Separate Customer Vendor """,
    "description": """ """,
    "version": "1.0.0",
    "category": "Tools",
    "author": "Umair Aslam",
    "maintainers": "Umair Aslam",
    "website": "",
    "license": "Other proprietary",
    "installable": True,

    "depends": ["sale_management", "purchase"],

    "data": [
        "views/sale_order_view.xml",
        "views/res_partner_view.xml",
        "views/purchase_order_view.xml",
        "views/account_move_view.xml",
    ],

}
