from odoo import models, fields, api
from datetime import datetime, timedelta

class QMSKPI(models.Model):
    _name = 'qms.kpi'
    _description = 'QMS Key Performance Indicator'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    name = fields.Char('KPI Name', required=True, tracking=True)
    code = fields.Char('KPI Code', required=True, tracking=True, readonly=True)
    sequence = fields.Integer('Sequence', default=10)
    
    process_id = fields.Many2one('qms.process', string='Process', required=True)
    department_id = fields.Many2one('hr.department', string='Department')
    owner_id = fields.Many2one('res.users', string='KPI Owner', required=True, tracking=True)
    
    description = fields.Text('Description')
    calculation_method = fields.Text('Calculation Method', required=True)
    measurement_frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('biannual', 'Biannual'),
        ('annual', 'Annual'),
    ], required=True, tracking=True)
    
    unit = fields.Char('Unit of Measure', required=True)
    target_value = fields.Float('Target Value', required=True)
    min_value = fields.Float('Minimum Acceptable Value')
    max_value = fields.Float('Maximum Acceptable Value')
    
    direction = fields.Selection([
        ('maximize', 'Higher is Better'),
        ('minimize', 'Lower is Better'),
        ('range', 'Keep in Range'),
    ], required=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], default='draft', tracking=True)
    
    measurement_ids = fields.One2many('qms.kpi.measurement', 'kpi_id', string='Measurements')
    current_value = fields.Float('Current Value', compute='_compute_current_value', store=True)
    trend = fields.Selection([
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
    ], compute='_compute_trend', store=True)
    
    standard_ids = fields.Many2many('qms.standard', string='Related Standards')
    category = fields.Selection([
        ('quality', 'Quality'),
        ('safety', 'Safety'),
        ('environmental', 'Environmental'),
        ('energy', 'Energy'),
        ('operational', 'Operational'),
        ('financial', 'Financial'),
    ], required=True)
    
    alert_ids = fields.One2many('qms.kpi.alert', 'kpi_id', string='Alerts')
    action_plan_ids = fields.One2many('qms.kpi.action', 'kpi_id', string='Action Plans')
    
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('qms.kpi.sequence')
        return super(QMSKPI, self).create(vals)
    
    @api.depends('measurement_ids.value', 'measurement_ids.date')
    def _compute_current_value(self):
        for kpi in self:
            latest_measurement = kpi.measurement_ids.sorted('date', reverse=True)[:1]
            kpi.current_value = latest_measurement.value if latest_measurement else 0.0
    
    @api.depends('measurement_ids.value', 'measurement_ids.date')
    def _compute_trend(self):
        for kpi in self:
            measurements = kpi.measurement_ids.sorted('date', reverse=True)[:5]
            if len(measurements) < 2:
                kpi.trend = 'stable'
                continue
            
            values = [m.value for m in measurements]
            if all(values[i] > values[i+1] for i in range(len(values)-1)):
                kpi.trend = 'improving' if kpi.direction == 'maximize' else 'declining'
            elif all(values[i] < values[i+1] for i in range(len(values)-1)):
                kpi.trend = 'declining' if kpi.direction == 'maximize' else 'improving'
            else:
                kpi.trend = 'stable'
    
    def action_activate(self):
        self.write({'state': 'active'})
    
    def action_deactivate(self):
        self.write({'state': 'inactive'})
    
    def check_alerts(self):
        """Check KPI values against thresholds and create alerts if needed"""
        for kpi in self:
            if kpi.state != 'active':
                continue
            
            if not kpi.current_value:
                continue
                
            alert_level = False
            alert_message = False
            
            if kpi.direction == 'maximize':
                if kpi.current_value < kpi.min_value:
                    alert_level = 'critical'
                    alert_message = f'Value {kpi.current_value} is below minimum {kpi.min_value}'
                elif kpi.current_value < kpi.target_value:
                    alert_level = 'warning'
                    alert_message = f'Value {kpi.current_value} is below target {kpi.target_value}'
            
            elif kpi.direction == 'minimize':
                if kpi.current_value > kpi.max_value:
                    alert_level = 'critical'
                    alert_message = f'Value {kpi.current_value} is above maximum {kpi.max_value}'
                elif kpi.current_value > kpi.target_value:
                    alert_level = 'warning'
                    alert_message = f'Value {kpi.current_value} is above target {kpi.target_value}'
            
            elif kpi.direction == 'range':
                if kpi.current_value < kpi.min_value:
                    alert_level = 'critical'
                    alert_message = f'Value {kpi.current_value} is below range minimum {kpi.min_value}'
                elif kpi.current_value > kpi.max_value:
                    alert_level = 'critical'
                    alert_message = f'Value {kpi.current_value} is above range maximum {kpi.max_value}'
            
            if alert_level and alert_message:
                self.env['qms.kpi.alert'].create({
                    'kpi_id': kpi.id,
                    'level': alert_level,
                    'message': alert_message,
                    'value': kpi.current_value,
                })

