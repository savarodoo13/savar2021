# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class MultipaymentAdvanceIt(models.Model):
	_name = 'multipayment.advance.it'

	@api.depends('nro_operation')
	def _get_name(self):
		for i in self:
			i.name = i.nro_operation

	name = fields.Char(compute=_get_name,store=True)
	journal_id = fields.Many2one('account.journal',string='Diario')
	payment_date = fields.Date(string='Fecha de pago')
	catalog_payment_id = fields.Many2one('einvoice.catalog.payment',string='Medio de Pago')
	glosa = fields.Char(string='Glosa')
	tc = fields.Float(string='Tipo Cambio',digits=(12,3),default=1)
	invoice_ids = fields.One2many('multipayment.advance.it.line','main_id',string='Facturas')
	lines_ids = fields.One2many('multipayment.advance.it.line2','main_id',string='Lineas')
	state = fields.Selection([('draft','Borrador'),('done','Finalizado')],string='Estado',default='draft')
	asiento_id = fields.Many2one('account.move',string='Asiento Contable')
	company_id = fields.Many2one('res.company',string=u'Compañía',default=lambda self: self.env.company)

	#OTRA INFORMACION
	partner_cash_id = fields.Many2one('res.partner',string='Partner Caja')
	type_document_cash_id = fields.Many2one('einvoice.catalog.01',string='Tipo Comprobante Caja')
	nro_operation = fields.Char(string=u'Nro Operación Caja')

	@api.onchange('payment_date')
	def on_change_payment_date(self):
		if self.payment_date:
			divisa_line = self.env['res.currency.rate'].search([('name','=',self.payment_date)])
			if len(divisa_line)>0:
				self.tc = divisa_line[0].sale_type

	@api.onchange('tc')
	def on_change_tc(self):
		if self.tc:
			for i in self.invoice_ids:
				i._update_debit_credit()

	def crear_asiento(self):
		lineas = []

		for elemnt in self.invoice_ids:
			vals = (0,0,{
				'account_id': elemnt.account_id.id,
				'partner_id':elemnt.partner_id.id,
				'type_document_id':elemnt.tipo_documento.id,
				'nro_comp': elemnt.invoice_id.nro_comp,
				'name': self.glosa,
				'currency_id': elemnt.currency_id.id,
				'amount_currency': elemnt.importe_divisa,
				'debit': elemnt.debe,
				'credit': elemnt.haber,
				'date_maturity':elemnt.fecha_vencimiento,
				'company_id': self.company_id.id,
				'reconciled':False,
				'tc': self.tc,
			})
			lineas.append(vals)

		for i in self.lines_ids:
			vals = (0,0,{
					'account_id': i.account_id.id,
					'partner_id':self.partner_cash_id.id if self.partner_cash_id else None,
					'type_document_id':self.type_document_cash_id.id if self.type_document_cash_id else None,
					'nro_comp': self.nro_operation,
					'name': self.glosa,
					'currency_id': i.currency_id.id,
					'amount_currency': i.importe_divisa,
					'debit': i.debe,
					'credit': i.haber,
					'company_id': self.company_id.id,
					'reconciled':False,
					'tc': self.tc,
				})
			lineas.append(vals)

		move_id = self.env['account.move'].create({
			'company_id': self.company_id.id,
			'journal_id': self.journal_id.id,
			'date': self.payment_date,
			'line_ids':lineas,
			'ref': self.nro_operation,
			'glosa':self.glosa,
			'td_payment_id': self.catalog_payment_id.id if self.catalog_payment_id else None,
			'type':'entry'})

		for c,elemnt in enumerate(self.invoice_ids):
			self.env['account.move.line'].browse([move_id.line_ids[c].id,self.invoice_ids[c].invoice_id.id]).reconcile()

		move_id.post()
		self.asiento_id = move_id.id
		self.state = 'done'

	def cancelar(self):
		if self.asiento_id.id:
			if self.asiento_id.state =='draft':
				pass
			else:
				for mm in self.asiento_id.line_ids:
					mm.remove_move_reconcile()
				self.asiento_id.button_cancel()
			self.asiento_id.line_ids.unlink()
			self.asiento_id.name = "/"
			self.asiento_id.unlink()

		self.state = 'draft'

	def unlink(self):
		for multi in self:
			if multi.state in ('done'):
				raise UserError("No puede eliminar un Pago Multiple que esta Finalizado")
		return super(MultipaymentAdvanceIt, self).unlink()

class MultipaymentAdvanceItLine(models.Model):
	_name = 'multipayment.advance.it.line'

	main_id = fields.Many2one('multipayment.advance.it')
	partner_id = fields.Many2one('res.partner',string='Partner')
	tipo_documento = fields.Many2one('einvoice.catalog.01',string='Tipo de Documento')	
	invoice_id = fields.Many2one('account.move.line',string='Factura')
	account_id = fields.Many2one('account.account',string='Cuenta',related='invoice_id.account_id')
	currency_id = fields.Many2one('res.currency',string='Moneda',related='invoice_id.currency_id')
	fecha_vencimiento = fields.Date(string='Fecha Vencimiento',related='invoice_id.date_maturity')
	saldo = fields.Monetary(string='Saldo')
	importe_divisa = fields.Float(string='Importe Divisa',digits=(12,2))
	debe = fields.Float(string='Debe',digits=(12,2),default=0)
	haber = fields.Float(string='Haber',digits=(12,2),default=0)

	@api.onchange('invoice_id')
	def on_change_invoice_id(self):
		if self.invoice_id:
			residual_amount = 0
			if self.invoice_id.currency_id:
				residual_amount = self.invoice_id.amount_residual_currency
			else:
				residual_amount = self.invoice_id.amount_residual
			self.saldo = residual_amount

	@api.onchange('importe_divisa')
	def _update_debit_credit(self):
		if self.importe_divisa:
			if self.invoice_id.currency_id and self.invoice_id.currency_id.name != 'PEN':
				self.debe = self.importe_divisa * self.main_id.tc if self.importe_divisa > 0 else 0
				self.haber = 0 if self.importe_divisa > 0 else abs(self.importe_divisa * self.main_id.tc)
			else:
				self.debe = self.importe_divisa if self.importe_divisa > 0 else 0
				self.haber = 0 if self.importe_divisa > 0 else abs(self.importe_divisa)

class MultipaymentAdvanceItLine2(models.Model):
	_name = 'multipayment.advance.it.line2'

	main_id = fields.Many2one('multipayment.advance.it')
	account_id = fields.Many2one('account.account',string='Cuenta')
	currency_id = fields.Many2one('res.currency',string='Moneda')	
	importe_divisa = fields.Float(string='Importe Divisa',digits=(12,2),default=0)
	debe = fields.Float(string='Debe',digits=(12,2))
	haber = fields.Float(string='Haber',digits=(12,2))

	@api.onchange('importe_divisa','currency_id')
	def _update_debit_credit(self):
		if self.importe_divisa:
			if self.currency_id and self.currency_id.name != 'PEN':
				self.debe = self.importe_divisa * self.main_id.tc if self.importe_divisa > 0 else 0
				self.haber = 0 if self.importe_divisa > 0 else abs(self.importe_divisa * self.main_id.tc)
			else:
				self.debe = self.importe_divisa if self.importe_divisa > 0 else 0
				self.haber = 0 if self.importe_divisa > 0 else abs(self.importe_divisa)