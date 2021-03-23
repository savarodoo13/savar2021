# -*- coding: utf-8 -*-

from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    landed_cost_ids = fields.One2many('landed.cost.it', 'invoice_id', string='Gastos Vinculados')
    landed_cost_visible = fields.Boolean(compute='_compute_landed_cost_visible',default=False)

    @api.depends('line_ids', 'line_ids.is_landed_cost_line')
    def _compute_landed_cost_visible(self):
        for account_move in self:
            if account_move.landed_cost_ids:
                account_move.landed_cost_visible = False
            else:
                account_move.landed_cost_visible = any(line.is_landed_cost_line for line in account_move.line_ids)

    def button_create_landed_cost(self):
        self.ensure_one()

        landed_costs = self.env['landed.cost.it'].create({
            'invoice_id': self.id,
            'partner_id': self.partner_id.id,
            'tomar_valor':'factura',
            'prorratear_en':'valor',
            'amount_invoice': self.amount_untaxed,
            'tc':self.currency_rate,
            'currency_id':self.currency_id.id,
            'company_id':self.company_id.id,
            'total_flete':self.amount_untaxed * self.currency_rate,
        })
        action = self.env.ref('landed_cost_it.action_landed_cost_it').read()[0]
        return dict(action, view_mode='form', res_id=landed_costs.id, views=[(False, 'form')])

    def action_view_landed_cost(self):
        self.ensure_one()
        action = self.env.ref('landed_cost_it.action_landed_cost_it').read()[0]
        domain = [('id', 'in', self.landed_cost_ids.ids)]
        context = dict(self.env.context, default_invoice_id=self.id)
        views = [(self.env.ref('landed_cost_it.view_landed_cost_it_tree').id, 'tree'), (False, 'form'), (False, 'kanban')]
        return dict(action, domain=domain, context=context, views=views)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_landed_cost_line = fields.Boolean(default=False)

    @api.onchange('product_id')
    def _onchange_is_landed_cost_line_product(self):
        if self.product_id.is_landed_cost:
            self.is_landed_cost_line = True
        else:
            self.is_landed_cost_line = False