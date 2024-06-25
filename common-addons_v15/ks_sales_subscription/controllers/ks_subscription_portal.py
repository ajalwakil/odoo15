# -*- coding: utf-8 -*-
from collections import OrderedDict

from odoo import http
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.http import request
from odoo.tools.translate import _


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        ks_values = super(CustomerPortal, self)._prepare_portal_layout_values()
        ks_partner = request.env.user.partner_id
        ks_company = request.env.user.company_id
        ks_values['ks_subscription_count'] = request.env['ks.sale.subscription'].sudo().search_count(
            [('ks_partner_id', '=', ks_partner.id), ('ks_company_id', '=', ks_company.id)])
        return ks_values

    @http.route(['/my/subscription', '/my/subscription/page/<int:page>'], type='http', auth="user", website=True)
    def ks_my_subscription(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):

        def _return_ks_searchbar_sortings():
            return {
                'date': {'label': _('Newest'), 'order': 'create_date desc, id desc'},
                'name': {'label': _('Name'), 'order': 'ks_name asc, id asc'}
            }

        def _return_ks_searchbar_filters():
            return {
                'all': {'label': _('All'), 'domain': []},
                'open': {'label': _('In Progress'), 'domain': [('ks_in_progress', '=', True)]},
                'pending': {'label': _('To Renew'), 'domain': [('ks_to_renew', '=', True)]},
                'close': {'label': _('Closed'), 'domain': [('ks_in_progress', '=', False)]},
            }

        ks_values = self._prepare_portal_layout_values()
        ks_partner = request.env.user.partner_id
        ks_company = request.env.user.company_id
        ks_domain = [('ks_partner_id', '=', ks_partner.id), ('ks_company_id', '=', ks_company.id)]

        # ks_groups_archive = self._get_archive_groups('ks.sale.subscription', ks_domain, ['ks_name', 'create_date'])
        if date_begin and date_end:
            ks_domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # default sort by value
        if not sortby:
            sortby = 'date'
        ks_order = _return_ks_searchbar_sortings()[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        ks_domain += _return_ks_searchbar_filters()[filterby]['domain']
        sub_count = request.env['ks.sale.subscription'].sudo().search_count(ks_domain)
        ks_pager = portal_pager(
            url="/my/subscription",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=sub_count,
            page=page,
            step=self._items_per_page
        )

        ks_subscriptions = request.env['ks.sale.subscription'].sudo().search(ks_domain, order=ks_order,
                                                                             limit=self._items_per_page,
                                                                             offset=ks_pager['offset'])
        request.session['my_subscriptions_history'] = ks_subscriptions.ids[:100]

        ks_values.update({
            'ks_subscriptions': ks_subscriptions.sudo(),
            'page_name': 'subscription',
            'pager': ks_pager,
            # 'archive_groups': ks_groups_archive,
            'default_url': '/my/subscription',
            'searchbar_sortings': _return_ks_searchbar_sortings(),
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(_return_ks_searchbar_filters().items())),
            'filterby': filterby,
        })
        return request.render("ks_sales_subscription.ks_portal_my_subscriptions", ks_values)


class ks_sale_subscription(http.Controller):

    @http.route(['/my/subscription/<int:ks_subscription>/',
                 ], type='http', auth="public", website=True)
    def ks_subscription_portal(self, ks_subscription, **kw):
        ks_subscriptions = request.env['ks.sale.subscription'].sudo().browse(ks_subscription)

        ks_values = {
            'ks_subscription': ks_subscriptions,
            'ks_pricelist': ks_subscriptions.ks_pricelist_id.sudo(),
            'ks_user': request.env.user,
        }
        return request.render("ks_sales_subscription.ks_subscription_template", ks_values)
