from odoo import models, fields, api
from datetime import datetime, timedelta

class QMSAudit(models.Model):
    _name = 'qms.audit'
    _description = 'QMS Audit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc'

    name = fields.Char('Title', required=True, tracking=True)
    code = fields.Char('Audit Code', required=True, tracking=True, readonly=True)
    
    type = fields.Selection([
        ('internal', 'Internal Audit'),
        ('external', 'External Audit'),
        ('certification', 'Certification Audit'),
    ], required=True, tracking=True)
    
    standard_ids = fields.Many2many('qms.standard', string='Standards')
    process_ids = fields.Many2many('qms.process', string='Processes to Audit')
    department_ids = fields.Many2many('hr.department', string='Departments to Audit')
    
    date_start = fields.Date('Start Date', required=True, tracking=True)
    date_end = fields.Date('End Date', required=True, tracking=True)
    duration = fields.Integer('Duration (days)', compute='_compute_duration', store=True)
    
    lead_auditor_id = fields.Many2one('res.users', string='Lead Auditor', required=True)
    auditor_ids = fields.Many2many('res.users', string='Audit Team')
    auditee_ids = fields.Many2many('res.users', string='Auditees')
    
    objective = fields.Text('Audit Objective', required=True)
    scope = fields.Text('Audit Scope', required=True)
    methodology = fields.Text('Audit Methodology')
    
    checklist_ids = fields.One2many('qms.audit.checklist', 'audit_id', string='Audit Checklist')
    finding_ids = fields.One2many('qms.audit.finding', 'audit_id', string='Audit Findings')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True)
    
    conclusion = fields.Text('Audit Conclusion')
    recommendations = fields.Text('Recommendations')
    
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('qms.audit.sequence')
        return super(QMSAudit, self).create(vals)
    
    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        for audit in self:
            if audit.date_start and audit.date_end:
                delta = audit.date_end - audit.date_start
                audit.duration = delta.days + 1
            else:
                audit.duration = 0
    
    def action_plan(self):
        self.write({'state': 'planned'})
    
    def action_start(self):
        self.write({'state': 'in_progress'})
    
    def action_complete(self):
        self.write({'state': 'completed'})
    
    def action_close(self):
        self.write({'state': 'closed'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})

class QMSAuditChecklist(models.Model):
    _name = 'qms.audit.checklist'
    _description = 'Audit Checklist'
    
    audit_id = fields.Many2one('qms.audit', string='Audit', required=True)
    sequence = fields.Integer('Sequence', default=10)
    requirement = fields.Text('Requirement', required=True)
    evidence_required = fields.Text('Evidence Required')
    
    result = fields.Selection([
        ('compliant', 'Compliant'),
        ('partially_compliant', 'Partially Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('not_applicable', 'Not Applicable'),
    ])
    
    evidence_obtained = fields.Text('Evidence Obtained')
    notes = fields.Text('Notes')
    attachment_ids = fields.Many2many('ir.attachment', string='Evidence Attachments')

class QMSAuditFinding(models.Model):
    _name = 'qms.audit.finding'
    _description = 'Audit Finding'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    audit_id = fields.Many2one('qms.audit', string='Audit', required=True)
    sequence = fields.Integer('Sequence', default=10)
    
    type = fields.Selection([
        ('nonconformity', 'Nonconformity'),
        ('observation', 'Observation'),
        ('opportunity', 'Improvement Opportunity'),
    ], required=True)
    
    standard_id = fields.Many2one('qms.standard', string='Standard Reference')
    requirement = fields.Char('Requirement Reference')
    description = fields.Text('Finding Description', required=True)
    evidence = fields.Text('Evidence')
    
    severity = fields.Selection([
        ('minor', 'Minor'),
        ('major', 'Major'),
        ('critical', 'Critical'),
    ], required=True)
    
    state = fields.Selection([
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ], default='open', tracking=True)
    
    root_cause = fields.Text('Root Cause Analysis')
    correction = fields.Text('Immediate Correction')
    corrective_action = fields.Text('Corrective Action')
    
    responsible_id = fields.Many2one('res.users', string='Responsible')
    due_date = fields.Date('Due Date')
    completion_date = fields.Date('Completion Date')
    
    verification_result = fields.Text('Verification Result')
    verified_by_id = fields.Many2one('res.users', string='Verified By')
    verification_date = fields.Date('Verification Date')
    
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

class QMSStandard(models.Model):
    _name = 'qms.standard'
    _description = 'QMS Standard'
    
    name = fields.Char('Standard Name', required=True)
    code = fields.Char('Standard Code', required=True)
    description = fields.Text('Description')
    version = fields.Char('Version')
    active = fields.Boolean('Active', default=True)