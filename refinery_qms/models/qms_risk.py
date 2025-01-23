from odoo import models, fields, api
from datetime import datetime, timedelta

class QMSRisk(models.Model):
    _name = 'qms.risk'
    _description = 'QMS Risk'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Title', required=True, tracking=True)
    code = fields.Char('Risk Code', required=True, tracking=True, readonly=True)
    
    type = fields.Selection([
        ('threat', 'Threat'),
        ('opportunity', 'Opportunity'),
    ], required=True, tracking=True)
    
    category = fields.Selection([
        ('strategic', 'Strategic'),
        ('operational', 'Operational'),
        ('financial', 'Financial'),
        ('compliance', 'Compliance'),
        ('hse', 'Health, Safety & Environment'),
        ('quality', 'Quality'),
        ('reputation', 'Reputation'),
    ], required=True)
    
    process_id = fields.Many2one('qms.process', string='Process', required=True)
    department_id = fields.Many2one('hr.department', string='Department')
    
    description = fields.Text('Description', required=True)
    causes = fields.Text('Causes')
    consequences = fields.Text('Consequences')
    
    likelihood = fields.Selection([
        ('1', 'Rare'),
        ('2', 'Unlikely'),
        ('3', 'Possible'),
        ('4', 'Likely'),
        ('5', 'Almost Certain'),
    ], required=True, tracking=True)
    
    impact = fields.Selection([
        ('1', 'Negligible'),
        ('2', 'Minor'),
        ('3', 'Moderate'),
        ('4', 'Major'),
        ('5', 'Severe'),
    ], required=True, tracking=True)
    
    risk_level = fields.Integer('Risk Level', compute='_compute_risk_level', store=True)
    risk_rating = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('extreme', 'Extreme'),
    ], compute='_compute_risk_rating', store=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('identified', 'Identified'),
        ('assessed', 'Assessed'),
        ('treatment', 'Under Treatment'),
        ('monitoring', 'Monitoring'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True)
    
    owner_id = fields.Many2one('res.users', string='Risk Owner', required=True, 
                              default=lambda self: self.env.user)
    assessor_id = fields.Many2one('res.users', string='Risk Assessor')
    reviewer_id = fields.Many2one('res.users', string='Risk Reviewer')
    
    identification_date = fields.Date('Identification Date', default=fields.Date.today)
    assessment_date = fields.Date('Assessment Date')
    review_date = fields.Date('Review Date')
    next_review_date = fields.Date('Next Review Date')
    
    existing_controls = fields.Text('Existing Controls')
    control_effectiveness = fields.Selection([
        ('ineffective', 'Ineffective'),
        ('partially', 'Partially Effective'),
        ('effective', 'Effective'),
        ('highly', 'Highly Effective'),
    ])
    
    treatment_required = fields.Boolean('Treatment Required')
    treatment_plan_ids = fields.One2many('qms.risk.treatment', 'risk_id', 
                                       string='Treatment Plans')
    
    monitoring_plan = fields.Text('Monitoring Plan')
    monitoring_frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('biannual', 'Biannual'),
        ('annual', 'Annual'),
    ])
    
    review_ids = fields.One2many('qms.risk.review', 'risk_id', string='Risk Reviews')
    kpi_ids = fields.Many2many('qms.kpi', string='Related KPIs')
    
    residual_likelihood = fields.Selection([
        ('1', 'Rare'),
        ('2', 'Unlikely'),
        ('3', 'Possible'),
        ('4', 'Likely'),
        ('5', 'Almost Certain'),
    ])
    residual_impact = fields.Selection([
        ('1', 'Negligible'),
        ('2', 'Minor'),
        ('3', 'Moderate'),
        ('4', 'Major'),
        ('5', 'Severe'),
    ])
    residual_risk_level = fields.Integer('Residual Risk Level', 
                                       compute='_compute_residual_risk_level', store=True)
    
    cost_estimate = fields.Float('Cost Estimate')
    benefit_estimate = fields.Float('Benefit Estimate')
    roi = fields.Float('ROI (%)', compute='_compute_roi', store=True)
    
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('qms.risk.sequence')
        return super(QMSRisk, self).create(vals)
    
    @api.depends('likelihood', 'impact')
    def _compute_risk_level(self):
        for risk in self:
            if risk.likelihood and risk.impact:
                risk.risk_level = int(risk.likelihood) * int(risk.impact)
            else:
                risk.risk_level = 0
    
    @api.depends('risk_level')
    def _compute_risk_rating(self):
        for risk in self:
            if risk.risk_level <= 4:
                risk.risk_rating = 'low'
            elif risk.risk_level <= 8:
                risk.risk_rating = 'medium'
            elif risk.risk_level <= 14:
                risk.risk_rating = 'high'
            else:
                risk.risk_rating = 'extreme'
    
    @api.depends('residual_likelihood', 'residual_impact')
    def _compute_residual_risk_level(self):
        for risk in self:
            if risk.residual_likelihood and risk.residual_impact:
                risk.residual_risk_level = int(risk.residual_likelihood) * int(risk.residual_impact)
            else:
                risk.residual_risk_level = 0
    
    @api.depends('cost_estimate', 'benefit_estimate')
    def _compute_roi(self):
        for risk in self:
            if risk.cost_estimate and risk.cost_estimate > 0:
                risk.roi = ((risk.benefit_estimate - risk.cost_estimate) / risk.cost_estimate) * 100
            else:
                risk.roi = 0.0
    
    def action_identify(self):
        self.write({'state': 'identified'})
    
    def action_assess(self):
        self.write({
            'state': 'assessed',
            'assessment_date': fields.Date.today(),
        })
    
    def action_treat(self):
        self.write({'state': 'treatment'})
    
    def action_monitor(self):
        self.write({'state': 'monitoring'})
    
    def action_close(self):
        self.write({'state': 'closed'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def schedule_next_review(self):
        """Schedule next review based on risk rating"""
        today = fields.Date.today()
        if self.risk_rating == 'extreme':
            months = 1
        elif self.risk_rating == 'high':
            months = 3
        elif self.risk_rating == 'medium':
            months = 6
        else:
            months = 12
            
        self.write({
            'next_review_date': today + timedelta(days=30*months)
        })