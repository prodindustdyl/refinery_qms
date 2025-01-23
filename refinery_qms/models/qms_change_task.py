from odoo import models, fields, api

class QMSChangeTask(models.Model):
    _name = 'qms.change.task'
    _description = 'Change Task'
    _order = 'sequence, id'
    
    change_id = fields.Many2one('qms.change', string='Change Request', required=True)
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
    verification_required = fields.Boolean('Verification Required')
    verification_result = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ], default='pending')
    
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