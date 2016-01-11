# -*- coding: utf-8 -*-

{
    'name': 'Registry and Evaluation of Training',
    'version': '1.0',
    'category': 'Marine',
    'complexity': "easy",
    'description': """
Cursos de interés personal, son los que realiza el personal militar su propio interés y medios, fuera de las horas laborales, en institutos y Centros de Especialización legalmente constituidos, tendiente mejorar su preparación y conocimiento, y que contribuyen a un mejor desempeño de sus funciones.
Los títulos Académicos, son los que se obtienen en Cursos de Especialización Profesional realizados en las Facultades de Universidades y Escuelas Politécnicas legalmente constituidas, realizados por el personal militar por su propio interés y sin la subvención o auspicio de la Fuerza, fuera de las horas laborales y no contemplados en el Plan de Carrera, que contribuyen a un mejor desempeño de sus funciones y que coadyuvan al cumplimiento de las misiones institucionales y de superación individual.
    """,
    'author': 'Manexware S.A.',
    'website': 'http://www.manexware.com',
    'images' : [
    ],
    'depends': ['hr_base'],
    'init_xml': [
    ],
    'data': [
        'hr_training_type/hr_training_type_view.xml'
        #'security/ir.model.access.csv',
        #'report/report.xml',
        #'views/valoration_view.xml',
        #'views/doc_valuation_view.xml',
        #'views/doc_registration_view.xml',
        #'data/demo.xml',
    ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
