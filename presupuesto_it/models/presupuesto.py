# -*- coding: utf-8 -*-
from odoo import models, fields, api

class presupuesto_unidad_operativa(models.Model):
	_name = 'presupuesto.unidad.operativa'

	name = fields.Char('Unidad Operativa',required=True)

class presupuesto_it(models.Model):
	_name = 'presupuesto.it'

	state = fields.Selection([('draft','Borrador'),('done','Terminado')] ,'Estado',default='draft')
	name = fields.Char('Presupuesto')
	project_id = fields.Many2one('project.project','Proyecto',required=True)
	unidad_operativa = fields.Many2one('presupuesto.unidad.operativa','Unidad Operativa',required=True)

	def cerrar(self):
		for i in self:
			i.state = 'done'

	def abrir(self):
		for i in self:
			i.state = 'draft'

	def actualizar(self):
		for i in self:
			for l in i.detalle_ids.sorted(lambda m: m.name.code):
				l.actualizar()

	num_contrato = fields.Char('Numero de Contrato',required=True)
	num_orden_trabajo = fields.Char('Numero de Orden de Trabajo',required=True)
	num_orden_cambio = fields.Char('Numero de Orden de Cambio',required=True)
	num_solped = fields.Char('Numero de SOLPED',required=True)
	description = fields.Text('Descripcion del Servicio',required=True)
	contratista = fields.Many2one('res.partner','Contratista')

	contrato = fields.Many2one('project.contract.type','Contrato')
	area = fields.Many2one('project.area','Area')

	budget_fecha_inicio = fields.Date('Fecha Inicio')
	budget_fecha_fin = fields.Date('Fecha Fin')
	budget_meses = fields.Integer('Nro. Meses')

	budget_total_cantidad = fields.Float('Cantidad')
	budget_total_unidad = fields.Many2one('uom.uom','Unidad')

	budget_total_pu = fields.Float('P.U.')	
	budget_total_moneda = fields.Many2one('res.currency','Moneda')
	budget_total_total = fields.Float('Total',compute="get_budget_total_total")

	def get_budget_total_total(self):
		for i in self:
			i.budget_total_total = i.budget_total_cantidad * i.budget_total_pu



	owm_fecha_inicio = fields.Date('Fecha Inicio')
	owm_fecha_fin = fields.Date('Fecha Fin')
	owm_meses = fields.Integer('Nro. Meses')
	
	owm_total_cantidad = fields.Float('Cantidad')
	owm_total_unidad = fields.Many2one('uom.uom','Unidad')

	owm_total_pu = fields.Float('P.U.')	
	owm_total_moneda = fields.Many2one('res.currency','Moneda')
	owm_total_total = fields.Float('Total',compute="get_owm_total_total")

	def get_owm_total_total(self):
		for i in self:
			i.owm_total_total = i.owm_total_cantidad * i.owm_total_pu

	detalle_ids= fields.One2many('presupuesto.linea.it','presupuesto_id','Detalle')

