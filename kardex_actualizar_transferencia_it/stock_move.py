# -*- encoding: utf-8 -*-
from openerp.osv import osv
from openerp import models,fields ,api


datos = []
llaves = {}

class valor_unitario_kardex(models.TransientModel):
	_name='valor.unitario.kardex'
	
	fecha_inicio = fields.Date('Fecha Inicio')
	fecha_final = fields.Date('Fecha Final')


	def do_valor(self):
		prods = self.env['product.product'].with_context({'active_test':False}).search([])
		locat = self.env['stock.location'].with_context({'active_test':False}).search([('usage','in',['internal','inventory','transit','procurement','production'])])

		lst_products  = prods.ids
		lst_locations = locat.ids
		productos='{'
		almacenes='{'
		date_ini= self.fecha_inicio.strftime('%Y-%m-%d').split('-')[0] + '-01-01'
		date_fin= self.fecha_final
		fecha_arr = self.fecha_inicio
		for producto in lst_products:
			productos=productos+str(producto)+','
		productos=productos[:-1]+'}'
		for location in lst_locations:
			almacenes=almacenes+str(location)+','
		almacenes=almacenes[:-1]+'}'

		self.env.cr.execute(""" 
			update stock_move set
price_unit_it = 0
where id in (
select sm.id from stock_move sm
inner join stock_location entrada on entrada.id = sm.location_id
inner join stock_location salida on salida.id = sm.location_dest_id
inner join stock_picking sp on sp.id = sm.picking_id
where entrada.usage in ('internal','transit') and salida.usage = 'internal'
and sp.kardex_date::date >='""" +str(self.fecha_inicio)+ """' and sp.kardex_date::date <='""" +str(self.fecha_final)+ """' 
and sm.company_id = """ +str(self.env.company.id)+ """
)
""")


		for m in self.env['stock.move'].search([('company_id','=',self.env.company.id),('location_id.usage','=','internal'),('location_dest_id.usage','in',('internal','transit') ),('picking_id.kardex_date','>=',self.fecha_inicio),('picking_id.kardex_date','<=',self.fecha_final),('picking_id.state','=','done')]).sorted(key=lambda r: [r.picking_id.kardex_date,r.id]):
			self.env.cr.execute("""  
				drop table if exists tmp_kardexv_veloz;
				create table tmp_kardexv_veloz as 


select vst_kardex_sunat.*,sp.name as doc_almac,sp.kardex_date as fecha_albaran, '' as pedido_compra, '' as licitacion,'' as lote,'1' as correlativovisual,
			''::character varying as ruc,''::character varying as comapnyname, ''::character varying as cod_sunat,ipx.value_text as ipxvalue,
			''::character varying as tipoprod ,''::character varying as coduni ,''::character varying as metodo, 0::numeric as cu_entrada , 0::numeric as cu_salida, ''::character varying as period_name  
			from vst_kardex_fisico_valorado as vst_kardex_sunat
left join stock_move sm on sm.id = vst_kardex_sunat.stock_moveid
left join stock_picking sp on sp.id = sm.picking_id
left join account_move_line ail on ail.id = vst_kardex_sunat.invoicelineid
left join product_product pp on pp.id = vst_kardex_sunat.product_id
left join product_template ptp on ptp.id = pp.product_tmpl_id
LEFT JOIN ir_property ipx ON ipx.res_id::text = ('product.template,'::text || ptp.id) AND ipx.name::text = 'cost_method'::text 
					
       where (fecha_num(vst_kardex_sunat.fecha::date) between """+str(self.fecha_inicio).replace('-','')+""" and """+str(self.fecha_final).replace('-','')+""")    
			 and sm.company_id = """ +str(self.env.company.id)+ """			 
			order by vst_kardex_sunat.location_id,vst_kardex_sunat.product_id,vst_kardex_sunat.fecha,vst_kardex_sunat.esingreso,vst_kardex_sunat.stock_moveid,vst_kardex_sunat.nro
    	""")

			self.env.cr.execute(""" select * from get_kardex_v_actualizar_veloz("""+ str(date_ini).replace("-","") + "," + str(date_fin).replace("-","") + ",'" + productos + """'::INT[], '""" + almacenes + """'::INT[],""" +str(fecha_arr).replace('-','')+ ""","""+str(m.id)+""", """+str(self.env.company.id)+""") """)
		return












