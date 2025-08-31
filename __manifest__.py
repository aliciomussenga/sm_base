# -*- coding: utf-8 -*-
{
    'name': 'Service Management - Base',
    'version': '18.0.1.0.0',
    'category': 'Técnico',
    'summary': 'Módulo base para gestão de serviços e assistência técnica',
    'description': """
Service Management ERP - Core Module
====================================
Este módulo fornece a estrutura base para a gestão de serviços:
- Configurações fundamentais
- Extensão do cadastro de parceiros (Clientes/Técnicos)
- Categorização inicial de serviços
    """,
    'author': 'Alício Mussenga',
    'license': 'LGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        "views/sm_service_views.xml",
        "views/sm_quotation_views.xml"
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}