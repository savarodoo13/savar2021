# -*- coding: utf-8 -*-

from collections import namedtuple
import json
import time
from odoo import api, fields, models, _ , exceptions

from openerp.osv import osv

class type_operation_kardex(models.Model):
	_name = 'type.operation.kardex'

	name = fields.Char('Nombre')
	code = fields.Char('Codigo')


class PickingType(models.Model):
	_inherit = "stock.picking"


	kardex_date = fields.Datetime(string='Fecha kardex', readonly=False,track_visibility='always')
	use_kardex_date = fields.Boolean('Usar Fecha kardex',default=True)
	invoice_id = fields.Many2one('account.move','Factura',domain=[('type', 'in', ['out_invoice','in_invoice','out_refund','in_refund'])])
	type_operation_sunat_id = fields.Many2one('type.operation.kardex','Tipo de Operacion SUNAT')
	no_mostrar = fields.Boolean('No mostrar en kardex',default=False)
	
	def action_done(self):
		t = super(PickingType,self).action_done()
		self.with_context({'permitido':1}).write({'kardex_date': fields.Datetime.now()})
		return t

	def write(self,vals):
		t = super(PickingType,self).write(vals)
		if 'kardex_date' in vals and 'permitido' in self.env.context:
			pass
		elif 'kardex_date' in vals and 'permitido' not in self.env.context:
			permiso = self.env['res.groups'].search([('name','=','Permitir Editar Fecha Kardex')])
			if len(permiso)>0:
				if self.env.uid in permiso[0].users.ids:
					pass
				else:
					raise osv.except_osv('Alerta','No tiene permisos de Edicion del Kardex')
		return t