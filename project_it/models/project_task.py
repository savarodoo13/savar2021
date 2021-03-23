# -*- coding: utf-8 -*-
from odoo import models, fields, api

class maintenance_component_report(models.Model):
	_name = 'maintenance.component.report'

	_auto = False

	name = fields.Char('Mantenimiento')
	company_id = fields.Many2one('res.company', string='Compañia')
	company_name = fields.Char('Compañia',related='company_id.name')

	category_id = fields.Many2one('maintenance.equipment.category', string='Categoria')
	category_name = fields.Char('Categoria',related='category_id.name')

	employee_id = fields.Many2one('hr.employee', string='Creador por')
	employee_name = fields.Char('Creador Por',related="employee_id.name")

	equipment_id = fields.Many2one('maintenance.equipment', string='Equipamiento')
	equipment_name = fields.Char('Equipamiento',related="equipment_id.name")


	type_preventivo = fields.Many2one('maintenance.request.preventivo','Tipo Preventivo')
	type_correctivo = fields.Many2one('maintenance.request.correctivo','Tipo Correctivo')

	type_preventivo_name = fields.Char('Tipo Preventivo',related="type_preventivo.name")
	type_correctivo_name = fields.Char('Tipo Correctivo',related="type_correctivo.name")


	user_id = fields.Many2one('res.users', string='Responsable')
	user_name = fields.Char('Responsable',related='user_id.name')


	priority = fields.Selection([('0', 'Muy baja'), ('1', 'Baja'), ('2', 'Normal'), ('3', 'Alta')], string='Prioridad')
	maintenance_type = fields.Selection([('corrective', 'Correctivo'), ('preventive', 'Preventivo')], string='Tipo de mantenimiento')
	schedule_date = fields.Datetime('Fecha Registro')
	fecha_registro = fields.Datetime('Fecha Registro',compute="get_fecha_reg")

	def get_fecha_reg(self):
		for i in self:
			i.fecha_registro = i.schedule_date

	maintenance_team_id = fields.Many2one('maintenance.team', string='Equipo')
	maintenance_team_name = fields.Char('Equipo',related='maintenance_team_id.name')
	equipo = fields.Char('Equipo',related='maintenance_team_id.name')

	duration = fields.Float(string="Duracion")
	email_cc = fields.Char('Correo Electrónico CC')
	expected_duration = fields.Float(string='Duracion Prevista')
	linea_report = fields.Many2one('maintenance.request.category.type.report','Tipo de Reporte')
	linea_report_name = fields.Char('Tipo de Reporte',compute="get_linea_report")

	def get_linea_report(self):
		for i in self:
			i.linea_report_name = i.linea_report.formato_id.name if i.linea_report.id and i.linea_report.formato_id.id else ''

	horometro_planing = fields.Float('Horometro Motor Planeado')
	horometro_real = fields.Float('Horometro Motor Real')
	horometro_real_percution = fields.Float('Horometro Percusion Real')
	request_date = fields.Date('Fecha')
	
	component_id = fields.Many2one('maintenance.component', string='Componente')
	component_name = fields.Char('Componente',related='component_id.name')

	product_id = fields.Many2one('product.product', string='Producto')
	product_name = fields.Char('Producto',related='product_id.name')

	lot_id = fields.Many2one('stock.production.lot', string='Codigo')
	lot_name = fields.Char('Codigo',related="lot_id.name")

	quantity = fields.Float('Cantidad')
	notes = fields.Char(string='Observaciones')


class stock_production_lot(models.Model):
	_inherit = 'stock.production.lot'

	date_vencimiento = fields.Date('Fecha Vencimiento')
	metros_total = fields.Float('Metros Totales')

	def write(self,vals):
		for i in self:
			if 'date_vencimiento' in vals and vals['date_vencimiento']:
				total = 0
				for j in self.env['account.analytic.line'].search([('task_id','!=',False),('aceros_id','=',i.id)]):
					total+= j.high
				for j in self.env['account.analytic.line'].search([('task_id','!=',False),('broca_id','=',i.id)]):
					total+= j.high
				for j in self.env['account.analytic.line'].search([('task_id','!=',False),('martillo_id','=',i.id)]):
					total+= j.high
				for j in self.env['account.analytic.line'].search([('task_id','!=',False),('pinbox_id','=',i.id)]):
					total+= j.high
				for j in self.env['account.analytic.line'].search([('task_id','!=',False),('chuck_id','=',i.id)]):
					total+= j.high
				for j in self.env['account.analytic.line'].search([('task_id','!=',False),('tubo1_id','=',i.id)]):
					total+= j.high
				for j in self.env['account.analytic.line'].search([('task_id','!=',False),('tubo2_id','=',i.id)]):
					total+= j.high
				for j in self.env['account.analytic.line'].search([('task_id','!=',False),('tubo3_id','=',i.id)]):
					total+= j.high
				for j in self.env['account.analytic.line'].search([('task_id','!=',False),('tubo4_id','=',i.id)]):
					total+= j.high
				for j in self.env['account.analytic.line'].search([('task_id','!=',False),('tubo5_id','=',i.id)]):
					total+= j.high
				for j in self.env['account.analytic.line'].search([('task_id','!=',False),('tubo6_id','=',i.id)]):
					total+= j.high
				
				vals['metros_total'] = total
			else:
				vals['metros_total'] = 0

			super(stock_production_lot,i).write(vals)
		

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	task_id = fields.Many2one('project.task', string='Tarea')
	empleado_resp_id = fields.Many2one('hr.employee', string='Empleado')
	
