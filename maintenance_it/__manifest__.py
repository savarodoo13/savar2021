# -*- coding: utf-8 -*-
{
    'name': 'Maintenance IT',
    'category': 'Maintenance',
    'author': 'ITGRUPO',
    'depends': ['maintenance','maintenance_buttons'],
    'version': '1.0',
    'description':"""
	Modulo base para Mantenimiento
	""",
    'auto_install': False,
    'demo': [],
    'data':	[
        'wizards/wizard.xml',
        'views/views.xml',
        'security/security.xml',
		'security/ir.model.access.csv',
    ],
    'installable': True

}
