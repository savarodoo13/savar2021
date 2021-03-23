# -*- coding: utf-8 -*-
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import time
import odoo.addons.decimal_precision as dp
from openerp.osv import osv
import base64
from odoo import models, fields, api
import codecs

values = {}


class contenedor_kardex_valorado_owm(models.Model):
	_name = 'contenedor.kardex.valorado.owm'
	_auto = False

	fecha_registro = fields.Date('Fecha Registro')
	type_doc = fields.Char('Tipo Documento')
	serial = fields.Char('Serie')
	nro = fields.Char('Numero')
	numdoc_cuadre = fields.Char('Nro. Cuadre')
	doc_partner = fields.Char('Doc. Partner')
	name = fields.Char('Partner')
	operation_type = fields.Char('Tipo Operacion')
	name_template = fields.Char('Producto')
	default_code = fields.Char('Cod. Producto')
	unidad = fields.Char('Unidad')
	ingreso = fields.Float('Ingreso Cantidad')
	debit = fields.Float('Costo Ingreso')
	salida = fields.Float('Salida Cantidad')
	credit = fields.Float('Costo Salida')
	saldof = fields.Float('Saldo Cantidad')
	saldov = fields.Float('Costo Saldo')
	cadquiere = fields.Float('Precio Adquicision')
	cprom = fields.Float('Costo Promedio')
	origen = fields.Char('Origen')
	destino = fields.Char('Destino')
	almacen = fields.Char('Almacen')
	prioridad_it = fields.Char('Prioridad')
	observacion_it = fields.Char('Observacion')
	trabajador_it = fields.Char('Trabajador')
	analytic_account_id = fields.Char('Cuenta Analitica')
	equipo = fields.Char('Equipo')


class product_marca(models.Model):
	_name = 'product.marca'

	name = fields.Char('Marca')

class product_template(models.Model):
	_inherit = 'product.template'

	marca_id = fields.Many2one('product.marca','Marca')


