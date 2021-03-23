# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SaleAdvancePaymentInv(models.TransientModel):
	_inherit = 'sale.advance.payment.inv'

	picking_ids = fields.Many2many('stock.picking', 'stock_picking_sale_advance_payment_inv', 'picking_id', 'sale_advance_id', string='Albaranes')

	@api.onchange('picking_ids')
	def _get_picking_domain(self):
		sale = self.env['sale.order'].browse(self._context.get('active_id', False))
		res = {'domain': {'picking_ids': [('state', '=', 'done'), ('invoice_id', '=', False), ('id', 'in', sale.picking_ids.ids)]}}
		return res

	def create_invoices(self):
		Sale = self.env['sale.order'].browse(self._context.get('active_id', False))
		before_invoices = Sale.invoice_ids
		res = super(SaleAdvancePaymentInv, self).create_invoices()
		after_invoices = Sale.invoice_ids
		new_invoice = after_invoices - before_invoices
		if len(new_invoice) == 1:
			self.picking_ids.write({'invoice_id': new_invoice.id})
			ebill = self.env['ir.module.module'].search([('name', '=', 'ebill')])
			if ebill and ebill.state == 'installed':
				for picking in self.picking_ids:
					self.env['move.guide.line'].create({
							'move_id': new_invoice.id,
							'numberg': picking.numberg
						})
		return res