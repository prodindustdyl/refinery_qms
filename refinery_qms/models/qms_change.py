from odoo import models, fields, api
from datetime import datetime, timedelta

class QMSChange(models.Model):
    _name = 'qms.change'
    _description = 'QMS Change Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Title', required=True, tracking=True)
    code = fields.Char('Change Code', required=True, tracking=True, readonly=True)
    
    type = fields.Selection([
        ('process', 'Process Change'),
        ('system', 'System Change'),
        ('organizational', 'Organizational Change'),
        ('product', 'Product Change'),
        ('equipment', 'Equipment Change'),
        ('document', 'Document Change'),
    ], required=True, tracking=True)
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Critical'),
    ], default='1', required=True, tracking=True)
    
    process_id = fields.Many2one('qms.process', string='Process')
    department_id = fields.Many2one('hr.department', string='Department')
    
    description = fields.Text('Change Description', required=True)
    justification = fields.Text('Change Justification', required=True)
    objectives = fields.Text('Change Objectives')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('analysis', 'Under Analysis'),
        ('approval', 'Pending Approval'),
        ('planning', 'Planning'),
        ('implementation', 'Implementation'),
        ('verification', 'Verification'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True)
    
    requester_id = fields.Many2one('res.users', string='Requested By', 
                                  default=lambda self: self.env.user)
    owner_id = fields.Many2one('res.users', string='Change Owner')
    approver_id = fields.Many2one('res.users', string='Approver')
    
    request_date = fields.Date('Request Date', default=fields.Date.today)
    planned_date = fields.Date('Planned Implementation Date')
    completion_date = fields.Date('Completion Date')
    
    risk_assessment_required = fields.Boolean('Risk Assessment Required')
    risk_assessment_ids = fields.One2many('qms.change.risk', 'change_id', 
                                        string='Risk Assessment')
    
    impact_analysis_ids = fields.One2many('qms.change.impact', 'change_id', 
                                        string='Impact Analysis')
    
    resource_ids = fields.One2many('qms.change.resource', 'change_id', 
                                  string='Required Resources')
    
    task_ids = fields.One2many('qms.change.task', 'change_id', string='Tasks')
    
    verification_plan = fields.Text('Verification Plan')
    verification_results = fields.Text('Verification Results')
    verification_status = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ], default='pending')
    
    effectiveness_criteria = fields.Text('Effectiveness Criteria')
    effectiveness_review = fields.Text('Effectiveness Review')
    effectiveness_date = fields.Date('Effectiveness Review Date')
    
    lessons_learned = fields.Text('Lessons Learned')
    notes = fields.Text('Notes')
    
    document_ids = fields.Many2many('qms.document', string='Related Documents')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    total_cost = fields.Float('Total Cost', compute='_compute_total_cost', store=True)
    
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('qms.change.sequence')
        return super(QMSChange, self).create(vals)
    
    @api.depends('resource_ids.cost')
    def _compute_total_cost(self):
        for change in self:
            change.total_cost = sum(resource.cost for resource in change.resource_ids)
    
    def action_submit(self):
        self.write({'state': 'submitted'})
    
    def action_analyze(self):
        self.write({'state': 'analysis'})
    
    def action_request_approval(self):
        self.write({'state': 'approval'})
    
    def action_approve(self):
        self.write({'state': 'planning'})
    
    def action_implement(self):
        self.write({'state': 'implementation'})
    
    def action_verify(self):
        self.write({'state': 'verification'})
    
    def action_complete(self):
        self.write({
            'state': 'completed',
            'completion_date': fields.Date.today(),
        })
    
    def action_reject(self):
        self.write({'state': 'rejected'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})