# -*- encoding: utf-8 -*-
{
	'name': 'Account Multipayment Advance IT',
	'category': 'account',
	'author': 'ITGRUPO',
	'depends': ['account_base_it','l10n_pe_currency_rate'],
	'version': '1.0',
	'description':"""
	Modulo para permitir el multipago de facturas
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'security/security.xml',
		'security/ir.model.access.csv',
		'views/multipayment_advance_it.xml'
		],
	'installable': True
}
