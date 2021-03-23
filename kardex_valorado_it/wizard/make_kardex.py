# -*- coding: utf-8 -*-
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import time
import odoo.addons.decimal_precision as dp
from openerp.osv import osv
import base64
from odoo import models, fields, api
import codecs
from datetime import timedelta

values = {}

class account_move(models.Model):
	_inherit = 'account.move'

	check_use_date_kardex = fields.Boolean('Establecer fecha en Kardex',default=False)
	date_kardex = fields.Datetime('Fecha Kardex')

class main_parameter(models.Model):
	_inherit = 'main.parameter'

	check_gastos_vinculados = fields.Boolean('Gastos Vinculados con Fecha Kardex del Albaran?',default=False)

class stock_picking(models.Model):
	_inherit = 'stock.picking'

	tc = fields.Float('Tipo Cambio',digits=(12,3),default=1)

	def write(selfs,vals):
		t = super(stock_picking,selfs).write(vals)    
		for self in selfs:
			if 'nomore' in self.env.context:
				pass
			else:
				fecha_pedido = False
				moneda = False
				for i in self.move_ids_without_package:
					if i.purchase_line_id.id and i.purchase_line_id.order_id.id and i.purchase_line_id.order_id.date_order:
						fecha_pedido = i.purchase_line_id.order_id.date_order - timedelta(hours=5)
						moneda = i.purchase_line_id.order_id.currency_id.name
				if self.state == 'done' and fecha_pedido and moneda == 'USD' and self.tc == 1:
					tp = self.env['res.currency.rate'].search([('currency_id.name','=','USD'),('name','=', fecha_pedido )])
					if self.invoice_id.id:
						tp = self.env['res.currency.rate'].search([('currency_id.name','=','USD'),('name','=', self.invoice_id.invoice_date )])
					if len(tp)==0 and not self.invoice_id.id:
						raise osv.except_osv('Alerta','No existen el tipo de cambio para ' + fecha_pedido.strftime("%Y-%m-%d") + ' del pedido de compra en dolares del albaran ' + self.name)						
					if len(tp)==0 and self.invoice_id.id:
						raise osv.except_osv('Alerta','No existen el tipo de cambio para ' + self.invoice_id.invoice_date.strftime("%Y-%m-%d") + ' de la facura en dolares del albaran ' + self.name)						
					self.with_context({'nomore':1}).write({'tc':tp[0].sale_type})
		return t


class stock_move(models.Model):
	_inherit = 'stock.move'

	price_unit_it = fields.Float('Precio Unitario',digits=(12,8))

	def write(selfs,vals):
		t = super(stock_move,selfs).write(vals)
		for self in selfs:
			if 'nomore' in self.env.context:
				pass
			else:
				if self.purchase_line_id.id and 'price_unit_it' not in vals:
					elem  = self.purchase_line_id.price_subtotal / self.purchase_line_id.product_qty if self.purchase_line_id.product_qty != 0 else 0
					elem = elem*self.purchase_line_id.product_uom.factor
					elem = elem*self.product_uom.factor_inv
					self.with_context({'nomore':1}).write({'price_unit_it':elem})

		return t

	def actualizar_priceunit(self):
		return {
			'context': {'form_view_initial_mode':'edit'},
			'name': 'Precio Unitario',
			'type': 'ir.actions.act_window',
			'res_model': 'stock.move',
			'view_mode': 'form',
			'target': 'new',
			'res_id': self.id,
			'views': [(self.env.ref('kardex_valorado_it.stockmove_editpriceunit').id, 'form')],
		}




