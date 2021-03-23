from odoo import api, fields, models, _
from datetime import datetime

class ProjectTask(models.Model):
	_inherit = 'project.task'

	def _action_create_timesheet(self, time_spent):
		res = super(ProjectTask, self)._action_create_timesheet(time_spent)
		res['context']['timesheet_timer_first_start'] = self.timesheet_timer_first_start
		return res