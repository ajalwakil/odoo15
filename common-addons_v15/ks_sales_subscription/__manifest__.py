# -*- coding: utf-8 -*-
{
	'name': 'Sales Subscription',

	'summary': """
This app offers customized subscription plans to be sold to customers by companies.
""",

	'description': """
Best Odoo Subscription Apps
        Odoo Subscription Apps
        Odoo Mail Subscription Apps
        Odoo Subscription Portal Apps
        Odoo Recurring Invoice Apps
        Mail Reminder
        Recurring Invoice Apps
        Subscription Portal Apps
        Mail Subscription Apps
        Sale Subscription Apps
        Product Subscription Apps
        Subscription Product Apps
        Subscription
        Subscription Management
        Subscription Page
        Upsell Subscription 
        Subscription Plan Reminder
        Sale Order Subscription Apps
        Message Auto Subscribe
        Mass Mailing Subscription
        Renew Subscription
        Automatic Invoice Subscription
        Email Subscription
    """,

     'author': "Ksolves India Ltd.",
     'license': 'OPL-1',
     'currency': 'USD',
     'price': 88.13,
     'website': "https://store.ksolves.com/",
     'maintainer': 'Ksolves India Ltd.',
     'live_test_url': 'http://salesubscription15.kappso.in/',
     'category': 'Tools',
     'version': '15.0.1.0.0',
     'support': 'sales@ksolves.com',
     "images": [
            "static/description/subscription_banner.gif",
        ],

    'depends': ['base', 'mail', 'sale_management', 'portal'],
    'data': [
        'security/ks_subscription_security.xml',
        'security/ir.model.access.csv',
        'data/ks_data.xml',
        'data/ks_mail_templates.xml',
        'views/ks_subscription_portal.xml',
        'views/ks_sale_subscription_view.xml',
        'views/ks_subscription_product.xml',
        'views/ks_subscription_templates.xml',
        'wizard/ks_subscription_close_reason_wizard_views.xml',
        'views/ks_subscription_close_reason.xml',
        'views/ks_sale_order_view.xml',
        'views/ks_subscription_stage.xml',

    ],
}
