# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime

class ProjectTaskCreateTimesheet(models.TransientModel):
	_inherit = 'project.task.create.timesheet'

	drill_id = fields.Many2one('project.drill', string='Taladro')
	high = fields.Float(string='Altura')

	def save_timesheet(self):
		res = super(ProjectTaskCreateTimesheet, self).save_timesheet()
		first_start = datetime.strptime(self.env.context['timesheet_timer_first_start'], '%Y-%m-%d %H:%M:%S')
		res.hour_from = self.env['report.base'].custom_round(first_start.hour + first_start.minute/60, 2)
		last_stop = fields.datetime.now()
		res.hour_to = self.env['report.base'].custom_round(last_stop.hour + last_stop.minute/60, 2)
		res.drill_id = self.drill_id
		res.high = self.high
		return res