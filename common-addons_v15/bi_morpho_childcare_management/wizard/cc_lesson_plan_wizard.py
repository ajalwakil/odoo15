# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields,_
from odoo.exceptions import ValidationError,UserError


class CCPlanLesson(models.TransientModel):
    _name = "cc.lesson.plan.wizard"
    _description = "Lesson Plan Wizard"      


    # Activity Details
    activity_id = fields.Many2one("cc.room.activity", string="Activity", readonly=True);
    name = fields.Char(string="Activity Name", readonly=True);
    description = fields.Text(string="Activity Description", readonly=True);
    start_datetime = fields.Datetime(string="Start Date & Time", readonly=True);
    end_datetime = fields.Datetime(string="End Date & Time", readonly=True);

    # Lesson Plan
    lesson_plan = fields.Html(string="Lesson Plan");

    @api.model
    def default_get(self, fields):
        res = super(CCPlanLesson, self).default_get(fields);
        res["activity_id"] = self._context.get("activity_id", False);
        res["name"] = self._context.get("name", False);
        res["description"] = self._context.get("description", False);
        res["start_datetime"] = self._context.get("start_datetime", False);
        res["end_datetime"] = self._context.get("end_datetime", False);
        return res;


    def add_lesson_plan(self):
        if len(self.lesson_plan) == 0:
            UserError(_("Please add lesson plan."));
        self.activity_id.update({"lesson_plan" : self.lesson_plan,})
        return self.activity_id;
