# -*- coding:utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

class StockBalanceReportLote(models.Model):
	_name = 'stock.balance.report.lote'
	_description = 'Balance Report Lote'

	producto = fields.Char(string='Producto')
	codigo = fields.Char(string='Cod. Producto')
	almacen = fields.Char(string=u'Almacén')
	entrada = fields.Float(string='Entrada', digits=(12,2))
	salida = fields.Float(string='Salida', digits=(12,2))
	saldo = fields.Float(string='Saldo', digits=(12,2))
	unidad = fields.Char(string='Unidad')
	categoria_1 = fields.Char(string='Categoria 1')
	categoria_2 = fields.Char(string='Categoria 2')
	categoria_3 = fields.Char(string='Categoria 3')
	lote = fields.Char(string='Lote')


	def get_balance_view(self):
		self.search([]).unlink()
		s_prod = [-1,-1,-1]
		s_loca = [-1,-1,-1]
		locat_ids = self.env['stock.location'].search( [('usage','in',('internal','internal'))] )
		lst_locations = locat_ids.ids
		productos='{'
		almacenes='{'
		lst_products = self.env['product.product'].with_context(active_test=False).search([]).ids
		if len(lst_products) == 0:
			raise UserError('Alerta','No existen productos seleccionados')

		for producto in lst_products:
			productos=productos+str(producto)+','
			s_prod.append(producto)
		productos=productos[:-1]+'}'
		for location in lst_locations:
			almacenes=almacenes+str(location)+','
			s_loca.append(location)
		almacenes=almacenes[:-1]+'}'
		date_ini = '01/01/2020'
		date_fin = fields.Date.today()
		self.env.cr.execute("""
			select 
			max(origen) AS "Ubicación Origen",
			max(destino) AS "Ubicación Destino",
			max(almacen) AS "Almacén",
			max(vstf.motivo_guia)::varchar AS "Tipo de operación",
			max(categoria) as "Categoria",
			producto as "Producto",
			cod_pro as "Codigo P.",
			max(unidad) as "unidad",
			max(vstf.fecha) as "Fecha",
			max(vstf.name) as "Doc. Almacén",
			sum(vstf.entrada) as "Entrada",
			sum(vstf.salida) as "Salida",
			categoria_id,
			p_id,
			alm_id,
			lote
			from
			(
			select location_dest_id as alm_id, product_id as p_id, categoria_id, vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_destino as almacen, vst_kardex_fisico.product_qty as entrada, 0 as salida,vst_kardex_fisico.id  as stock_move,vst_kardex_fisico.guia as motivo_guia, producto,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id,location_dest_id as almacen_id, lote from vst_kardex_fisico_lote("""+str(self.env.company.id)+""") as vst_kardex_fisico
			union all
			select location_id as alm_id, product_id as p_id, categoria_id, vst_kardex_fisico.date as fecha,u_origen as origen, u_destino as destino, u_origen as almacen, 0 as entrada, vst_kardex_fisico.product_qty as salida,vst_kardex_fisico.id  as stock_move ,vst_kardex_fisico.guia as motivo_guia ,producto ,vst_kardex_fisico.estado,vst_kardex_fisico.name, cod_pro, categoria, unidad,product_id, location_id as almacen_id, lote from vst_kardex_fisico_lote("""+str(self.env.company.id)+""") as vst_kardex_fisico
			) as vstf
			where vstf.fecha::date >='""" +str(date_ini)+ """' and vstf.fecha::date <='""" +str(date_fin)+ """'
			and vstf.product_id in """ +str(tuple(s_prod))+ """
			and vstf.almacen_id in """ +str(tuple(s_loca))+ """
			and vstf.estado = 'done'
			group by
			producto,cod_pro,categoria_id, p_id, alm_id,lote;
		""")
		
		for line in self.env.cr.fetchall():
			Category_1 = self.env['product.category'].browse(line[12])
			Product = self.env['product.product'].browse(line[13])
			Location = self.env['stock.location'].browse(line[14])
			Category_2 = Category_3 = None
			if Category_1 and Category_1.parent_id:
				Category_2 = self.env['product.category'].browse(Category_1.parent_id.id)
				if Category_2 and Category_2.parent_id:
					Category_3 = self.env['product.category'].browse(Category_2.parent_id.id)
			if True: #Location.location_id.name != 'Virtual Locations' and (line[10] - line[11]) > 0:
				self.create({
							'producto': line[5],
							'codigo': line[6],
							'almacen': line[2],
							'entrada': line[10],
							'salida': line[11],
							'saldo': line[10] - line[11],
							'unidad': Product.uom_id.name or '',
							'categoria_1': Category_1.complete_name if Category_1 else '',
							'categoria_2': Category_2.complete_name if Category_2 else '',
							'categoria_3': Category_3.complete_name if Category_3 else '',
							'lote': line[15],
						})
		return {
			'name': 'Reporte de Saldos x Lote',
			'type': 'ir.actions.act_window',
			'res_model': 'stock.balance.report.lote',
			'view_mode': 'tree,pivot,graph',
			'views': [(False, 'tree'), (False, 'pivot'), (False, 'graph')]
		}
