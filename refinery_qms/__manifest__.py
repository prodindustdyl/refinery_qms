{
    'name': 'Refinery Quality Management System',
    'version': '18.0.1.0.0',
    'category': 'Quality',
    'summary': 'Quality Management System for Oil Refinery',
    'description': """
        Quality Management System module for Oil Refinery implementing ISO 9001 requirements.
        Features:
        - Document Management
        - Process Control
        - Audit Management
        - Non-conformity Management
        - KPI Tracking
        - Continuous Improvement
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mail',
        'web',
        'resource',
        'portal',
    ],
    'data': [
        'security/qms_security.xml',
        'security/ir.model.access.csv',
        'views/qms_document_views.xml',
        'views/qms_process_views.xml',
        'views/qms_audit_views.xml',
        'views/qms_nonconformity_views.xml',
        'views/qms_kpi_views.xml',
        'views/qms_improvement_views.xml',
        'views/qms_menus.xml',
        'data/qms_sequence.xml',
    ],
    'demo': [
        'demo/qms_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}