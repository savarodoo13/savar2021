# -*- coding: utf-8 -*-

import time
from datetime import datetime
import tempfile
import binascii
import xlrd
from datetime import date, datetime
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, _
import logging

_logger = logging.getLogger(__name__)
import io

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class ImportProjectWizard(models.TransientModel):
    _name = 'import.project.wizard'

    move_id = fields.Many2one('project.task', string='Asiento', required=True)
    document_file = fields.Binary(string='Excel',
                                  help="El archivo Excel debe ir con la cabecera: drill_id, terrain, drill_type, hardness, high, hour_from, hour_to, unit_amount, details")
    name_file = fields.Char(string='Nombre de Archivo')

    def importar(self):
        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.document_file))
            fp.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)

        except:
            raise Warning(_("Archivo invalido!"))

        lineas = []

        for row_no in range(sheet.nrows):
            if row_no <= 0:
                continue
            else:
                line = list(map(lambda row: isinstance(row.value,bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                # print(line)
                if len(line) == 8:
                    values.update({'drill_id': line[0],
                                   'terrain': line[1],
                                   'drill_type': line[2],
                                   'hardness': line[3],
                                   'high': line[4],
                                   'hour_from': line[5],
                                   'hour_to': line[6],
                                   # 'unit_amount':line[7],
                                   'details': line[7],
                                   })
                elif len(line) > 8:
                    raise Warning(
                        ('Tu archivo tiene mas columnas de lo esperado.'))
                else:
                    raise Warning(
                        ('Tu archivo tiene menos columnas de lo esperado.'))

                lineas.append(self.create_entry_line(values))
                # print(values)
                # print(lineas)
        self.move_id.write({'timesheet_ids': lineas})
        return {'type': 'ir.actions.act_window_close'}

    def create_entry_line(self, values):
        if values.get("drill_id") == "":
            raise Warning(_('El campo de drill_id no puede estar vacío.'))

        s = str(values.get("drill_id"))
        drill = s.rstrip('0').rstrip('.') if '.' in s else s
        drill_id = self.find_drill(drill)

        x = str(values.get("terrain"))
        x = x.rstrip('0').rstrip('.') if '.' in x else x
        y = str(values.get("drill_type"))
        y = y.rstrip('0').rstrip('.') if '.' in y else y
        z = str(values.get("hardness"))
        z = z.rstrip('0').rstrip('.') if '.' in z else z

        vals = (0, 0, {
            'account_id': self.move_id.project_id.analytic_account_id.id,
            'drill_id': drill_id.id if drill_id else None,  # drill,
            'terrain': x,
            'drill_type': y,
            'hardness': z,
            'high': values.get("high"),
            'hour_from': values.get("hour_from"),
            'hour_to': values.get("hour_to"),
            # 'unit_amount': values.get("unit_amount"),
            'details': values.get("details")
        })
        return vals

    def find_drill(self, code):
        drill_obj = self.env['project.drill']
        drill_search = drill_obj.search([('name', '=', str(code))], limit=1)
        return drill_search

    def download_template(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_project_line',
            'target': 'new',
        }
