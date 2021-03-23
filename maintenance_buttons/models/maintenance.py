# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch, landscape
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT, TA_LEFT
import base64

class reporte_template_name(models.Model):
	_name = 'reporte.template.name'

	name = fields.Char('Nombre de Items',required=True)
	code = fields.Char('Codigo de Referencia')

class MaintenanceRequest(models.Model):
	_inherit = 'maintenance.request'

	hoja_servicio = fields.Many2one('formato.maintenance.request','Hoja de Servicio')
	purchase_order_ids = fields.One2many('purchase.order', 'maintenance_request_id', string='Compras')
	purchase_count = fields.Integer(compute='_compute_purchase_count')
	stock_picking_ids = fields.One2many('stock.picking', 'maintenance_request_id', string='Almacenes')
	picking_count = fields.Integer(compute='_compute_picking_count')

	hoja_count = fields.Integer(compute='get_hoja_servicio')
	linea_report = fields.Many2one('maintenance.request.category.type.report','Tipo de Reporte')

	stage_name = fields.Char(related='stage_id.name')
	expected_duration = fields.Float(string='Duracion Prevista')

	horometro_planing = fields.Float('Horometro Motor Planeado')
	horometro_real = fields.Float('Horometro Motor Real')
	horometro_real_percution = fields.Float('Horometro Percusion Real')
	analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta Analitica')
	component_lines = fields.One2many('maintenance.component.line', 'request_id')

	def print_format(self):
		MainParameter = self.env['main.parameter'].search([('company_id', '=', self.company_id.id)], limit=1)
		Sheet = self.hoja_servicio
		Equipment = self.equipment_id
		if not MainParameter.dir_create_file:
			raise UserError(u'No existe un Directorio de Descarga configurado en Parametros Principales de Contabilidad para su Compañía')
		doc = SimpleDocTemplate(MainParameter.dir_create_file + '%s.pdf' % Sheet.name, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=20)
		elements = []
		ReportBase = self.env['report.base']
		style_title_16 = ParagraphStyle(name='Title', alignment=TA_CENTER, fontSize=14, fontName="times-roman")
		style_title = ParagraphStyle(name='Title', alignment=TA_CENTER, fontSize=12, fontName="times-roman")
		style_center = ParagraphStyle(name='Center', alignment=TA_CENTER, fontSize=8, fontName="times-roman")
		style_right = ParagraphStyle(name='Right', alignment=TA_RIGHT, fontSize=8, fontName="times-roman")
		style_left = ParagraphStyle(name='Left', alignment=TA_LEFT, fontSize=8, fontName="times-roman")
		style_left_tab = ParagraphStyle(name='Left Tab', alignment=TA_LEFT, fontSize=8, fontName="times-roman", leftIndent=20)
		internal_width = [2.5 * cm]
		bg_color = '#E5C338'
		spacer = Spacer(5, 20)

		global_format = [
			('ALIGN', (0, 0), (0, 0), 'LEFT'),
			('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
			('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
			('BOX', (0, 0), (-1, -1), 0.25, colors.black)
		]

		elements = []
		I = ReportBase.create_image(self.env.company.logo, MainParameter.dir_create_file + 'logo.jpg', 130.0, 32.0)
		data = [[I if I else '',
				Paragraph('<strong>HOJA DE SERVICIO DE MANTENIMIENTO PREVENTIVO<br/>\
							PERFORADORA ROC - DRILL %s</strong>' % Equipment.name, style_title),
				Paragraph('%s Hrs.' % Sheet.name.split(' ')[1], style_title_16)]
				]
		t = Table(data, [5 * cm, 12 * cm, 3 * cm])
		t.setStyle(TableStyle(global_format))
		elements.append(t)
		data = [
				[Paragraph('<strong>OBRA:</strong>', style_left), Paragraph(self.name or '', style_left),
				 Paragraph('<strong>CODIGO DE EQUIPO:</strong>', style_left), Paragraph(Equipment.code_equipment or '', style_left)],
				[Paragraph('<strong>FECHA:</strong>', style_left), Paragraph(str(self.request_date) if self.request_date else '', style_left),
				 Paragraph('<strong>HOROMETRO MOTOR:</strong>', style_left), Paragraph(str(self.horometro_real or ''), style_left)],
				['', '', Paragraph('<strong>HOROMETRO PERCUSION:</strong>', style_left), Paragraph(str(self.horometro_real_percution or ''), style_left)],
				[Paragraph('* Todo trabajo de reparación requiere el bloqueo de la máquina<br/>\
							* Todo bloqueo es individual y se hace en la llave de corte general de energía.<br/>\
							* El aceite caliente puede causar daños severos a la piel.', style_left_tab), '', '', ''],
		]
		t = Table(data, [3 * cm, 7 * cm, 5 * cm, 5 * cm])
		t.setStyle(TableStyle([
			('ALIGN', (0, 0), (-1, -1), 'CENTER'),
			('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
			('BOX', (0, 0), (-1, -1), 0.25, colors.black),
			('SPAN', (0, 3), (3, 3)),
		]))
		elements.append(t)

		data = [
				[Paragraph('<strong>SERVICIO A EJECUTAR</strong>', style_center), '', Paragraph('<strong>SI</strong>', style_center),
				 Paragraph('<strong>NO</strong>', style_center), Paragraph('<strong>OBSERVACIONES</strong>', style_center)],
		]
		aux_format = [
			('ALIGN', (0, 0), (-1, -1), 'CENTER'),
			('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
			('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
			('BOX', (0, 0), (-1, -1), 0.25, colors.black),
			('SPAN', (0, 0), (1, 0))
		]
		for c, line in enumerate(Sheet.detalle_ids, 1):
			if line.display_type == 'line_section':
				data.append([Paragraph(line.name.name, style_center), '', '', '', ''])
				aux_format.append(('SPAN', (0, c), (4, c)))
				aux_format.append(('BACKGROUND', (0, c), (4, c), bg_color))
			else:
				data.append([
						Paragraph(str(line.order or ''), style_center),
						Paragraph(line.name.name or '', style_left),
						Paragraph('X' if line.valor == 'si' else '', style_left),
						Paragraph('X' if line.valor == 'no' else '', style_left),
						Paragraph(line.description or '', style_left)
					]
				)
		t = Table(data, [1 * cm, 10 * cm, 1 * cm, 1 * cm, 7 * cm])
		t.setStyle(TableStyle(aux_format))
		elements.append(t)
		elements.append(PageBreak())

		data = [
				[Paragraph('<strong>OBSERVACIONES</strong>', style_center)],
				[Paragraph(self.description or '', style_left)]
		]
		t = Table(data, [20 * cm])
		t.setStyle(TableStyle([
			('ALIGN', (0, 0), (-1, -1), 'CENTER'),
			('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
			('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
			('BOX', (0, 0), (-1, -1), 0.25, colors.black),
			('BACKGROUND', (0, 0), (0, 0), bg_color)
		]))
		elements.append(t)
		elements.append(spacer)

		data = [
				[Paragraph('<strong>__________________________<br/>NOMBRE TEC. RESPONSABLE</strong>', style_center),
				 Paragraph('<strong>__________________________<br/>FIRMA TEC. RESPONSABLE</strong>', style_center)],
		]

		t = Table(data, [10 * cm, 10 * cm])
		t.setStyle(TableStyle([
			('ALIGN', (0, 0), (-1, -1), 'CENTER'),
			('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
		]))
		elements.append(t)
		elements.append(spacer)

		data = [
				[Paragraph('<strong>__________________________<br/>FIRMA OPERADOR</strong>', style_center),
				 Paragraph('<strong>__________________________<br/>FIRMA SUPERVISOR</strong>', style_center),
				 Paragraph('<strong>__________________________<br/>FIRMA JEFE MANTTO</strong>', style_center)]
		]
		t = Table(data, [7 * cm, 7 * cm, 6 * cm])
		t.setStyle(TableStyle([
			('ALIGN', (0, 0), (-1, -1), 'CENTER'),
			('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
		]))
		elements.append(t)

		doc.build(elements)
		f = open(MainParameter.dir_create_file + '%s.pdf' % Sheet.name, 'rb')
		return self.env['popup.it'].get_file('%s.pdf' % Sheet.name,base64.encodestring(b''.join(f.readlines())))

	def get_hoja_servicio(self):
		for record in self:
			record.hoja_count = 1 if record.hoja_servicio.id else 0
	

	def get_report(self):
		self.ensure_one()
		if self.hoja_servicio.id:
			pass
		else:
			if self.linea_report.formato_id.id:
				hoja = self.env['formato.maintenance.request'].create({'name':self.linea_report.formato_id.name})
				for i in self.linea_report.formato_id.detalle_ids:
					linea = self.env['formato.maintenance.request.line'].create({
						'formato_id':hoja.id,
						'sequence': i.sequence,
						'name': i.name.id,
						'valor': False,
						'display_type': i.display_type,
						})
				self.hoja_servicio = hoja.id
		return {
			"type": "ir.actions.act_window",
			"res_model": "formato.maintenance.request",
			"views": [[False, "form"]],
			"res_id": self.hoja_servicio.id,
			"name": "Hoja de Servicio",
		}

	def _compute_purchase_count(self):
		for record in self:
			record.purchase_count = len(self.purchase_order_ids)
	
	def _compute_picking_count(self):
		for record in self:
			record.picking_count = len(self.stock_picking_ids)

	def get_maintenance_purchases(self):
		self.ensure_one()
		return {
			"type": "ir.actions.act_window",
			"res_model": "purchase.order",
			"views": [[False, "tree"], [False, "form"]],
			"domain": [['id', 'in', self.purchase_order_ids.ids]],
			"name": "Pedidos de compra",
			"context": {'default_maintenance_request_id': self.id}
		}

	def get_maintenance_pickings(self):
		self.ensure_one()
		return {
			"type": "ir.actions.act_window",
			"res_model": "stock.picking",
			"views": [[False, "tree"], [False, "form"]],
			"domain": [['id', 'in', self.stock_picking_ids.ids]],
			"name": "Transferencias",
			"context": {'default_maintenance_request_id': self.id}
		}

class formato_maintenance_request(models.Model):
	_name = 'formato.maintenance.request'

	name = fields.Char('Formato de Reporte',copy=True)
	detalle_ids = fields.One2many('formato.maintenance.request.line','formato_id','Detalle',copy=True)

class formato_maintenance_request_line(models.Model):
	_name = 'formato.maintenance.request.line'

	formato_id = fields.Many2one('formato.maintenance.request','Formato')
	sequence = fields.Integer('Secuencia')
	order = fields.Integer('Nro. Orden')
	name = fields.Many2one('reporte.template.name','Nombre',copy=True)	
	valor = fields.Selection([('si','Si'),('no','No')],'Si/No',default='no')
	description = fields.Text('Descripcion')
	display_type = fields.Selection([('line_section', 'Section')], default=False, help="Technical field for UX purpose.")


class formato_maintenance_request_template(models.Model):
	_name = 'formato.maintenance.request.template'

	name = fields.Char('Formato de Reporte',copy=True)
	code = fields.Char('Codigo')
	detalle_ids = fields.One2many('formato.maintenance.request.line.template','formato_id','Detalle',copy=True)


class formato_maintenance_request_line_template(models.Model):
	_name = 'formato.maintenance.request.line.template'

	formato_id = fields.Many2one('formato.maintenance.request.template','Formato')
	sequence = fields.Integer('Secuencia')
	name = fields.Many2one('reporte.template.name','Nombre',copy=True)	
	display_type = fields.Selection([('line_section', 'Section')], default=False, help="Technical field for UX purpose.")





class maintenance_request_category_type_report(models.Model):
	_name = 'maintenance.request.category.type.report'

	_rec_name = 'formato_id'
	category_id = fields.Many2one('maintenance.equipment.category','Categoria')
	formato_id = fields.Many2one('formato.maintenance.request.template','Formato')


class maintenance_equipment(models.Model):
	_inherit = 'maintenance.equipment'

	code_equipment = fields.Char('Codigo de Equipo')


class maintenance_equipment_category(models.Model):
	_inherit = 'maintenance.equipment.category'

	tipo_mantenimiento = fields.One2many('maintenance.request.category.type.report','category_id','Tipo de Mantenimiento')



class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	maintenance_request_id = fields.Many2one('maintenance.request')

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	maintenance_request_id = fields.Many2one('maintenance.request')


class MaintenanceEquipment(models.Model):
	_inherit = 'maintenance.equipment'

	horometer_line_ids = fields.One2many('horometer.line', 'equipment_id')

	def get_horometer_lines(self):
		self.horometer_line_ids.unlink()
		Tasks = self.env['project.task'].search([('equipment_id', '=', self.id)])
		for task in Tasks:
			self.env['horometer.line'].create({
										'equipment_id': self.id,
										'date': task.date_deadline,
										'fuel_hour_from': task.fuel_hour_from,
										'fuel_hour_to': task.fuel_hour_to,
										'refuel_time': task.refuel_time,
										'fuel_qty': task.fuel_qty
										})

class HorometerLine(models.Model):
	_name = 'horometer.line'

	equipment_id = fields.Many2one('maintenance.equipment', ondelete="cascade")
	date = fields.Date(string='Fecha')
	fuel_hour_from = fields.Float(string='Hora Inicial')
	fuel_hour_to = fields.Float(string='Hora Final')
	percution_hour_from = fields.Float(string='Hora Ini Percusion')
	percution_hour_to = fields.Float(string='Hora Fin Percusion')
	diesel_hour_from = fields.Float(string='Hora Ini Diesel')
	diesel_hour_to = fields.Float(string='Hora Fin Diesel')
	refuel_time = fields.Float(string='Horometro Abast')
	fuel_qty = fields.Float(string='Combustible')

class MaintenanceComponentLine(models.Model):
	_name = 'maintenance.component.line'

	request_id = fields.Many2one('maintenance.request')
	component_id = fields.Many2one('maintenance.component', string='Componente')
	product_id = fields.Many2one('product.product', string='Producto')
	lot_id = fields.Many2one('stock.production.lot', string='Codigo')
	quantity = fields.Float('Cantidad')
	notes = fields.Char(string='Observaciones')

class MaintenanceComponent(models.Model):
	_name = 'maintenance.component'

	name = fields.Char(string='Nombre')