class ProjectTask(models.Model):
	_inherit = 'project.task'

	timesheet_ids2 = fields.One2many('account.analytic.line', 'task_id', 'Timesheets')
	supervisor_id = fields.Many2one('hr.employee', string='Supervisor', required=True)
	operator_id = fields.Many2one('hr.employee', string='Operador')
	helper_id = fields.Many2one('hr.employee', string='Ayudante')
	area_id = fields.Many2one('project.area', string='Area')	
	contract_type_id = fields.Many2one('project.contract.type', string='Tipo Contrato')
	equipment_id = fields.Many2one('maintenance.equipment', string='Maquina')
	shift = fields.Selection([('A', 'A'),
							  ('B', 'B')], string="Turno")
	drills = fields.Float(string='Taladros', compute='_get_totals', store=True)
	highs = fields.Float(string='Metros', compute='_get_totals', store=True)
	
	@api.depends('timesheet_ids')
	def _get_totals(self):
		for record in self:
			total_high, total_minutes = 0, 0
			for line in record.timesheet_ids:
				total_high += line.high
			record.drills = len(record.timesheet_ids)
			record.highs = total_high

	binnacle_ids = fields.One2many('project.binnacle', 'project_task_id')
	fuel_hour_from = fields.Float(string='Hora Inicial Percusion')
	fuel_hour_to = fields.Float(string='Hora Final Percusion')
	fuel_diesel_hour_from = fields.Float(string='Hora Inicial Diesel')
	fuel_diesel_hour_to = fields.Float(string='Hora Final Diesel')
	refuel_time = fields.Float(string='Horometro Abast')
	fuel_qty = fields.Float(string='Combustible')

	####ACEROS####
	product_id_1 = fields.Many2one('product.product', string='Aceros', related='lot_id_1.product_id')
	lot_id_1 = fields.Many2one('stock.production.lot', string='Codigo')
	acumulated_meters_1 = fields.Float(compute="_get_acumulated_meters_1", string='Metros Acumulados')
	final_meters_1 = fields.Float(string='Metros Finales')
	product_condition_id_1 = fields.Many2one('product.condition', string='Condicion')

	@api.depends('date_deadline', 'final_meters_1')
	def _get_acumulated_meters_1(self):
		for record in self:
			Tasks = self.env['project.task'].search([
						('date_deadline', '<=', record.date_deadline), 
						('product_id_1', '=', record.product_id_1.id),
						('lot_id_1', '=', record.lot_id_1.id)
					])
			meters = Tasks.mapped('final_meters_1')
			print(meters)
			record.acumulated_meters_1 = sum(meters)

	def _get_product_1(self):
		MainParameter = self.env['stock.main.parameter'].get_main_parameter()
		return MainParameter.product_id_1.id or None

	product_id_2 = fields.Many2one('product.product', string='Aceros', related='lot_id_2.product_id')
	lot_id_2 = fields.Many2one('stock.production.lot', string='Codigo')
	acumulated_meters_2 = fields.Float(compute="_get_acumulated_meters_2", string='Metros Acumulados')
	final_meters_2 = fields.Float(string='Metros Finales')
	product_condition_id_2 = fields.Many2one('product.condition', string='Condicion')

	@api.depends('date_deadline', 'final_meters_2')
	def _get_acumulated_meters_2(self):
		for record in self:
			Tasks = self.env['project.task'].search([
						('date_deadline', '<=', record.date_deadline), 
						('product_id_2', '=', record.product_id_2.id),
						('lot_id_2', '=', record.lot_id_2.id)
					])
			meters = Tasks.mapped('final_meters_2')
			record.acumulated_meters_2 = sum(meters)

	def _get_product_2(self):
		MainParameter = self.env['stock.main.parameter'].get_main_parameter()
		return MainParameter.product_id_2.id or None

	product_id_3 = fields.Many2one('product.product', string='Aceros',  related='lot_id_3.product_id')
	lot_id_3 = fields.Many2one('stock.production.lot', string='Codigo')
	acumulated_meters_3 = fields.Float(compute="_get_acumulated_meters_3", string='Metros Acumulados')
	final_meters_3 = fields.Float(string='Metros Finales')
	product_condition_id_3 = fields.Many2one('product.condition', string='Condicion')

	@api.depends('date_deadline', 'final_meters_3')
	def _get_acumulated_meters_3(self):
		for record in self:
			Tasks = self.env['project.task'].search([
						('date_deadline', '<=', record.date_deadline), 
						('product_id_3', '=', record.product_id_3.id),
						('lot_id_3', '=', record.lot_id_3.id)
					])
			meters = Tasks.mapped('final_meters_3')
			record.acumulated_meters_3 = sum(meters)

	def _get_product_3(self):
		MainParameter = self.env['stock.main.parameter'].get_main_parameter()
		return MainParameter.product_id_3.id or None

	product_id_4 = fields.Many2one('product.product', string='Aceros',  related='lot_id_4.product_id')
	lot_id_4 = fields.Many2one('stock.production.lot', string='Codigo')
	acumulated_meters_4 = fields.Float(compute="_get_acumulated_meters_4", string='Metros Acumulados')
	final_meters_4 = fields.Float(string='Metros Finales')
	product_condition_id_4 = fields.Many2one('product.condition', string='Condicion')

	@api.depends('date_deadline', 'final_meters_4')
	def _get_acumulated_meters_4(self):
		for record in self:
			Tasks = self.env['project.task'].search([
						('date_deadline', '<=', record.date_deadline), 
						('product_id_4', '=', record.product_id_4.id),
						('lot_id_4', '=', record.lot_id_4.id)
					])
			meters = Tasks.mapped('final_meters_4')
			record.acumulated_meters_4 = sum(meters)

	def _get_product_4(self):
		MainParameter = self.env['stock.main.parameter'].get_main_parameter()
		return MainParameter.product_id_4.id or None

	product_id_5 = fields.Many2one('product.product', string='Aceros',  related='lot_id_5.product_id')
	lot_id_5 = fields.Many2one('stock.production.lot', string='Codigo')
	acumulated_meters_5 = fields.Float(compute="_get_acumulated_meters_5", string='Metros Acumulados')
	final_meters_5 = fields.Float(string='Metros Finales')
	product_condition_id_5 = fields.Many2one('product.condition', string='Condicion')

	@api.depends('date_deadline', 'final_meters_5')
	def _get_acumulated_meters_5(self):
		for record in self:
			Tasks = self.env['project.task'].search([
						('date_deadline', '<=', record.date_deadline), 
						('product_id_5', '=', record.product_id_5.id),
						('lot_id_5', '=', record.lot_id_5.id)
					])
			meters = Tasks.mapped('final_meters_5')
			record.acumulated_meters_5 = sum(meters)

	def _get_product_5(self):
		MainParameter = self.env['stock.main.parameter'].get_main_parameter()
		return MainParameter.product_id_5.id or None

	product_id_6 = fields.Many2one('product.product', string='Aceros',  related='lot_id_6.product_id')
	lot_id_6 = fields.Many2one('stock.production.lot', string='Codigo')
	acumulated_meters_6 = fields.Float(compute="_get_acumulated_meters_6", string='Metros Acumulados')
	final_meters_6 = fields.Float(string='Metros Finales')
	product_condition_id_6 = fields.Many2one('product.condition', string='Condicion')

	@api.depends('date_deadline', 'final_meters_6')
	def _get_acumulated_meters_6(self):
		for record in self:
			Tasks = self.env['project.task'].search([
						('date_deadline', '<=', record.date_deadline), 
						('product_id_6', '=', record.product_id_6.id),
						('lot_id_6', '=', record.lot_id_6.id)
					])
			meters = Tasks.mapped('final_meters_6')
			record.acumulated_meters_6 = sum(meters)

	def _get_product_6(self):
		MainParameter = self.env['stock.main.parameter'].get_main_parameter()
		return MainParameter.product_id_6.id or None

	product_id_7 = fields.Many2one('product.product', string='Aceros',  related='lot_id_7.product_id')
	lot_id_7 = fields.Many2one('stock.production.lot', string='Codigo')
	acumulated_meters_7 = fields.Float(compute="_get_acumulated_meters_7", string='Metros Acumulados')
	final_meters_7 = fields.Float(string='Metros Finales')
	product_condition_id_7 = fields.Many2one('product.condition', string='Condicion')

	@api.depends('date_deadline', 'final_meters_7')
	def _get_acumulated_meters_7(self):
		for record in self:
			Tasks = self.env['project.task'].search([
						('date_deadline', '<=', record.date_deadline), 
						('product_id_7', '=', record.product_id_7.id),
						('lot_id_7', '=', record.lot_id_7.id)
					])
			meters = Tasks.mapped('final_meters_7')
			record.acumulated_meters_7 = sum(meters)

	def _get_product_7(self):
		MainParameter = self.env['stock.main.parameter'].get_main_parameter()
		return MainParameter.product_id_7.id or None

	product_id_8 = fields.Many2one('product.product', string='Aceros',  related='lot_id_8.product_id')
	lot_id_8 = fields.Many2one('stock.production.lot', string='Codigo')
	acumulated_meters_8 = fields.Float(compute="_get_acumulated_meters_8", string='Metros Acumulados')
	final_meters_8 = fields.Float(string='Metros Finales')
	product_condition_id_8 = fields.Many2one('product.condition', string='Condicion')

	@api.depends('date_deadline', 'final_meters_8')
	def _get_acumulated_meters_8(self):
		for record in self:
			Tasks = self.env['project.task'].search([
						('date_deadline', '<=', record.date_deadline), 
						('product_id_8', '=', record.product_id_8.id),
						('lot_id_8', '=', record.lot_id_8.id)
					])
			meters = Tasks.mapped('final_meters_8')
			record.acumulated_meters_8 = sum(meters)

	def _get_product_8(self):
		MainParameter = self.env['stock.main.parameter'].get_main_parameter()
		return MainParameter.product_id_8.id or None
	####ACEROS####

	def get_location(self):
		return {
			'name': 'Transferencias',
			'type': 'ir.actions.act_window',
			'res_model': 'stock.picking',
			'view_mode': 'tree, kanban, form, calendar',
			'views': [(self.env.ref('stock.vpicktree').id, 'tree'),
					  (self.env.ref('stock.view_picking_form').id, 'form')],
			'context': {'contact_display': 'partner_address', 
						'default_company_id': self.env.company.id,
						'default_task_id': self.id},
			'domain': [('task_id', '=', self.id)]
		}

	@api.model
	def create(self, vals):
		record = super(ProjectTask, self).create(vals)
		for line in record.timesheet_ids:
			line.unit_amount = line.hour_to - line.hour_from
		return record

	def write(self, vals):
		if 'timesheet_ids' in vals:
			for line in vals['timesheet_ids']:
				if line[2]:
					line[2]['employee_id'] = self.supervisor_id.id
		res = super(ProjectTask, self).write(vals)
		for line in self.timesheet_ids:
			line.unit_amount = line.hour_to - line.hour_from
		return res

	def get_steel_sql(self):
		sql = """
			DROP VIEW IF EXISTS project_steel_report;
			CREATE OR REPLACE VIEW project_steel_report AS (
				select
				row_number() OVER () AS id,
				extract(year from pt.date_deadline)::character varying as year,
				extract(month from pt.date_deadline)::character varying as month,
				pt.date_deadline as date,
				pt.shift,
				coalesce(it.value,me.name) as machine,
				pa.name as area,
				pb.name as block,
				pba.name as bank,
				pw.name as project,
				pd.name as drill_code,
				project_terrain.name as terrain,
				project_type_drill.name as drill_type,
				project_hardness.name as hardness,
				aal.high,
				spl_broca_id.name  as broca_id,
				spl_broca_id.date_vencimiento  as broca_fecha,
				spl_broca_id.note as broca_note,				
				spl_broca_id.metros_total  as broca_metros,

				spl_martillo_id.name  as martillo_id,
				spl_martillo_id.date_vencimiento  as martillo_fecha,
				spl_martillo_id.note as martillo_note,
				spl_martillo_id.metros_total  as martillo_metros,

				spl_pinbox_id.name  as pinbox_id,
				spl_pinbox_id.date_vencimiento  as pinbox_fecha,
				spl_pinbox_id.note as pinbox_note,
				spl_pinbox_id.metros_total  as pinbox_metros,

				spl_chuck_id.name  as chuck_id,
				spl_chuck_id.date_vencimiento  as chuck_fecha,
				spl_chuck_id.metros_total  as chuck_metros,
				spl_chuck_id.note as chuck_note,

				spl_tubo1_id.name  as tubo1_id,
				spl_tubo1_id.date_vencimiento  as tubo1_fecha,
				spl_tubo1_id.note as tubo1_note,
				spl_tubo1_id.metros_total  as tubo1_metros,

				spl_tubo2_id.name  as tubo2_id,
				spl_tubo2_id.date_vencimiento  as tubo2_fecha,
				spl_tubo2_id.note as tubo2_note,
				spl_tubo2_id.metros_total  as tubo2_metros,

				spl_tubo3_id.name  as tubo3_id,
				spl_tubo3_id.date_vencimiento  as tubo3_fecha,
				spl_tubo3_id.note as tubo3_note,
				spl_tubo3_id.metros_total  as tubo3_metros,

				spl_tubo4_id.name  as tubo4_id,
				spl_tubo4_id.date_vencimiento  as tubo4_fecha,
				spl_tubo4_id.note as tubo4_note,
				spl_tubo4_id.metros_total  as tubo4_metros,

				spl_tubo5_id.name  as tubo5_id,
				spl_tubo5_id.date_vencimiento  as tubo5_fecha,
				spl_tubo5_id.note as tubo5_note,
				spl_tubo5_id.metros_total  as tubo5_metros,

				spl_tubo6_id.name  as tubo6_id,
				spl_tubo6_id.date_vencimiento  as tubo6_fecha,
				spl_tubo6_id.note as tubo6_note,
				spl_tubo6_id.metros_total  as tubo6_metros,


				aal.hour_from,
				aal.hour_to,
				case when aal.hour_to - aal.hour_from = 0 then 0 else aal.high/(aal.hour_to - aal.hour_from) end as rop,
				pt.name as task,
				pct.name as contract,

				rp_ru_t.name as usuario_odoo,
				operator.name as operator,
				supervisor.name as supervisor,
				ayudante.name as ayudante,
				aal.details


				from project_task pt
				left join project_contract_type pct on pct.id = pt.contract_type_id
				left join res_users ru on ru.id = pt.user_id
				left join res_partner rp_ru_t on rp_ru_t.id = ru.partner_id
				left join hr_employee operator on operator.id = pt.operator_id
				left join hr_employee supervisor on supervisor.id = pt.supervisor_id
				left join hr_employee ayudante on ayudante.id = pt.helper_id

				left join maintenance_equipment me on me.id = pt.equipment_id

			 left join ir_translation it ON me.id = it.res_id and it.name = 'maintenance.equipment,name' and it.lang = 'es_PE' and it.state = 'translated'
				left join project_area pa on pa.id = pt.area_id
				left join account_analytic_line aal on aal.task_id = pt.id

				left join project_terrain on project_terrain.id = aal.terrain_obj
				left join project_type_drill on project_type_drill.id = aal.drill_type_obj
				left join project_hardness on project_hardness.id = aal.hardness_obj


				left join project_block pb on pb.id = aal.block_id
				left join project_bank pba on pba.id = aal.bank_id
				left join project_work pw on pw.id = aal.project_work_id
				left join project_drill pd on pd.id = aal.drill_id
				left join product_product pp1 on pp1.id = pt.product_id_1
				left join product_template pt1 on pt1.id = pp1.product_tmpl_id
				left join product_condition pc1 on pc1.id = pt.product_condition_id_1
				left join stock_production_lot spl1 on spl1.id = pt.lot_id_1
				left join stock_production_lot spl4 on spl4.id = pt.lot_id_4
				left join stock_production_lot spl5 on spl5.id = pt.lot_id_5
				left join stock_production_lot spl6 on spl6.id = pt.lot_id_6
				left join stock_production_lot spl7 on spl7.id = pt.lot_id_7
				left join stock_production_lot spl8 on spl8.id = pt.lot_id_8
				left join product_product pp2 on pp2.id = pt.product_id_2
				left join product_template pt2 on pt2.id = pp2.product_tmpl_id
				left join product_condition pc2 on pc2.id = pt.product_condition_id_2
				left join stock_production_lot spl2 on spl2.id = pt.lot_id_2
				left join product_product pp3 on pp3.id = pt.product_id_3
				left join product_template pt3 on pt3.id = pp3.product_tmpl_id
				left join product_condition pc3 on pc3.id = pt.product_condition_id_3
				left join stock_production_lot spl3 on spl3.id = pt.lot_id_3

				
				left join stock_production_lot spl_aceros_id on spl_aceros_id.id = aal.aceros_id
				left join stock_production_lot spl_broca_id on spl_broca_id.id = aal.broca_id
				left join stock_production_lot spl_martillo_id on spl_martillo_id.id = aal.martillo_id
				left join stock_production_lot spl_pinbox_id on spl_pinbox_id.id = aal.pinbox_id
				left join stock_production_lot spl_chuck_id on spl_chuck_id.id = aal.chuck_id
				left join stock_production_lot spl_tubo1_id on spl_tubo1_id.id = aal.tubo1_id
				left join stock_production_lot spl_tubo2_id on spl_tubo2_id.id = aal.tubo2_id
				left join stock_production_lot spl_tubo3_id on spl_tubo3_id.id = aal.tubo3_id
				left join stock_production_lot spl_tubo4_id on spl_tubo4_id.id = aal.tubo4_id
				left join stock_production_lot spl_tubo5_id on spl_tubo5_id.id = aal.tubo5_id
				left join stock_production_lot spl_tubo6_id on spl_tubo6_id.id = aal.tubo6_id

				where pt.equipment_id is not null
				and pt.company_id = %d
			)
		""" % self.env.company.id
		return sql

	def get_steel_view(self):
		self._cr.execute(self.get_steel_sql())
		return {
			'name': 'Registro de Aceros',
			'type': 'ir.actions.act_window',
			'res_model': 'project.steel.report',
			'view_mode': 'tree,pivot,graph',
			'views': [(self.env.ref('project_it.project_steel_report_tree').id, 'tree'),
					  (self.env.ref('project_it.project_steel_report_pivot').id, 'pivot'),
					  (self.env.ref('project_it.project_steel_report_graph').id, 'graph')]
		}



	def get_mantenimiento_sql(self):
		sql = """
			DROP VIEW IF EXISTS maintenance_component_report;
			CREATE OR REPLACE VIEW maintenance_component_report AS (
				select
				row_number() OVER () AS id,

				mr.name,
				mr.employee_id,
				mr.equipment_id,
				mr.category_id,
				mr.linea_report,
				mr.request_date,
				mr.maintenance_type,
				mr.maintenance_team_id,
				mr.user_id,
				mr.schedule_date,
				mr.expected_duration,
				mr.duration,
				mr.priority,
				mr.email_cc,
				mr.company_id,

	mr.horometro_planing,
	mr.horometro_real,
	mr.horometro_real_percution,
	mr.type_preventivo,
	mr.type_correctivo,

				mcl.component_id,
				mcl.product_id,
				mcl.lot_id,
				mcl.quantity,
				mcl.notes
				from maintenance_request mr
				left join maintenance_component_line mcl on mcl.request_id = mr.id
				where mr.company_id = %d
			)
		""" % self.env.company.id
		return sql

	def get_mantenimiento_view(self):
		self._cr.execute(self.get_mantenimiento_sql())
		return {
			'name': 'Registro de Mantenimiento',
			'type': 'ir.actions.act_window',
			'res_model': 'maintenance.component.report',
			'view_mode': 'tree,pivot,graph',
			'views': [(self.env.ref('project_it.xmaintenance_request_report_detalle_tree').id, 'tree'),
					  (self.env.ref('project_it.xmaintenance_request_pivotcomponent').id, 'pivot'),
					  (self.env.ref('project_it.xmaintenance_request_graphcomponent').id, 'graph')]
		}
	def get_binnacle_sql(self):
		sql = """
			DROP VIEW IF EXISTS project_binnacle_report;
			CREATE OR REPLACE VIEW project_binnacle_report AS (
				select
				row_number() OVER () AS id,
				extract(year from pt.date_deadline)::character varying as year,
				extract(month from pt.date_deadline)::character varying as month,
				pt.date_deadline as date,
				pct.name as type_contract,
				pa.name as area,
				rpu.name as user_odoo,
				pt.shift,
				heo.name as operador,
				hres.name as supervisor,
				hreh.name as helper,
				coalesce(it.value,me.name) as machine,
				po.name as operation_name,
				po.description as operation_description,
				pb.hour_from,
				pb.hour_to,
				coalesce(pb.hour_to - pb.hour_from,0) as unit_amount,
				pb.observation
				from project_task pt
				left join maintenance_equipment me on me.id = pt.equipment_id
				left join ir_translation it ON me.id = it.res_id and it.name = 'maintenance.equipment,name' and it.lang = 'es_PE' and it.state = 'translated'
				left join project_area pa on pa.id = pt.area_id
				left join project_binnacle pb on pb.project_task_id = pt.id
				left join project_operation po on po.id = pb.operation_id
				left join project_contract_type pct on pt.contract_type_id =pct.id
				left join res_users ruo on pt.user_id =ruo.id
				left join res_partner rpu on ruo.partner_id =rpu.id
				left join hr_employee heo on heo.id = pt.operator_id
				left join hr_employee hres on pt.supervisor_id =hres.id
				left join hr_employee hreh on pt.helper_id =hreh.id
				where pt.equipment_id is not null
				and pt.company_id = %d
			)
		""" % self.env.company.id
		return sql


			 

	def get_binnacle_view(self):
		self._cr.execute(self.get_binnacle_sql())
		return {
			'name': 'Registro de Bitacora',
			'type': 'ir.actions.act_window',
			'res_model': 'project.binnacle.report',
			'view_mode': 'tree,pivot,graph',
			'views': [(self.env.ref('project_it.project_binnacle_report_tree').id, 'tree'),
					  (self.env.ref('project_it.project_binnacle_report_pivot').id, 'pivot'),
					  (self.env.ref('project_it.project_binnacle_report_graph').id, 'graph')]
		}
	def get_hourmeter_sql(self):
		sql = """
			DROP VIEW IF EXISTS project_hourmeter_report;
			CREATE OR REPLACE VIEW project_hourmeter_report AS (
				select
				row_number() OVER () AS id,
				extract(year from pt.date_deadline)::character varying as year,
				extract(month from pt.date_deadline)::character varying as month,
				pt.date_deadline as date,
				pct.name as type_contract,
				pa.name as area,
				rpu.name as user_odoo,
				pt.shift,
				heo.name as operador,
				hres.name as supervisor,
				hreh.name as helper,
				coalesce(it.value,me.name) as machine,

				pt.fuel_hour_from,
				pt.fuel_hour_to,
				pt.fuel_diesel_hour_from,
				pt.fuel_diesel_hour_to,
				pt.refuel_time,
				pt.fuel_qty

				from project_task pt
				left join maintenance_equipment me on me.id = pt.equipment_id
				left join ir_translation it ON me.id = it.res_id and it.name = 'maintenance.equipment,name' and it.lang = 'es_PE' and it.state = 'translated'
				left join project_area pa on pa.id = pt.area_id
				left join project_binnacle pb on pb.project_task_id = pt.id
				left join project_operation po on po.id = pb.operation_id
				left join project_contract_type pct on pt.contract_type_id =pct.id
				left join res_users ruo on pt.user_id =ruo.id
				left join res_partner rpu on ruo.partner_id =rpu.id
				left join hr_employee heo on heo.id = pt.operator_id
				left join hr_employee hres on pt.supervisor_id =hres.id
				left join hr_employee hreh on pt.helper_id =hreh.id
				where pt.equipment_id is not null
				and pt.company_id = %d
			)
		""" % self.env.company.id
		return sql

	def get_hourmeter_view(self):
		self._cr.execute(self.get_hourmeter_sql())
		return {
			'name': 'Registro de Horometro',
			'type': 'ir.actions.act_window',
			'res_model': 'project.hourmeter.report',
			'view_mode': 'tree,pivot,graph',
			'views': [(self.env.ref('project_it.project_hourmeter_report_tree').id, 'tree'),
					  (self.env.ref('project_it.project_hourmeter_report_pivot').id, 'pivot'),
					  (self.env.ref('project_it.project_hourmeter_report_graph').id, 'graph')]
		}

	def get_time_sql(self):
		sql = """
			DROP VIEW IF EXISTS project_time_report;
			CREATE OR REPLACE VIEW project_time_report AS (
				select
				row_number() OVER () AS id,
				extract(year from pt.date_deadline)::character varying as year,
				extract(month from pt.date_deadline)::character varying as month,
				pt.date_deadline as date,
				pt.shift,
				pct.name as type_contract,
				rpu.name as user_odoo,
				coalesce(it.value,me.name) as machine,
				heo.name as operator,
				heh.name as helper,
				hes.name as supervisor,
				pa.name as area,
				--pb.name as block,
				--pba.name as bank,
				--pw.name as project,
				''::varchar as block,
				''::varchar as bank,
				''::varchar as project,
				pt.effective_hours,
				pt.drills,
				pt.highs,
				pt.fuel_hour_from,
				pt.fuel_hour_to,
				pt.refuel_time,
				pt.fuel_qty,
				pj.name as project_work,
				pt.name as task,
				pct.name as contract



				from project_task pt
				left join project_contract_type pct on pct.id = pt.contract_type_id
				left join project_project pj on pj.id = pt.project_id 
				left join maintenance_equipment me on me.id = pt.equipment_id
				left join ir_translation it ON me.id = it.res_id and it.name = 'maintenance.equipment,name' and it.lang = 'es_PE' and it.state = 'translated'
				left join hr_employee heo on heo.id = pt.operator_id
				left join hr_employee hes on hes.id = pt.supervisor_id
				left join hr_employee heh on heh.id = pt.helper_id
				left join project_area pa on pa.id = pt.area_id
				left join res_users ruo on pt.user_id =ruo.id
				left join res_partner rpu on ruo.partner_id =rpu.id				
				--left join project_block pb on pb.id = pt.block_id
				--left join project_bank pba on pba.id = pt.bank_id
				--left join project_work pw on pw.id = pt.project_work_id
				
				where pt.equipment_id is not null
				and pt.company_id = %d
			)
		""" % self.env.company.id
		return sql

	def get_time_view(self):
		self._cr.execute(self.get_time_sql())
		return {
			'name': 'Registro de Tiempos',
			'type': 'ir.actions.act_window',
			'res_model': 'project.time.report',
			'view_mode': 'tree,pivot,graph',
			'views': [(self.env.ref('project_it.project_time_report_tree').id, 'tree'),
					  (self.env.ref('project_it.project_time_report_pivot').id, 'pivot'),
					  (self.env.ref('project_it.project_time_report_graph').id, 'graph')]
		}


