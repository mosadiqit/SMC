# -*- coding: utf-8 -*-
{
    'name': "purchase_import_order",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Erum Asghar",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase', 'purchase_stock','branch'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/import_order_security.xml',
        'views/views.xml',
        #'views/templates.xml',
        'data/import_order_seq.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
