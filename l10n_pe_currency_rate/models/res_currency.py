# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_compare
import pytz
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class ResCurrency(models.Model):
	_inherit = "res.currency"
	
	purchase_type = fields.Float(string='Tipo Compra', compute='_compute_peruvian_current_rate', digits=(16, 3))
	sale_type = fields.Float(string='Tipo Venta', compute='_compute_peruvian_current_rate', digits=(16, 3))
	
	@api.depends('rate')
	def _compute_peruvian_current_rate(self):
		date = self._context.get('date') or fields.Date.today()
		company_id = self._context.get('company_id') or self.env.user.company_id.id
		for currency in self:
			rate = self.env['res.currency.rate'].search([('currency_id','=',currency.id), ('company_id','=',company_id), ('name', '<=',date)], 
												 order='company_id, name DESC', limit=1)
			currency.purchase_type = rate and rate.purchase_type or (float_compare(currency.rate,1.0, precision_digits=16)==1 and 1.0 or 0.0)
			currency.sale_type = rate and rate.sale_type or (float_compare(currency.rate,1.0, precision_digits=16)==1 and 1.0 or 0.0)

	#######################

	@api.model
	def _action_sunat_exchange_rate(self):
		url = 'http://www.sbs.gob.pe/app/pp/SISTIP_PORTAL/Paginas/Publicacion/TipoCambioPromedio.aspx'
		try:
			res_html = urllib.request.urlopen(url)
			html = BeautifulSoup(res_html, "lxml")
			tr = html.find("tr", id="ctl00_cphContent_rgTipoCambio_ctl00__0")
			currency = self.env.ref('base.USD')
			if tr and currency:
				tds = tr.findAll("td", {"class": "APLI_fila2"})
				if tds:
					values = {
						'compra': float(tds[0].text.strip()),
						'venta': float(tds[1].text.strip()),
					}
					rate_date = fields.Datetime.now().replace(tzinfo=pytz.UTC).astimezone(pytz.timezone(self.env.user.tz or 'UTC')) + relativedelta(days=1)
					currency_rate = self.env['res.currency.rate']
					for cmpny in self.env['res.company'].search([]):
						rate = currency_rate.search([
							('currency_id', '=', currency.id),
							('name', '=', rate_date.date()),
							('company_id','=',cmpny.id)
						], limit=1)
						if not rate:
							currency_rate.create({
								'currency_id': currency.id,
								'rate': 1.0 / values['venta'],
								'name': rate_date,
								'sale_type': values['venta'],
								'purchase_type': values['compra'],
								'company_id': cmpny.id,
							})
						else:
							rate.write({
								'rate': 1.0 / values['venta'],
								'name': rate_date,
								'sale_type': values['venta'],
								'purchase_type': values['compra'],
							})
		except urllib.error.HTTPError as e:
			print('Error: %s' % e)
		except urllib.error.URLError as a:
			print('Error: %s' % a)
			
	#######################
class ResCurrencyRate(models.Model):
	_inherit = "res.currency.rate"

	purchase_type = fields.Float(string='Tipo Compra',digits=(16, 3))
	sale_type = fields.Float(string='Tipo Venta',digits=(16, 3))

	@api.onchange('sale_type')
	def _update_currency(self):
		for i in self:
			if i.sale_type:
				i.rate = 1/i.sale_type