class make_kardex_valorado(models.TransientModel):
	_inherit = "make.kardex.valorado"

	check_account = fields.Boolean('Mostrar Cuentas Contables',default=False)

	def do_csvtoexcel(self):
		cad = ""

		s_prod = [-1,-1,-1]
		s_loca = [-1,-1,-1]
		if self.alllocations == True:
			locat_ids = self.env['stock.location'].search( [('usage','in',('internal','inventory','transit','procurement','production'))] )
			lst_locations = locat_ids.ids
		else:
			lst_locations = self.location_ids.ids
		lst_products  = self.products_ids.ids
		productos='{'
		almacenes='{'
		date_ini=self.fini
		date_fin=self.ffin
		if self.allproducts:
			lst_products = self.env['product.product'].with_context(active_test=False).search([]).ids

		else:
			lst_products = self.products_ids.ids

		if len(lst_products) == 0:
			raise osv.except_osv('Alerta','No existen productos seleccionados')

		for producto in lst_products:
			productos=productos+str(producto)+','
			s_prod.append(producto)
		productos=productos[:-1]+'}'
		for location in lst_locations:
			almacenes=almacenes+str(location)+','
			s_loca.append(location)
		almacenes=almacenes[:-1]+'}'



		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		workbook = Workbook(direccion +'kardex_producto.xlsx')
		worksheet = workbook.add_worksheet("Kardex")
		bold = workbook.add_format({'bold': True})
		bold.set_font_size(8)
		normal = workbook.add_format()
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=2)
		boldbord.set_align('center')
		boldbord.set_align('vcenter')
		boldbord.set_text_wrap()
		boldbord.set_font_size(8)
		boldbord.set_bg_color('#DCE6F1')

		especial1 = workbook.add_format({'bold': True})
		especial1.set_align('center')
		especial1.set_align('vcenter')
		especial1.set_text_wrap()
		especial1.set_font_size(15)

		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'0.00'})
		numberseis = workbook.add_format({'num_format':'0.000000'})
		numberseis.set_font_size(8)
		numberocho = workbook.add_format({'num_format':'0.00000000'})
		numberocho.set_font_size(8)
		bord = workbook.add_format()
		bord.set_border(style=1)
		bord.set_font_size(8)
		numberdos.set_border(style=1)
		numberdos.set_font_size(8)
		numbertres.set_border(style=1)
		numberseis.set_border(style=1)
		numberocho.set_border(style=1)
		numberdosbold = workbook.add_format({'num_format':'0.00','bold':True})
		numberdosbold.set_font_size(8)

		formatdate = workbook.add_format({'num_format': 'dd-mm-yyyy hh:mm'})
		x= 10
		tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tam_letra = 1.2


		worksheet.merge_range(1,5,1,10, "KARDEX VALORADO", especial1)
		worksheet.write(2,0,'FECHA INICIO:',bold)
		worksheet.write(3,0,'FECHA FIN:',bold)

		worksheet.write(2,1,str(self.fini))
		worksheet.write(3,1,str(self.ffin))			
		import datetime		

		#worksheet.merge_range(8,0,9,0, u"Fecha Alm.",boldbord)
		worksheet.merge_range(8,1,9,1, u"Fecha",boldbord)
		worksheet.merge_range(8,2,9,2, u"Tipo",boldbord)
		worksheet.merge_range(8,3,9,3, u"Serie",boldbord)
		worksheet.merge_range(8,4,9,4, u"Número",boldbord)

		worksheet.merge_range(8,5,9,5, u"Doc. Almacen",boldbord)
		worksheet.merge_range(8,6,9,6, u"RUC",boldbord)
		worksheet.merge_range(8,7,9,7, u"Empresa",boldbord)

		worksheet.merge_range(8,8,9,8, u"T. OP.",boldbord)

		worksheet.merge_range(8,9,9,9, u"Producto",boldbord)
		worksheet.merge_range(8,10,9,10, u"Codigo Producto",boldbord)				
		worksheet.merge_range(8,11,9,11, u"Unidad",boldbord)
			
		worksheet.merge_range(8,12,8,13, u"Ingreso",boldbord)
		worksheet.write(9,12, "Cantidad",boldbord)
		worksheet.write(9,13, "Costo",boldbord)
		worksheet.merge_range(8,14,8,15, u"Salida",boldbord)
		worksheet.write(9,14, "Cantidad",boldbord)
		worksheet.write(9,15, "Costo",boldbord)
		worksheet.merge_range(8,16,8,17, u"Saldo",boldbord)
		worksheet.write(9,16, "Cantidad",boldbord)
		worksheet.write(9,17, "Costo",boldbord)

		worksheet.merge_range(8,18,9,18, u"Costo Adquisición",boldbord)
		worksheet.merge_range(8,19,9,19, "Costo Promedio",boldbord)

		worksheet.merge_range(8,20,9,20, "Ubicacion Origen",boldbord)
		worksheet.merge_range(8,21,9,21, "Ubicacion Destino",boldbord)
		worksheet.merge_range(8,22,9,22, "Almacen",boldbord)


		worksheet.merge_range(8,23,9,23, u"Categoria de Producto",boldbord)
		worksheet.merge_range(8,24,9,24, u"Marca",boldbord)
		worksheet.merge_range(8,25,9,25, u"Guia de Remision",boldbord)
		worksheet.merge_range(8,26,9,26, u"Orden de Compra",boldbord)
		worksheet.merge_range(8,27,9,27, u"Empleado",boldbord)
		worksheet.merge_range(8,28,9,28, u"Glosa",boldbord)



		worksheet.merge_range(8,29,9,29, u"Prioridad",boldbord)
		worksheet.merge_range(8,30,9,30, u"Observacion",boldbord)
		worksheet.merge_range(8,31,9,31, u"Trabajador",boldbord)

		if self.check_account:
			worksheet.merge_range(8,32,9,32, u"Cuenta Valuación",boldbord)
			worksheet.merge_range(8,33,9,33, u"Cuenta Salida",boldbord)
			worksheet.merge_range(8,34,9,34, u"Cuenta Analítica",boldbord)
			worksheet.merge_range(8,35,9,35, u"Etiqueta Analítica",boldbord)

		self.env.cr.execute("""
				 select 

				fecha_albaran as "Fecha Alb.",	
				fecha::date as "Fecha",
				type_doc as "T. Doc.",
				serial as "Serie",
				nro as "Nro. Documento",
				numdoc_cuadre as "Nro. Documento",
				doc_partner as "Nro Doc. Partner",
				name as "Proveedor",							
				operation_type as "Tipo de operacion",				 
				name_template as "Producto",
				default_code as "Cod Producto",
				unidad as "Unidad",				 
				ingreso as "Ingreso Fisico",
				round(debit,6) as "Ingreso Valorado.",
				salida as "Salida Fisico",
				round(credit,6) as "Salida Valorada",
				saldof as "Saldo Fisico",
				round(saldov,6) as "Saldo valorado",
				round(cadquiere,6) as "Costo adquisicion",
				round(cprom,6) as "Costo promedio",
					origen as "Origen",
					destino as "Destino",
				almacen AS "Almacen",
				stock_moveid as "id move"
				from get_kardex_v("""+ str(date_ini).replace('-','') + "," + str(date_fin).replace('-','') + ",'" + productos + """'::INT[], '""" + almacenes + """'::INT[],"""+str(self.env.company.id)+""")
				
		""")

		ingreso1= 0
		ingreso2= 0
		salida1= 0
		salida2= 0

		for line in self.env.cr.fetchall():
			#worksheet.write(x,0,line[0] if line[0] else '' ,formatdate )
			worksheet.write(x,1,line[1] if line[1] else '' ,formatdate )
			worksheet.write(x,2,line[2] if line[2] else '' ,bord )
			worksheet.write(x,3,line[3] if line[3] else '' ,bord )
			worksheet.write(x,4,line[4] if line[4] else '' ,bord )
			worksheet.write(x,5,line[5] if line[5] else '' ,bord )
			worksheet.write(x,6,line[6] if line[6] else '' ,bord )
			worksheet.write(x,7,line[7] if line[7] else '' ,bord )
			worksheet.write(x,8,line[8] if line[8] else '' ,bord )
			worksheet.write(x,9,line[9] if line[9] else '' ,bord )
			worksheet.write(x,10,line[10] if line[10] else '' ,bord )
			worksheet.write(x,11,line[11] if line[11] else '' ,bord )
			
			worksheet.write(x,12,line[12] if line[12] else 0 ,numberdos )
			worksheet.write(x,13,line[13] if line[13] else 0 ,numberdos )
			worksheet.write(x,14,line[14] if line[14] else 0 ,numberdos )
			worksheet.write(x,15,line[15] if line[15] else 0 ,numberdos )
			worksheet.write(x,16,line[16] if line[16] else 0 ,numberdos )
			worksheet.write(x,17,line[17] if line[17] else 0 ,numberseis )
			worksheet.write(x,18,line[18] if line[18] else 0 ,numberocho )
			worksheet.write(x,19,line[19] if line[19] else 0 ,numberocho )

			worksheet.write(x,20,line[20] if line[20] else '' ,bord )
			worksheet.write(x,21,line[21] if line[21] else '' ,bord )
			worksheet.write(x,22,line[22] if line[22] else '' ,bord )

			move = self.env['stock.move'].browse(line[23])

			worksheet.write(x,23,move.product_id.categ_id.name if move.product_id.categ_id.name else ''  ,bord )
			worksheet.write(x,24,move.product_id.marca_id.name if move.product_id.marca_id.name else '' ,bord )
			worksheet.write(x,25,move.picking_id.numberg if move.picking_id.numberg else '' ,bord )
			worksheet.write(x,26,move.picking_id.origin if move.picking_id.origin else '' ,bord )
			worksheet.write(x,27,move.picking_id.empleado_resp_id.name if move.picking_id.empleado_resp_id.name else '' ,bord )
			worksheet.write(x,28,move.name if move.name else '' ,bord )


			worksheet.write(x,29,move.prioridad_it if move.prioridad_it else '' ,bord )
			worksheet.write(x,30,move.observacion_it if move.observacion_it else '' ,bord )
			worksheet.write(x,31,move.trabajador_it if move.trabajador_it else '' ,bord )

			if self.check_account:
				if move.id:
					worksheet.write(x,32, move.product_id.categ_id.property_stock_valuation_account_id.code ,bord )
					worksheet.write(x,33, move.product_id.categ_id.property_stock_account_output_categ_id.code ,bord )
					worksheet.write(x,34, move.analytic_account_id.name or '' ,bord )
					worksheet.write(x,35, move.analytic_tag_id.name or '' ,bord )
			
			ingreso1 += line[12] if line[12] else 0
			ingreso2 +=line[13] if line[13] else 0
			salida1 +=line[14] if line[14] else 0
			salida2 += line[15] if line[15] else 0

			x = x +1

		tam_col = [11,11,5,5,7,5,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11]

		worksheet.write(x,11,'TOTALES:' ,bold )
		worksheet.write(x,12,ingreso1 ,numberdosbold )
		worksheet.write(x,13,ingreso2 ,numberdosbold )
		worksheet.write(x,14,salida1 ,numberdosbold )
		worksheet.write(x,15,salida2 ,numberdosbold )

		worksheet.set_column('A:A', tam_col[0])
		worksheet.set_column('B:B', tam_col[1])
		worksheet.set_column('C:C', tam_col[2])
		worksheet.set_column('D:D', tam_col[3])
		worksheet.set_column('E:E', tam_col[4])
		worksheet.set_column('F:F', tam_col[5])
		worksheet.set_column('G:G', tam_col[6])
		worksheet.set_column('H:H', tam_col[7])
		worksheet.set_column('I:I', tam_col[8])
		worksheet.set_column('J:J', tam_col[9])
		worksheet.set_column('K:K', tam_col[10])
		worksheet.set_column('L:L', tam_col[11])
		worksheet.set_column('M:M', tam_col[12])
		worksheet.set_column('N:N', tam_col[13])
		worksheet.set_column('O:O', tam_col[14])
		worksheet.set_column('P:P', tam_col[15])
		worksheet.set_column('Q:Q', tam_col[16])
		worksheet.set_column('R:R', tam_col[17])
		worksheet.set_column('S:S', tam_col[18])
		worksheet.set_column('T:Z', tam_col[19])

		workbook.close()


		f = open(direccion + 'kardex_producto.xlsx', 'rb')

		return self.env['popup.it'].get_file('Kardex_Valorado.xlsx',base64.encodestring(b''.join(f.readlines())))




