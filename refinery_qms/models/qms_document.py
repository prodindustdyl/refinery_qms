from odoo import models, fields, api
from datetime import datetime

class QMSDocument(models.Model):
    _name = 'qms.document'
    _description = 'QMS Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char('Title', required=True, tracking=True)
    code = fields.Char('Document Code', required=True, tracking=True, readonly=True)
    document_type = fields.Selection([
        ('manual', 'Manual'),
        ('procedure', 'Procedure'),
        ('instruction', 'Technical Instruction'),
        ('record', 'Record'),
        ('plan', 'Plan'),
        ('policy', 'Policy'),
    ], required=True, tracking=True)
    
    process_id = fields.Many2one('qms.process', string='Process', required=True)
    department_id = fields.Many2one('hr.department', string='Department')
    version = fields.Integer('Version', default=1, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('obsolete', 'Obsolete'),
    ], default='draft', tracking=True)
    
    content = fields.Html('Content', required=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    owner_id = fields.Many2one('res.users', string='Document Owner', 
                              default=lambda self: self.env.user)
    reviewer_ids = fields.Many2many('res.users', string='Reviewers')
    approver_id = fields.Many2one('res.users', string='Approver')
    
    effective_date = fields.Date('Effective Date')
    review_date = fields.Date('Next Review Date')
    
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self._generate_document_code(vals)
        return super(QMSDocument, self).create(vals)
    
    def _generate_document_code(self, vals):
        company_code = "RF"  # Refinery code
        process = self.env['qms.process'].browse(vals.get('process_id'))
        process_code = process.code or "XX"
        doc_type_map = {
            'manual': 'MN',
            'procedure': 'PR',
            'instruction': 'IT',
            'record': 'RC',
            'plan': 'PL',
            'policy': 'PO',
        }
        doc_type = doc_type_map.get(vals.get('document_type'), 'XX')
        department = self.env['hr.department'].browse(vals.get('department_id'))
        dept_code = department.code or "XX"
        
        sequence = self.env['ir.sequence'].next_by_code('qms.document.sequence')
        
        return f"{company_code}-{process_code}-{doc_type}-{dept_code}-{sequence}"
    
    def action_submit_review(self):
        self.write({'state': 'review'})
    
    def action_approve(self):
        self.write({
            'state': 'approved',
            'version': self.version + 1,
        })
    
    def action_publish(self):
        self.write({
            'state': 'published',
            'effective_date': fields.Date.today(),
        })
    
    def action_obsolete(self):
        self.write({'state': 'obsolete'})