class presupuesto_linea_it(models.Model):
	_name = 'presupuesto.linea.it'

	_order = 'name desc'

	presupuesto_id = fields.Many2one('presupuesto.it','Presupuesto')
	presupuesto_name = fields.Char('Presupuesto',related="presupuesto_id.name")



	presupuesto_state = fields.Selection([('draft','Borrador'),('done','Terminado')] ,'Estado',default='draft',related="presupuesto_id.state")

	presupuesto_project_id = fields.Char('Proyecto',compute="get_presupuesto_datos")
	presupuesto_unidad_operativa = fields.Char('Unidad Operativa',compute="get_presupuesto_datos")


	presupuesto_num_contrato = fields.Char('Numero de Contrato',related="presupuesto_id.num_contrato")
	presupuesto_num_orden_trabajo = fields.Char('Numero de Orden de Trabajo',related="presupuesto_id.num_orden_trabajo")
	presupuesto_num_orden_cambio = fields.Char('Numero de Orden de Cambio',related="presupuesto_id.num_orden_cambio")
	presupuesto_num_solped = fields.Char('Numero de SOLPED',related="presupuesto_id.num_solped")
	presupuesto_description = fields.Text('Descripcion del Servicio',related="presupuesto_id.description")

	presupuesto_contratista = fields.Char('Contratista',compute="get_presupuesto_datos")
	presupuesto_contrato = fields.Char('Contrato',compute="get_presupuesto_datos")	
	presupuesto_area = fields.Char('Area',compute="get_presupuesto_datos")



	presupuesto_budget_fecha_inicio = fields.Date('Fecha Inicio',related="presupuesto_id.budget_fecha_inicio")
	presupuesto_budget_fecha_fin = fields.Date('Fecha Fin',related="presupuesto_id.budget_fecha_fin")
	presupuesto_budget_meses = fields.Integer('Nro. Meses',related="presupuesto_id.budget_meses")

	presupuesto_budget_total_cantidad = fields.Float('Cantidad',related="presupuesto_id.budget_total_cantidad")

	presupuesto_budget_total_unidad = fields.Char('Unidad',compute="get_presupuesto_datos")

	presupuesto_budget_total_pu = fields.Float('P.U.',related="presupuesto_id.budget_total_pu")	
	presupuesto_budget_total_moneda = fields.Char('Moneda',compute="get_presupuesto_datos")
	presupuesto_budget_total_total = fields.Float('Total',compute="get_presupuesto_datos")


	presupuesto_owm_fecha_inicio = fields.Date('Fecha Inicio',related="presupuesto_id.owm_fecha_inicio")
	presupuesto_owm_fecha_fin = fields.Date('Fecha Fin',related="presupuesto_id.owm_fecha_fin")
	presupuesto_owm_meses = fields.Integer('Nro. Meses',related="presupuesto_id.owm_meses")
	
	presupuesto_owm_total_cantidad = fields.Float('Cantidad',related="presupuesto_id.owm_total_cantidad")
	presupuesto_owm_total_unidad = fields.Char('Unidad',compute="get_presupuesto_datos")

	presupuesto_owm_total_pu = fields.Float('P.U.',related="presupuesto_id.owm_total_pu")	
	presupuesto_owm_total_moneda = fields.Char('Moneda',compute="get_presupuesto_datos")
	presupuesto_owm_total_total = fields.Float('Total',compute="get_presupuesto_datos")

	def get_presupuesto_datos(self):
		for i in self:
			i.presupuesto_unidad_operativa = i.presupuesto_id.unidad_operativa.name
			i.presupuesto_project_id = i.presupuesto_id.project_id.name
			i.presupuesto_contratista= i.presupuesto_id.contratista.name
			i.presupuesto_contrato= i.presupuesto_id.contrato.name
			i.presupuesto_area= i.presupuesto_id.area.name
			i.presupuesto_budget_total_unidad= i.presupuesto_id.budget_total_unidad.name
			i.presupuesto_budget_total_moneda= i.presupuesto_id.budget_total_moneda.name
			i.presupuesto_budget_total_total= i.presupuesto_id.budget_total_total
			i.presupuesto_owm_total_unidad= i.presupuesto_id.owm_total_unidad.name
			i.presupuesto_owm_total_moneda= i.presupuesto_id.owm_total_moneda.name
			i.presupuesto_owm_total_total= i.presupuesto_id.owm_total_total










	name = fields.Many2one('account.period','Mes',domain=[('is_opening_close','=',False)])
	name_lineal = fields.Char('Mes',related='name.name')

	inicio_mes = fields.Date('Fecha Inicio',related='name.date_start')
	fin_mes = fields.Date('Fecha Final',related='name.date_end')

	inicio_periodo = fields.Date('Fecha Inicio')
	fin_periodo = fields.Date('Fecha Final')
	

	
	budget_cliente_total_cantidad = fields.Float('Cantidad')
	budget_cliente_total_unidad = fields.Many2one('uom.uom','Unidad')
	budget_cliente_total_unidad_name = fields.Char('Unidad',related="budget_cliente_total_unidad.name")

	budget_cliente_total_pu = fields.Float('P.U.')	
	budget_cliente_total_moneda = fields.Many2one('res.currency','Moneda')
	budget_cliente_total_moneda_name = fields.Char('Moneda',related="budget_cliente_total_moneda.name")
	budget_cliente_total_total = fields.Float('Total',compute="get_budget_cliente_total_total")

	def get_budget_cliente_total_total(self):
		for i in self:
			i.budget_cliente_total_total = i.budget_cliente_total_cantidad * i.budget_cliente_total_pu


	
	budget_owm_total_cantidad = fields.Float('Cantidad')
	budget_owm_total_unidad = fields.Many2one('uom.uom','Unidad')
	budget_owm_total_unidad_name = fields.Char('Unidad',related="budget_owm_total_unidad.name")

	budget_owm_total_pu = fields.Float('P.U.')	
	budget_owm_total_moneda = fields.Many2one('res.currency','Moneda')
	budget_owm_total_moneda_name = fields.Char('Moneda',related="budget_owm_total_moneda.name")
	budget_owm_total_total = fields.Float('Total',compute="get_budget_owm_total_total")

	def get_budget_owm_total_total(self):
		for i in self:
			i.budget_owm_total_total = i.budget_owm_total_cantidad * i.budget_owm_total_pu


	
	forecast_cliente_total_cantidad = fields.Float('Cantidad')
	forecast_cliente_total_unidad = fields.Many2one('uom.uom','Unidad')
	forecast_cliente_total_unidad_name = fields.Char('Unidad',related="forecast_cliente_total_unidad.name")

	forecast_cliente_total_pu = fields.Float('P.U.')	
	forecast_cliente_total_moneda = fields.Many2one('res.currency','Moneda')
	forecast_cliente_total_moneda_name = fields.Char('Moneda',related="forecast_cliente_total_moneda.name")
	forecast_cliente_total_total = fields.Float('Total',compute="get_forecast_cliente_total_total")

	def get_forecast_cliente_total_total(self):
		for i in self:
			i.forecast_cliente_total_total = i.forecast_cliente_total_cantidad * i.forecast_cliente_total_pu


	
	forecast_owm_total_cantidad = fields.Float('Cantidad')
	forecast_owm_total_unidad = fields.Many2one('uom.uom','Unidad')
	forecast_owm_total_unidad_name = fields.Char('Unidad',related="forecast_owm_total_unidad.name")

	forecast_owm_total_pu = fields.Float('P.U.')	
	forecast_owm_total_moneda = fields.Many2one('res.currency','Moneda')
	forecast_owm_total_moneda_name = fields.Char('Moneda',related="forecast_owm_total_moneda.name")
	forecast_owm_total_total = fields.Float('Total',compute="get_forecast_owm_total_total")

	def get_forecast_owm_total_total(self):
		for i in self:
			i.forecast_owm_total_total = i.forecast_owm_total_cantidad * i.forecast_owm_total_pu


	budget_cliente_ant_cantidad = fields.Float('Cantidad')
	budget_cliente_ant_porc = fields.Float('Porcentaje')
	budget_cliente_ant_total = fields.Float('Total')
	
	budget_owm_ant_cantidad = fields.Float('Cantidad')
	budget_owm_ant_porc = fields.Float('Porcentaje')
	budget_owm_ant_total = fields.Float('Total')
	
	forecast_cliente_ant_cantidad = fields.Float('Cantidad')
	forecast_cliente_ant_porc = fields.Float('Porcentaje')
	forecast_cliente_ant_total = fields.Float('Total')
	
	forecast_owm_ant_cantidad = fields.Float('Cantidad')
	forecast_owm_ant_porc = fields.Float('Porcentaje')
	forecast_owm_ant_total = fields.Float('Total')

	


	budget_cliente_actual_cantidad = fields.Float('Cantidad')
	budget_cliente_actual_porc = fields.Float('Porcentaje')
	budget_cliente_actual_total = fields.Float('Total')
	
	budget_owm_actual_cantidad = fields.Float('Cantidad')
	budget_owm_actual_porc = fields.Float('Porcentaje')
	budget_owm_actual_total = fields.Float('Total')
	
	forecast_cliente_actual_cantidad = fields.Float('Cantidad')
	forecast_cliente_actual_porc = fields.Float('Porcentaje')
	forecast_cliente_actual_total = fields.Float('Total')
	
	forecast_owm_actual_cantidad = fields.Float('Cantidad')
	forecast_owm_actual_porc = fields.Float('Porcentaje')
	forecast_owm_actual_total = fields.Float('Total')

	


	budget_cliente_acum_cantidad = fields.Float('Cantidad')
	budget_cliente_acum_porc = fields.Float('Porcentaje')
	budget_cliente_acum_total = fields.Float('Total')
	
	budget_owm_acum_cantidad = fields.Float('Cantidad')
	budget_owm_acum_porc = fields.Float('Porcentaje')
	budget_owm_acum_total = fields.Float('Total')
	
	forecast_cliente_acum_cantidad = fields.Float('Cantidad')
	forecast_cliente_acum_porc = fields.Float('Porcentaje')
	forecast_cliente_acum_total = fields.Float('Total')
	
	forecast_owm_acum_cantidad = fields.Float('Cantidad')
	forecast_owm_acum_porc = fields.Float('Porcentaje')
	forecast_owm_acum_total = fields.Float('Total')

	


	budget_cliente_saldo_cantidad = fields.Float('Cantidad')
	budget_cliente_saldo_porc = fields.Float('Porcentaje')
	budget_cliente_saldo_total = fields.Float('Total')
	
	budget_owm_saldo_cantidad = fields.Float('Cantidad')
	budget_owm_saldo_porc = fields.Float('Porcentaje')
	budget_owm_saldo_total = fields.Float('Total')
	
	forecast_cliente_saldo_cantidad = fields.Float('Cantidad')
	forecast_cliente_saldo_porc = fields.Float('Porcentaje')
	forecast_cliente_saldo_total = fields.Float('Total')
	
	forecast_owm_saldo_cantidad = fields.Float('Cantidad')
	forecast_owm_saldo_porc = fields.Float('Porcentaje')
	forecast_owm_saldo_total = fields.Float('Total')

	def actualizar(self):
		for i in self:
			cant_total = 0
			#for elem in self.env['project.task'].search([('area_id','=',i.presupuesto_id.area.id ),('contract_type_id','=',i.presupuesto_id.contrato.id),('date_deadline','>=',i.inicio_periodo),('date_deadline','>=',i.fin_periodo)]):
			#	cant_total += elem.highs
			#i.budget_owm_total_cantidad =cant_total
			#i.budget_owm_total_unidad = i.presupuesto_id.owm_total_unidad
			#i.budget_owm_total_pu = i.presupuesto_id.owm_total_pu
			#i.budget_owm_total_moneda = i.presupuesto_id.owm_total_moneda

			i.refresh()


			i.budget_cliente_acum_cantidad = 0
			i.budget_cliente_acum_total = 0
	
			i.budget_owm_acum_cantidad = 0
			i.budget_owm_acum_total = 0
	
			i.forecast_cliente_acum_cantidad = 0
			i.forecast_cliente_acum_total = 0
	
			i.forecast_owm_acum_cantidad = 0
			i.forecast_owm_acum_total = 0


			for anterior in self.env['presupuesto.linea.it'].search([ ('name.code','<',i.name.code),('presupuesto_id','=',i.presupuesto_id.id) ]).sorted(lambda m: m.name.code):

				i.budget_cliente_ant_cantidad = anterior.budget_cliente_total_cantidad
				i.budget_cliente_ant_porc = (anterior.budget_cliente_total_cantidad * 100.0) / i.presupuesto_id.budget_total_cantidad
				i.budget_cliente_ant_total = anterior.budget_cliente_total_total
				

				i.budget_owm_ant_cantidad = anterior.budget_owm_total_cantidad
				i.budget_owm_ant_porc = (anterior.budget_owm_total_cantidad * 100.0) / i.presupuesto_id.owm_total_cantidad
				i.budget_owm_ant_total = anterior.budget_owm_total_total
				
				
				i.forecast_cliente_ant_cantidad = anterior.forecast_cliente_total_cantidad
				i.forecast_cliente_ant_porc = (anterior.forecast_cliente_total_cantidad * 100.0) / i.presupuesto_id.budget_total_cantidad
				i.forecast_cliente_ant_total = anterior.forecast_cliente_total_total
				

				i.forecast_owm_ant_cantidad = anterior.forecast_owm_total_cantidad
				i.forecast_owm_ant_porc = (anterior.forecast_owm_total_cantidad * 100.0) / i.presupuesto_id.owm_total_cantidad
				i.forecast_owm_ant_total = anterior.forecast_owm_total_total


				i.budget_cliente_acum_cantidad += anterior.budget_cliente_total_cantidad
				i.budget_cliente_acum_total += anterior.budget_cliente_total_total
		
				i.budget_owm_acum_cantidad += anterior.budget_owm_total_cantidad
				i.budget_owm_acum_total += anterior.budget_owm_total_total
		
				i.forecast_cliente_acum_cantidad += anterior.forecast_cliente_total_cantidad
				i.forecast_cliente_acum_total += anterior.forecast_cliente_total_total
		
				i.forecast_owm_acum_cantidad += anterior.forecast_owm_total_cantidad
				i.forecast_owm_acum_total += anterior.forecast_owm_total_total

		


			i.budget_cliente_actual_cantidad = i.budget_cliente_total_cantidad
			i.budget_cliente_actual_porc = (i.budget_cliente_total_cantidad * 100.0) / i.presupuesto_id.budget_total_cantidad
			i.budget_cliente_actual_total = i.budget_cliente_total_total

	
			i.budget_owm_actual_cantidad = i.budget_owm_total_cantidad
			i.budget_owm_actual_porc = (i.budget_owm_total_cantidad * 100.0) / i.presupuesto_id.owm_total_cantidad
			i.budget_owm_actual_total = i.budget_owm_total_total

			i.forecast_cliente_actual_cantidad = i.forecast_cliente_total_cantidad
			i.forecast_cliente_actual_porc = (i.forecast_cliente_total_cantidad * 100.0) / i.presupuesto_id.budget_total_cantidad
			i.forecast_cliente_actual_total = i.forecast_cliente_total_total

	
			i.forecast_owm_actual_cantidad = i.forecast_owm_total_cantidad
			i.forecast_owm_actual_porc = (i.forecast_owm_total_cantidad * 100.0) / i.presupuesto_id.owm_total_cantidad
			i.forecast_owm_actual_total = i.forecast_owm_total_total



			i.budget_cliente_acum_cantidad += i.budget_cliente_actual_cantidad
			i.budget_cliente_acum_total += i.budget_cliente_actual_total
	
			i.budget_owm_acum_cantidad += i.budget_owm_actual_cantidad
			i.budget_owm_acum_total += i.budget_owm_actual_total
	
			i.forecast_cliente_acum_cantidad += i.forecast_cliente_actual_cantidad
			i.forecast_cliente_acum_total += i.forecast_cliente_actual_total
	
			i.forecast_owm_acum_cantidad += i.forecast_owm_actual_cantidad
			i.forecast_owm_acum_total += i.forecast_owm_actual_total





			i.budget_cliente_acum_porc = (i.budget_cliente_acum_cantidad * 100.0) / i.presupuesto_id.budget_total_cantidad	
			i.budget_owm_acum_porc = (i.budget_owm_acum_cantidad * 100.0) / i.presupuesto_id.owm_total_cantidad	
			i.forecast_cliente_acum_porc = (i.forecast_cliente_acum_cantidad * 100.0) / i.presupuesto_id.budget_total_cantidad	
			i.forecast_owm_acum_porc = (i.forecast_owm_acum_cantidad * 100.0) / i.presupuesto_id.owm_total_cantidad

			i.refresh()

			i.budget_cliente_saldo_cantidad = i.presupuesto_id.budget_total_cantidad - i.budget_cliente_acum_cantidad
			i.budget_cliente_saldo_porc = (i.budget_cliente_saldo_cantidad * 100.0) / i.presupuesto_id.budget_total_cantidad
			i.budget_cliente_saldo_total = i.presupuesto_id.budget_total_total - i.budget_cliente_acum_total
	

			i.budget_owm_saldo_cantidad = i.presupuesto_id.owm_total_cantidad - i.budget_owm_acum_cantidad
			i.budget_owm_saldo_porc = (i.budget_owm_saldo_cantidad * 100.0) / i.presupuesto_id.owm_total_cantidad
			i.budget_owm_saldo_total = i.presupuesto_id.owm_total_total - i.budget_owm_acum_total
	
			i.forecast_cliente_saldo_cantidad = i.presupuesto_id.budget_total_cantidad - i.forecast_cliente_acum_cantidad
			i.forecast_cliente_saldo_porc = (i.forecast_cliente_saldo_cantidad * 100.0) / i.presupuesto_id.budget_total_cantidad
			i.forecast_cliente_saldo_total = i.presupuesto_id.budget_total_total - i.forecast_cliente_acum_total
	
			i.forecast_owm_saldo_cantidad = i.presupuesto_id.owm_total_cantidad - i.forecast_owm_acum_cantidad
			i.forecast_owm_saldo_porc = (i.forecast_owm_saldo_cantidad * 100.0) / i.presupuesto_id.owm_total_cantidad
			i.forecast_owm_saldo_total = i.presupuesto_id.owm_total_total - i.forecast_owm_acum_total