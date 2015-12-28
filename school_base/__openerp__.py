{
    'name': 'School Base',
    'version': '1.0',
    'category': 'Marine',
    'complexity': "normal",
    'description': """
Module Basic for School Digedo
    """,
    'author': 'Manexware SA',
    'website': 'http://www.manexware.com',
    'images' : [
        'images/school.png', 
        'images/school_hover.png',
    ],
    'depends': ['account', 'hr'],
    'data': [
        'school_grade/school_grade_view.xml',
        'school_specialty/school_specialty_view.xml',
        'hr_employee/hr_employee_view.xml',

        'menu/menu.xml',
        'data/grade_data.xml',
        'data/specialty_data.xml',
    ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
