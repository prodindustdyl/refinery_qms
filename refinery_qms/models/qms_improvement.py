from odoo import models, fields, api
from datetime import datetime, timedelta

class QMSImprovement(models.Model):
    _name = 'qms.improvement'
    _description = 'QMS Improvement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, id desc'

    name = fields.Char('Title', required=True, tracking=True)
    code = fields.Char('Code', required=True, tracking=True, readonly=True)
    
    type = fields.Selection([
        ('suggestion', 'Improvement Suggestion'),
        ('opportunity', 'Improvement Opportunity'),
        ('innovation', 'Innovation Project'),
        ('kaizen', 'Kaizen Initiative'),
    ], required=True, tracking=True)
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Critical'),
    ], default='1', required=True, tracking=True)
    
    process_id = fields.Many2one('qms.process', string='Process', required=True)
    department_id = fields.Many2one('hr.department', string='Department')
    
    description = fields.Text('Description', required=True)
    justification = fields.Text('Justification')
    expected_benefits = fields.Text('Expected Benefits')
    
    category = fields.Selection([
        ('quality', 'Quality'),
        ('safety', 'Safety'),
        ('efficiency', 'Efficiency'),
        ('cost', 'Cost Reduction'),
        ('environmental', 'Environmental'),
        ('workplace', 'Workplace'),
    ], required=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('evaluation', 'Under Evaluation'),
        ('approved', 'Approved'),
        ('implementation', 'In Implementation'),
        ('review', 'Under Review'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True)
    
    submitted_by_id = fields.Many2one('res.users', string='Submitted By', 
                                     default=lambda self: self.env.user)
    submit_date = fields.Date('Submission Date')
    evaluator_id = fields.Many2one('res.users', string='Evaluator')
    evaluation_date = fields.Date('Evaluation Date')
    approved_by_id = fields.Many2one('res.users', string='Approved By')
    approval_date = fields.Date('Approval Date')
    
    implementation_team_ids = fields.Many2many('res.users', string='Implementation Team')
    planned_hours = fields.Float('Planned Hours')
    actual_hours = fields.Float('Actual Hours')
    planned_cost = fields.Float('Planned Cost')
    actual_cost = fields.Float('Actual Cost')
    
    start_date = fields.Date('Start Date')
    target_date = fields.Date('Target Completion Date')
    completion_date = fields.Date('Actual Completion Date')
    
    task_ids = fields.One2many('qms.improvement.task', 'improvement_id', string='Tasks')
    review_ids = fields.One2many('qms.improvement.review', 'improvement_id', string='Reviews')
    
    evaluation_criteria = fields.Text('Evaluation Criteria')
    evaluation_result = fields.Text('Evaluation Result')
    evaluation_score = fields.Float('Evaluation Score')
    
    risk_assessment = fields.Text('Risk Assessment')
    resource_requirements = fields.Text('Resource Requirements')
    
    success_criteria = fields.Text('Success Criteria')
    success_indicators = fields.One2many('qms.improvement.indicator', 'improvement_id', 
                                       string='Success Indicators')
    
    lessons_learned = fields.Text('Lessons Learned')
    recommendations = fields.Text('Recommendations')
    
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('qms.improvement.sequence')
        return super(QMSImprovement, self).create(vals)
    
    def action_submit(self):
        self.write({
            'state': 'submitted',
            'submit_date': fields.Date.today(),
        })
    
    def action_evaluate(self):
        self.write({
            'state': 'evaluation',
            'evaluator_id': self.env.user.id,
            'evaluation_date': fields.Date.today(),
        })
    
    def action_approve(self):
        self.write({
            'state': 'approved',
            'approved_by_id': self.env.user.id,
            'approval_date': fields.Date.today(),
        })
    
    def action_implement(self):
        self.write({
            'state': 'implementation',
            'start_date': fields.Date.today(),
        })
    
    def action_review(self):
        self.write({'state': 'review'})
    
    def action_complete(self):
        self.write({
            'state': 'completed',
            'completion_date': fields.Date.today(),
        })
    
    def action_reject(self):
        self.write({'state': 'rejected'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})

class QMSImprovementTask(models.Model):
    _name = 'qms.improvement.task'
    _description = 'Improvement Task'
    _order = 'sequence, id'
    
    improvement_id = fields.Many2one('qms.improvement', string='Improvement', required=True)
    sequence = fields.Integer('Sequence', default=10)
    name = fields.Char('Task Name', required=True)
    description = fields.Text('Description')
    
    assigned_to_id = fields.Many2one('res.users', string='Assigned To')
    planned_hours = fields.Float('Planned Hours')
    actual_hours = fields.Float('Actual Hours')
    
    planned_start = fields.Date('Planned Start')
    planned_end = fields.Date('Planned End')
    actual_start = fields.Date('Actual Start')
    actual_end = fields.Date('Actual End')
    
    state = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='planned')
    
    progress = fields.Float('Progress (%)', default=0.0)
    notes = fields.Text('Notes')
    
    def action_start(self):
        self.write({
            'state': 'in_progress',
            'actual_start': fields.Date.today(),
        })
    
    def action_complete(self):
        self.write({
            'state': 'completed',
            'actual_end': fields.Date.today(),
            'progress': 100.0,
        })
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})

class QMSImprovementReview(models.Model):
    _name = 'qms.improvement.review'
    _description = 'Improvement Review'
    _order = 'date desc, id desc'
    
    improvement_id = fields.Many2one('qms.improvement', string='Improvement', required=True)
    date = fields.Date('Review Date', required=True, default=fields.Date.today)
    reviewer_id = fields.Many2one('res.users', string='Reviewer', 
                                 default=lambda self: self.env.user)
    
    type = fields.Selection([
        ('progress', 'Progress Review'),
        ('milestone', 'Milestone Review'),
        ('final', 'Final Review'),
    ], required=True)
    
    effectiveness = fields.Selection([
        ('ineffective', 'Ineffective'),
        ('partially', 'Partially Effective'),
        ('effective', 'Effective'),
        ('highly', 'Highly Effective'),
    ])
    
    achievements = fields.Text('Achievements')
    challenges = fields.Text('Challenges')
    recommendations = fields.Text('Recommendations')
    next_steps = fields.Text('Next Steps')
    
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

class QMSImprovementIndicator(models.Model):
    _name = 'qms.improvement.indicator'
    _description = 'Success Indicator'
    
    improvement_id = fields.Many2one('qms.improvement', string='Improvement', required=True)
    name = fields.Char('Indicator Name', required=True)
    description = fields.Text('Description')
    
    type = fields.Selection([
        ('quantitative', 'Quantitative'),
        ('qualitative', 'Qualitative'),
    ], required=True)
    
    unit = fields.Char('Unit of Measure')
    baseline_value = fields.Float('Baseline Value')
    target_value = fields.Float('Target Value')
    actual_value = fields.Float('Actual Value')
    
    measurement_date = fields.Date('Measurement Date')
    achievement_rate = fields.Float('Achievement Rate (%)', compute='_compute_achievement')
    notes = fields.Text('Notes')
    
    @api.depends('baseline_value', 'target_value', 'actual_value')
    def _compute_achievement(self):
        for indicator in self:
            if indicator.type != 'quantitative':
                indicator.achievement_rate = 0.0
                continue
                
            if indicator.target_value == indicator.baseline_value:
                indicator.achievement_rate = 100.0 if indicator.actual_value >= indicator.target_value else 0.0
            else:
                total_change = indicator.target_value - indicator.baseline_value
                actual_change = indicator.actual_value - indicator.baseline_value
                indicator.achievement_rate = (actual_change / total_change * 100.0) if total_change else 0.0