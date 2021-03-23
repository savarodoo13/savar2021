# -*- coding: utf-8 -*-
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import time
import odoo.addons.decimal_precision as dp
from openerp.osv import osv
import base64
from odoo import models, fields, api
import codecs

values = {}





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

		formatdate = workbook.add_format({'num_format': 'dd-mm-yyyy'})
		x= 10
		tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tam_letra = 1.2


		worksheet.merge_range(1,5,1,10, "KARDEX VALORADO", especial1)
		worksheet.write(2,1,'FECHA INICIO:',bold)
		worksheet.write(3,1,'FECHA FIN:',bold)

		worksheet.write(2,2,str(self.fini))
		worksheet.write(3,2,str(self.ffin))			
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

		if self.check_account:
			worksheet.merge_range(8,23,9,23, u"Cuenta Valuación",boldbord)
			worksheet.merge_range(8,24,9,24, u"Cuenta Salida",boldbord)
			worksheet.merge_range(8,25,9,25, u"Cuenta Analítica",boldbord)
			# worksheet.merge_range(8,26,9,26, u"Etiqueta Analítica",boldbord)

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
				stock_moveid as "id move",
				ctanalitica as "Cta Analitica"
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

			if self.check_account:
				move = self.env['stock.move'].browse(line[23])
				if move.id:
					worksheet.write(x,23, move.product_id.categ_id.property_stock_valuation_account_id.code ,bord )
					worksheet.write(x,24, move.product_id.categ_id.property_stock_account_output_categ_id.code ,bord )
					worksheet.write(x,25, line[24] if line[24] else '' ,bord )
					# worksheet.write(x,26, move.analytic_tag_id.name or '' ,bord )
			
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


