from odoo import models, fields, api

class QMSChangeResource(models.Model):
    _name = 'qms.change.resource'
    _description = 'Change Resource'
    
    change_id = fields.Many2one('qms.change', string='Change Request', required=True)
    name = fields.Char('Resource Name', required=True)
    
    type = fields.Selection([
        ('human', 'Human Resource'),
        ('material', 'Material'),
        ('equipment', 'Equipment'),
        ('financial', 'Financial'),
        ('other', 'Other'),
    ], required=True)
    
    quantity = fields.Float('Quantity')
    unit = fields.Char('Unit of Measure')
    cost = fields.Float('Cost')
    
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    
    provider = fields.Char('Provider/Supplier')
    notes = fields.Text('Notes')