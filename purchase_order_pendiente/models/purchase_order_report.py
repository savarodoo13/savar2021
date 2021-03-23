# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError

class purchase_order_report(models.Model):
	_inherit = 'purchase.order'

	pendiente=fields.Char(string="Pendiente",compute="get_pendiente")

	detalle_ids= fields.One2many('purchase.order.line','order_id','Detalles',delete='cascade')

	total_catidad = fields.Float('Total Cantidad',compute="get_total")
	total_recibido = fields.Float('Total Recibido',compute="get_total")

	def get_total(self):
		for i in self:
			acum_cant = 0
			acum_rec = 0
			for x in i.detalle_ids:
				acum_cant += x.product_qty
				acum_rec += x.qty_received
			i.total_catidad= acum_cant
			i.total_recibido = acum_rec

	def get_pendiente(self):
		for i in self:
			if i.total_catidad-i.total_recibido==0:
				i.pendiente="No"
			else:
				i.pendiente="Si"

class purchase_order_report(models.Model):
	_inherit = 'purchase.order.line'

