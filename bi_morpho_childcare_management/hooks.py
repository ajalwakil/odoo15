from odoo import api, SUPERUSER_ID


def bi_uninstall_hook(cr, registry):
	env = api.Environment(cr, SUPERUSER_ID, {});
	env.ref("base.res_partner_portal_public_rule").domain_force = "[('id', 'child_of', user.commercial_partner_id.id)]";
	env.ref("crm.crm_rule_personal_lead").domain_force = "['|',('user_id','=',user.id),('user_id','=',False)]";
	env.ref("crm.crm_rule_all_lead").domain_force = "[(1,'=',1)]";
	