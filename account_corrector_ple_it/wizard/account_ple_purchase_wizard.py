# -- coding: utf-8 --

from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountPlePurchaseFix(models.TransientModel):
	_name = 'account.ple.purchase.wizard'

	name = fields.Char()
	company_id = fields.Many2one('res.company',string=u'Compañia',required=True, default=lambda self: self.env.company,readonly=True)
	fiscal_year_id = fields.Many2one('account.fiscal.year',string=u'Ejercicio',required=True)
	period = fields.Many2one('account.period',string='Periodo',required=True)

	@api.onchange('company_id')
	def get_fiscal_year(self):
		if self.company_id:
			fiscal_year = self.env['main.parameter'].search([('company_id','=',self.company_id.id)],limit=1).fiscal_year
			if fiscal_year:
				self.fiscal_year_id = fiscal_year.id
			else:
				raise UserError(u'No existe un año Fiscal configurado en Parametros Principales de Contabilidad para esta Compañía')

	def get_report(self):
		sql = """
			CREATE OR REPLACE view account_ple_purchase_book as (%s)""" % (
				self._get_sql()
			)

		self.env.cr.execute(sql)

		return {
			'name': 'Corrector PLE Compras',
			'type': 'ir.actions.act_window',
			'res_model': 'account.ple.purchase.book',
			'view_mode': 'tree',
			'view_type': 'form',
		}

	def _get_sql(self):
		sql = """
			select row_number() OVER () AS id, t.* from (
			select a1.periodo,a1.fecha_cont,a1.libro,a1.fecha_e,a1.td,a1.serie,a1.numero,a2.campo_41_purchase as estado,
			case when a1.td in ('03','10','02') or a1.partner_id = (select cancelation_partner from main_parameter where company_id = %s) then '0'
				when a1.td not in ('03','10','02') and a1.fecha_e < a1.fecha_cont then '6'
			else '1' end as estado_c,
			a1.am_id
			from vst_compras_1_1 a1
			left join account_move a2 on a2.id = a1.am_id
			where a1.periodo = '%s'
			and a1.company = %s) t
			where t.estado<>t.estado_c
		""" % (str(self.company_id.id),self.period.code, str(self.company_id.id))

		return sql