class project_terrain(models.Model):
	_name = 'project.terrain'

	name = fields.Char('Nombre')
	active = fields.Boolean('Activo',default=True)

class project_type_drill(models.Model):
	_name = 'project.type.drill'

	name = fields.Char('Nombre')
	active = fields.Boolean('Activo',default=True)

class project_hardness(models.Model):
	_name = 'project.hardness'

	name = fields.Char('Nombre')
	active = fields.Boolean('Activo',default=True)

class AccountAnalyticLine(models.Model):
	_inherit = 'account.analytic.line'

	name = fields.Char(default='Descripcion')
	employee_id = fields.Many2one(string='Supervisor')
	operator_id = fields.Many2one('hr.employee', related='task_id.operator_id', string='Operador', store=True)
	helper_id = fields.Many2one('hr.employee', related='task_id.helper_id', string='Ayudante', store=True)
	block_id = fields.Many2one('project.block', related=False, string='Tajo', store=True)
	bank_id = fields.Many2one('project.bank', related=False, string='Banco', store=True)
	project_work_id = fields.Many2one('project.work', string='Proyecto')
	area_id = fields.Many2one('project.area', related='task_id.area_id', string='Area', store=True)
	equipment_id = fields.Many2one('maintenance.equipment', related='task_id.equipment_id', string='Taladro', store=True)
	drill_id = fields.Many2one('project.drill', string='Taladro')


	terrain_obj = fields.Many2one('project.terrain','Terreno')
	drill_type_obj = fields.Many2one('project.type.drill','Tipo Taladro')
	hardness_obj = fields.Many2one('project.hardness','Dureza')


	terrain = fields.Selection([('1', 'R'),
								('2', 'F'),
								('3', 'V'),
								('4', 'A'),
								('5', 'C')], string='Terreno')
	drill_type = fields.Selection([('1', 'P'),
								   ('2', 'PC'),
								   ('3', 'B1'),
								   ('4', 'B2'),
								   ('5', 'PS'),
								   ('6', 'EX'),
								   ('7', 'HR'),
								   ('8', 'VR')], string='Tipo Taladro')
	hardness = fields.Selection([('1', 'S'),
								 ('2', 'M'),
								 ('3', 'D')], string='Dureza')
	high = fields.Float(string='Altura')
	hour_from = fields.Float(string='Hora Ini')
	hour_to = fields.Float(string='Hora Fin')
	details = fields.Text(string='Observaciones')




	aceros_id = fields.Many2one('stock.production.lot', string='Aceros')

	broca_id = fields.Many2one('stock.production.lot', string='Broca')

	martillo_id = fields.Many2one('stock.production.lot', string='Martillo')

	pinbox_id = fields.Many2one('stock.production.lot', string='Pinbox')

	chuck_id = fields.Many2one('stock.production.lot', string='Chuck')

	tubo1_id = fields.Many2one('stock.production.lot', string='Tubo1')

	tubo2_id = fields.Many2one('stock.production.lot', string='Tubo2')

	tubo3_id = fields.Many2one('stock.production.lot', string='Tubo3')

	tubo4_id = fields.Many2one('stock.production.lot', string='Tubo4')

	tubo5_id = fields.Many2one('stock.production.lot', string='Tubo5')

	tubo6_id = fields.Many2one('stock.production.lot', string='Tubo6')





