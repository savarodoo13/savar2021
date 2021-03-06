# -*- coding: utf-8 -*-
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import time
import odoo.addons.decimal_precision as dp
from openerp.osv import osv
import base64
from odoo import models, fields, api
import codecs

values = {}




class make_kardex(models.TransientModel):
	_inherit = "make.kardex"


	def do_popup(self):		
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




		self.env.cr.execute("""
			drop table if exists tree_view_kardex_fisico;
			create table tree_view_kardex_fisico AS
			select row_number() OVER () as id,
origen AS u_origen,
destino AS u_destino,
almacen AS almacen,
vstf.motivo_guia::varchar AS t_opera,
categoria as categoria,
producto as producto,
cod_pro as cod_pro,
unidad as unidad,
vstf.fecha as fecha,
vstf.name as doc_almacen,
vstf.entrada as entrada,
vstf.salida as salida
from
(
select vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_destino as almacen, vst_kardex_fisico.product_qty as entrada, 0 as salida,vst_kardex_fisico.id  as stock_move,vst_kardex_fisico.guia as motivo_guia, producto,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id,location_dest_id as almacen_id from vst_kardex_fisico("""+str(self.env.company.id)+""")
union all
select vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_origen as almacen, 0 as entrada, vst_kardex_fisico.product_qty as salida,vst_kardex_fisico.id  as stock_move ,vst_kardex_fisico.guia as motivo_guia ,producto ,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id, location_id as almacen_id from vst_kardex_fisico("""+str(self.env.company.id)+""")
) as vstf
where vstf.fecha >='""" +str(date_ini)+ """'::timestamp + interval '5' hour and vstf.fecha <='""" +str(date_fin)+ """'::timestamp + interval '29' hour
and vstf.product_id in """ +str(tuple(s_prod))+ """
and vstf.almacen_id in """ +str(tuple(s_loca))+ """
and vstf.estado = 'done'
order by
almacen,producto,vstf.fecha;
		""")



		return {
			'name': 'Kardex Fisico',
			'type': 'ir.actions.act_window',
			'res_model': 'tree.view.kardex.fisico',
			'view_mode': 'tree',
			'views': [(False, 'tree')],
		}




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
		worksheet.merge_range(8,3,9,3, u"Tipo de Operaci??n",boldbord)
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



		self.env.cr.execute("""

select 
origen AS "Ubicaci??n Origen",
destino AS "Ubicaci??n Destino",
almacen AS "Almac??n",
vstf.motivo_guia::varchar AS "Tipo de operaci??n",
categoria as "Categoria",
producto as "Producto",
cod_pro as "Codigo P.",
unidad as "unidad",
(vstf.fecha - interval '5' hour)::date as "Fecha",
vstf.name as "Doc. Almac??n",
vstf.entrada as "Entrada",
vstf.salida as "Salida"
from
(
select vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_destino as almacen, vst_kardex_fisico.product_qty as entrada, 0 as salida,vst_kardex_fisico.id  as stock_move,vst_kardex_fisico.guia as motivo_guia, producto,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id,location_dest_id as almacen_id from vst_kardex_fisico("""+str(self.env.company.id)+""")
union all
select vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_origen as almacen, 0 as entrada, vst_kardex_fisico.product_qty as salida,vst_kardex_fisico.id  as stock_move ,vst_kardex_fisico.guia as motivo_guia ,producto ,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id, location_id as almacen_id from vst_kardex_fisico("""+str(self.env.company.id)+""")
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





	def do_csv(self):
		data = self.read()
		cad=""
		if data[0]['products_ids']==[]:
			if data[0]['allproducts']:
				if data[0]['allproducts']==False:
					raise osv.except_osv('Alerta','No existen productos seleccionados')
					return
				else:
					#prods= self.pool.get('product.product').search(cr,uid,[])
					lst_products  = self.env['product.product'].search([]).ids
			else:
				raise osv.except_osv('Alerta','No existen productos seleccionados')
				return
		else:
			lst_products  = data[0]['products_ids']

		s_prod = [-1,-1,-1]
		s_loca = [-1,-1,-1]

		lst_locations = data[0]['location_ids']
		productos='{0,'
		almacenes='{0,'
		date_ini=data[0]['fini']
		date_fin=data[0]['ffin']
		if 'allproducts' in data[0]:
			if data[0]['allproducts']:
				lst_products = self.env['product.product'].with_context(active_test=False).search([]).ids
			else:
				lst_products  = data[0]['products_ids']
		else:
			lst_products  = data[0]['products_ids']

		if 'alllocations' in data[0]:
			lst_locations = self.env['stock.location'].search( [('usage','in',('internal','internal'))] ).ids

		for producto in lst_products:
			productos=productos+str(producto)+','
			s_prod.append(producto)
		productos=productos[:-1]+'}'
		for location in lst_locations:
			almacenes=almacenes+str(location)+','
			s_loca.append(location)
		almacenes=almacenes[:-1]+'}'
		direccion = self.env['main.parameter'].search([])[0].dir_create_file


		cadf=u"""



		copy (

select 
origen AS "Ubicaci??n Origen",
destino AS "Ubicaci??n Destino",
almacen AS "Almac??n",
vstf.motivo_guia::varchar AS "Tipo de operaci??n",
categoria as "Categoria",
producto as "Producto",
cod_pro as "Codigo P.",
unidad as "unidad",
(vstf.fecha - interval '5' hour)::date as "Fecha",
vstf.name as "Doc. Almac??n",
vstf.entrada as "Entrada",
vstf.salida as "Salida"
from
(
select vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_destino as almacen, vst_kardex_fisico.product_qty as entrada, 0 as salida,vst_kardex_fisico.id  as stock_move,vst_kardex_fisico.guia as motivo_guia, producto,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id,location_dest_id as almacen_id from vst_kardex_fisico("""+str(self.env.company.id)+""")
union all
select vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_origen as almacen, 0 as entrada, vst_kardex_fisico.product_qty as salida,vst_kardex_fisico.id  as stock_move ,vst_kardex_fisico.guia as motivo_guia ,producto ,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id, location_id as almacen_id from vst_kardex_fisico("""+str(self.env.company.id)+""")
) as vstf
where vstf.fecha >='""" +str(date_ini)+ """'::timestamp + interval '5' hour and vstf.fecha <='""" +str(date_fin)+ """'::timestamp + interval '29' hour
and vstf.product_id in """ +str(tuple(s_prod))+ u"""
and vstf.almacen_id in """ +str(tuple(s_loca))+ u"""
and vstf.estado = 'done'
order by
almacen,producto,vstf.fecha




) to '"""+direccion+u"""kardex.csv'  WITH DELIMITER ',' CSV HEADER
		"""
		
		self.env.cr.execute(cadf)
		import gzip
		import shutil

		f = open(direccion+'kardex.csv', 'rb')

		return self.env['popup.it'].get_file('Kardex_Fisico.csv',base64.encodestring(b''.join(f.readlines())))







class make_kardex_product(models.TransientModel):
	_inherit = "make.kardex.product"


	def do_popup(self):		
		cad = ""

		s_prod = [-1,-1,-1]
		s_loca = [-1,-1,-1]
		if self.alllocations == True:
			locat_ids = self.env['stock.location'].search( [('usage','in',('internal','internal'))] )
			lst_locations = locat_ids.ids
		else:
			lst_locations = self.location_ids.ids
		lst_products  = [self.env.context['active_id']]
		productos='{'
		almacenes='{'
		date_ini=self.fini
		date_fin=self.ffin
		

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




		self.env.cr.execute("""
			drop table if exists tree_view_kardex_fisico;
			create table tree_view_kardex_fisico AS


			select row_number() OVER () as id,
origen AS u_origen,
destino AS u_destino,
almacen AS almacen,
vstf.motivo_guia::varchar AS t_opera,
categoria as categoria,
producto as producto,
cod_pro as cod_pro,
unidad as unidad,
(vstf.fecha - interval '5' hour)::date as fecha,
vstf.name as doc_almacen,
vstf.entrada as entrada,
vstf.salida as salida
from
(
select vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_destino as almacen, vst_kardex_fisico.product_qty as entrada, 0 as salida,vst_kardex_fisico.id  as stock_move,vst_kardex_fisico.guia as motivo_guia, producto,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id,location_dest_id as almacen_id from vst_kardex_fisico("""+str(self.env.company.id)+""")
union all
select vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_origen as almacen, 0 as entrada, vst_kardex_fisico.product_qty as salida,vst_kardex_fisico.id  as stock_move ,vst_kardex_fisico.guia as motivo_guia ,producto ,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id, location_id as almacen_id from vst_kardex_fisico("""+str(self.env.company.id)+""")
) as vstf
where vstf.fecha >='""" +str(date_ini)+ """'::timestamp + interval '5' hour and vstf.fecha <='""" +str(date_fin)+ """'::timestamp + interval '29' hour
and vstf.product_id in """ +str(tuple(s_prod))+ """
and vstf.almacen_id in """ +str(tuple(s_loca))+ """
and vstf.estado = 'done'
order by
almacen,producto,vstf.fecha;


		""")



		return {
			'name': 'Kardex Fisico',
			'type': 'ir.actions.act_window',
			'res_model': 'tree.view.kardex.fisico',
			'view_mode': 'tree',
			'views': [(False, 'tree')],
		}




	def do_csvtoexcel(self):
		cad = ""

		s_prod = [-1,-1,-1]
		s_loca = [-1,-1,-1]
		if self.alllocations == True:
			locat_ids = self.env['stock.location'].search( [('usage','in',('internal','internal'))] )
			lst_locations = locat_ids.ids
		else:
			lst_locations = self.location_ids.ids
		lst_products  = [self.env.context['active_id']]
		productos='{'
		almacenes='{'
		date_ini=self.fini
		date_fin=self.ffin
		

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
		formatdate = workbook.add_format({'num_format': 'dd-mm-yyyy'})
		numberdosbold.set_font_size(8)
		x= 10
		tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tam_letra = 1.2

		product = self.env['product.product'].browse(self.env.context['active_id'])

		worksheet.merge_range(1,5,1,10, "KARDEX FISICO - " + product.name, especial1)
		worksheet.write(2,0,'FECHA INICIO:',bold)
		worksheet.write(3,0,'FECHA FIN:',bold)

		worksheet.write(2,1,str(self.fini))
		worksheet.write(3,1,str(self.ffin))
		import datetime

		worksheet.merge_range(8,0,9,0, u"Ubicacion Origen",boldbord)
		worksheet.merge_range(8,1,9,1, u"Ubicacion Destino",boldbord)
		worksheet.merge_range(8,2,9,2, u"Almacen",boldbord)
		worksheet.merge_range(8,3,9,3, u"Tipo de Operaci??n",boldbord)
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



		self.env.cr.execute("""


select 
origen AS "Ubicaci??n Origen",
destino AS "Ubicaci??n Destino",
almacen AS "Almac??n",
vstf.motivo_guia::varchar AS "Tipo de operaci??n",
categoria as "Categoria",
producto as "Producto",
cod_pro as "Codigo P.",
unidad as "unidad",
(vstf.fecha - interval '5' hour)::date as "Fecha",
vstf.name as "Doc. Almac??n",
vstf.entrada as "Entrada",
vstf.salida as "Salida"
from
(
select vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_destino as almacen, vst_kardex_fisico.product_qty as entrada, 0 as salida,vst_kardex_fisico.id  as stock_move,vst_kardex_fisico.guia as motivo_guia, producto,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id,location_dest_id as almacen_id from vst_kardex_fisico("""+str(self.env.company.id)+""")
union all
select vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_origen as almacen, 0 as entrada, vst_kardex_fisico.product_qty as salida,vst_kardex_fisico.id  as stock_move ,vst_kardex_fisico.guia as motivo_guia ,producto ,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id, location_id as almacen_id from vst_kardex_fisico("""+str(self.env.company.id)+""")
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
			worksheet.write(x,8,str(line[8]) if line[8] else '' ,formatdate )
			worksheet.write(x,9,line[9] if line[9] else '' ,bord )
			worksheet.write(x,10,line[10] if line[10] else 0 ,numberdos )
			worksheet.write(x,11,line[11] if line[11] else 0 ,numberdos )
			worksheet.write(x,12,saldo ,numberdos )

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





	def do_csv(self):
		data = self.read()
		cad=""
		
		lst_products  = [self.env.context['active_id']]

		s_prod = [-1,-1,-1]
		s_loca = [-1,-1,-1]

		lst_locations = data[0]['location_ids']
		productos='{0,'
		almacenes='{0,'
		date_ini=data[0]['fini']
		date_fin=data[0]['ffin']
		
		if 'alllocations' in data[0]:
			lst_locations = self.env['stock.location'].search( [('usage','in',('internal','internal'))] ).ids

		for producto in lst_products:
			productos=productos+str(producto)+','
			s_prod.append(producto)
		productos=productos[:-1]+'}'
		for location in lst_locations:
			almacenes=almacenes+str(location)+','
			s_loca.append(location)
		almacenes=almacenes[:-1]+'}'
		direccion = self.env['main.parameter'].search([])[0].dir_create_file


		cadf=u"""



		copy (


select 
origen AS "Ubicaci??n Origen",
destino AS "Ubicaci??n Destino",
almacen AS "Almac??n",
vstf.motivo_guia::varchar AS "Tipo de operaci??n",
categoria as "Categoria",
producto as "Producto",
cod_pro as "Codigo P.",
unidad as "unidad",
(vstf.fecha - interval '5' hour)::date as "Fecha",
vstf.name as "Doc. Almac??n",
vstf.entrada as "Entrada",
vstf.salida as "Salida"
from
(
select vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_destino as almacen, vst_kardex_fisico.product_qty as entrada, 0 as salida,vst_kardex_fisico.id  as stock_move,vst_kardex_fisico.guia as motivo_guia, producto,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id,location_dest_id as almacen_id from vst_kardex_fisico("""+str(self.env.company.id)+""")
union all
select vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_origen as almacen, 0 as entrada, vst_kardex_fisico.product_qty as salida,vst_kardex_fisico.id  as stock_move ,vst_kardex_fisico.guia as motivo_guia ,producto ,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id, location_id as almacen_id from vst_kardex_fisico("""+str(self.env.company.id)+""")
) as vstf
where vstf.fecha >='""" +str(date_ini)+ """'::timestamp + interval '5' hour and vstf.fecha <='""" +str(date_fin)+ """'::timestamp + interval '29' hour
and vstf.product_id in """ +str(tuple(s_prod))+ u"""
and vstf.almacen_id in """ +str(tuple(s_loca))+ u"""
and vstf.estado = 'done'
order by
almacen,producto,vstf.fecha


) to '"""+direccion+u"""kardex.csv'  WITH DELIMITER ',' CSV HEADER
		"""
		
		self.env.cr.execute(cadf)
		import gzip
		import shutil

		f = open(direccion+'kardex.csv', 'rb')

		return self.env['popup.it'].get_file('Kardex_Fisico.csv',base64.encodestring(b''.join(f.readlines())))