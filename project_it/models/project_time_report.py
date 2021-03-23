# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProjectTimeReport(models.Model):
	_name = 'project.time.report'
	_auto = False

	year = fields.Char(string='Año')
	month = fields.Selection([('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'),
		('8', 'Agosto'), ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')], string='Mes')
	date = fields.Date(string='Fecha')
	shift = fields.Char(string='Turno')
	machine = fields.Char(string='Maquina')
	area = fields.Char(string='Area')

	type_contract= fields.Char('Tipo de Contrato')
	user_odoo = fields.Char('Ususario Odoo')

	operator = fields.Char(string='Operador')
	helper = fields.Char(string='Ayudante')
	supervisor = fields.Char(string='Supervisor')
	
	block = fields.Char(string='Tajo')
	bank = fields.Char(string='Banco')
	project = fields.Char(string='Proyecto')
	effective_hours = fields.Float(string='Horas Trabajadas')
	drills = fields.Integer(string='Taladros')
	highs = fields.Float(string='Metros')
	fuel_hour_from = fields.Float(string='Horometro Hora Inicial')
	fuel_hour_to = fields.Float(string='Horometro Hora Final')
	refuel_time = fields.Float(string='Horometro Abastecimiento')
	fuel_qty = fields.Float(string='Cantidad de Combustible')
	project_work = fields.Char(string='Proyecto')
	task = fields.Char(string='Tarea')
	contract = fields.Char(string='Tipo Contrato')



