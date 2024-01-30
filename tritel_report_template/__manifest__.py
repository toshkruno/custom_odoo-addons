# -*- coding: utf-8 -*-
{
    'name': "Clever Report Templates",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        A collection of nice invoicing templates.
    """,

    'author': "Tritel Technologies",
    'website': "http://www.yourcompany.com",
    'depends': ['base', 'account', 'sale_management', 'purchase'],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/advanced_template.xml',
        'views/creative_template.xml',
        'views/custom_template.xml',
        'views/elegant_template.xml',
        'views/exclusive_template.xml',
        'views/incredible_template.xml',
        'views/innovative_template.xml',
        'views/invoice_view.xml',
        'views/professional_template.xml',
        'views/report_extra_content_view.xml',
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
        'views/template_report.xml',
        'views/templates.xml',
    ],

    'css': [
        'static/src/css/report_styles.css',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
