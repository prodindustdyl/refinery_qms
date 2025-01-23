from odoo import models, fields, api
from datetime import datetime, timedelta

class QMSNonconformity(models.Model):
    _name = 'qms.nonconformity'
    _description = 'QMS Nonconformity'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char('Title', required=True, tracking=True)
    code = fields.Char('NC Code', required=True, tracking=True, readonly=True)
    
    type = fields.Selection([
        ('product', 'Product Nonconformity'),
        ('process', 'Process Nonconformity'),
        ('system', 'System Nonconformity'),
        ('service', 'Service Nonconformity'),
    ], required=True, tracking=True)
    
    origin = fields.Selection([
        ('internal_audit', 'Internal Audit'),
        ('external_audit', 'External Audit'),
        ('customer_complaint', 'Customer Complaint'),
        ('process_monitoring', 'Process Monitoring'),
        ('employee_report', 'Employee Report'),
    ], required=True, tracking=True)
    
    process_id = fields.Many2one('qms.process', string='Process', required=True)
    department_id = fields.Many2one('hr.department', string='Department')
    standard_id = fields.Many2one('qms.standard', string='Standard Reference')
    requirement = fields.Char('Requirement Reference')
    
    description = fields.Text('Description', required=True)
    immediate_actions = fields.Text('Immediate Actions Taken')
    containment_actions = fields.Text('Containment Actions')
    
    severity = fields.Selection([
        ('minor', 'Minor'),
        ('major', 'Major'),
        ('critical', 'Critical'),
    ], required=True, tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('analysis', 'Under Analysis'),
        ('action', 'Action Required'),
        ('verification', 'Under Verification'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True)
    
    reported_by_id = fields.Many2one('res.users', string='Reported By', 
                                    default=lambda self: self.env.user)
    assigned_to_id = fields.Many2one('res.users', string='Assigned To')
    verified_by_id = fields.Many2one('res.users', string='Verified By')
    closed_by_id = fields.Many2one('res.users', string='Closed By')
    
    report_date = fields.Date('Report Date', default=fields.Date.today)
    due_date = fields.Date('Due Date')
    closure_date = fields.Date('Closure Date')
    
    root_cause_ids = fields.One2many('qms.root.cause', 'nonconformity_id', 
                                    string='Root Causes')
    action_ids = fields.One2many('qms.corrective.action', 'nonconformity_id', 
                                string='Corrective Actions')
    cost_ids = fields.One2many('qms.nonconformity.cost', 'nonconformity_id', 
                              string='Associated Costs')
    
    recurrence_check = fields.Boolean('Check for Recurrence')
    recurrence_period = fields.Integer('Recurrence Check Period (days)')
    recurrence_date = fields.Date('Recurrence Check Date')
    recurrence_notes = fields.Text('Recurrence Check Notes')
    
    effectiveness_check = fields.Selection([
        ('not_checked', 'Not Checked'),
        ('effective', 'Effective'),
        ('partially_effective', 'Partially Effective'),
        ('not_effective', 'Not Effective'),
    ], default='not_checked', tracking=True)
    
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    total_cost = fields.Float('Total Cost', compute='_compute_total_cost', store=True)
    
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('qms.nonconformity.sequence')
        return super(QMSNonconformity, self).create(vals)
    
    @api.depends('cost_ids.amount')
    def _compute_total_cost(self):
        for nc in self:
            nc.total_cost = sum(cost.amount for cost in nc.cost_ids)
    
    def action_analyze(self):
        self.write({'state': 'analysis'})
    
    def action_plan(self):
        self.write({'state': 'action'})
    
    def action_verify(self):
        self.write({'state': 'verification'})
    
    def action_close(self):
        self.write({
            'state': 'closed',
            'closure_date': fields.Date.today(),
            'closed_by_id': self.env.user.id,
        })
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})

class QMSRootCause(models.Model):
    _name = 'qms.root.cause'
    _description = 'Root Cause Analysis'
    
    nonconformity_id = fields.Many2one('qms.nonconformity', string='Nonconformity')
    category = fields.Selection([
        ('man', 'Man/People'),
        ('machine', 'Machine/Equipment'),
        ('method', 'Method/Process'),
        ('material', 'Material'),
        ('measurement', 'Measurement'),
        ('environment', 'Environment'),
    ], required=True)
    description = fields.Text('Description', required=True)
    analysis_method = fields.Selection([
        ('5why', '5 Why Analysis'),
        ('fishbone', 'Fishbone Diagram'),
        ('pareto', 'Pareto Analysis'),
        ('fmea', 'FMEA'),
        ('other', 'Other'),
    ])
    evidence = fields.Text('Evidence')
    attachment_ids = fields.Many2many('ir.attachment', string='Analysis Documents')

class QMSCorrectiveAction(models.Model):
    _name = 'qms.corrective.action'
    _description = 'Corrective Action'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    nonconformity_id = fields.Many2one('qms.nonconformity', string='Nonconformity')
    sequence = fields.Integer('Sequence', default=10)
    name = fields.Char('Action Title', required=True)
    description = fields.Text('Description', required=True)
    
    type = fields.Selection([
        ('correction', 'Correction'),
        ('corrective', 'Corrective Action'),
        ('preventive', 'Preventive Action'),
    ], required=True)
    
    state = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='planned', tracking=True)
    
    responsible_id = fields.Many2one('res.users', string='Responsible')
    planned_date = fields.Date('Planned Date')
    completion_date = fields.Date('Completion Date')
    
    effectiveness_criteria = fields.Text('Effectiveness Criteria')
    effectiveness_evaluation = fields.Text('Effectiveness Evaluation')
    effectiveness_result = fields.Selection([
        ('effective', 'Effective'),
        ('partially_effective', 'Partially Effective'),
        ('not_effective', 'Not Effective'),
    ])
    
    notes = fields.Text('Notes')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

class QMSNonconformityCost(models.Model):
    _name = 'qms.nonconformity.cost'
    _description = 'Nonconformity Cost'
    
    nonconformity_id = fields.Many2one('qms.nonconformity', string='Nonconformity')
    name = fields.Char('Description', required=True)
    type = fields.Selection([
        ('material', 'Material Loss'),
        ('rework', 'Rework Cost'),
        ('inspection', 'Additional Inspection'),
        ('delay', 'Delay Cost'),
        ('compensation', 'Customer Compensation'),
        ('other', 'Other'),
    ], required=True)
    amount = fields.Float('Amount', required=True)
    date = fields.Date('Date', default=fields.Date.today)
    notes = fields.Text('Notes')