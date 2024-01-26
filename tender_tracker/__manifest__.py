# -*- coding: utf-8 -*-
{
    'name': "Tender Management System",

    'description': """
        A simple app to help manage tenders more harmoniously. 
    """,

    'author': "Anthony K Mukami",
    'website': "https://toshkruno.github.io/my-portfolio/",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'web', 'sale', 'board', 'mail'],
    'data': [
        'data/mail_templates.xml',
        'security/ir.model.access.csv',
        # 'security/ir.model.access.csv',
        'views/menu.xml',
        'views/tender_views.xml',
        # 'views/dashboard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
