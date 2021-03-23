# -*- encoding: utf-8 -*-
{
    'name': 'Kardex',
    'version': '1.0',
    'author': 'ITGRUPO-COMPATIBLE-BO',
    'website': '',
    'category': 'account',
    'depends': ['kardex_valorado_it_multi','owm_fields_it','stock_picking_note','sale','purchase','products_alternatives_code_it','kardex_fisico_it_multi','kardex_fisico_it_multi_lote'],
    'description': """KARDEX""",
    'demo': [],
    'data': [
        'wizard/make_kardex_view.xml',
    ],
    'auto_install': False,
    'installable': True
}
