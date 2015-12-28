{
    'name': 'Training',
    'version': '1.0',
    'category': 'Marine',
    'complexity': "normal",
    'description': """
Training
    """,
    'author': 'Manexware SA',
    'website': 'http://www.manexware.com',
    'depends': ['school_base'],
    'update_xml': [
        'school_training_category/school_training_category_view.xml',
        'school_training_sector/school_training_sector_view.xml',
        'school_training_city/school_training_city_view.xml',
        'school_training_educational_institution/school_training_educational_institution_view.xml',
        'school_training_financial_concept/school_training_financial_concept_view.xml',
        'school_training_financial_detail/school_training_financial_detail_view.xml',
        'school_training_model/school_training_view.xml',
        'school_training_news_report/school_training_news_report_view.xml',
        'security/training_security.xml',
        'security/ir.model.access.csv',
        #'views/training_view.xml',
        #'views/city_view.xml',
        #'views/educational_institution_view.xml',
        #'views/news_report_view.xml'
        'menu/menu.xml'
    ],
    'data': [
        'data/sector_data.xml',
        'data/course_category_data.xml',
        'data/concept_data.xml',
        'data/city_data.xml'
    ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
