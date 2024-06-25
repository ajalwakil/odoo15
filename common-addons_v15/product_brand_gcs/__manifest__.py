# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#################################################################################
# Author      : Grow Consultancy Services (<https://www.growconsultancyservices.com/>)
# Copyright(c): 2021-Present Grow Consultancy Services
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################
{
    # Application Information
    'name': 'Product Brand GCS',
    'version': '15.0.0',
    'category': 'Technical',
    'license': 'LGPL-3',
    
    'summary': """
        This app allow you to create Product Brands and set to all product.
    """,
    'description': """ 
        This app allow you to create Product Brands and set to all product.
    """,
    
    # Author Information
    'author': 'Grow Consultancy Services',
    'maintainer': 'Grow Consultancy Services',
    'website': 'http://www.growconsultancyservices.com',
    
    # Application Price Information
    'price': 0,
    'currency': 'EUR',

    # Dependencies
    'depends': ['base', 'sale_management'],
    
    # Views
    'data': [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/product_brand_views.xml",
        "views/product_template_views.xml",
        #'view/'
        # wizard/
    ],
    
    # Application Main Image    
    'images': ['static/description/app_profile_image.png'],

    # Technical
    'installable': True,
    'application' : True,
    'auto_install': False,
    'active': False,
}
