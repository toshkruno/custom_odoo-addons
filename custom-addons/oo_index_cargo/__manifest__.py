# -*- coding: utf-8 -*-
{
    'name': "Tritel Customizations",

    'summary': """
        """,

    'description': """
    """,

    'author': "Tritel",
    'website': "http://www.tritel.com",


    'category': 'Accounting',
    'version': '15.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'hr_payroll', 'sale', 'freight_management_system'],

    # always loaded
    'data': [
        'reports/invoice.xml',
        'reports/payslip.xml',
        'reports/sale_order.xml',
        'views/views.xml',
    ],

}
