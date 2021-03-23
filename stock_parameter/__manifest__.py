# -*- encoding: utf-8 -*-
{
	'name': 'Stock Parameter',
	'category': 'stock',
	'author': 'ITGRUPO',
	'depends': ['stock'],
	'version': '1.0',
	'description':"""
	Modulo para crear tabla de Parametros en Almacen
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
			'security/security.xml',
			'security/ir.model.access.csv',
			'views/stock_main_parameter.xml',
			],
	'installable': True
}
