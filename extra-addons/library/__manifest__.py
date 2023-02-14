# -*- coding: utf-8 -*-
{
    'name': "My Library",  # Module title
    'summary': "Manage books easily",  # Module subtitle phrase
    'description': """
Manage Library
==============
Description related to library.
    """,  # Supports reStructuredText(RST) format
    'author': "Parth Gajjar",
    'website': "http://www.example.com",
    'category': 'Library',
    'version': '14.0.1',
    'depends': ['base','contacts','mail','website'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/library_book.xml',
        'views/library_book_categ.xml',
        'views/library_book_rent.xml',
        'views/library_book_rent_statistics.xml',
        'views/templates.xml',
        'views/snippets.xml',
        'data/library_atage.xml',
        'reports/book_rent_templates.xml',
        'reports/book_rent_report.xml',
        #'views/library_teste.xml',
        #'views/res_config_settings_views.xml',
        'wizard/library_rent_wizard.xml',
        'wizard/library_return_wizard.xml',
        
        
        
    ],
    # This demo data files will be loaded if db initialize with demo data (commented because file is not used in this example)
     'demo': [
         'data/demo.xml'
     ],
}