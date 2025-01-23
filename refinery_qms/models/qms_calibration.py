from odoo import models, fields, api
from datetime import datetime, timedelta

class QMSEquipment(models.Model):
    _name = 'qms.equipment'
    _description = 'Measurement Equipment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Equipment Name', required=True, tracking=True)
    code = fields.Char('Equipment Code', required=True, tracking=True, readonly=True)
    serial_number = fields.Char('Serial Number', required=True)
    manufacturer = fields.Char('Manufacturer')
    model = fields.Char('Model')
    
    type = fields.Selection([
        ('pressure', 'Pressure Gauge'),
        ('temperature', 'Temperature Sensor'),
        ('flow', 'Flow Meter'),
        ('level', 'Level Sensor'),
        ('weight', 'Weighing Scale'),
        ('analytical', 'Analytical Instrument'),
        ('other', 'Other'),
    ], required=True)
    
    location = fields.Char('Location')
    department_id = fields.Many2one('hr.department', string='Department')
    process_id = fields.Many2one('qms.process', string='Process')
    
    measurement_range = fields.Char('Measurement Range')
    accuracy = fields.Char('Accuracy')
    resolution = fields.Char('Resolution')
    
    calibration_frequency = fields.Integer('Calibration Frequency (days)', required=True)
    last_calibration = fields.Date('Last Calibration Date')
    next_calibration = fields.Date('Next Calibration Date', compute='_compute_next_calibration', store=True)
    calibration_ids = fields.One2many('qms.calibration', 'equipment_id', string='Calibration History')
    
    state = fields.Selection([
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('calibration', 'Under Calibration'),
        ('inactive', 'Inactive'),
    ], default='active', tracking=True)
    
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('qms.equipment.sequence')
        return super(QMSEquipment, self).create(vals)
    
    @api.depends('last_calibration', 'calibration_frequency')
    def _compute_next_calibration(self):
        for equipment in self:
            if equipment.last_calibration and equipment.calibration_frequency:
                equipment.next_calibration = fields.Date.from_string(equipment.last_calibration) + \
                                           timedelta(days=equipment.calibration_frequency)

class QMSCalibration(models.Model):
    _name = 'qms.calibration'
    _description = 'Equipment Calibration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'
    
    name = fields.Char('Reference', required=True, readonly=True)
    equipment_id = fields.Many2one('qms.equipment', string='Equipment', required=True)
    date = fields.Date('Calibration Date', required=True, default=fields.Date.today)
    due_date = fields.Date('Next Due Date', compute='_compute_due_date', store=True)
    
    type = fields.Selection([
        ('initial', 'Initial Calibration'),
        ('routine', 'Routine Calibration'),
        ('special', 'Special Calibration'),
        ('post_repair', 'Post Repair Calibration'),
    ], required=True)
    
    performed_by = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External Service Provider'),
    ], required=True)
    
    calibrator_id = fields.Many2one('res.users', string='Calibrator')
    service_provider = fields.Char('Service Provider', 
                                 attrs="{'invisible': [('performed_by', '=', 'internal')]}")
    
    reference_equipment_ids = fields.Many2many('qms.equipment', string='Reference Equipment')
    procedure = fields.Text('Calibration Procedure')
    environmental_conditions = fields.Text('Environmental Conditions')
    
    measurement_points = fields.One2many('qms.calibration.measurement', 'calibration_id', 
                                       string='Measurement Points')
    
    result = fields.Selection([
        ('pass', 'Pass'),
        ('conditional', 'Conditional Pass'),
        ('fail', 'Fail'),
    ], required=True)
    
    adjustment_made = fields.Boolean('Adjustment Made')
    adjustment_details = fields.Text('Adjustment Details')
    
    certificate_number = fields.Char('Certificate Number')
    certificate_file = fields.Binary('Certificate File')
    
    notes = fields.Text('Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('verified', 'Verified'),
    ], default='draft', tracking=True)
    
    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('qms.calibration.sequence')
        return super(QMSCalibration, self).create(vals)
    
    @api.depends('date', 'equipment_id.calibration_frequency')
    def _compute_due_date(self):
        for record in self:
            if record.date and record.equipment_id.calibration_frequency:
                record.due_date = fields.Date.from_string(record.date) + \
                                timedelta(days=record.equipment_id.calibration_frequency)
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
        if self.result in ['pass', 'conditional']:
            self.equipment_id.write({
                'last_calibration': self.date,
                'state': 'active',
            })
    
    def action_verify(self):
        self.write({'state': 'verified'})

class QMSCalibrationMeasurement(models.Model):
    _name = 'qms.calibration.measurement'
    _description = 'Calibration Measurement Points'
    
    calibration_id = fields.Many2one('qms.calibration', string='Calibration')
    sequence = fields.Integer('Sequence', default=10)
    
    nominal_value = fields.Float('Nominal Value')
    measured_value = fields.Float('Measured Value')
    unit = fields.Char('Unit')
    
    tolerance_plus = fields.Float('Tolerance (+)')
    tolerance_minus = fields.Float('Tolerance (-)')
    error = fields.Float('Error', compute='_compute_error', store=True)
    within_tolerance = fields.Boolean('Within Tolerance', compute='_compute_within_tolerance', store=True)
    
    @api.depends('nominal_value', 'measured_value')
    def _compute_error(self):
        for record in self:
            record.error = record.measured_value - record.nominal_value
    
    @api.depends('error', 'tolerance_plus', 'tolerance_minus')
    def _compute_within_tolerance(self):
        for record in self:
            record.within_tolerance = (-record.tolerance_minus <= record.error <= record.tolerance_plus)