class update_sql_price_unit(models.Model):
	_name = 'update.sql.price.unit'

	_auto = False

	def init(self):
		self._cr.execute("""




CREATE OR REPLACE FUNCTION get_kardex_v_actualizar_veloz(IN date_ini integer, IN date_end integer, IN productos integer[], IN almacenes integer[], IN fechaini integer, IN datemove_id integer, IN company_id integer,OUT almacen character varying, OUT categoria character varying, OUT name_template character varying, OUT fecha timestamp without time zone, OUT periodo character varying, OUT ctanalitica character varying, OUT serial character varying, OUT nro character varying, OUT operation_type character varying, OUT name character varying, OUT ingreso numeric, OUT salida numeric, OUT saldof numeric, OUT debit numeric, OUT credit numeric, OUT cadquiere numeric, OUT saldov numeric, OUT cprom numeric, OUT type character varying, OUT esingreso text, OUT product_id integer, OUT location_id integer, OUT doc_type_ope character varying, OUT ubicacion_origen integer, OUT ubicacion_destino integer, OUT stock_moveid integer, OUT account_invoice character varying, OUT product_account character varying, OUT default_code character varying, OUT unidad character varying, OUT mrpname character varying, OUT ruc character varying, OUT comapnyname character varying, OUT cod_sunat character varying, OUT tipoprod character varying, OUT coduni character varying, OUT metodo character varying, OUT cu_entrada numeric, OUT cu_salida numeric, OUT period_name character varying, OUT stock_doc character varying, OUT origen character varying, OUT destino character varying, OUT type_doc character varying, OUT numdoc_cuadre character varying, OUT doc_partner character varying, OUT fecha_albaran timestamp without time zone, OUT pedido_compra character varying, OUT licitacion character varying, OUT doc_almac character varying, OUT lote character varying, OUT correlativovisual integer)
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


  rf record;
  loc_1 record;
  loc_2 record;
  
  pp_1 record;
  pp_2 record;

datos_con record;
	
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
      		select * from tmp_kardexv_veloz
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


						select t_pp.id, max(t_pt.name)::varchar || ' ' || replace(array_agg(pav.name)::varchar,'{NULL}','') as new_name from product_product t_pp
inner join product_template t_pt on t_pp.product_tmpl_id = t_pt.id
left join product_variant_combination pvc on pvc.product_product_id = t_pp.id
left join product_template_attribute_value ptav on ptav.id = pvc.product_template_attribute_value_id
left join product_attribute_value pav on pav.id = ptav.product_attribute_value_id
where t_pp.id = dr.product_id
group by t_pp.id   into hproduct;


															select * from stock_location where id = dr.location_id into h2;


            select * from stock_location where id = dr.id_origen into loc_1;
            select * from stock_location where id = dr.id_destino into loc_2;
 
            select put.factor as f1 , pu.factor as f2 from stock_move sm 
            inner join product_product pp on pp.id = sm.product_id
            inner join product_template pt2 on pt2.id = pp.product_tmpl_id
            inner join uom_uom pu on pu.id = pt2.uom_id
            inner join uom_uom put on put.id = sm.product_uom           
            where sm.id = dr.stock_moveid  into pp_1;

           select sp.name,sm.product_id from
           stock_picking sp
           inner join stock_move sm on sm.picking_id = sp.id
           where sm.id = dr.stock_moveid into datos_con;

          ---- esto es para las variables que estan en el crusor y pasarlas a las variables output
          select * from stock_move where id = dr.stock_moveid into rf;
          if loc_1.usage = 'internal' and loc_2.usage='internal' and fecha_num(dr.fecha) >= $5 and dr.stock_moveid = $6 and dr.id_origen = dr.location_id then
            UPDATE stock_move set price_unit_it = (cprom/ pp_1.f2) * pp_1.f1  where id = dr.stock_moveid;
          end if;
          if loc_1.usage = 'internal' and loc_2.usage='transit' and fecha_num(dr.fecha) >= $5 and dr.stock_moveid = $6 and dr.id_origen = dr.location_id then
            UPDATE stock_move set price_unit_it = (cprom/ pp_1.f2) * pp_1.f1  where stock_move.origin = datos_con.name and stock_move.product_id = datos_con.product_id;
          end if;

				
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
					saldov = saldov + (debit - credit);
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








