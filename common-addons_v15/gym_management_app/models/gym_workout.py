from odoo import api, fields, models, _
from datetime import datetime,date
from dateutil.relativedelta import relativedelta


class GymExercise(models.Model):
    _name = "gym.exercise"
    _description = "Gym Exercise"

    name = fields.Char(string='Exercise name')
    body_part = fields.Many2one('body.parts', string='Body Part')
    equipment = fields.Many2one('gym.equipment', string='Equipment')
    benifits = fields.Html(string ='Benifits')
    steps = fields.Html(string ='Steps')

class GymWorkout(models.Model):
    _name = "gym.workout"
    _description = "Gym Workout"

    name = fields.Char(string='name')
    days_ids = fields.Many2many('gym.days', string='Days')
    exercise_list_ids = fields.One2many('list.exercise','exercise_id', string = 'name')
    
class ListExercise(models.Model):
    _name = "list.exercise"
    _description = "List Exercise"

    exercise_id = fields.Many2one('gym.workout')
    exercises_id = fields.Many2one('gym.exercise')
    exercise_for_id = fields.Many2one(related='exercises_id.body_part')
    equipment_id = fields.Many2one(related='exercises_id.equipment')
    sets = fields.Float(string='Sets')
    repeat = fields.Float(string='Repeat')
    kgs = fields.Float(string='Kgs')

class Gymdays(models.Model):
    _name = "gym.days"
    _description = "Gym Days"

    name = fields.Char(string='Name')
    sequence = fields.Char(string='Sequence')   

class DietFood(models.Model):
    _name = "diet.food"
    _description = "Diet Food"

    name = fields.Char(string='Food Name', required=True)
    unit_of_measure = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    image_small = fields.Binary(string = 'Image', attachment=True)

class DietPlan(models.Model):
    _name = "diet.plan"
    _description = "Diet Plan"

    name = fields.Char(string='Plan Name', required=True)
    interval_id = fields.Many2one('diet.interval', string='Diet Interval')
    food_line_ids = fields.One2many('diet.food.line','diet_plan_id',string="Diet Food Line")
    
class DietFoodLine(models.Model):
    _name = "diet.food.line"
    _description = "Diet Food Line"

    diet_plan_id = fields.Many2one('diet.plan')
    food_id = fields.Many2one('diet.food', string='Food Item')
    quantity = fields.Integer(string='Quantity')

class AccountInvoice(models.Model):
    _inherit = "account.move"

    company_currency_id = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id.id)
    
    