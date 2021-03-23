# -*- encoding: utf-8 -*-
{
    'name': 'Project IT',
    'version': '1.0',
    'author': 'ITGRUPO',
    'category': 'project',
    'depends': ['project', 'hr_timesheet', 'stock', 'hr', 'maintenance', 'hr_maintenance', 'stock_parameter','maintenance_buttons'],
    'description': """
        Modulo de Proyectos Personalizado
    """,
    'demo': [],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/project_task.xml',
        'views/project_steel_report.xml',
        'views/project_time_report.xml'
    ],
    'auto_install': False,
    'installable': True
}