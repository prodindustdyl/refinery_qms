from odoo import models, fields, api

class QMSProcess(models.Model):
    _name = 'qms.process'
    _description = 'QMS Process'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Process Name', required=True, tracking=True)
    code = fields.Char('Process Code', required=True, tracking=True)
    type = fields.Selection([
        ('strategic', 'Strategic'),
        ('operational', 'Operational'),
        ('support', 'Support'),
    ], required=True, tracking=True)
    
    owner_id = fields.Many2one('res.users', string='Process Owner', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', string='Department')
    
    description = fields.Html('Description')
    objective = fields.Text('Objective', required=True)
    scope = fields.Text('Scope', required=True)
    
    input_ids = fields.One2many('qms.process.io', 'process_id', 
                               string='Inputs', domain=[('io_type', '=', 'input')])
    output_ids = fields.One2many('qms.process.io', 'process_id', 
                                string='Outputs', domain=[('io_type', '=', 'output')])
    
    resource_ids = fields.Many2many('qms.process.resource', string='Resources')
    risk_ids = fields.One2many('qms.process.risk', 'process_id', string='Risks')
    kpi_ids = fields.One2many('qms.kpi', 'process_id', string='KPIs')
    
    document_ids = fields.One2many('qms.document', 'process_id', string='Documents')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('under_review', 'Under Review'),
        ('inactive', 'Inactive'),
    ], default='draft', tracking=True)
    
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('qms.process.sequence')
        return super(QMSProcess, self).create(vals)
    
    def action_activate(self):
        self.write({'state': 'active'})
    
    def action_review(self):
        self.write({'state': 'under_review'})
    
    def action_deactivate(self):
        self.write({'state': 'inactive'})

class QMSProcessIO(models.Model):
    _name = 'qms.process.io'
    _description = 'Process Inputs and Outputs'
    
    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    io_type = fields.Selection([
        ('input', 'Input'),
        ('output', 'Output'),
    ], required=True)
    process_id = fields.Many2one('qms.process', string='Process')
    source_process_id = fields.Many2one('qms.process', string='Source Process')
    target_process_id = fields.Many2one('qms.process', string='Target Process')

class QMSProcessResource(models.Model):
    _name = 'qms.process.resource'
    _description = 'Process Resources'
    
    name = fields.Char('Name', required=True)
    type = fields.Selection([
        ('human', 'Human Resource'),
        ('infrastructure', 'Infrastructure'),
        ('equipment', 'Equipment'),
        ('software', 'Software'),
        ('material', 'Material'),
    ], required=True)
    description = fields.Text('Description')
    quantity = fields.Float('Quantity')
    unit = fields.Char('Unit of Measure')

class QMSProcessRisk(models.Model):
    _name = 'qms.process.risk'
    _description = 'Process Risks'
    
    name = fields.Char('Risk Description', required=True)
    process_id = fields.Many2one('qms.process', string='Process')
    probability = fields.Selection([
        ('1', 'Very Low'),
        ('2', 'Low'),
        ('3', 'Medium'),
        ('4', 'High'),
        ('5', 'Very High'),
    ], required=True)
    impact = fields.Selection([
        ('1', 'Very Low'),
        ('2', 'Low'),
        ('3', 'Medium'),
        ('4', 'High'),
        ('5', 'Very High'),
    ], required=True)
    risk_level = fields.Integer('Risk Level', compute='_compute_risk_level', store=True)
    mitigation_plan = fields.Text('Mitigation Plan')
    responsible_id = fields.Many2one('res.users', string='Responsible')
    
    @api.depends('probability', 'impact')
    def _compute_risk_level(self):
        for risk in self:
            risk.risk_level = int(risk.probability) * int(risk.impact)