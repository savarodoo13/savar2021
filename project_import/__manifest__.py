
# -*- encoding: utf-8 -*-
{
    'name': "Project Import",
    'version': '1.0',
    'author': 'ITGRUPO',
    'category': 'project',
    'depends': ['project_it'],
    'description': """
        Modulo de Proyectos Personalizado para importar registros
    """,
    'demo': [],
    'data': [
        'data/attachment_sample.xml',
		'views/project_task.xml',
        'wizard/import_project_wizard.xml',
    ],
    'auto_install': False,
    'installable': True
}