class QMSKPIMeasurement(models.Model):
    _name = 'qms.kpi.measurement'
    _description = 'KPI Measurement'
    _order = 'date desc, id desc'
    
    kpi_id = fields.Many2one('qms.kpi', string='KPI', required=True, ondelete='cascade')
    date = fields.Date('Measurement Date', required=True, default=fields.Date.today)
    value = fields.Float('Value', required=True)
    notes = fields.Text('Notes')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    @api.model
    def create(self, vals):
        res = super(QMSKPIMeasurement, self).create(vals)
        res.kpi_id.check_alerts()
        return res

class QMSKPIAlert(models.Model):
    _name = 'qms.kpi.alert'
    _description = 'KPI Alert'
    _order = 'create_date desc'
    
    kpi_id = fields.Many2one('qms.kpi', string='KPI', required=True, ondelete='cascade')
    date = fields.Datetime('Alert Date', default=fields.Datetime.now, required=True)
    level = fields.Selection([
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ], required=True)
    message = fields.Text('Alert Message', required=True)
    value = fields.Float('KPI Value')
    state = fields.Selection([
        ('new', 'New'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ], default='new')
    
    acknowledged_by_id = fields.Many2one('res.users', string='Acknowledged By')
    acknowledged_date = fields.Datetime('Acknowledged Date')
    resolution_notes = fields.Text('Resolution Notes')
    
    def action_acknowledge(self):
        self.write({
            'state': 'acknowledged',
            'acknowledged_by_id': self.env.user.id,
            'acknowledged_date': fields.Datetime.now(),
        })
    
    def action_resolve(self):
        self.write({'state': 'resolved'})

class QMSKPIAction(models.Model):
    _name = 'qms.kpi.action'
    _description = 'KPI Action Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    kpi_id = fields.Many2one('qms.kpi', string='KPI', required=True)
    name = fields.Char('Action Title', required=True)
    description = fields.Text('Description', required=True)
    
    type = fields.Selection([
        ('preventive', 'Preventive Action'),
        ('corrective', 'Corrective Action'),
        ('improvement', 'Improvement Action'),
    ], required=True)
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Critical'),
    ], default='1', required=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True)
    
    responsible_id = fields.Many2one('res.users', string='Responsible')
    planned_date = fields.Date('Planned Date')
    completion_date = fields.Date('Completion Date')
    
    expected_impact = fields.Text('Expected Impact')
    actual_impact = fields.Text('Actual Impact')
    notes = fields.Text('Notes')
    
    def action_plan(self):
        self.write({'state': 'planned'})
    
    def action_start(self):
        self.write({'state': 'in_progress'})
    
    def action_complete(self):
        self.write({
            'state': 'completed',
            'completion_date': fields.Date.today(),
        })
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})