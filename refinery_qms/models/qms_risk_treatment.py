from odoo import models, fields, api

class QMSRiskTreatment(models.Model):
    _name = 'qms.risk.treatment'
    _description = 'Risk Treatment Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'
    
    risk_id = fields.Many2one('qms.risk', string='Risk', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    name = fields.Char('Treatment Name', required=True)
    
    type = fields.Selection([
        ('avoid', 'Avoid'),
        ('mitigate', 'Mitigate'),
        ('transfer', 'Transfer'),
        ('accept', 'Accept'),
        ('exploit', 'Exploit'),  # For opportunities
        ('enhance', 'Enhance'),  # For opportunities
        ('share', 'Share'),      # For opportunities
    ], required=True)
    
    description = fields.Text('Description', required=True)
    expected_impact = fields.Text('Expected Impact')
    resources_required = fields.Text('Resources Required')
    
    responsible_id = fields.Many2one('res.users', string='Responsible')
    start_date = fields.Date('Start Date')
    due_date = fields.Date('Due Date')
    completion_date = fields.Date('Completion Date')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True)
    
    progress = fields.Float('Progress (%)', default=0.0)
    effectiveness = fields.Selection([
        ('ineffective', 'Ineffective'),
        ('partially', 'Partially Effective'),
        ('effective', 'Effective'),
        ('highly', 'Highly Effective'),
    ])
    
    cost = fields.Float('Cost')
    benefit = fields.Float('Benefit')
    
    notes = fields.Text('Notes')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    def action_plan(self):
        self.write({'state': 'planned'})
    
    def action_start(self):
        self.write({
            'state': 'in_progress',
            'start_date': fields.Date.today(),
        })
    
    def action_complete(self):
        self.write({
            'state': 'completed',
            'completion_date': fields.Date.today(),
            'progress': 100.0,
        })
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})