class make_kardex_valorado(models.TransientModel):
	_name = "make.kardex.valorado"

	fini= fields.Date('Fecha inicial',required=True)
	ffin= fields.Date('Fecha final',required=True)
	products_ids=fields.Many2many('product.product','rel_wiz_kardex_valorado','product_id','kardex_id')
	location_ids=fields.Many2many('stock.location','rel_kardex_location_valorado','location_id','kardex_id','Ubicacion',required=True)
	allproducts=fields.Boolean('Todos los productos',default=True)
	destino = fields.Selection([('csv','CSV')],'Destino')
	check_fecha = fields.Boolean('Editar Fecha')
	alllocations = fields.Boolean('Todos los almacenes',default=True)

	fecha_ini_mod = fields.Date('Fecha Inicial')
	fecha_fin_mod = fields.Date('Fecha Final')
	analizador = fields.Boolean('Analizador')

	@api.onchange('fecha_ini_mod')
	def onchange_fecha_ini_mod(self):
		self.fini = self.fecha_ini_mod


	@api.onchange('fecha_fin_mod')
	def onchange_fecha_fin_mod(self):
		self.ffin = self.fecha_fin_mod


	@api.model
	def default_get(self, fields):
		res = super(make_kardex_valorado, self).default_get(fields)
		import datetime
		fecha_hoy = str(datetime.datetime.now())[:10]
		fecha_inicial = fecha_hoy[:4] + '-01-01'
		res.update({'fecha_ini_mod':fecha_inicial})
		res.update({'fecha_fin_mod':fecha_hoy})
		res.update({'fini':fecha_inicial})
		res.update({'ffin':fecha_hoy})

		#locat_ids = self.pool.get('stock.location').search(cr, uid, [('usage','in',('internal','inventory','transit','procurement','production'))])
		locat_ids = self.env['stock.location'].search([('usage','in',('internal','inventory','transit','procurement','production'))])
		locat_ids = [elemt.id for elemt in locat_ids]
		res.update({'location_ids':[(6,0,locat_ids)]})
		return res

	@api.onchange('alllocations')
	def onchange_alllocations(self):
		if self.alllocations == True:
			locat_ids = self.env['stock.location'].search( [('usage','in',('internal','inventory','transit','procurement','production'))] )
			self.location_ids = [(6,0,locat_ids.ids)]
		else:
			self.location_ids = [(6,0,[])]



	def do_popup(self):		
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




		self.env.cr.execute("""
			drop table if exists tree_view_kardex_fisico;
			create table tree_view_kardex_fisico AS
			select row_number() OVER () as id,
origen.complete_name AS u_origen,
destino.complete_name AS u_destino,
almacen.complete_name AS almacen,
vstf.motivo_guia::varchar AS t_opera,
pc.name as categoria,
coalesce(it.value,pt.name) as producto,
pp.default_code as cod_pro,
pu.name as unidad,
vstf.fecha as fecha,
sp.name as doc_almacen,
vstf.entrada as entrada,
vstf.salida as salida
from
(
select vst_kardex_fisico.date::date as fecha,vst_kardex_fisico.location_id as origen, vst_kardex_fisico.location_dest_id as destino, vst_kardex_fisico.location_dest_id as almacen, vst_kardex_fisico.product_qty as entrada, 0 as salida,vst_kardex_fisico.id  as stock_move,vst_kardex_fisico.guia as motivo_guia,vst_kardex_fisico.product_id,vst_kardex_fisico.estado from vst_kardex_fisico
join stock_move sm on sm.id = vst_kardex_fisico.id
join stock_picking sp on sm.picking_id = sp.id
join stock_location l_o on l_o.id = vst_kardex_fisico.location_id
join stock_location l_d on l_d.id = vst_kardex_fisico.location_dest_id
where ( (l_o.usage = 'internal' and l_o.usage = 'internal' )  or ( l_o.usage != 'internal' or l_o.usage != 'internal' ) )
union all
select vst_kardex_fisico.date::date as fecha,vst_kardex_fisico.location_id as origen, vst_kardex_fisico.location_dest_id as destino, vst_kardex_fisico.location_id as almacen, 0 as entrada, vst_kardex_fisico.product_qty as salida,vst_kardex_fisico.id  as stock_move ,vst_kardex_fisico.guia as motivo_guia ,vst_kardex_fisico.product_id ,vst_kardex_fisico.estado from vst_kardex_fisico
) as vstf
inner join stock_location origen on origen.id = vstf.origen
inner join stock_location destino on destino.id = vstf.destino
inner join stock_location almacen on almacen.id = vstf.almacen
inner join product_product pp on pp.id = vstf.product_id
inner join product_template pt on pt.id = pp.product_tmpl_id
inner join product_category pc on pc.id = pt.categ_id
inner join uom_uom pu on pu.id = pt.uom_id
inner join stock_move sm on sm.id = vstf.stock_move
inner join stock_picking sp on sp.id = sm.picking_id
left join ir_translation it ON pt.id = it.res_id and it.name = 'product.template,name' and it.lang = 'es_PE' and it.state = 'translated'
where vstf.fecha >='""" +str(date_ini)+ """' and vstf.fecha <='""" +str(date_fin)+ """'
and vstf.product_id in """ +str(tuple(s_prod))+ """
and vstf.almacen in """ +str(tuple(s_loca))+ """
and vstf.estado = 'done'
and almacen.usage = 'internal'
order by
almacen.id,pp.id,vstf.fecha,vstf.entrada desc;
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
				almacen AS "Almacen"

				from get_kardex_v("""+ str(date_ini).replace('-','') + "," + str(date_fin).replace('-','') + ",'" + productos + """'::INT[], '""" + almacenes + """'::INT[]) 
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
			lst_locations = self.env['stock.location'].search([]).ids

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

				--fecha_albaran as "Fecha Alb.",	
				fecha as "Fecha",
				type_doc as "T. Doc.",
				serial as "Serie",
				nro as "Nro. Documento",
				numdoc_cuadre as "Nro. Documento",
				doc_partner as "Nro Doc. Partner",
				name as "Proveedor",							
				operation_type as "Tipo de operacion",				 
				name_template as "Producto",
				default_code as "Cod. Producto",
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
				almacen AS "Almacen"

				from get_kardex_v("""+ str(date_ini).replace('-','') + "," + str(date_fin).replace('-','') + ",'" + productos + """'::INT[], '""" + almacenes + """'::INT[]) 


) to '"""+direccion+u"""kardex.csv'  WITH DELIMITER ',' CSV HEADER
		"""
		
		self.env.cr.execute(cadf)
		import gzip
		import shutil

		f = open(direccion+'kardex.csv', 'rb')

		return self.env['popup.it'].get_file('Kardex_Fisico.csv',base64.encodestring(b''.join(f.readlines())))






class update_sql_valorado(models.Model):
	_name = 'update.sql.valorado'

	_auto = False

	def init(self):
		self._cr.execute("""


CREATE OR REPLACE FUNCTION fecha_num(date)
	RETURNS integer AS
$BODY$
		SELECT to_char($1, 'YYYYMMDD')::integer;
$BODY$
	LANGUAGE sql VOLATILE
	COST 100;


CREATE OR REPLACE FUNCTION public.getserial("number" character varying)
		RETURNS character varying AS
	$BODY$
	DECLARE
	number1 ALIAS FOR $1;
	res varchar;
	BEGIN
		 select substring(number1,0,position('-' in number1)) into res;
		 return res;  
	END;$BODY$
		LANGUAGE plpgsql VOLATILE
		COST 100;

	CREATE OR REPLACE FUNCTION public.getnumber("number" character varying)
			RETURNS character varying AS
		$BODY$
		DECLARE
		number1 ALIAS FOR $1;
		res varchar;
		BEGIN
			 select substring(number1,position('-' in number1)+1) into res;
			 return res;  
		END;$BODY$
			LANGUAGE plpgsql VOLATILE
			COST 100;




	CREATE OR REPLACE FUNCTION public.getperiod(
		move_id integer,
		date_picking date,
		special boolean)
	RETURNS character varying AS
$BODY$
DECLARE
move_id1 ALIAS FOR $1;
date_picking1 ALIAS FOR $2;
res varchar;
isspecial alias for special;
BEGIN
		IF move_id1 !=0 THEN
	select account_period.name into res from account_move 
	inner join account_period on account_period.date_start <= account_move.date and account_period.date_stop >= account_move.date  and account_period.special = account_move.fecha_specia
	where account_move.id=move_id1;
		ELSE 
	select account_period.name into res from account_period
	where date_start<=date_picking1 and date_stop>=date_picking1 and account_period.special=isspecial;
	 END IF;
	 return res;  
END;$BODY$
	LANGUAGE plpgsql VOLATILE
	COST 100;



	CREATE OR REPLACE FUNCTION public.getperiod(
		date_picking timestamp without time zone,
		special boolean)
	RETURNS character varying AS
$BODY$
DECLARE
date_picking1 ALIAS FOR $1;
res varchar;
isspecial alias for $2;
BEGIN
	select account_period.name into res from account_period
	where date_start<=date_picking1 and date_stop>=date_picking1 and account_period.special=isspecial;
	 return res;  
END;$BODY$
	LANGUAGE plpgsql VOLATILE
	COST 100;



CREATE OR REPLACE VIEW vst_kardex_fisico1 AS 
 SELECT stock_move.product_uom, 
        CASE
            WHEN sl.usage::text = 'supplier'::text THEN 0::double precision
            ELSE 
            CASE
                WHEN original.id <> uomt.id THEN round((stock_move.price_unit_it * original.factor::double precision / uomt.factor::double precision)::numeric, 6)::double precision
                ELSE stock_move.price_unit_it
            END
        END AS price_unit, 
        CASE
            WHEN uom_uom.id <> uomt.id THEN round((stock_move.product_uom_qty::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
            ELSE stock_move.product_uom_qty
        END AS product_qty, 
    stock_move.location_id, stock_move.location_dest_id, 
    stock_move.picking_type_id, stock_move.product_id, stock_move.picking_id, 
    stock_picking.invoice_id AS invoice_id, 
        CASE
            WHEN stock_picking.use_kardex_date THEN stock_picking.kardex_date::timestamp without time zone
            ELSE 
            coalesce( invoice.invoice_date::timestamp without time zone,stock_picking.kardex_date::timestamp without time zone)
        END AS date, 
    stock_picking.name, stock_picking.partner_id, 
    case when tok.id is not null then tok.code || '-' || tok.name else '' end AS guia, null::text as analitic_id, stock_move.id, 
    product_product.default_code, stock_move.state AS estado,



l_o.complete_name AS u_origen,
l_o.usage as usage_origen,
l_d.complete_name AS u_destino,
l_d.usage as usage_destino,
pc.name as categoria,
pc.id as categoria_id,
pname.new_name  as producto,
product_product.default_code as cod_pro,
uomt.name as unidad



   FROM stock_move
   join uom_uom ON stock_move.product_uom = uom_uom.id
   join stock_location l_o on l_o.id = stock_move.location_id
   join stock_location l_d on l_d.id = stock_move.location_dest_id
   JOIN stock_picking ON stock_move.picking_id = stock_picking.id
    left join account_move as invoice on invoice.id = stock_picking.invoice_id
   JOIN stock_picking_type ON stock_picking.picking_type_id = stock_picking_type.id
   JOIN stock_location sl ON sl.id = stock_move.location_dest_id
   JOIN product_product ON stock_move.product_id = product_product.id
   LEFT JOIN (
   select t_pp.id, (max(t_pt.name)::varchar || ' ' || replace(array_agg(pav.name)::varchar,'{NULL}',''))::varchar as new_name from product_product t_pp
inner join product_template t_pt on t_pp.product_tmpl_id = t_pt.id
left join product_variant_combination pvc on pvc.product_product_id = t_pp.id
left join product_template_attribute_value ptav on ptav.id = pvc.product_template_attribute_value_id
left join product_attribute_value pav on pav.id = ptav.product_attribute_value_id
group by t_pp.id
   ) as pname on pname.id = product_product.id
   JOIN product_template ON product_product.product_tmpl_id = product_template.id
left join ir_translation it ON product_template.id = it.res_id and it.name = 'product.template,name' and it.lang = 'es_PE' and it.state = 'translated'
  inner join product_category pc on pc.id = product_template.categ_id
   join uom_uom uomt ON uomt.id = product_template.uom_id
   join uom_uom original ON original.id = product_template.uom_id
   LEFT JOIN type_operation_kardex tok ON stock_picking.type_operation_sunat_id = tok.id
  WHERE (stock_move.state::text = ANY (ARRAY['done'::text, 'assigned'::text])) AND product_template.type::text = 'product'::text AND stock_move.picking_id IS NOT NULL ;

-- DROP VIEW public.vst_kardex_fisico_gastos_vinculados;




CREATE OR REPLACE VIEW public.vst_kardex_fisico1 AS 
 SELECT stock_move.product_uom,
        CASE
            WHEN sl.usage::text = 'supplier'::text THEN 0::double precision
            ELSE
            CASE
                WHEN uom_uom.id <> uomt.id THEN round((stock_move.price_unit_it::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)::double precision
                ELSE stock_move.price_unit_it::double precision
            END
        END AS price_unit,
        CASE
            WHEN uom_uom.id <> uomt.id THEN round((sml.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
            ELSE sml.qty_done
        END AS product_qty,
    sml.location_id,
    sml.location_dest_id,
    stock_move.picking_type_id,
    stock_move.product_id,
    stock_move.picking_id,
    stock_picking.invoice_id,
        CASE
            WHEN stock_picking.use_kardex_date THEN stock_picking.kardex_date
            ELSE COALESCE(invoice.invoice_date::timestamp without time zone, stock_picking.kardex_date)
        END AS date,
    stock_picking.name,
    stock_picking.partner_id,
        CASE
            WHEN tok.id IS NOT NULL THEN (tok.code::text || '-'::text) || tok.name::text
            ELSE ''::text
        END AS guia,
    aaait.name::text AS analitic_id,
    stock_move.id,
    product_product.default_code,
    stock_move.state AS estado,
    l_o.complete_name AS u_origen,
    l_o.usage AS usage_origen,
    l_d.complete_name AS u_destino,
    l_d.usage AS usage_destino,
    pc.name AS categoria,
    pc.id AS categoria_id,
    pname.new_name AS producto,
    product_product.default_code AS cod_pro,
    uomt.name AS unidad
   FROM stock_move
    JOIN stock_move_line sml on sml.move_id = stock_move.id
     JOIN uom_uom ON stock_move.product_uom = uom_uom.id
     JOIN stock_location l_o ON l_o.id = sml.location_id
     JOIN stock_location l_d ON l_d.id = sml.location_dest_id
     JOIN stock_picking ON stock_move.picking_id = stock_picking.id
     LEFT JOIN account_move invoice ON invoice.id = stock_picking.invoice_id
     JOIN stock_picking_type ON stock_picking.picking_type_id = stock_picking_type.id
     JOIN stock_location sl ON sl.id = sml.location_dest_id
     JOIN product_product ON stock_move.product_id = product_product.id
     LEFT JOIN ( SELECT t_pp.id,
            ((     coalesce(max(it.value),max(t_pt.name::text))::character varying::text || ' '::text) || replace(array_agg(pav.name)::character varying::text, '{NULL}'::text, ''::text))::character varying AS new_name
           FROM product_product t_pp
             JOIN product_template t_pt ON t_pp.product_tmpl_id = t_pt.id
			 left join ir_translation it ON t_pt.id = it.res_id and it.name = 'product.template,name' and it.lang = 'es_PE' and it.state = 'translated'
             LEFT JOIN product_variant_combination pvc ON pvc.product_product_id = t_pp.id
             LEFT JOIN product_template_attribute_value ptav ON ptav.id = pvc.product_template_attribute_value_id
             LEFT JOIN product_attribute_value pav ON pav.id = ptav.product_attribute_value_id
          GROUP BY t_pp.id) pname ON pname.id = product_product.id
     JOIN product_template ON product_product.product_tmpl_id = product_template.id
     LEFT JOIN ir_translation it ON product_template.id = it.res_id AND it.name::text = 'product.template,name'::text AND it.lang::text = 'es_PE'::text AND it.state::text = 'translated'::text
     JOIN product_category pc ON pc.id = product_template.categ_id
     JOIN uom_uom uomt ON uomt.id = product_template.uom_id
     JOIN uom_uom original ON original.id = product_template.uom_id
     left join account_analytic_account aaait on aaait.id = stock_move.analytic_account_id
     LEFT JOIN type_operation_kardex tok ON stock_picking.type_operation_sunat_id = tok.id
  WHERE (stock_move.state::text = ANY (ARRAY['done'::text, 'assigned'::text])) AND product_template.type::text = 'product'::text AND stock_move.picking_id IS NOT NULL  and  coalesce(stock_picking.no_mostrar,false) = false
 union all

select 
sm.product_uom,

        CASE
                WHEN uom_uom.id <> uomt.id THEN round((sm.price_unit_it::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)::double precision
                ELSE sm.price_unit_it::double precision
            
        END AS price_unit,
        CASE
            WHEN uom_uom.id <> uomt.id THEN round((sml.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
            ELSE sml.qty_done
        END AS product_qty,
        sls.id as location_id,
        sld.id as location_dest_id,
        sm.picking_type_id,
        sm.product_id,
        null::integer as picking_id,
        null::integer as invoice_id,
        sm.date as date,
        sm.name as name,
        null::integer as partner_id,
        ''::text as guia,
        aaait.name::text as analitic_id,
        sm.id,
        pp.default_code,
        sm.state as estado,
        sls.complete_name as u_origen,
        sls.usage as usage_origen,
        sld.complete_name as u_destino,
        sld.usage as usage_destino,
        pc.name as categoria,
        pc.id as categoria_id,
    	pname.new_name AS producto,
        pp.default_code as cod_pro,
        uomt.name as unidad
from stock_move sm 
     JOIN uom_uom ON sm.product_uom = uom_uom.id
inner join stock_move_line sml on sml.move_id = sm.id
inner join product_product pp on pp.id = sml.product_id
     LEFT JOIN ( SELECT t_pp.id,
            ((     coalesce(max(it.value),max(t_pt.name::text))::character varying::text || ' '::text) || replace(array_agg(pav.name)::character varying::text, '{NULL}'::text, ''::text))::character varying AS new_name
           FROM product_product t_pp
             JOIN product_template t_pt ON t_pp.product_tmpl_id = t_pt.id
			 left join ir_translation it ON t_pt.id = it.res_id and it.name = 'product.template,name' and it.lang = 'es_PE' and it.state = 'translated'
             LEFT JOIN product_variant_combination pvc ON pvc.product_product_id = t_pp.id
             LEFT JOIN product_template_attribute_value ptav ON ptav.id = pvc.product_template_attribute_value_id
             LEFT JOIN product_attribute_value pav ON pav.id = ptav.product_attribute_value_id
          GROUP BY t_pp.id) pname ON pname.id = pp.id
inner join product_template pt on pt.id = pp.product_tmpl_id
left join ir_translation it on pt.id = it.res_id and it.name = 'product.template,name' and it.lang = 'es_PE' and it.state = 'translated'
inner join product_category pc on pc.id = pt.categ_id
inner join uom_uom uomt on uomt.id = pt.uom_id
     left join account_analytic_account aaait on aaait.id = sm.analytic_account_id
inner join stock_location sls on sls.id = sml.location_id
inner join stock_location sld on sld.id = sml.location_dest_id where sm.state = 'done' and sm.picking_type_id is null and sm.picking_id is null
;

DROP VIEW IF EXISTS public.vst_kardex_fisico_gastos_vinculados cascade;

CREATE OR REPLACE VIEW public.vst_kardex_fisico_gastos_vinculados AS 
select aml.product_uom_id as product_uom,
	NULL::integer AS move_dest_id,
	aml.debit+aml.credit as price_unit,
	0 as product_qty,
	NULL::integer AS location_id,
	aml.location_id as location_dest_id,
	NULL::integer as picking_type_id,
	aml.product_id as product_id,
	NULL::integer AS picking_id,
	NULL::integer AS invoice_id,
	CASE WHEN COALESCE(am.check_use_date_kardex,false) then am.date_kardex + interval '1 second' else
        am.date::timestamp + interval '5 hours' end AS date,
        am.ref AS name,        
    am.partner_id as partner_id,    
    '00'::character varying(4) AS guia,    
    aaa.name::text AS analitic_id,    
    T.id::integer AS id,
    
    pp.default_code,
    'done'::character varying AS estado,
    --slo.complete_name AS u_origen,
    ''::varchar AS u_origen,
    sl.complete_name AS u_destino,
    --slo.usage AS usage_origen,
    ''::varchar AS usage_origen,
    sl.usage AS usage_destino,
    pct.name AS categoria,
    pt.categ_id AS categoria_id,
    COALESCE(it.value, pt.name::text)::character varying AS producto,
    pp.default_code AS cod_pro,
    uomt.name AS unidad
    
 from account_move am
inner join account_move_line aml on aml.move_id = am.id
left join account_analytic_account aaa on aaa.id = aml.analytic_account_id
inner join (
	select product_id, company_id, min(id) as id from stock_move 
	where state = 'done'
	group by product_id, company_id
) T on T.product_id = aml.product_id and T.company_id = am.company_id

     JOIN product_product pp ON pp.id = aml.product_id
     JOIN product_template pt ON pt.id = pp.product_tmpl_id
     JOIN stock_location sl ON sl.id = aml.location_id
     JOIN product_category pct ON pt.categ_id = pct.id
     JOIN uom_uom uomt ON uomt.id = pt.uom_id
     JOIN main_parameter mpit on mpit.company_id = am.company_id
     LEFT JOIN ir_translation it ON pt.id = it.res_id AND it.name::text = 'product.template,name'::text AND it.lang::text = 'es_PE'::text AND it.state::text = 'translated'::text
     where aml.location_id is not null and am.state in ('posted')

union all

 SELECT pt.uom_id AS product_uom,
    NULL::integer AS move_dest_id,
    gvdd.flete AS price_unit,
    0 AS product_qty,
    NULL::integer AS location_id,
    sl.id AS location_dest_id,
    sp.picking_type_id,
    pp.id AS product_id,
    NULL::integer AS picking_id,
    NULL::integer AS invoice_id,
        CASE WHEN COALESCE(mpit.check_gastos_vinculados,false) then sp.kardex_date + interval '1 second' else
        gvd.date_kardex::timestamp  end AS date,
        gvd.name AS name,
    sp.partner_id as partner_id,
    '00'::character varying(4) AS guia,
    aaait.name::text AS analitic_id,
    gvdd.stock_move_id::integer AS id,
    pp.default_code,
    'done'::character varying AS estado,
    --slo.complete_name AS u_origen,
    ''::varchar AS u_origen,
    sl.complete_name AS u_destino,
    --slo.usage AS usage_origen,
    ''::varchar AS usage_origen,
    sl.usage AS usage_destino,
    pct.name AS categoria,
    pt.categ_id AS categoria_id,
    COALESCE(it.value, pt.name::text)::character varying AS producto,
    pp.default_code AS cod_pro,
    uomt.name AS unidad
   FROM landed_cost_it gvd
     JOIN landed_cost_it_line gvdd ON gvdd.gastos_id = gvd.id
     JOIN stock_move sm ON gvdd.stock_move_id = sm.id
     JOIN stock_picking sp ON sp.id = sm.picking_id
     JOIN product_product pp ON pp.id = sm.product_id
     JOIN product_template pt ON pt.id = pp.product_tmpl_id
     JOIN stock_location sl ON sl.id = sp.location_dest_id
     JOIN stock_location slo ON slo.id = sp.location_id
     JOIN product_category pct ON pt.categ_id = pct.id
     JOIN uom_uom uomt ON uomt.id = pt.uom_id
     JOIN main_parameter mpit on mpit.company_id = sm.company_id
     left join account_analytic_account aaait on aaait.id = sm.analytic_account_id
     LEFT JOIN ir_translation it ON pt.id = it.res_id AND it.name::text = 'product.template,name'::text AND it.lang::text = 'es_PE'::text AND it.state::text = 'translated'::text
  WHERE gvd.state::text = 'done'::text;


-- View: vst_kardex_fisico_proc_1

-- DROP VIEW vst_kardex_fisico_proc_1;


CREATE OR REPLACE VIEW public.vst_kardex_fisico_proc_1 AS 
 SELECT k.origen,
    k.destino,
    k.serial,
    k.nro,
    k.cantidad,
    k.producto,
    k.fecha,
    k.id_origen,
    k.id_destino,
    k.product_id,
    k.id,
    k.categoria,
    k.name,
    k.unidad,
    k.default_code,
    k.price_unit,
    k.currency_rate,
    k.invoice_id,
    k.periodo,
    k.ctanalitica,
    k.operation_type,
    k.doc_type_ope,
    k.category_id,
    k.stock_doc,
    k.type_doc,
    k.numdoc_cuadre,
    k.nro_documento,
    (aa_cp.code::text || ' - '::text) || aa_cp.name::text AS product_account,
    k.u_origen,
    k.u_destino,
    k.usage_origen,
    k.usage_destino
   FROM ( SELECT vst_stock_move.u_origen AS origen,
            vst_stock_move.u_destino AS destino,
                CASE
                    WHEN vst_stock_move.location_id IS NULL THEN getserial(vst_stock_move.name)
                    ELSE getserial(account_invoice.ref)
                END AS serial,
                CASE
                    WHEN vst_stock_move.location_id IS NULL THEN getnumber(vst_stock_move.name)
                    ELSE
                    CASE
                        WHEN vst_stock_move.invoice_id <> 0 AND vst_stock_move.location_id IS NOT NULL THEN getnumber(account_invoice.ref)::character varying(10)
                        ELSE ''::character varying
                    END
                END AS nro,
            vst_stock_move.product_qty AS cantidad,
            vst_stock_move.producto,
            vst_stock_move.date AS fecha,
            vst_stock_move.location_id AS id_origen,
            vst_stock_move.location_dest_id AS id_destino,
            vst_stock_move.product_id,
            vst_stock_move.id,
            vst_stock_move.categoria,
                CASE
                    WHEN vst_stock_move.invoice_id = 0 OR vst_stock_move.invoice_id IS NULL THEN res_partner.name
                    ELSE rp.name
                END AS name,
            vst_stock_move.unidad,
            vst_stock_move.cod_pro AS default_code,
                CASE
                    WHEN vst_stock_move.location_id IS NOT NULL THEN vst_stock_move.price_unit * COALESCE(sp.tc, 1::numeric)::double precision
                    ELSE vst_stock_move.price_unit::double precision
                END AS price_unit,
            sp.tc AS currency_rate,
            vst_stock_move.invoice_id,
            account_period.name AS periodo,
            vst_stock_move.analitic_id::character varying AS ctanalitica,
            lpad(vst_stock_move.guia, 2, '0'::text)::character varying AS operation_type,
            lpad(
                CASE
                    WHEN vst_stock_move.location_id IS NULL THEN it_type_document.code
                    ELSE it_type_document.code
                END::text, 2, '0'::text) AS doc_type_ope,
            vst_stock_move.categoria_id AS category_id,
                CASE
                    WHEN vst_stock_move.location_id IS NULL THEN ''::character varying
                    ELSE vst_stock_move.name
                END AS stock_doc,
                CASE
                    WHEN vst_stock_move.location_id IS NULL AND vst_stock_move.picking_type_id IS NULL THEN it_type_document.code
                    ELSE
                    CASE
                        WHEN vst_stock_move.location_id IS NULL THEN it_type_document.code
                        ELSE it_type_document.code
                    END
                END AS type_doc,
            vst_stock_move.name AS numdoc_cuadre,
            res_partner.vat AS nro_documento,
            vst_stock_move.u_origen,
            vst_stock_move.u_destino,
            vst_stock_move.usage_origen,
            vst_stock_move.usage_destino,
            sm.company_id
           FROM ( SELECT vst_kardex_fisico.product_uom,
                    vst_kardex_fisico.price_unit,
                    vst_kardex_fisico.product_qty,
                    vst_kardex_fisico.location_id,
                    vst_kardex_fisico.location_dest_id,
                    vst_kardex_fisico.picking_type_id,
                    vst_kardex_fisico.product_id,
                    vst_kardex_fisico.picking_id,
                    vst_kardex_fisico.invoice_id,
                    vst_kardex_fisico.date,
                    vst_kardex_fisico.name,
                    vst_kardex_fisico.partner_id,
                    vst_kardex_fisico.guia,
                    vst_kardex_fisico.analitic_id,
                    vst_kardex_fisico.id,
                    vst_kardex_fisico.default_code,
                    vst_kardex_fisico.estado,
                    NULL::integer AS move_dest_id,
                    vst_kardex_fisico.u_origen,
                    vst_kardex_fisico.u_destino,
                    vst_kardex_fisico.usage_origen,
                    vst_kardex_fisico.usage_destino,
                    vst_kardex_fisico.categoria,
                    vst_kardex_fisico.categoria_id,
                    vst_kardex_fisico.producto,
                    vst_kardex_fisico.cod_pro,
                    vst_kardex_fisico.unidad
                   FROM vst_kardex_fisico() vst_kardex_fisico(product_uom, price_unit, product_qty, location_id, location_dest_id, picking_type_id, product_id, picking_id, invoice_id, date, name, partner_id, guia, analitic_id, id, default_code, estado, u_origen, usage_origen, u_destino, usage_destino, categoria, categoria_id, producto, cod_pro, unidad)
                UNION ALL
                 SELECT kfgv.product_uom,
                    kfgv.price_unit,
                    kfgv.product_qty,
                    kfgv.location_id,
                    kfgv.location_dest_id,
                    kfgv.picking_type_id,
                    kfgv.product_id,
                    kfgv.picking_id,
                    kfgv.invoice_id,
                    kfgv.date,
                    kfgv.name,
                    kfgv.partner_id,
                    kfgv.guia,
                    kfgv.analitic_id,
                    kfgv.id,
                    kfgv.default_code,
                    kfgv.estado,
                    kfgv.move_dest_id,
                    kfgv.u_origen,
                    kfgv.u_destino,
                    kfgv.usage_origen,
                    kfgv.usage_destino,
                    kfgv.categoria,
                    kfgv.categoria_id,
                    kfgv.producto,
                    kfgv.cod_pro,
                    kfgv.unidad
                   FROM vst_kardex_fisico_gastos_vinculados kfgv) vst_stock_move
             LEFT JOIN account_move account_invoice ON account_invoice.id = vst_stock_move.invoice_id
             LEFT JOIN res_partner rp_i ON rp_i.id = vst_stock_move.partner_id
             LEFT JOIN res_partner ON res_partner.id =
                CASE
                    WHEN rp_i.parent_id IS NOT NULL THEN rp_i.parent_id
                    ELSE rp_i.id
                END
             LEFT JOIN res_partner rp_i2 ON rp_i2.id = account_invoice.partner_id
             LEFT JOIN res_partner rp ON rp.id =
                CASE
                    WHEN rp_i2.parent_id IS NOT NULL THEN rp_i2.parent_id
                    ELSE rp_i2.id
                END
             LEFT JOIN stock_move sm ON sm.id = vst_stock_move.id
             LEFT JOIN stock_picking sp ON sp.id = sm.picking_id
             LEFT JOIN purchase_order_line pol ON pol.id = sm.purchase_line_id
             LEFT JOIN purchase_order po ON po.id = pol.order_id
             LEFT JOIN sale_order so ON so.procurement_group_id = sp.group_id
             LEFT JOIN product_pricelist pplist ON pplist.id = so.pricelist_id
             LEFT JOIN account_period ON account_period.date_start <= vst_stock_move.date AND account_period.date_end >= vst_stock_move.date AND COALESCE(account_period.is_opening_close, false) = false
             LEFT JOIN einvoice_catalog_01 it_type_document ON account_invoice.type_document_id = it_type_document.id
          WHERE vst_stock_move.estado::text = 'done'::text) k
     LEFT JOIN ( SELECT "substring"(ir_property.res_id::text, "position"(ir_property.res_id::text, ','::text) + 1)::integer AS categ_id,ir_property.company_id,
            "substring"(ir_property.value_reference::text, "position"(ir_property.value_reference::text, ','::text) + 1)::integer AS account_id
           FROM ir_property
          WHERE ir_property.name::text = 'property_stock_valuation_account_id'::text) j ON k.category_id = j.categ_id and j.company_id = k.company_id
     LEFT JOIN account_account aa_cp ON j.account_id = aa_cp.id;





CREATE OR REPLACE VIEW public.vst_kardex_fisico_proc_2 AS
 SELECT vst_kardex_fis_1.id,
		vst_kardex_fis_1.origen,
		vst_kardex_fis_1.destino,
		vst_kardex_fis_1.serial,
		vst_kardex_fis_1.nro,
		vst_kardex_fis_1.cantidad AS ingreso,
		0::numeric AS salida,
		0::numeric AS saldof,
		vst_kardex_fis_1.producto,
		vst_kardex_fis_1.fecha,
		vst_kardex_fis_1.id_origen,
		vst_kardex_fis_1.id_destino,
		vst_kardex_fis_1.product_id,
		vst_kardex_fis_1.id_destino AS location_id,
		vst_kardex_fis_1.destino AS almacen,
		vst_kardex_fis_1.categoria,
		vst_kardex_fis_1.name,
		'in'::text AS type,
		'ingreso'::text AS esingreso,
		vst_kardex_fis_1.default_code,
		vst_kardex_fis_1.unidad,
				CASE
						WHEN vst_kardex_fis_1.invoice_id IS NULL AND vst_kardex_fis_1.price_unit > 0::double precision AND coalesce(vst_kardex_fis_1.cantidad,0) = 0 --AND vst_kardex_fis_1.id IS NULL 
						      THEN vst_kardex_fis_1.price_unit
						ELSE
						CASE
					WHEN vst_kardex_fis_1.invoice_id is not null and vst_kardex_fis_1.id_origen is null then vst_kardex_fis_1.price_unit
								WHEN false THEN vst_kardex_fis_1.price_unit
								ELSE
								CASE
										WHEN btrim(vst_kardex_fis_1.type_doc::text) = '07'::text THEN vst_kardex_fis_1.price_unit * vst_kardex_fis_1.cantidad::double precision
										ELSE vst_kardex_fis_1.price_unit * vst_kardex_fis_1.cantidad::double precision
								END
						END
				END AS debit,
				CASE
						WHEN vst_kardex_fis_1.invoice_id IS NULL AND vst_kardex_fis_1.price_unit < 0::double precision AND vst_kardex_fis_1.id IS NULL THEN - vst_kardex_fis_1.price_unit::numeric
						ELSE 0::numeric
				END AS credit,
		0::numeric AS saldov,
				CASE
						WHEN btrim(vst_kardex_fis_1.type_doc::text) = '07'::text THEN vst_kardex_fis_1.price_unit
						ELSE vst_kardex_fis_1.price_unit
				END AS cadquiere,
		0::numeric AS cprom,
		vst_kardex_fis_1.periodo,
		vst_kardex_fis_1.ctanalitica,
		vst_kardex_fis_1.operation_type,
		vst_kardex_fis_1.doc_type_ope,
		vst_kardex_fis_1.product_account,
		vst_kardex_fis_1.stock_doc,
		vst_kardex_fis_1.type_doc,
		vst_kardex_fis_1.numdoc_cuadre,
		vst_kardex_fis_1.nro_documento
	 FROM vst_kardex_fisico_proc_1 vst_kardex_fis_1
	WHERE usage_destino::text = 'internal'::text AND (COALESCE(usage_destino::text, ''::text) = 'internal'::text AND COALESCE(usage_origen::text, ''::text) = 'internal'::text  OR COALESCE(usage_destino::text, ''::text) <> 'internal'::text OR COALESCE(usage_origen::text, ''::text) <> 'internal'::text)
UNION ALL
 SELECT vst_kardex_fis_1.id,
		vst_kardex_fis_1.origen,
		vst_kardex_fis_1.destino,
		vst_kardex_fis_1.serial,
		vst_kardex_fis_1.nro,
		0::numeric AS ingreso,
		vst_kardex_fis_1.cantidad AS salida,
		0::numeric AS saldof,
		vst_kardex_fis_1.producto,
		vst_kardex_fis_1.fecha,
		vst_kardex_fis_1.id_origen,
		vst_kardex_fis_1.id_destino,
		vst_kardex_fis_1.product_id,
		vst_kardex_fis_1.id_origen AS location_id,
		vst_kardex_fis_1.origen AS almacen,
		vst_kardex_fis_1.categoria,
		vst_kardex_fis_1.name,
		'out'::text AS type,
		'salida'::text AS esingreso,
		vst_kardex_fis_1.default_code,
		vst_kardex_fis_1.unidad,
		0::numeric AS debit,
		0::numeric AS credit,
		0::numeric AS saldov,
		0::numeric AS cadquiere,
		0::numeric AS cprom,
		vst_kardex_fis_1.periodo,
		vst_kardex_fis_1.ctanalitica,
		vst_kardex_fis_1.operation_type,
		vst_kardex_fis_1.doc_type_ope,
		vst_kardex_fis_1.product_account,
		vst_kardex_fis_1.stock_doc,
		vst_kardex_fis_1.type_doc,
		vst_kardex_fis_1.numdoc_cuadre,
		vst_kardex_fis_1.nro_documento
	 FROM vst_kardex_fisico_proc_1 vst_kardex_fis_1
	WHERE usage_origen::text = 'internal'::text;












CREATE OR REPLACE VIEW vst_kardex_fisico_valorado AS 
 SELECT t.almacen, t.categoria, t.producto, t.fecha, t.periodo, t.ctanalitica, 
		t.serial, t.nro, t.operation_type, t.name, t.ingreso, t.salida, 
		0::numeric AS saldof, t.debit::numeric AS debit, t.credit, 
		t.cadquiere::numeric AS cadquiere, 0::numeric AS saldov, 
		0::numeric AS cprom, t.type::character varying AS type, t.esingreso, 
		t.product_id, t.location_id, t.doc_type_ope, t.stock_moveid, 
		t.product_account, t.default_code, t.unidad, t.stock_doc, t.origen, 
		t.destino, t.type_doc, t.numdoc_cuadre, t.nro_documento, t.invoicelineid, 
		t.id_origen, t.id_destino
	 FROM ( SELECT vst_kardex_fis_1_1.almacen, vst_kardex_fis_1_1.categoria, 
						vst_kardex_fis_1_1.producto, 
						vst_kardex_fis_1_1.fecha AS fecha, vst_kardex_fis_1_1.periodo, 
						vst_kardex_fis_1_1.ctanalitica, vst_kardex_fis_1_1.serial, 
						vst_kardex_fis_1_1.nro, vst_kardex_fis_1_1.operation_type, 
						vst_kardex_fis_1_1.name, vst_kardex_fis_1_1.ingreso, 
						vst_kardex_fis_1_1.salida, vst_kardex_fis_1_1.debit, 
						vst_kardex_fis_1_1.credit, vst_kardex_fis_1_1.type, 
						vst_kardex_fis_1_1.esingreso, vst_kardex_fis_1_1.product_id, 
						vst_kardex_fis_1_1.location_id, vst_kardex_fis_1_1.cadquiere, 
						vst_kardex_fis_1_1.doc_type_ope::character varying AS doc_type_ope, 
						vst_kardex_fis_1_1.origen, vst_kardex_fis_1_1.destino, 
						vst_kardex_fis_1_1.id_origen, vst_kardex_fis_1_1.id_destino, 
						vst_kardex_fis_1_1.id AS stock_moveid, 
						vst_kardex_fis_1_1.product_account, vst_kardex_fis_1_1.default_code, 
						vst_kardex_fis_1_1.unidad, vst_kardex_fis_1_1.stock_doc, 
						vst_kardex_fis_1_1.type_doc, vst_kardex_fis_1_1.numdoc_cuadre, 
						vst_kardex_fis_1_1.nro_documento, 0 AS invoicelineid
					 FROM vst_kardex_fisico_proc_2 vst_kardex_fis_1_1) t
	ORDER BY t.almacen, t.producto, t.periodo, t.fecha, t.esingreso;











CREATE OR REPLACE FUNCTION get_kardex_v(IN date_ini integer, IN date_end integer, IN productos integer[], IN almacenes integer[], OUT almacen character varying, OUT categoria character varying, OUT name_template character varying, OUT fecha timestamp without time zone, OUT periodo character varying, OUT ctanalitica character varying, OUT serial character varying, OUT nro character varying, OUT operation_type character varying, OUT name character varying, OUT ingreso numeric, OUT salida numeric, OUT saldof numeric, OUT debit numeric, OUT credit numeric, OUT cadquiere numeric, OUT saldov numeric, OUT cprom numeric, OUT type character varying, OUT esingreso text, OUT product_id integer, OUT location_id integer, OUT doc_type_ope character varying, OUT ubicacion_origen integer, OUT ubicacion_destino integer, OUT stock_moveid integer, OUT account_invoice character varying, OUT product_account character varying, OUT default_code character varying, OUT unidad character varying, OUT mrpname character varying, OUT ruc character varying, OUT comapnyname character varying, OUT cod_sunat character varying, OUT tipoprod character varying, OUT coduni character varying, OUT metodo character varying, OUT cu_entrada numeric, OUT cu_salida numeric, OUT period_name character varying, OUT stock_doc character varying, OUT origen character varying, OUT destino character varying, OUT type_doc character varying, OUT numdoc_cuadre character varying, OUT doc_partner character varying, OUT fecha_albaran timestamp without time zone, OUT pedido_compra character varying, OUT licitacion character varying, OUT doc_almac character varying, OUT lote character varying, OUT correlativovisual integer)
	RETURNS SETOF record AS
$BODY$  
DECLARE 
	location integer;
	product integer;
	precprom numeric;
	h record;
	h1 record;
	hproduct record;
	h2 record;
	dr record;
	pt record;
	il record;
	loc_id integer;
	prod_id integer;
	contador integer;
	lote_idmp varchar;
	avanceop integer;
	
BEGIN

	select res_partner.name,res_partner.vat as nro_documento from res_company 
	inner join res_partner on res_company.partner_id = res_partner.id
	into h;

	-- foreach product in array $3 loop
		
						loc_id = -1;
						prod_id = -1;
						lote_idmp = -1;
--    foreach location in array $4  loop
--      for dr in cursor_final loop
			saldof =0;
			saldov =0;
			cprom =0;
			cadquiere =0;
			ingreso =0;
			salida =0;
			debit =0;
			credit =0;
			avanceop = 0;
			contador = 2;
			
			
			for dr in 
			select *,sp.name as doc_almac,sp.kardex_date as fecha_albaran, '' as pedido_compra, '' as licitacion,'' as lote,'1' as correlativovisual,
			''::character varying as ruc,''::character varying as comapnyname, ''::character varying as cod_sunat,''::character varying as default_code,ipx.value_text as ipxvalue,
			''::character varying as tipoprod ,''::character varying as coduni ,''::character varying as metodo, 0::numeric as cu_entrada , 0::numeric as cu_salida, ''::character varying as period_name  
			from vst_kardex_fisico_valorado as vst_kardex_sunat
left join stock_move sm on sm.id = vst_kardex_sunat.stock_moveid
left join stock_picking sp on sp.id = sm.picking_id
left join account_move_line ail on ail.id = vst_kardex_sunat.invoicelineid
left join product_product pp on pp.id = vst_kardex_sunat.product_id
left join product_template ptp on ptp.id = pp.product_tmpl_id
LEFT JOIN ir_property ipx ON ipx.res_id::text = ('product.template,'::text || ptp.id) AND ipx.name::text = 'cost_method'::text 
					
			 where vst_kardex_sunat.fecha between (substring($1::varchar,1,4) || '-' || substring($1::varchar,5,2) || '-' || substring($1::varchar,7,2) )::timestamp + interval '5' hour and 
			 (substring($2::varchar,1,4) || '-' || substring($2::varchar,5,2) || '-' || substring($2::varchar,7,2) )::timestamp + interval '29' hour  
			order by vst_kardex_sunat.location_id,vst_kardex_sunat.product_id,vst_kardex_sunat.fecha,vst_kardex_sunat.esingreso,vst_kardex_sunat.stock_moveid,vst_kardex_sunat.nro
				loop
				if dr.location_id = ANY ($4) and dr.product_id = ANY ($3) then
					if dr.ipxvalue = 'specific' then
										if loc_id = dr.location_id then
							contador = 1;
							else
							
							loc_id = dr.location_id;
							prod_id = dr.product_id;
					--    foreach location in array $4  loop
							
					--      for dr in cursor_final loop
							saldof =0;
							saldov =0;
							cprom =0;
							cadquiere =0;
							ingreso =0;
							salida =0;
							debit =0;
							credit =0;
						end if;
							else
						

								if prod_id = dr.product_id and loc_id = dr.location_id then
								contador =1;
								else

							loc_id = dr.location_id;
							prod_id = dr.product_id;
					--    foreach location in array $4  loop
					--      for dr in cursor_final loop
								saldof =0;
								saldov =0;
								cprom =0;
								cadquiere =0;
								ingreso =0;
								salida =0;
								debit =0;
								credit =0;
								end if;
					 end if;

						select '' as category_sunat_code, '' as uom_sunat_code, product_product.default_code as codigoproducto
						from product_product
						inner join product_template on product_product.product_tmpl_id = product_template.id
						inner join product_category on product_template.categ_id = product_category.id
						inner join uom_uom on product_template.uom_id = uom_uom.id
						--left join category_product_sunat on product_category.cod_sunat = category_product_sunat.id
						--left join category_uom_sunat on uom_uom.cod_sunat = category_uom_sunat.id
						where product_product.id = dr.product_id into h1;


						select t_pp.id, 
            ((     coalesce(max(it.value),max(t_pt.name::text))::character varying::text || ' '::text) || replace(array_agg(pav.name)::character varying::text, '{NULL}'::text, ''::text))::character varying AS new_name
           FROM product_product t_pp
             JOIN product_template t_pt ON t_pp.product_tmpl_id = t_pt.id
			 left join ir_translation it ON t_pt.id = it.res_id and it.name = 'product.template,name' and it.lang = 'es_PE' and it.state = 'translated'

left join product_variant_combination pvc on pvc.product_product_id = t_pp.id
left join product_template_attribute_value ptav on ptav.id = pvc.product_template_attribute_value_id
left join product_attribute_value pav on pav.id = ptav.product_attribute_value_id
where t_pp.id = dr.product_id
group by t_pp.id   into hproduct;


															select * from stock_location where id = dr.location_id into h2;
				
					---- esto es para las variables que estan en el crusor y pasarlas a las variables output
					
					almacen=dr.almacen;
					categoria=dr.categoria;
					name_template=hproduct.new_name;
					fecha=dr.fecha - interval '5' hour;
					periodo=dr.periodo;
					ctanalitica=dr.ctanalitica;
					serial=dr.serial;
					nro=dr.nro;
					operation_type=dr.operation_type;
					name=dr.name;
					type=dr.type;
					esingreso=dr.esingreso;
					product_id=dr.product_id;
					correlativovisual = dr.correlativovisual;

					correlativovisual = avanceop;

					avanceop = avanceop +1;

					location_id=dr.location_id;
					doc_type_ope=dr.doc_type_ope;
					ubicacion_origen=dr.id_origen;
					ubicacion_destino=dr.id_destino;
					stock_moveid=dr.stock_moveid;
					account_invoice=0;
					product_account=dr.product_account;
					default_code=h1.codigoproducto;
					unidad=dr.unidad;
					mrpname='';
					stock_doc=dr.stock_doc;
					origen=dr.origen;
					destino=dr.destino;
					type_doc=dr.type_doc;
								numdoc_cuadre=dr.numdoc_cuadre;
								if dr.numdoc_cuadre::varchar = ''::varchar then
									numdoc_cuadre=dr.doc_almac;
								end if;
								doc_partner=dr.nro_documento;
								lote= dr.lote;


				

					 ruc = h.nro_documento;
					 comapnyname = h.name;
					 cod_sunat = ''; 
					 default_code = h1.codigoproducto;
					 tipoprod = h1.category_sunat_code; 
					 coduni = h1.uom_sunat_code;
					 metodo = 'Costo promedio';
					 
					 period_name = dr.period_name;
					
					 fecha_albaran = dr.fecha_albaran - interval '5' hour;
					 pedido_compra = dr.pedido_compra;
					 licitacion = dr.licitacion;
					 doc_almac = dr.doc_almac;


					--- final de proceso de variables output

				
					ingreso =coalesce(dr.ingreso,0);
					salida =coalesce(dr.salida,0);
					--if dr.serial is not null then 
						debit=coalesce(dr.debit,0);
					--else
						--if dr.ubicacion_origen=8 then
							--debit =0;
						--else
							---debit = coalesce(dr.debit,0);
						--end if;
					--end if;
					

					
						credit =coalesce(dr.credit,0);
					
					cadquiere =coalesce(dr.cadquiere,0);
					precprom = cprom;
					if cadquiere <=0::numeric then
						cadquiere=cprom;
					end if;
					if salida>0::numeric then
						credit = cadquiere * salida;
					end if;
					saldov = saldov + (round(debit,2) - round(credit,2));
					saldof = saldof + (ingreso - salida);
					if saldof > 0::numeric then
						if esingreso= 'ingreso' or ingreso > 0::numeric then
							if saldof != 0 then
								cprom = saldov/saldof;
							else
											cprom = saldov;
								 end if;
							if ingreso = 0 then
											cadquiere = cprom;
							else
									cadquiere =debit/ingreso;
							end if;
							--cprom = saldov / saldof;
							--cadquiere = debit / ingreso;
						else
							if salida = 0::numeric then
								if debit + credit > 0::numeric then
									cprom = saldov / saldof;
									cadquiere=cprom;
								end if;
							else
								credit = salida * cprom;
							end if;
						end if;
					else
						cprom = 0;
					end if;
						

					if saldov <= 0::numeric and saldof <= 0::numeric then
						dr.cprom = 0;
						cprom = 0;
					end if;
					--if cadquiere=0 then
					--  if trim(dr.operation_type) != '05' and trim(dr.operation_type) != '' and dr.operation_type is not null then
					--    cadquiere=precprom;
					--    debit = ingreso*cadquiere;
					--    credit=salida*cadquiere;
					--  end if;
					--end if;
					debit= round(debit,2);
					credit= round(credit,2);
					saldov= round(saldov,2);
					dr.debit = round(debit,8);
					dr.credit = round(credit,8);
					dr.cprom = round(cprom,8);
					dr.cadquiere = round(cadquiere,8);
					dr.credit = round(credit,8);
					dr.saldof = round(saldof,8);
					dr.saldov = round(saldov,8);
					if ingreso>0 then
						cu_entrada =debit/ingreso;
					else
						cu_entrada =debit;
					end if;

					if salida>0 then
						cu_salida =credit/salida;
					else
					cu_salida =credit;
					end if;

					RETURN NEXT;
				end if;
	end loop;
	--return query select * from vst_kardex_sunat where fecha_num(vst_kardex_sunat.fecha) between $1 and $2 and vst_kardex_sunat.product_id = ANY($3) and vst_kardex_sunat.location_id = ANY($4) order by location_id,product_id,fecha;
END
$BODY$
	LANGUAGE plpgsql VOLATILE
	COST 100
	ROWS 1000;


			""")








class LandedCostItLine(models.Model):
	_inherit = 'landed.cost.it.line'

	precio_unitario_rel = fields.Float(string='Precio Unitario', compute="get_price_unit_it")

	def get_price_unit_it(self):
		for i in self:
			i.precio_unitario_rel = i.stock_move_id.price_unit_it * i.stock_move_id.picking_id.tc