class make_kardex(models.TransientModel):
	_inherit = "make.kardex"


	def do_csvtoexcel(self):
		cad = ""

		s_prod = [-1,-1,-1]
		s_loca = [-1,-1,-1]
		if self.alllocations == True:
			locat_ids = self.env['stock.location'].search( [('usage','in',('internal','internal'))] )
			lst_locations = locat_ids.ids
		else:
			lst_locations = self.location_ids.ids
		lst_products  = self.products_ids.ids
		productos='{'
		almacenes='{'
		date_ini=self.fini
		date_fin=self.ffin
		if self.allproducts:
			lst_products = self.env['product.product'].with_context(active_test=False).search([]).ids

		else:
			lst_products = self.products_ids.ids

		if len(lst_products) == 0:
			raise osv.except_osv('Alerta','No existen productos seleccionados')

		for producto in lst_products:
			productos=productos+str(producto)+','
			s_prod.append(producto)
		productos=productos[:-1]+'}'
		for location in lst_locations:
			almacenes=almacenes+str(location)+','
			s_loca.append(location)
		almacenes=almacenes[:-1]+'}'



		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		workbook = Workbook(direccion +'kardex_producto.xlsx')
		worksheet = workbook.add_worksheet("Kardex")
		bold = workbook.add_format({'bold': True})
		bold.set_font_size(8)
		normal = workbook.add_format()
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=2)
		boldbord.set_align('center')
		boldbord.set_align('vcenter')
		boldbord.set_text_wrap()
		boldbord.set_font_size(8)
		boldbord.set_bg_color('#DCE6F1')

		especial1 = workbook.add_format({'bold': True})
		especial1.set_align('center')
		especial1.set_align('vcenter')
		especial1.set_text_wrap()
		especial1.set_font_size(15)

		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'0.00'})
		numberseis = workbook.add_format({'num_format':'0.000000'})
		numberseis.set_font_size(8)
		numberocho = workbook.add_format({'num_format':'0.00000000'})
		numberocho.set_font_size(8)
		bord = workbook.add_format()
		bord.set_border(style=1)
		bord.set_font_size(8)
		numberdos.set_border(style=1)
		numberdos.set_font_size(8)
		numbertres.set_border(style=1)
		numberseis.set_border(style=1)
		numberocho.set_border(style=1)
		numberdosbold = workbook.add_format({'num_format':'0.00','bold':True})
		numberdosbold.set_font_size(8)
		
		formatdate = workbook.add_format({'num_format': 'dd-mm-yyyy'})
		x= 10
		tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tam_letra = 1.2

		worksheet.merge_range(1,5,1,10, "KARDEX FISICO", especial1)
		worksheet.write(2,0,'FECHA INICIO:',bold)
		worksheet.write(3,0,'FECHA FIN:',bold)

		worksheet.write(2,1,str(self.fini))
		worksheet.write(3,1,str(self.ffin))
		import datetime

		worksheet.merge_range(8,0,9,0, u"Ubicacion Origen",boldbord)
		worksheet.merge_range(8,1,9,1, u"Ubicacion Destino",boldbord)
		worksheet.merge_range(8,2,9,2, u"Almacen",boldbord)
		worksheet.merge_range(8,3,9,3, u"Tipo de Operación",boldbord)
		worksheet.merge_range(8,4,9,4, u"Categoria",boldbord)

		worksheet.merge_range(8,5,9,5, u"Producto",boldbord)
		worksheet.merge_range(8,6,9,6, u"Codigo P.",boldbord)
		worksheet.merge_range(8,7,9,7, u"Unidad",boldbord)

		worksheet.merge_range(8,8,9,8, u"Fecha",boldbord)

		worksheet.merge_range(8,9,9,9, u"Doc. Almacen",boldbord)

		worksheet.write(8,10, "Ingreso",boldbord)
		worksheet.write(9,10, "Cantidad",boldbord)
		worksheet.write(8,11, "Salida",boldbord)
		worksheet.write(9,11, "Cantidad",boldbord)
		worksheet.write(8,12, "Saldo",boldbord)
		worksheet.write(9,12, "Cantidad",boldbord)


		worksheet.merge_range(8,13,9,13, u"Prioridad",boldbord)
		worksheet.merge_range(8,14,9,14, u"Observacion",boldbord)
		worksheet.merge_range(8,15,9,15, u"Trabajador",boldbord)
		worksheet.merge_range(8,16,9,16, u"Cuenta Analitica",boldbord)
		worksheet.merge_range(8,17,9,17, u"Etiqueta Analitica",boldbord)


		self.env.cr.execute("""

select 
origen AS "Ubicación Origen",
destino AS "Ubicación Destino",
almacen AS "Almacén",
vstf.motivo_guia::varchar AS "Tipo de operación",
categoria as "Categoria",
producto as "Producto",
cod_pro as "Codigo P.",
unidad as "unidad",
(vstf.fecha - interval '5' hour)::date as "Fecha",
vstf.name as "Doc. Almacén",
vstf.entrada as "Entrada",
vstf.salida as "Salida",
vstf.move_id as "Move"
from
(
select vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_destino as almacen, vst_kardex_fisico.product_qty as entrada, 0 as salida,vst_kardex_fisico.id  as stock_move,vst_kardex_fisico.guia as motivo_guia, producto,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id,location_dest_id as almacen_id, id as move_id from vst_kardex_fisico("""+str(self.env.company.id)+""")
union all
select vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_origen as almacen, 0 as entrada, vst_kardex_fisico.product_qty as salida,vst_kardex_fisico.id  as stock_move ,vst_kardex_fisico.guia as motivo_guia ,producto ,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id, location_id as almacen_id, id as move_id from vst_kardex_fisico("""+str(self.env.company.id)+""")
) as vstf
where vstf.fecha >='""" +str(date_ini)+ """'::timestamp + interval '5' hour and vstf.fecha <='""" +str(date_fin)+ """'::timestamp + interval '29' hour
and vstf.product_id in """ +str(tuple(s_prod))+ """
and vstf.almacen_id in """ +str(tuple(s_loca))+ """
and vstf.estado = 'done'
order by
almacen,producto,vstf.fecha;


		""")

		ingreso1= 0
		ingreso2= 0
		salida1= 0
		salida2= 0

		saldo = 0
		almacen = None
		producto = None
		for line in self.env.cr.fetchall():
			if almacen == None:
				almacen = (line[2] if line[2] else '')
				producto = (line[5] if line[5] else '')
				saldo = line[10] - line[11]
			elif almacen != (line[2] if line[2] else '') or producto != (line[5] if line[5] else ''):
				almacen = (line[2] if line[2] else '')
				producto = (line[5] if line[5] else '')
				saldo = line[10] - line[11]
			else:
				saldo = saldo + line[10] - line[11]

			worksheet.write(x,0,line[0] if line[0] else '' ,bord )
			worksheet.write(x,1,line[1] if line[1] else '' ,bord )
			worksheet.write(x,2,line[2] if line[2] else '' ,bord )
			worksheet.write(x,3,line[3] if line[3] else '' ,bord )
			worksheet.write(x,4,line[4] if line[4] else '' ,bord )
			worksheet.write(x,5,line[5] if line[5] else '' ,bord )
			worksheet.write(x,6,line[6] if line[6] else '' ,bord )
			worksheet.write(x,7,line[7] if line[7] else '' ,bord )
			worksheet.write(x,8,line[8] if line[8] else '' ,formatdate )
			worksheet.write(x,9,line[9] if line[9] else '' ,bord )
			worksheet.write(x,10,line[10] if line[10] else 0 ,numberdos )
			worksheet.write(x,11,line[11] if line[11] else 0 ,numberdos )
			worksheet.write(x,12,saldo ,numberdos )

			move = self.env['stock.move'].browse(line[12])

			worksheet.write(x,13,move.prioridad_it if move.prioridad_it else '' ,bord )
			worksheet.write(x,14,move.observacion_it if move.observacion_it else '' ,bord )
			worksheet.write(x,15,move.trabajador_it if move.trabajador_it else '' ,bord )

			worksheet.write(x,16, move.analytic_account_id.name or '' ,bord )
			worksheet.write(x,17, move.analytic_tag_id.name or '' ,bord )


			x = x +1

		tam_col = [11,11,5,5,7,5,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11]


		worksheet.set_column('A:A', tam_col[0])
		worksheet.set_column('B:B', tam_col[1])
		worksheet.set_column('C:C', tam_col[2])
		worksheet.set_column('D:D', tam_col[3])
		worksheet.set_column('E:E', tam_col[4])
		worksheet.set_column('F:F', tam_col[5])
		worksheet.set_column('G:G', tam_col[6])
		worksheet.set_column('H:H', tam_col[7])
		worksheet.set_column('I:I', tam_col[8])
		worksheet.set_column('J:J', tam_col[9])
		worksheet.set_column('K:K', tam_col[10])
		worksheet.set_column('L:L', tam_col[11])
		worksheet.set_column('M:M', tam_col[12])
		worksheet.set_column('N:N', tam_col[13])
		worksheet.set_column('O:O', tam_col[14])
		worksheet.set_column('P:P', tam_col[15])
		worksheet.set_column('Q:Q', tam_col[16])
		worksheet.set_column('R:R', tam_col[17])
		worksheet.set_column('S:S', tam_col[18])
		worksheet.set_column('T:Z', tam_col[19])

		workbook.close()


		f = open(direccion + 'kardex_producto.xlsx', 'rb')

		return self.env['popup.it'].get_file('Kardex_Fisico.xlsx',base64.encodestring(b''.join(f.readlines())))