class ProductCondition(models.Model):
	_name = 'product.condition'

	name = fields.Char(string='Nombre', required=True)
	code = fields.Char(string='Codigo')
	product_id = fields.Many2one('product.product', string='Acero', required=True)

class ProjectBlock(models.Model):
	_name = 'project.block'

	name = fields.Char(string='Nombre', required=True)
	active = fields.Boolean('Activo',default=True)

class ProjectBank(models.Model):
	_name = 'project.bank'

	name = fields.Char(string='Nombre', required=True)
	active = fields.Boolean('Activo',default=True)

class ProjectArea(models.Model):
	_name = 'project.area'

	name = fields.Char(string='Nombre', required=True)
	active = fields.Boolean('Activo',default=True)

class ProjectWork(models.Model):
	_name = 'project.work'

	name = fields.Char(string='Nombre', required=True)
	active = fields.Boolean('Activo',default=True)

class ProjectDrill(models.Model):
	_name = 'project.drill'

	name = fields.Char(string='Nombre', required=True)
	code = fields.Char(string='Codigo')
	active = fields.Boolean('Activo',default=True)

class ProjectContractType(models.Model):
	_name = 'project.contract.type'

	name = fields.Char(string='Nombre', required=True)
	amount_by_drill = fields.Float(string='Monto por metro de Taladro')
	active = fields.Boolean('Activo',default=True)

