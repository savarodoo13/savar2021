# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	landed_cost_purchase_ids = fields.One2many('landed.cost.it', 'purchase_order_id', string='Gastos Vinculados')
	landed_cost_purchase_visible = fields.Boolean(compute='_compute_landed_cost_purchase_visible',default=False)

	@api.depends('order_line', 'order_line.is_landed_cost_line')
	def _compute_landed_cost_purchase_visible(self):
		for purchase_order in self:
			if purchase_order.landed_cost_purchase_ids:
				purchase_order.landed_cost_purchase_visible = False
			else:
				purchase_order.landed_cost_purchase_visible = any(line.is_landed_cost_line for line in purchase_order.order_line)

	def button_create_landed_cost(self):
		self.ensure_one()

		landed_costs = self.env['landed.cost.it'].create({
			'purchase_order_id': self.id,
			'partner_id': self.partner_id.id,
			'tomar_valor':'pedido',
			'prorratear_en':'cantidad',
			'amount_purchase': self.amount_untaxed,
			'tc':1,
			'currency_id':self.currency_id.id,
			'company_id':self.company_id.id,
			'total_flete':self.amount_untaxed,
		})
		action = self.env.ref('landed_cost_it.action_landed_cost_it').read()[0]
		return dict(action, view_mode='form', res_id=landed_costs.id, views=[(False, 'form')])

	def action_view_landed_cost(self):
		self.ensure_one()
		action = self.env.ref('landed_cost_it.action_landed_cost_it').read()[0]
		domain = [('id', 'in', self.landed_cost_purchase_ids.ids)]
		context = dict(self.env.context, default_purchase_order_id=self.id)
		views = [(self.env.ref('landed_cost_it.view_landed_cost_it_tree').id, 'tree'), (False, 'form'), (False, 'kanban')]
		return dict(action, domain=domain, context=context, views=views)

class PurchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'

	is_landed_cost_line = fields.Boolean(default=False)

	@api.onchange('product_id')
	def _onchange_is_landed_cost_line_product(self):
		if self.product_id.is_landed_cost:
			self.is_landed_cost_line = True
		else:
			self.is_landed_cost_line = False