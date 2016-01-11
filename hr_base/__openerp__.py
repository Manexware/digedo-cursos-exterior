# -*- coding: utf-8 -*-

{
    'name': 'Safety for DIGEDO\'s departments',
    'version': '1.0',
    'category': 'Marine',
    'complexity': "easy",
    'description': """
Implementa los roles para diferentes departamentos en DIGEDO.
    """,
    'author': 'Manexware S.A.',
    'website': 'http://www.manexware.com',
    'images' : [
    ],
    'depends': ['hr'],
    'init_xml': [
    ],
    'data': [
        'security/safety.xml',
        'security/ir.model.access.csv',
        'views/school_view.xml',
    ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
