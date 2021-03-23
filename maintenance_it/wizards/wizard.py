# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo import tools

# consulta mediante ORM
class List_Report(models.Model):
    _name = 'list.report'

    name = fields.Char(string="Maquina")
    mttr = fields.Float(string="MTTR")
    mtbf = fields.Float(string="MTBF")
    disponibilidad = fields.Float(string="Disponibilidad")

class wizard_libro(models.TransientModel):
    _name = 'wizard.maintenance'

    fecha_inicial= fields.Date(string="Fecha Inicial")
    fecha_final= fields.Date(string="Fecha Final")

    def get_report(self):





        for i in self:
            for line in self.env['list.report'].search([]):
                line.unlink()


            if self.env['maintenance.request'].search([('schedule_date' , '>=', self.fecha_inicial),('schedule_date' , '<=', self.fecha_final)]):

                self.env.cr.execute(self._get_sql())
                res = self.env.cr.dictfetchall()
                # print(res)

                # z=self.env['maintenance.request'].search([])
                # x=sum(z.mapped('duration'))
                for elem in res:
                    # print(elem['equipo'])
                    # print(elem['count'])
                    # print(elem['total'])
                    # print(elem['duration'])
                    # print(elem['duration2'])

                    if elem['total'] == 0:
                        raise UserError(u'Falta Ingresar Tiempo Disponible del mes en curso al Equipo: ' + elem['equipo'])
                    else:
                        if elem['count'] != 0:
                            mt=(elem['total'] - elem['duration'])/(elem['count']*24)
                            mb=elem['duration']/(elem['count']*24)
                        else:
                            mt=0
                            mb=0

                        if elem['total'] != 0:
                            di=(elem['total']-elem['duration']-elem['duration2'])*100/elem['total']
                        else:
                            di=0

                        data={
                            'name':elem['equipo'],
                            'mttr': mb,
                            'mtbf':mt,
                            'disponibilidad':di,
                        }
                        self.env['list.report'].create(data)
                    # print(rs0.mapped(lambda r: (r.id, r.name, r.expected_duration)))

        return {
            'name':'Reporte Equipos',
            'type':'ir.actions.act_window',
            'view_mode':'tree,pivot,graph',
            'res_model':'list.report',
        }



    def _get_sql(self):
        sql = """
            SELECT COALESCE(T1.equipment_id,0) as equipment_id, COALESCE(me.name,'') as equipo, T1.count, COALESCE(T2.total,0) as total, COALESCE(T1.duration,0) as duration,COALESCE(T1.duration2,0) as duration2
            FROM(SELECT T3.equipment_id,count(T3.equipment_id), round(sum(T3.duration)::numeric,2)  as duration, round(sum(T4.duration2)::numeric,2)  as duration2
            FROM (SELECT equipment_id, duration
            FROM maintenance_request
            WHERE maintenance_type ='corrective' and (schedule_date between '{year1}' and '{year2}'))T3
            LEFT JOIN
            (SELECT equipment_id, round(duration::numeric,2)  as duration2 
            FROM maintenance_request
            WHERE maintenance_type ='preventive' and (schedule_date between '{year1}' and '{year2}'))T4
            ON T3.equipment_id=T4.equipment_id
            GROUP BY T3.equipment_id)T1
            LEFT JOIN
            (SELECT detalle as equipment_id, sum(horas) as total from maintenance_detalle
            where (fecha between '{year1}' and '{year2}')
            group by detalle)T2 ON T2.equipment_id = T1.equipment_id
            LEFT JOIN maintenance_equipment me ON me.id = T1.equipment_id
        """.format(
				year1 = str(self.fecha_inicial.strftime('%Y/%m/%d')),
                year2 = str(self.fecha_final.strftime('%Y/%m/%d'))
			# 	# company_id = str(self.company_id.id)
			)
        return sql

# #   consulta mediante SQL
# class list_report(models.Model):
#     _name = 'list.report'
#     _auto = False
#
#     equipment_id = fields.Many2one('maintenance.equipment',string="Maquina")
#     expected_duration = fields.Float(string="MTTR", compute="get_mttr")
#     # duration = fields.Float(string="MTBF", compute="")
#     # email_cc = fields.Char(string="Disponibilidad", compute="")
#     request_date = fields.Date(string="Fecha de Peticion de Mantenimiento")
#
#     def get_mttr(self):
#         for i in self:
#             rs0 = self.env['maintenance.request'].search([])
#             x=sum(rs0.mapped('expected_duration'))
#             print(rs0.mapped('expected_duration'))
#             print(x)
#             i.expected_duration=x
#
#             # print(len(rs0))
#             # print(rs0.mapped('name'))
#             # print(rs0.mapped(lambda r: (r.id, r.name, r.expected_duration)))
#
#
# class wizard_libro(models.TransientModel):
#     _name = 'wizard.maintenance'
#
#     fecha_inicial= fields.Date(string="Fecha Inicial")
#     fecha_final= fields.Date(string="Fecha Final")
#
#     def get_report(self):
#         tools.drop_view_if_exists(self.env.cr, 'list_report')
#         sql=("""
#             CREATE OR REPLACE VIEW list_report AS
#             SELECT
#                 id,
#                 equipment_id,
#                 request_date
#             FROM
#             maintenance_request
#         """)
#         self.env.cr.execute(sql)
#
#         return {
#             'name':'Reporte Equipos',
#             'type':'ir.actions.act_window',
#             'view_mode':'tree',
#             'res_model':'list.report',
#             'domain':[('request_date' , '>=', self.fecha_inicial),('request_date' , '<=', self.fecha_final)]
#         }
