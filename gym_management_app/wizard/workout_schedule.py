from odoo import api, fields, models, _
from datetime import datetime,date
from dateutil.relativedelta import relativedelta

class WorkoutSchedule(models.TransientModel):
	_name = "workout.schedule"
	_description = "Workout Schedule"

	workout_id = fields.Many2one('gym.workout', string='Workout')
	gym_members_id = fields.Many2one('hr.employee', string='Gym Members', required=True)
	gym_trainers_id = fields.Many2one('hr.employee', string='Gym Trainers', related="gym_members_id.trainer_id", readonly=True)
	from_date = fields.Date(string = 'Start date', required=True)
	to_date = fields.Date(string = 'End date', required=True)
	days_ids = fields.Many2many(related='workout_id.days_ids', string='Days')

	def create_workout(self):
		gym_members = self.env['hr.employee'].search([('name','=',self.gym_members_id.name)])
		gym_members.write({'workout_ids':[(0, 0, {
												'members_workout_id': self.gym_members_id.id,
												'gym_members_id' : self.gym_members_id.id,
												'gym_trainers_id' : self.gym_trainers_id.id,
												'workout_id' : self.workout_id.id,
												'from_date' :self.from_date,
												'to_date' :self.to_date,
												'days_ids' :self.days_ids.ids,
												})]
						})

class BuyMembership(models.TransientModel):
	_name = "buy.membership"
	_description = "Buy Membership"

	membership_id = fields.Many2one('gym.membership', string='Membership', required=True)
	price = fields.Float(related='membership_id.fees', string='Membership Price', required=True)


	def _get_computed_account(self, product, account_move):
		self.ensure_one()
		self = self.with_company(account_move.journal_id.company_id)
		fiscal_position = account_move.fiscal_position_id
		accounts = product.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
		if account_move.is_sale_document(include_receipts=True):
			# Out invoice.
			return accounts['income']
		elif account_move.is_purchase_document(include_receipts=True):
			# In invoice.
			return accounts['expense']

	def _get_computed_taxes(self, product, account_move, account_id):
		self.ensure_one()

		if account_move.is_sale_document(include_receipts=True):
			# Out invoice.
			if product.taxes_id:
				tax_ids = product.taxes_id.filtered(lambda tax: tax.company_id == account_move.company_id)
			elif account_id.tax_ids:
				tax_ids = account_id.tax_ids
			else:
				tax_ids = self.env['account.tax']
			if not tax_ids:
				tax_ids = account_move.company_id.account_sale_tax_id
		elif account_move.is_purchase_document(include_receipts=True):
			# In invoice.
			if product.supplier_taxes_id:
				tax_ids = product.supplier_taxes_id.filtered(lambda tax: tax.company_id == account_move.company_id)
			elif account_id.tax_ids:
				tax_ids = account_id.tax_ids
			else:
				tax_ids = self.env['account.tax']
			if not tax_ids:
				tax_ids = account_move.company_id.account_purchase_tax_id
		else:
			# Miscellaneous operation.
			tax_ids = account_id.tax_ids

		if account_move.company_id and tax_ids:
			tax_ids = tax_ids.filtered(lambda tax: tax.company_id == account_move.company_id)

		return tax_ids

	def create_invoice(self):
		active_id = self.env.context.get('active_id')
		employee_id = self.env['hr.employee'].browse(active_id)
		total_amount = self.price
		total_wage = self.price
		invoice_vals = self._prepare_invoice()
		account_move = self.env['account.move'].create(invoice_vals)
		product = self.env['product.product'].search([], limit=1)
		account_id = product.property_account_income_id or product.categ_id.property_account_income_categ_id
		currency = account_move.company_id.currency_id
		qty = 1
		if account_move:
			account_id = self._get_computed_account(product, account_move)
		if account_id:
			taxes = self._get_computed_taxes(product, account_move, account_id)
			if taxes and account_move.fiscal_position_id:
				taxes = account_move.fiscal_position_id.map_tax(taxes)
			account_move.update({'invoice_line_ids':[(0,0,{
				'name': '%s' % (account_move.partner_id.name),
				'move_id': account_move.id,
				'currency_id': currency and currency.id or False,
				'date_maturity': account_move.invoice_date_due,
				'product_uom_id': False,
				'product_id': False,
				'account_id':account_id.id,
				'quantity': qty,
				'tax_ids': [(6, 0, taxes.ids)],
				'partner_id': account_move.partner_id.id,
				'price_unit': self.price,})],
				})
		else:
			raise ValidationError('Please Configure Income/Expence Account In Product.')
		if account_move:
			account_move.action_post()
		employee_id.update({
			'invoice_id': account_move.id,
			'invoice_ids':[(0, 0, {
				'employee_id': employee_id.id,
				'join_date': employee_id.start_date,
				'membership': self.membership_id.name,
				'fees' : total_amount,
				'invoice_id' : account_move.id
			})]
		})
		form_id = self.env.ref('account.view_move_form').id
		tree_id = self.env.ref('account.view_move_tree').id
		return {'type': 'ir.actions.act_window',
				'name':_('Invoice'),
				'res_model':'account.move',
				'view_mode':'tree, form',
				'views':[(tree_id,'tree'),(form_id,'form')],
				'domain' : [('id', 'in', account_move.ids)],
				'res_id': account_move.id
				}

	def _prepare_invoice(self):
		"""
		Prepare the dict of values to create the new invoice for a sales order. This method may be
		overridden to implement custom invoice generation (making sure to call super() to establish
		a clean extension chain).
		"""
		self.ensure_one()
		active_id = self.env.context.get('active_id')
		employee_id = self.env['hr.employee'].browse(active_id)
		journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
		if not journal:
			raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

		partner_id = self.env['res.partner'].search([('name','=', employee_id.name)], limit=1)
		if not partner_id:
			partner = self.env['res.partner'].create({'name': employee_id.name})
			partner_id = partner

		invoice_vals = {
			'move_type': 'out_invoice',
			'invoice_user_id': self.env.user and self.env.user.id,
			'partner_id': partner_id.id,
			'partner_bank_id': employee_id.company_id.partner_id.bank_ids[:1].id,
			'journal_id': journal.id,  # company comes from the journal
			'company_id': employee_id.company_id.id,
		}
		return invoice_vals


