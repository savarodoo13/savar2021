# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class StockMainParameter(models.Model):
	_name = 'stock.main.parameter'

	name = fields.Char(default='Parametros Principales')
	company_id = fields.Many2one('res.company', string=u'Compañía', default=lambda self: self.env.company.id)
	picking_type_id = fields.Many2one('stock.picking.type', string='Tipo de Operacion Aceros')
	product_id_1 = fields.Many2one('product.product', string='Broca')
	product_id_2 = fields.Many2one('product.product', string='Martillo')
	product_id_3 = fields.Many2one('product.product', string='Pinbox')
	product_id_4 = fields.Many2one('product.product', string='Barra 1')
	product_id_5 = fields.Many2one('product.product', string='Barra 2')
	product_id_6 = fields.Many2one('product.product', string='Barra 3')
	product_id_7 = fields.Many2one('product.product', string='Barra 4')
	product_id_8 = fields.Many2one('product.product', string='Barra 5')

	@api.model
	def create(self,vals):
		if len(self.search([('company_id', '=', self.env.company.id)])) > 0:
			raise UserError(u'No se puede crear mas de un Parametro Principal por Compañía')
		return super(StockMainParameter,self).create(vals)

	def get_main_parameter(self):
		MainParameter = self.search([('company_id', '=', self.env.company.id)], limit=1)
		if not MainParameter:
			raise UserError('No se ha creado Parametros Generales de Inventario para esta compañia')
		return MainParameter