class MaintenanceEquipmentType(models.Model):
	_name = 'maintenance.equipment.type'

	name = fields.Char(string='Nombre', required=True)
	active = fields.Boolean('Activo',default=True)

class ProjectBinnacle(models.Model):
	_name = 'project.binnacle'

	project_task_id = fields.Many2one('project.task')
	operation_id = fields.Many2one('project.operation', string='Codigo de Operacion')
	hour_from = fields.Float(string='Hora Ini')
	hour_to = fields.Float(string='Hora Fin')
	unit_amount = fields.Float(string=u'Duración (Horas)', compute='_get_difference')
	observation=fields.Text(string='Observaciones')

	@api.depends('unit_amount')
	def _get_difference(self):
		for record in self:
			record.unit_amount = record.hour_to - record.hour_from

class ProjectOperation(models.Model):
	_name = 'project.operation'

	name = fields.Char(string='Codigo')
	description = fields.Char(string='Description', required=True)


class MaintenanceRequestPreventivo(models.Model):
	_name = 'maintenance.request.preventivo'

	name = fields.Char('Tipo Preventivo',required=True)
	active = fields.Boolean('Activo',default=True)

class MaintenanceRequestCorrectivo(models.Model):
	_name = 'maintenance.request.correctivo'

	name = fields.Char('Tipo Correctivo',required=True)
	active = fields.Boolean('Activo',default=True)

