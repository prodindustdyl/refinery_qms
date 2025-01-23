from odoo import models, fields, api

class QMSChangeImpact(models.Model):
    _name = 'qms.change.impact'
    _description = 'Change Impact Analysis'
    
    change_id = fields.Many2one('qms.change', string='Change Request', required=True)
    area = fields.Selection([
        ('process', 'Process'),
        ('quality', 'Quality'),
        ('safety', 'Safety'),
        ('environmental', 'Environmental'),
        ('operational', 'Operational'),
        ('financial', 'Financial'),
        ('customer', 'Customer'),
        ('regulatory', 'Regulatory'),
    ], required=True)
    
    description = fields.Text('Impact Description', required=True)
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], required=True)
    
    mitigation_required = fields.Boolean('Mitigation Required')
    mitigation_plan = fields.Text('Mitigation Plan')
    
    responsible_id = fields.Many2one('res.users', string='Responsible')
    verification_required = fields.Boolean('Verification Required')
    verification_method = fields.Text('Verification Method')