# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64

class make_kardex_mrp_report_v2(models.Model):
	_name = 'make.kardex.mrp.report.v2'

	_auto = False

	def fake_init(self):
		self.env.cr.execute(""" 

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
    NULL::text AS analitic_id,
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
     LEFT JOIN type_operation_kardex tok ON stock_picking.type_operation_sunat_id = tok.id
  WHERE (stock_move.state::text = ANY (ARRAY['done'::text, 'assigned'::text])) AND product_template.type::text = 'product'::text AND stock_move.picking_id IS NOT NULL 

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
        mp.name as name,
        null::integer as partner_id,
        ''::text as guia,
        NULL::text as analitic_id,
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
from mrp_production mp
inner join stock_move sm on sm.production_id = mp.id  or sm.raw_material_production_id = mp.id
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
inner join stock_location sls on sls.id = sml.location_id
inner join stock_location sld on sld.id = sml.location_dest_id where sm.state = 'done';
 """ )





class make_kardex(models.TransientModel):
	_inherit = "make.kardex"

	def do_csvtoexcel_v3(self):
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
vstf.fecha as "Fecha",
vstf.name as "Doc. Almacén",
vstf.entrada as "Entrada",
vstf.salida as "Salida"
from
(
select u_origen as origen, u_destino as destino, u_destino as almacen, vst_kardex_fisico.guia as motivo_guia, categoria, producto, cod_pro, unidad, vst_kardex_fisico.date as fecha, vst_kardex_fisico.name, vst_kardex_fisico.product_qty as entrada, 0 as salida, vst_kardex_fisico.estado, product_id,location_dest_id as almacen_id, categoria_id from vst_kardex_fisico()
union all
select u_origen as origen, u_destino as destino, u_origen as almacen, vst_kardex_fisico.guia as motivo_guia, categoria, producto, cod_pro, unidad, vst_kardex_fisico.date as fecha, vst_kardex_fisico.name, 0 as entrada, vst_kardex_fisico.product_qty as salida, vst_kardex_fisico.estado, product_id,location_id as almacen_id, categoria_id from vst_kardex_fisico()
) as vstf
where vstf.fecha::date >='""" +str(date_ini)+ """' and vstf.fecha::date <='""" +str(date_fin)+ """'
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