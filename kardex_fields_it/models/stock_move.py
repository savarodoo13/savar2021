# -*- coding:utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

class StockMove(models.Model):
	_inherit = 'stock.move'

	analytic_account_id = fields.Many2one('account.analytic.account', string=u'Cuenta Analítica')
	analytic_tag_id = fields.Many2one('account.analytic.tag', string=u'Etiqueta Analítica')