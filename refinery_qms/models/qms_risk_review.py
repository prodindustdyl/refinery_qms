from odoo import models, fields, api

class QMSRiskReview(models.Model):
    _name = 'qms.risk.review'
    _description = 'Risk Review'
    _order = 'review_date desc, id desc'
    
    risk_id = fields.Many2one('qms.risk', string='Risk', required=True, ondelete='cascade')
    reviewer_id = fields.Many2one('res.users', string='Reviewer', 
                                 default=lambda self: self.env.user)
    review_date = fields.Date('Review Date', required=True, default=fields.Date.today)
    
    previous_risk_level = fields.Integer('Previous Risk Level')
    current_risk_level = fields.Integer('Current Risk Level')
    risk_trend = fields.Selection([
        ('increasing', 'Increasing'),
        ('stable', 'Stable'),
        ('decreasing', 'Decreasing'),
    ], compute='_compute_risk_trend', store=True)
    
    control_effectiveness = fields.Selection([
        ('ineffective', 'Ineffective'),
        ('partially', 'Partially Effective'),
        ('effective', 'Effective'),
        ('highly', 'Highly Effective'),
    ], required=True)
    
    changes_since_last = fields.Text('Changes Since Last Review')
    review_findings = fields.Text('Review Findings')
    recommendations = fields.Text('Recommendations')
    
    requires_escalation = fields.Boolean('Requires Escalation')
    escalation_notes = fields.Text('Escalation Notes')
    
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    @api.depends('previous_risk_level', 'current_risk_level')
    def _compute_risk_trend(self):
        for review in self:
            if not review.previous_risk_level or not review.current_risk_level:
                review.risk_trend = 'stable'
            elif review.current_risk_level > review.previous_risk_level:
                review.risk_trend = 'increasing'
            elif review.current_risk_level < review.previous_risk_level:
                review.risk_trend = 'decreasing'
            else:
                review.risk_trend = 'stable'