# -*- encoding: utf-8 -*-
{
	'name': 'Stock Balance Report OWM',
	'category': 'stock',
	'author': 'ITGRUPO',
	'depends': ['stock_balance_report'],
	'version': '1.0',
	'description':"""
	Reporte de Saldos
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'security/security.xml',
		'security/ir.model.access.csv',
		'views/stock_balance_report.xml'
	],
	'installable': True
}