class DietSchedule(models.TransientModel):
	_name = "diet.schedule"
	_description = "Diet Schedule"

	members_id = fields.Many2one('hr.employee', string='Member Name' , required=True)
	trainers_id = fields.Many2one('hr.employee', string='Gym Trainers', related="members_id.trainer_id", readonly=True)
	diet_plan_id = fields.Many2one('diet.plan', string='Diet Plan')
	interval = fields.Char(related='diet_plan_id.interval_id.name', string='Interval')
	from_date = fields.Date(string = 'Start date', required=True)
	to_date = fields.Date(string = 'End date', required=True)
	total_days = fields.Integer(string='Total Days')

	@api.onchange('to_date')
	def calculate_total_days(self):
		for rec in self:
			if rec.from_date and rec.to_date:
				total_days = (rec.to_date - rec.from_date).days
				rec.total_days = total_days

	def create_diet(self):
		gym_members = self.env['hr.employee'].search([('name','=',self.members_id.name)])
		gym_members.write({'diet_ids':[(0, 0, {
												'members_diet_id': self.members_id.id,
												'members_id' : self.members_id.id,
												'interval' : self.interval,
												'trainers_id' : self.trainers_id.id,
												'diet_plan_id' : self.diet_plan_id.id,
												'from_date' :self.from_date,
												'to_date' :self.to_date,
												'total_days' :self.total_days,
												})]
						})


class WorkoutScheduleReport(models.TransientModel):
	_name = "workout.schedule.report"
	_description = "Workout Schedule Report"

	members_id = fields.Many2one('hr.employee', string='Gym Members', required=True)
	from_date = fields.Date(string = 'Start date', required=True)
	to_date = fields.Date(string = 'End date', required=True)

	def print_workout_report(self):
		[data] = self.read()
		datas = {
		'model' : 'workout.schedule.report',
		'form' : data
		}
		
		return self.env.ref('gym_management_app.action_schedule_workout_report').report_action(self, data=datas)


class DietScheduleReport(models.TransientModel):
	_name = "diet.schedule.report"
	_description = "Diet Schedule Report"

	members_id = fields.Many2one('hr.employee', string='Gym Members', required=True)
	interval_id = fields.Many2one('diet.interval', string='Diet Interval', required=True)
	from_date = fields.Date(string = 'Start date', required=True)
	to_date = fields.Date(string = 'End date', required=True)

	def print_diet_report(self):
		[data] = self.read()
		datas = {
		'model' : 'diet.schedule.report',
		'form' : data
		}
		
		return self.env.ref('gym_management_app.action_schedule_diet_report').report_action(self, data=datas)