class make_kardex_lote(models.TransientModel):
	_inherit = "make.kardex.lote"


	def do_csvtoexcel(self):
		cad = ""

		s_prod = [-1,-1,-1]
		s_loca = [-1,-1,-1]
		if self.alllocations == True:
			locat_ids = self.env['stock.location'].search( [('usage','in',('internal','internal'))] )
			lst_locations = locat_ids.ids
		else:
			lst_locations = self.location_ids.ids
		lst_products  = self.products_ids.ids
		productos='{'
		almacenes='{'
		date_ini=self.fini
		date_fin=self.ffin
		if self.allproducts:
			lst_products = self.env['product.product'].with_context(active_test=False).search([]).ids

		else:
			lst_products = self.products_ids.ids

		if len(lst_products) == 0:
			raise osv.except_osv('Alerta','No existen productos seleccionados')

		for producto in lst_products:
			productos=productos+str(producto)+','
			s_prod.append(producto)
		productos=productos[:-1]+'}'
		for location in lst_locations:
			almacenes=almacenes+str(location)+','
			s_loca.append(location)
		almacenes=almacenes[:-1]+'}'



		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		workbook = Workbook(direccion +'kardex_producto.xlsx')
		worksheet = workbook.add_worksheet("Kardex")
		bold = workbook.add_format({'bold': True})
		bold.set_font_size(8)
		normal = workbook.add_format()
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=2)
		boldbord.set_align('center')
		boldbord.set_align('vcenter')
		boldbord.set_text_wrap()
		boldbord.set_font_size(8)
		boldbord.set_bg_color('#DCE6F1')

		especial1 = workbook.add_format({'bold': True})
		especial1.set_align('center')
		especial1.set_align('vcenter')
		especial1.set_text_wrap()
		especial1.set_font_size(15)

		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'0.00'})
		numberseis = workbook.add_format({'num_format':'0.000000'})
		numberseis.set_font_size(8)
		numberocho = workbook.add_format({'num_format':'0.00000000'})
		numberocho.set_font_size(8)
		bord = workbook.add_format()
		bord.set_border(style=1)
		bord.set_font_size(8)
		numberdos.set_border(style=1)
		numberdos.set_font_size(8)
		numbertres.set_border(style=1)
		numberseis.set_border(style=1)
		numberocho.set_border(style=1)
		numberdosbold = workbook.add_format({'num_format':'0.00','bold':True})
		numberdosbold.set_font_size(8)
		
		formatdate = workbook.add_format({'num_format': 'dd-mm-yyyy'})
		x= 10
		tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tam_letra = 1.2

		worksheet.merge_range(1,5,1,10, "KARDEX FISICO", especial1)
		worksheet.write(2,0,'FECHA INICIO:',bold)
		worksheet.write(3,0,'FECHA FIN:',bold)

		worksheet.write(2,1,str(self.fini))
		worksheet.write(3,1,str(self.ffin))
		import datetime

		worksheet.merge_range(8,0,9,0, u"Ubicacion Origen",boldbord)
		worksheet.merge_range(8,1,9,1, u"Ubicacion Destino",boldbord)
		worksheet.merge_range(8,2,9,2, u"Almacen",boldbord)
		worksheet.merge_range(8,3,9,3, u"Tipo de Operación",boldbord)
		worksheet.merge_range(8,4,9,4, u"Categoria",boldbord)

		worksheet.merge_range(8,5,9,5, u"Producto",boldbord)
		worksheet.merge_range(8,6,9,6, u"Codigo P.",boldbord)
		worksheet.merge_range(8,7,9,7, u"Unidad",boldbord)

		worksheet.merge_range(8,8,9,8, u"Fecha",boldbord)

		worksheet.merge_range(8,9,9,9, u"Doc. Almacen",boldbord)

		worksheet.write(8,10, "Ingreso",boldbord)
		worksheet.write(9,10, "Cantidad",boldbord)
		worksheet.write(8,11, "Salida",boldbord)
		worksheet.write(9,11, "Cantidad",boldbord)
		worksheet.write(8,12, "Saldo",boldbord)
		worksheet.write(9,12, "Cantidad",boldbord)
		worksheet.merge_range(8,13,9,13, u"Lote",boldbord)



		worksheet.merge_range(8,14,9,14, u"Prioridad",boldbord)
		worksheet.merge_range(8,15,9,15, u"Observacion",boldbord)
		worksheet.merge_range(8,16,9,16, u"Trabajador",boldbord)
		worksheet.merge_range(8,17,9,17, u"Cuenta Analitica",boldbord)
		worksheet.merge_range(8,18,9,18, u"Etiqueta Analitica",boldbord)

		self.env.cr.execute("""

select 
origen AS "Ubicación Origen",
destino AS "Ubicación Destino",
almacen AS "Almacén",
vstf.motivo_guia::varchar AS "Tipo de operación",
categoria as "Categoria",
producto as "Producto",
cod_pro as "Codigo P.",
unidad as "unidad",
(vstf.fecha - interval '5' hour)::date as "Fecha",
vstf.name as "Doc. Almacén",
vstf.entrada as "Entrada",
vstf.salida as "Salida",
vstf.lote as "Lote",
vstf.move_id as "Move"
from
(
select vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_destino as almacen, vst_kardex_fisico.product_qty as entrada, 0 as salida,vst_kardex_fisico.id  as stock_move,vst_kardex_fisico.guia as motivo_guia, producto,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id,location_dest_id as almacen_id,lote, id as move_id from vst_kardex_fisico_lote("""+str(self.env.company.id)+""") as vst_kardex_fisico
union all
select vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_origen as almacen, 0 as entrada, vst_kardex_fisico.product_qty as salida,vst_kardex_fisico.id  as stock_move ,vst_kardex_fisico.guia as motivo_guia ,producto ,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id, location_id as almacen_id , lote, id as move_id from vst_kardex_fisico_lote("""+str(self.env.company.id)+""") as vst_kardex_fisico
) as vstf
where vstf.fecha >='""" +str(date_ini)+ """'::timestamp + interval '5' hour and vstf.fecha <='""" +str(date_fin)+ """'::timestamp + interval '29' hour
and vstf.product_id in """ +str(tuple(s_prod))+ """
and vstf.almacen_id in """ +str(tuple(s_loca))+ """
and vstf.estado = 'done'
order by
almacen,producto,vstf.fecha;


		""")

		ingreso1= 0
		ingreso2= 0
		salida1= 0
		salida2= 0

		saldo = 0
		almacen = None
		producto = None
		for line in self.env.cr.fetchall():
			if almacen == None:
				almacen = (line[2] if line[2] else '')
				producto = (line[5] if line[5] else '')
				saldo = line[10] - line[11]
			elif almacen != (line[2] if line[2] else '') or producto != (line[5] if line[5] else ''):
				almacen = (line[2] if line[2] else '')
				producto = (line[5] if line[5] else '')
				saldo = line[10] - line[11]
			else:
				saldo = saldo + line[10] - line[11]

			worksheet.write(x,0,line[0] if line[0] else '' ,bord )
			worksheet.write(x,1,line[1] if line[1] else '' ,bord )
			worksheet.write(x,2,line[2] if line[2] else '' ,bord )
			worksheet.write(x,3,line[3] if line[3] else '' ,bord )
			worksheet.write(x,4,line[4] if line[4] else '' ,bord )
			worksheet.write(x,5,line[5] if line[5] else '' ,bord )
			worksheet.write(x,6,line[6] if line[6] else '' ,bord )
			worksheet.write(x,7,line[7] if line[7] else '' ,bord )
			worksheet.write(x,8,line[8] if line[8] else '' ,formatdate )
			worksheet.write(x,9,line[9] if line[9] else '' ,bord )
			worksheet.write(x,10,line[10] if line[10] else 0 ,numberdos )
			worksheet.write(x,11,line[11] if line[11] else 0 ,numberdos )
			worksheet.write(x,12,saldo ,numberdos )
			worksheet.write(x,13,line[12] if line[12] else '' ,bord )


			move = self.env['stock.move'].browse(line[13])

			worksheet.write(x,14,move.prioridad_it if move.prioridad_it else '' ,bord )
			worksheet.write(x,15,move.observacion_it if move.observacion_it else '' ,bord )
			worksheet.write(x,16,move.trabajador_it if move.trabajador_it else '' ,bord )

			worksheet.write(x,17, move.analytic_account_id.name or '' ,bord )
			worksheet.write(x,18, move.analytic_tag_id.name or '' ,bord )


			x = x +1

		tam_col = [11,11,5,5,7,5,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11]


		worksheet.set_column('A:A', tam_col[0])
		worksheet.set_column('B:B', tam_col[1])
		worksheet.set_column('C:C', tam_col[2])
		worksheet.set_column('D:D', tam_col[3])
		worksheet.set_column('E:E', tam_col[4])
		worksheet.set_column('F:F', tam_col[5])
		worksheet.set_column('G:G', tam_col[6])
		worksheet.set_column('H:H', tam_col[7])
		worksheet.set_column('I:I', tam_col[8])
		worksheet.set_column('J:J', tam_col[9])
		worksheet.set_column('K:K', tam_col[10])
		worksheet.set_column('L:L', tam_col[11])
		worksheet.set_column('M:M', tam_col[12])
		worksheet.set_column('N:N', tam_col[13])
		worksheet.set_column('O:O', tam_col[14])
		worksheet.set_column('P:P', tam_col[15])
		worksheet.set_column('Q:Q', tam_col[16])
		worksheet.set_column('R:R', tam_col[17])
		worksheet.set_column('S:S', tam_col[18])
		worksheet.set_column('T:Z', tam_col[19])

		workbook.close()


		f = open(direccion + 'kardex_producto.xlsx', 'rb')

		return self.env['popup.it'].get_file('Kardex_Fisico.xlsx',base64.encodestring(b''.join(f.readlines())))


