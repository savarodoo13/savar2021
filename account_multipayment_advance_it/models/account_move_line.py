from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	def name_get(self):
		result = []
		for move_line in self:
			result.append((move_line.id, move_line.nro_comp))
		return result