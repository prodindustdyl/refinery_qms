from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class QMSUser(models.Model):
    _inherit = 'res.users'
    
    employee_number = fields.Char('Employee Number', unique=True)
    position = fields.Many2one('hr.job', string='Position')
    department_id = fields.Many2one('hr.department', string='Department')
    
    # QMS specific fields
    qms_role = fields.Selection([
        ('user', 'QMS User'),
        ('auditor', 'QMS Auditor'),
        ('manager', 'QMS Manager'),
        ('admin', 'QMS Administrator')
    ], string='QMS Role', default='user', required=True)
    
    process_ids = fields.Many2many('qms.process', string='Assigned Processes')
    is_process_owner = fields.Boolean('Is Process Owner')
    
    certification_ids = fields.One2many('qms.user.certification', 'user_id', 
                                      string='QMS Certifications')
    training_ids = fields.One2many('qms.training.participant', 'employee_id', 
                                  string='QMS Training Records')
    
    last_password_change = fields.Datetime('Last Password Change')
    password_expiry_date = fields.Datetime('Password Expiry Date', 
                                         compute='_compute_password_expiry')
    
    @api.constrains('employee_number')
    def _check_employee_number(self):
        for record in self:
            if record.employee_number:
                if not re.match("^[A-Z]{2}[0-9]{6}$", record.employee_number):
                    raise ValidationError("Employee Number must be in format: XX000000")
    
    @api.depends('last_password_change')
    def _compute_password_expiry(self):
        password_validity_days = self.env['ir.config_parameter'].sudo().get_param(
            'qms.password_validity_days', default='90')
        validity_days = int(password_validity_days)
        
        for user in self:
            if user.last_password_change:
                user.password_expiry_date = user.last_password_change + \
                                          timedelta(days=validity_days)
            else:
                user.password_expiry_date = False

class QMSUserCertification(models.Model):
    _name = 'qms.user.certification'
    _description = 'QMS User Certification'
    
    user_id = fields.Many2one('res.users', string='User', required=True)
    name = fields.Char('Certification Name', required=True)
    certification_number = fields.Char('Certification Number')
    issuing_body = fields.Char('Issuing Body')
    issue_date = fields.Date('Issue Date')
    expiry_date = fields.Date('Expiry Date')
    status = fields.Selection([
        ('valid', 'Valid'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked')
    ], compute='_compute_status', store=True)
    
    @api.depends('expiry_date')
    def _compute_status(self):
        today = fields.Date.today()
        for cert in self:
            if not cert.expiry_date:
                cert.status = 'valid'
            elif cert.expiry_date < today:
                cert.status = 'expired'
            else:
                cert.status = 'valid'