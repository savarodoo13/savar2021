# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import json
import pytz
import logging

from datetime import datetime
from psycopg2 import IntegrityError

from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from odoo.addons.base.models.ir_qweb_fields import nl2br

_logger = logging.getLogger(__name__)


class ApiWebService(http.Controller):

    @http.route('/api/webservice/projecttimereport/', type='http', auth="public", methods=['POST'],csrf=False)
    def api_projecttimereport_post(self, *args, **kw):
        try:
            user = kw['UserName']
            password = kw['Password']
            data = []
            if user == 'APIUser' and password == 'Api$pass&33tn9G30BB32RTY9':
                for i in request.env['project.time.report'].sudo().search([]):
                    data.append(i.read())            
                return str(data)
            else:
                rpta = {
                    'status':'Error Data',
                    'log':'Datos de Conexion erroneos',
                }
                return str(rpta)
        except Exception as err:
            rpta = {
                'status':'Error Process',
                'log':'Datos de Conexion erroneos',
                'detail': str(err),
            }
            return str(rpta)

    @http.route('/api/webservice/projectsteelreport/', type='http', auth="public", methods=['POST'],csrf=False)
    def api_projectsteelreport_post(self, *args, **kw):
        try:
            user = kw['UserName']
            password = kw['Password']
            data = []
            if user == 'APIUser' and password == 'Api$pass&33tn9G30BB32RTY9':
                for i in request.env['project.steel.report'].sudo().search([]):
                    data.append(i.read())            
                return str(data)
            else:
                rpta = {
                    'status':'Error Data',
                    'log':'Datos de Conexion erroneos',
                }
                return str(rpta)
        except Exception as err:
            rpta = {
                'status':'Error Process',
                'log':'Datos de Conexion erroneos',
                'detail': str(err),
            }
            return str(rpta)


    @http.route('/api/webservice/maintenancereport/', type='http', auth="public", methods=['POST'],csrf=False)
    def api_maintenancereport_post(self, *args, **kw):
        try:
            user = kw['UserName']
            password = kw['Password']
            date_ini = kw['DateIni']
            date_end = kw['DateEnd']

            data = []

            obj1= request.env['wizard.maintenance'].sudo().create({'fecha_inicial': date_ini,'fecha_final': date_end})
            obj1.sudo().get_report()

            if user == 'APIUser' and password == 'Api$pass&33tn9G30BB32RTY9':
                for i in request.env['list.report'].sudo().search([]):
                    data.append(i.read())            
                return str(data)
            else:
                rpta = {
                    'status':'Error Data',
                    'log':'Datos de Conexion erroneos',
                }
                return str(rpta)
        except Exception as err:
            rpta = {
                'status':'Error Process',
                'log':'Datos de Conexion erroneos',
                'detail': str(err),
            }
            return str(rpta)
