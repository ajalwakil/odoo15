from odoo import api, fields, models, _
from datetime import datetime,date
from dateutil.relativedelta import relativedelta

class GymMembers(models.Model):
    _inherit = "hr.employee"
    _description = "Gym Members"

    name = fields.Char(string='Name', required=True)
    name_sequence = fields.Char(string='Member Id', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    birth_date = fields.Date(string = 'Date of Birth')
    age = fields.Integer(string='Age',compute="compute_age_calc",copy=False,store=True)
    mobile_no = fields.Char(string = "Contact No.")
    email = fields.Char(string = "Email-Id")
    address = fields.Text(string ='Address')
    gender = fields.Selection(selection_add=[('male', 'Male'), ('female', 'Female')],string = 'Gender')
    trainer_id = fields.Many2one('hr.employee',string="Trainer")
    specialist_id = fields.Many2many('trainer.skill',string = 'Trainer Skill')
    start_date = fields.Date(string = 'Membership Start Date',default=fields.Date.context_today)
    end_date = fields.Date(string = 'Membership End Date')
    calculate_invoice = fields.Integer(string="Invoice",compute="invoice_count",copy=False)
    invoice_ids = fields.One2many('member.invoice','employee_id',string="Invoice Record")
    bmi_ids = fields.One2many('bmi.calculation','members_bmi_id',string="BMI Record")
    weight_ids = fields.One2many('member.weight','members_weight_id',string="Weight Record")
    workout_ids = fields.One2many('member.workout.schedule','members_workout_id',string="Workout Record")
    diet_ids = fields.One2many('employee.diet.schedule','members_diet_id',string="Diet Record")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id.id)
    is_member = fields.Boolean(default=False ,string='Is Member')
    invoice_amount = fields.Integer(string="Total",compute="calculated_invoive_amount",copy=False,store=True)
    invoice_number = fields.Integer(string="Count",compute="calculated_invoive_count",copy=False,store=True)
    invoice_id = fields.Many2one('account.move','Account Invoice')
    departure_reason = fields.Char("Departure Reason")


    @api.model
    def _get_date_diff(self, date_from=False, date_to=False):
        res = 0.0
        if date_from:
            date_from = date_from.strftime("%Y-%m-%d")
            if date_from < datetime.today().date().strftime("%Y-%m-%d"):
                diff = ""
                if date_to:
                    diff = relativedelta(datetime.strptime(date_to, '%Y-%m-%d'),
                                         datetime.strptime(date_from, '%Y-%m-%d'))
                else:
                    diff = relativedelta(datetime.today(),
                                         datetime.strptime(date_from, '%Y-%m-%d'))
                res = str(diff.years) + '.' + str(diff.months)
        return float(res)

    @api.depends('birth_date')
    def compute_age_calc(self):
        for rec in  self:
            if rec.birth_date:
                res = self._get_date_diff(rec.birth_date)
                rec.age = res
            else:
                rec.age = 0

    @api.depends('invoice_ids')
    def calculated_invoive_amount(self):
        total_amount = 0
        for each in self:
            for rec in each.invoice_ids:
                total_amount += rec.fees
            each.invoice_amount = total_amount


    @api.depends('invoice_ids')       
    def calculated_invoive_count(self):
        for rec in self:
            rec.invoice_number = len(rec.invoice_ids)

            
    def invoice_count(self):
        account_move_obj = self.env['account.move']
        for group in self:
            group.calculate_invoice = account_move_obj.search_count([('id', 'in', group.invoice_ids.invoice_id.ids)])

    @api.model
    def create(self, vals):
        if vals.get('name_sequence', _('New')) == _('New'):
            vals['name_sequence'] = self.env['ir.sequence'].next_by_code('hr.employee.sequence') or _('New')
        result = super(GymMembers, self).create(vals)
        return result
    
    def open_account_move_details(self):
        xml_id = 'account.view_invoice_tree'
        tree_view_id = self.env.ref(xml_id).id
        xml_id = 'account.view_move_form'
        form_view_id = self.env.ref(xml_id).id
        return {
            'name': _('Invoice'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'res_model': 'account.move',
            'domain': [('id', 'in', self.invoice_ids.invoice_id.ids)],
            'type': 'ir.actions.act_window',
        }

    def create_invoice(self):
        tree_id = self.env.ref('account.view_move_form').id
        form_id = self.env.ref('account.view_move_form').id
        return{'type': 'ir.actions.act_window',
                'name':_('Invoice'),
                'res_model':'account.move',
                'view_mode':'tree,form',
                'views':[(tree_id,'tree'),(form_id,'form')],
                'context':{},
                'targer':'new'}

    def create_tax(self):
        tax = self.env['account.tax'].search([('name','=','GST 5%')])
        if not tax:
            tax = self.env['account.tax'].create({
            'name': 'GST 5%',
            'amount': 5.0,
            'amount_type': 'percent',
            'type_tax_use': 'sale',
            })

    def action_member_since(self):
        return True

class MemberInvoice(models.Model):
    _name = "member.invoice"
    _description = "Member Invoice"

    invoice_id = fields.Many2one('account.move',string="Invoice")
    employee_id = fields.Many2one('hr.employee',string="Employee")
    join_date = fields.Date(string = 'Join date')
    membership = fields.Char('Membership')
    fees = fields.Float(string='Fees')
    status = fields.Selection(related='invoice_id.state', string="Status", store=True, readonly=True)

class EmployeeDietSchedule(models.Model):
    _name = "employee.diet.schedule"
    _description = "Employee Diet Schedule"

    members_diet_id = fields.Many2one('hr.employee')
    members_id = fields.Many2one('hr.employee', string='Member Name')
    trainers_id = fields.Many2one('hr.employee', string='Gym Trainers')
    diet_plan_id = fields.Many2one('diet.plan', string='Diet Plan')
    interval = fields.Char(related='diet_plan_id.interval_id.name', string='Interval')
    from_date = fields.Date(string = 'Start date')
    to_date = fields.Date(string = 'End date')
    total_days = fields.Integer(string='Total Days')

class MemberWorkoutSchedule(models.Model):
    _name = "member.workout.schedule"
    _description = "Member Workout Schedule"

    members_workout_id = fields.Many2one('hr.employee')
    workout_id = fields.Many2one('gym.workout', string='Workout')
    gym_members_id = fields.Many2one('hr.employee', string='Gym Members')
    gym_trainers_id = fields.Many2one('hr.employee', string='Gym Trainers')
    from_date = fields.Date(string = 'Start date')
    to_date = fields.Date(string = 'End date')
    days_ids = fields.Many2many(related='workout_id.days_ids', string='Days')


class GymTrainers(models.Model):
    _inherit = "hr.employee"
    _description = "Gym Trainers"

    name = fields.Char(string='Name', required=True)
    mobile_no = fields.Char(string = "Mobile No.")
    phone_no = fields.Char(string = "Phone No.")
    email = fields.Char(string = "Email-Id")
    specialist_id = fields.Many2many('trainer.skill',string="Trainer Skill")
    is_trainer = fields.Boolean(default=False ,string='Is Trainer')
    department = fields.Char(string = "Department")
    location = fields.Char(string = "location")
    calculate_members = fields.Integer(string="Members",compute="member_count",copy=False)
    
    def member_count(self):
        for line in self:
            total_members = self.env['hr.employee'].search([('trainer_id','=',self.id)])
            line.calculate_members = len(total_members)
 
    def member_record(self):
        members_list = []
        gym_members = self.env['hr.employee'].search([('trainer_id','=',self.id)])
        view_id = self.env.ref('gym_management_app.view_gym_members_tree_trainer').id
        
        for members in gym_members:
            members_list.append(members.id)  
        return {
                'name': _('Member Record'),
                'view_mode': 'tree,form',
                'res_model': 'hr.employee',
                'type': 'ir.actions.act_window',
                'domain' :[('id', '=', members_list)],
                'views': [[view_id, 'list']],
            }
    
class TrainerSkill(models.Model):
    _name = "trainer.skill"
    _description = "Trainer Skill"

    name = fields.Char(string='Name', required=True)
    sequence = fields.Char(string = 'Code')


class DietInterval(models.Model):
    _name = "diet.interval"
    _description = "Diet Interval"

    name = fields.Char(string='Name', required=True)


class BodyParts(models.Model):
    _name = "body.parts"
    _description = "Body Parts"

    name = fields.Char(string='Name', required=True)


class GymMembership(models.Model):
    _name = "gym.membership"
    _description = "Gym Membership"

    name = fields.Char(string='Name', required=True)
    fees = fields.Float(string='Fees')
    
    

class GymEquipment(models.Model):
    _name = "gym.equipment"
    _description = "Gym Equipment"

    name = fields.Char(string='Name', required=True)

class BmiCalculation(models.Model):
    _name = "bmi.calculation"
    _description = "Bmi Calculation"

    name = fields.Many2one('hr.employee', required=True, string="Member Name")
    members_bmi_id = fields.Many2one('hr.employee', related='name', string='Member')
    date = fields.Date(string = 'Date')
    age = fields.Integer('Age',related='name.age')
    height = fields.Float('Height')
    weight = fields.Float('Weight')
    bmi_calculation = fields.Float('BMI')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],string = 'Gender',related='name.gender')
    
    @api.onchange('weight')
    def calculate_bmi(self):
        bmi_list = []
        gym_members = self.env['hr.employee'].search([('id','=',self.name.id)])
        
        for rec in self:
            if rec.height and rec.weight:
                bmi = rec.weight / ((rec.height/100) * (rec.height/100))
                rec.bmi_calculation = bmi

            
class BmiCalculation(models.Model):
    _name = "member.weight"
    _description = "Member Weight"

    name = fields.Many2one('hr.employee', required=True, string='Member')
    members_weight_id = fields.Many2one('hr.employee', related='name', string='Member')
    date = fields.Date(string = 'Date', required=True)
    weight = fields.Float('Weight', required=True)