class MaintenanceRequest(models.Model):
	_inherit = 'maintenance.request'

	type_preventivo = fields.Many2one('maintenance.request.preventivo','Tipo Preventivo')
	type_correctivo = fields.Many2one('maintenance.request.correctivo','Tipo Correctivo')
	horometer_percusion_final = fields.Float('Horometro Final Percusion',compute="get_horometer_perdie")
	horometer_diesel_final = fields.Float('Horometro Final Diesel',compute="get_horometer_perdie")
	correlativo = fields.Char('Correlativo')

	def get_horometer_perdie(self):
		for i in self:
			t1= 0
			t2= 0
			if i.equipment_id.id:
				tareas = self.env['project.task'].search([('equipment_id','=',i.equipment_id.id),('date_deadline','<=',i.request_date)]).sorted(lambda m: m.date_deadline )
				if len(tareas)>0:
					t1 = tareas[-1].fuel_diesel_hour_to
					t2 = tareas[-1].fuel_hour_to

			i.horometer_diesel_final = t1
			i.horometer_percusion_final = t2


	@api.model
	def create(self,vals):
		id_seq = self.env['ir.sequence'].search([('name','=','Mantenimiento Secuenciador')], limit=1)        
		if not id_seq:
			id_seq = self.env['ir.sequence'].create({'name':'Mantenimiento Secuenciador','implementation':'no_gap','active':True,'prefix':'Mant-','padding':6,'number_increment':1,'number_next_actual' :1})
		vals['correlativo'] = id_seq._next()
		t = super(MaintenanceRequest,self).create(vals)
		return t
