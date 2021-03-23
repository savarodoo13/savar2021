# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProjectSteelReport(models.Model):
	_name = 'project.steel.report'
	_auto = False

	year = fields.Char(string='Año')
	month = fields.Selection([('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), 
		('8', 'Agosto'), ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')], string='Mes')
	date = fields.Date(string='Fecha')

	fecha_registro = fields.Date(string='Fecha Registro',compute="get_fecha_reg")

	def get_fecha_reg(self):
		for i in self:
			i.fecha_registro = i.date


	shift = fields.Char(string='Turno')
	machine = fields.Char(string='Maquina')
	equipo = fields.Char(string='Equipo',compute="get_machine")

	def get_machine(self):
		for i in self:
			i.equipo = i.machine


	area = fields.Char(string='Area')
	block = fields.Char(string='Tajo')
	bank = fields.Char(string='Banco')
	project = fields.Char(string='Proyecto')
	drill_code = fields.Char(string='Codigo de Taladro')
	high = fields.Float(string='Altura')
	drill_type = fields.Char(string='Tipo de Taladro')
	hardness = fields.Char(string='Dureza de Roca')
	details = fields.Text('Observaciones')

	usuario_odoo = fields.Char(string='Usuario Odoo')
	operator = fields.Char(string='Operador')
	supervisor = fields.Char(string='Supervisor')
	ayudante = fields.Char(string='Ayudante')
	terrain = fields.Char(string='Terreno')

	broca_id = fields.Char( string='Broca')
	broca_fecha = fields.Date('Fecha Vencimiento')
	broca_note = fields.Text('Descripcion')
	broca_metros = fields.Float('Metros')

	martillo_id = fields.Char( string='Martillo')
	martillo_fecha = fields.Date('Fecha Vencimiento')
	martillo_note = fields.Text('Descripcion')
	martillo_metros = fields.Float('Metros')

	pinbox_id = fields.Char( string='Pinbox')
	pinbox_fecha = fields.Date('Fecha Vencimiento')
	pinbox_note = fields.Text('Descripcion')
	pinbox_metros = fields.Float('Metros')

	chuck_id = fields.Char( string='Chuck')
	chuck_fecha = fields.Date('Fecha Vencimiento')
	chuck_note = fields.Text('Descripcion')
	chuck_metros = fields.Float('Metros')

	tubo1_id = fields.Char( string='Tubo1')
	tubo1_fecha = fields.Date('Fecha Vencimiento')
	tubo1_note = fields.Text('Descripcion')
	tubo1_metros = fields.Float('Metros')

	tubo2_id = fields.Char( string='Tubo2')
	tubo2_fecha = fields.Date('Fecha Vencimiento')
	tubo2_note = fields.Text('Descripcion')
	tubo2_metros = fields.Float('Metros')

	tubo3_id = fields.Char( string='Tubo3')
	tubo3_fecha = fields.Date('Fecha Vencimiento')
	tubo3_note = fields.Text('Descripcion')
	tubo3_metros = fields.Float('Metros')

	tubo4_id = fields.Char( string='Tubo4')
	tubo4_fecha = fields.Date('Fecha Vencimiento')
	tubo4_note = fields.Text('Descripcion')
	tubo4_metros = fields.Float('Metros')

	tubo5_id = fields.Char( string='Tubo5')
	tubo5_fecha = fields.Date('Fecha Vencimiento')
	tubo5_note = fields.Text('Descripcion')
	tubo5_metros = fields.Float('Metros')

	tubo6_id = fields.Char( string='Tubo6')
	tubo6_fecha = fields.Date('Fecha Vencimiento')
	tubo6_note = fields.Text('Descripcion')
	tubo6_metros = fields.Float('Metros')


	hour_from = fields.Float(string='Hora Inicial')
	hour_to = fields.Float(string='Hora Final')
	rop = fields.Float(string='ROP', digits=(12,2))
	task = fields.Char(string='Tarea')
	contract = fields.Char(string='Tipo Contrato')


class ProjectBinnacleReport(models.Model):
	_name = 'project.binnacle.report'
	_auto = False

	year = fields.Char(string='Año')
	month = fields.Selection([('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), 
		('8', 'Agosto'), ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')], string='Mes')
	date = fields.Date(string='Fecha')
	shift = fields.Char(string='Turno')
	machine = fields.Char(string='Maquina')
	area = fields.Char(string='Area')	
	operador = fields.Char('Operador')
	operation_name = fields.Char(string='Codigo de Operacion')
	operation_description = fields.Char(string='Descripcion de Operacion')
	hour_from = fields.Float(string='Hora Ini')
	hour_to = fields.Float(string='Hora Fin')
	unit_amount = fields.Float(string=u'Duración (Horas)')
	observation=fields.Text(string='Observaciones')

	type_contract= fields.Char('Tipo de Contrato')
	user_odoo = fields.Char('Ususario Odoo')
	supervisor = fields.Char('Supervisor')
	helper= fields.Char('Ayudante')


class ProjectHourmeterReport(models.Model):
	_name = 'project.hourmeter.report'
	_auto = False

	year = fields.Char(string='Año')
	month = fields.Selection([('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), 
		('8', 'Agosto'), ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')], string='Mes')
	date = fields.Date(string='Fecha')
	shift = fields.Char(string='Turno')
	machine = fields.Char(string='Maquina')
	area = fields.Char(string='Area')	
	
	fuel_hour_from = fields.Float(string='Hora Inicial Percusion')
	fuel_hour_to = fields.Float(string='Hora Final Percusion')
	fuel_diesel_hour_from = fields.Float(string='Hora Inicial Diesel')
	fuel_diesel_hour_to = fields.Float(string='Hora Final Diesel')
	refuel_time = fields.Float(string='Horometro Abast')
	fuel_qty = fields.Float(string='Combustible')

	type_contract= fields.Char('Tipo de Contrato')
	user_odoo = fields.Char('Ususario Odoo')
	supervisor = fields.Char('Supervisor')
	helper= fields.Char('Ayudante')
	operador= fields.Char('Operador')