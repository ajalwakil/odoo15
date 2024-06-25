from odoo import tools
from odoo import api, fields, models
from datetime import datetime,date

class ScheduledWorkoutReport(models.AbstractModel):
    _name = 'report.gym_management_app.schedule_workout_report_view'
    _description = 'Scheduled Workout Report'

    def _get_report_values(self, docids, data=None):
        s_date = data['form']['from_date']
        e_date = data['form']['to_date']
        members_id = data['form']['members_id']
        ids = members_id[0]
        
        workout_schedule = self.env['workout.schedule'].search([('from_date', '>=', s_date), ('to_date', '<=', e_date), ('gym_members_id', '=', ids)],limit=1)
        return {
            'doc_ids': workout_schedule,
            'doc_model': 'workout.schedule',
            'docs': workout_schedule,
            'proforma': True
        }

class ScheduledWorkoutReport(models.AbstractModel):
    _name = 'report.gym_management_app.schedule_diet_report_view'
    _description = 'Scheduled Diet Report'

    def _get_report_values(self, docids, data=None):
        s_date = data['form']['from_date']
        e_date = data['form']['to_date']
        members_id = data['form']['members_id']
        ids = members_id[0]
        interval = data['form']['interval_id']
        interval_time = interval[1]
        
        diet_schedule = self.env['diet.schedule'].search([('from_date', '>=', s_date), ('to_date', '<=', e_date), ('members_id', '=', ids), ('interval', '=', interval_time)],limit=1)
        return {
            'doc_ids': diet_schedule,
            'doc_model': 'diet.schedule',
            'docs': diet_schedule,
            'proforma': True
        }
        

    