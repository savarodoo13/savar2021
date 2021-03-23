# -- encoding: utf-8 --
{
	'name': 'CORRECTOR PLE IT',
	'category': 'account',
	'author': 'ITGRUPO',
	'depends': ['account_sunat_rep_it'],
	'version': '1.0',
	'description':"""
	Corrector de PLE de Compras y PLE de Ventas
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'security/ir.model.access.csv',
		'views/account_ple_purchase_book.xml',
		'views/account_ple_sale_book.xml',
		'wizard/account_ple_purchase_wizard.xml',
		'wizard/account_ple_sale_wizard.xml'
		],
	'installable': True
}