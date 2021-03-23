# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from datetime import *

class MrpProduction(models.Model):
	_inherit = 'mrp.production'

	kardex_date = fields.Date(string="Fecha Kardex", default=lambda self: date.today() - timedelta(hours=5))
	operation_type_sunat_consume = fields.Many2one('type.operation.kardex', string="Tipo de Operacion Sunat Consumo")
	operation_type_sunat_fp = fields.Many2one('type.operation.kardex', string="Tipo de Operacion Sunat Producto Terminado")

	def button_mark_done(self):
		self.ensure_one()
		error = ''
		for line in self.move_raw_ids:
			if line.quantity_done == 0:
				error += '- %s.\n' % (line.product_id.name)
		if error:
			raise UserError('Las cantidades consumidas no pueden quedar en cero en los siguientes productos:\n %s' % (error))
		return super(MrpProduction, self).button_mark_done()