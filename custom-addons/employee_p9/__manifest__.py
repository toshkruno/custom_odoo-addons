# -*- coding: utf-8 -*-
{
    'name': "P9",

    'summary': """
        Employee P9""",

    'description': """
       
    """,

    'author': "Eric Waweru",
    'website': "http://www.yourcompany.com",

    'category': 'Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr', 'hr_ke'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizards/p9.xml',
        'views/views.xml',
        'reports/misc.xml',
        'reports/templates.xml',
        'reports/main.xml',
        'reports/report.xml',
        
    ],

}
