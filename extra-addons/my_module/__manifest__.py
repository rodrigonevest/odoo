# -*- coding: utf-8 -*-
{
    'name': "My Module",  # Module title
    'description': """Long description""",  # You can also rst format
    'author': "Rodrigo Neves",
    'website': "http://www.example.com",
    'category': 'Uncategorized',
    'version': '14.0.1',
    'depends': ['base', 'account','project'],
    'data': [
        #'views/my_contacts.xml',
        'views/my_contatcts_kanban.xml',
        'views/my_tasks.xml',
        #'views/my_tasks_calendar.xml',
        'views/my_tasks_graph_pivot.xml',
        'views/my_tasks_dashboard.xml',
    ],
}