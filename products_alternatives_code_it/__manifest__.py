# -*- encoding: utf-8 -*-
{
    'name': 'Filtro Productos Alternativos',
    'category': '',
    'author': 'ITGRUPO',
    'depends': ['product','sale_management','stock','purchase','purchase_stock'],
    'version': '1.0',
    'description':"""
     Filtro Productos Alternativos
    """,
    'auto_install': False,
    'demo': [],
    'data': [
        #'security/ir.model.access.csv',
        'views/views.xml',
        'views/security.xml',
        'views/logistica.xml',
        #'data/plantilla.xml'
        ],
    'installable': True
}