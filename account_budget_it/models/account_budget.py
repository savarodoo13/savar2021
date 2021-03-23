# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CrossoveredBudgetLines(models.Model):
	_inherit = 'crossovered.budget.lines'

	def _compute_percentage(self):
		for line in self:
			if line.planned_amount != 0.00:
				line.percentage = float((line.practical_amount or 0.0) / line.planned_amount)
			else:
				line.percentage = 0.00