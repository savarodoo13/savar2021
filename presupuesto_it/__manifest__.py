# -*- encoding: utf-8 -*-
{
    'name': 'Presupuesto IT',
    'version': '1.0',
    'author': 'ITGRUPO',
    'category': 'presupuesto',
    'depends': ['project_it'],
    'description': """
        Modulo de Presupuesto
    """,
    'demo': [],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/presupuesto.xml',
    ],
    'auto_install': False,
    'installable': True
}