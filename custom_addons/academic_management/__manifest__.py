# -*- coding: utf-8 -*-
{
    'name': "Gestión Académica",
    'summary': """Módulo para la matriculación y gestión de contratos estudiantiles""",
    'description': """
        Este módulo maneja el proceso de matriculación, asignación de materias y profesores,
        y la elaboración de contratos para estudiantes, incluyendo costos y pagos.
    """,
    'author': "Navor Iturvi",
   
    'category': 'Education',
    'version': '0.1',
    'depends': ['base', 'contacts', 'account'],
    'data': [
        'data/academic_sequence.xml',
        'security/ir.model.access.csv',
        'views/academic_subject_views.xml', 
        'views/academic_contract_views.xml', 
        'views/academic_menu.xml',  
        'views/res_partner_views.xml'
    ],
    'installable': True,
    'application': True, 
    'auto_install': False,
    'license': 'LGPL-3',
    
}
