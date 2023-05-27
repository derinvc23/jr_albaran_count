# -*- coding: utf-8 -*-
{
    'name': "Report qty",

   
    'author': "jesus rodriguez",
    

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock',"account","stock_account"],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        
       
        
        
        'security/ir.model.access.csv',

        'views/view_albaran.xml',
    
    ],
    # only loaded in demonstration mode
    
}
