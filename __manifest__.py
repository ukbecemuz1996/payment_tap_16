# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Tap Payment Acquirer',
    'version': '2.0',
    'category': 'Accounting/Payment Acquirers',
    'sequence': 501,
    'summary': 'Payment Acquirer: Tap Implementation',
    'description': """Tap Payment Acquirer""",
    'depends': ['payment'],
    'data': [
        'data/payment_acquirer_data.xml',
        'views/payment_views.xml',
        'views/payment_templates.xml',
    ],
    'application': True,
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
