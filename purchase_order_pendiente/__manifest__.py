# -*- coding: utf-8 -*-

{
    'name': 'Pendiente en Orden de Compra',
    'version': '1.0',
    'summary': '',
    'category': 'Tools',
    'description': """
		modulo para saber pendientes en orden de compra
    """,
    'license':'OPL-1',
    'author': 'ITGRUPO-OWM',
    'depends': ['base', 'purchase'],
    'data': [
        'views/custom_purchase_order_report.xml',
    ],
	'qweb': [
		],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}