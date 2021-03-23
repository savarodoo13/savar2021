# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
	_inherit = 'account.move'

	doc_origin_customer = fields.Char(string='Doc Origen Cliente')