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
        "security/sm_security.xml",
        "security/ir.model.access.csv",
        "security/sm_record_rules.xml",
        "data/sm_quotation_sequence.xml",
        "data/sm_work_order_sequence.xml",
        "views/sm_service_views.xml",
        "views/sm_quotation_views.xml",
        "views/sm_work_order_views.xml",
        "views/sm_service_request_views.xml",
        "wizards/sm_quotation_refuse_wizard_views.xml",

        # 4. Relatórios QWeb
        "report/sm_quotation_reports.xml",
        "report/sm_quotation_templates.xml",

        "views/sm_menus.xml",
],
    'installable': True,
    'application': True,
    'auto_install': False,
}