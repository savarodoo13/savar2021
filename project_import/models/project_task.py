from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def import_lines(self):
        wizard = self.env['import.project.wizard'].create({
            'move_id': self.id
        })
        # print(__name__)
        # print(__name__.split('addons.'))
        # print(__name__.split('addons.')[1])
        # print(__name__.split('addons.')[1].split('.')[0])
        module = __name__.split('addons.')[1].split('.')[0]
        view = self.env.ref('%s.view_import_project_wizard_form' % module)
        # print(wizard)
        # print(wizard.id)
        # print(view)
        # print(view.id)
        return {
            'name': u'Importador de Horas Planeadas',
            'res_id': wizard.id,
            'view_mode': 'form',
            'res_model': 'import.project.wizard',
            'view_id': view.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
