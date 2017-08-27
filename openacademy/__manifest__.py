# -*- coding: utf-8 -*-
{
    'name': "openacademy",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        them vao si so ma khong duoc ne
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale'],#

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/openacademy.xml',
        'views/partner.xml',
        #'views/session_workflow.xml',
        #'views/sale_order_in_openacademy.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "application":True,
    "sequence":1
}