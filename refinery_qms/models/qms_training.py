from odoo import models, fields, api
from datetime import datetime, timedelta

class QMSTraining(models.Model):
    _name = 'qms.training'
    _description = 'QMS Training'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc'

    name = fields.Char('Title', required=True, tracking=True)
    code = fields.Char('Training Code', required=True, tracking=True, readonly=True)
    
    type = fields.Selection([
        ('induction', 'Induction Training'),
        ('quality', 'Quality Management'),
        ('safety', 'Safety Training'),
        ('technical', 'Technical Training'),
        ('certification', 'Certification Training'),
        ('refresher', 'Refresher Course'),
    ], required=True, tracking=True)
    
    process_id = fields.Many2one('qms.process', string='Related Process')
    department_id = fields.Many2one('hr.department', string='Department')
    trainer_id = fields.Many2one('res.users', string='Trainer')
    
    date_start = fields.Date('Start Date', required=True, tracking=True)
    date_end = fields.Date('End Date', required=True, tracking=True)
    duration = fields.Float('Duration (hours)', required=True)
    
    objective = fields.Text('Training Objective', required=True)
    content = fields.Html('Training Content')
    prerequisites = fields.Text('Prerequisites')
    
    max_participants = fields.Integer('Maximum Participants')
    min_participants = fields.Integer('Minimum Participants')
    participant_ids = fields.One2many('qms.training.participant', 'training_id', string='Participants')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True)
    
    effectiveness_evaluation = fields.Selection([
        ('pending', 'Pending'),
        ('effective', 'Effective'),
        ('partially', 'Partially Effective'),
        ('ineffective', 'Ineffective'),
    ], default='pending', tracking=True)
    
    evaluation_method = fields.Selection([
        ('test', 'Written Test'),
        ('practical', 'Practical Assessment'),
        ('presentation', 'Presentation'),
        ('project', 'Project Work'),
        ('observation', 'Workplace Observation'),
    ])
    
    passing_score = fields.Float('Passing Score (%)', default=70)
    certificate_validity = fields.Integer('Certificate Validity (months)')
    requires_renewal = fields.Boolean('Requires Renewal')
    
    cost = fields.Float('Training Cost')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('qms.training.sequence')
        return super(QMSTraining, self).create(vals)
    
    def action_plan(self):
        self.write({'state': 'planned'})
    
    def action_start(self):
        self.write({'state': 'in_progress'})
    
    def action_complete(self):
        self.write({'state': 'completed'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})

class QMSTrainingParticipant(models.Model):
    _name = 'qms.training.participant'
    _description = 'Training Participant'
    _rec_name = 'employee_id'
    
    training_id = fields.Many2one('qms.training', string='Training', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    attendance = fields.Float('Attendance %')
    score = fields.Float('Score')
    result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('pending', 'Pending'),
    ], compute='_compute_result', store=True)
    
    certificate_number = fields.Char('Certificate Number')
    certificate_date = fields.Date('Certificate Date')
    expiry_date = fields.Date('Expiry Date')
    
    feedback = fields.Text('Participant Feedback')
    trainer_remarks = fields.Text('Trainer Remarks')
    
    @api.depends('score', 'training_id.passing_score')
    def _compute_result(self):
        for record in self:
            if not record.score:
                record.result = 'pending'
            else:
                record.result = 'pass' if record.score >= record.training_id.passing_score else 'fail'

class QMSCompetencyMatrix(models.Model):
    _name = 'qms.competency.matrix'
    _description = 'Competency Matrix'
    
    process_id = fields.Many2one('qms.process', string='Process', required=True)
    position_id = fields.Many2one('hr.job', string='Position', required=True)
    required_training_ids = fields.Many2many('qms.training', string='Required Training')
    
    knowledge_requirements = fields.Text('Knowledge Requirements')
    skill_requirements = fields.Text('Skill Requirements')
    experience_requirements = fields.Text('Experience Requirements')
    
    certification_requirements = fields.Text('Certification Requirements')
    renewal_frequency = fields.Integer('Renewal Frequency (months)')
    
    notes = fields.Text('Notes')