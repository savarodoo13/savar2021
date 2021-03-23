# -*- encoding: utf-8 -*-
{
	'name': 'Maintenance Buttons',
	'category': 'maintenance',
	'author': 'ITGRUPO',
	'depends': ['maintenance', 'purchase', 'stock', 'stock_balance_report'],
	'version': '1.0.0',
	'description':"""
	Modulo para añadir Botones de Compras y Almacenes a la Peticion de Mantenimiento
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
			'security/ir.model.access.csv',
			'views/maintenance.xml'],
	'installable': True
}