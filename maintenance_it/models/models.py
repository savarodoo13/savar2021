# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Maintenance_Equipment(models.Model):
    _inherit = 'maintenance.equipment'
    #date = fields.Date(string="Fecha")
    detail_ids	= fields.One2many('maintenance.detalle','detalle','Detalles')


class Maintenance_detalle(models.Model):
    _name = 'maintenance.detalle'

    fecha = fields.Date(string='Periodo')
    horas=fields.Float(string='Horas')
    detalle = fields.Many2one('maintenance.equipment',string='Detalle',required=True)
