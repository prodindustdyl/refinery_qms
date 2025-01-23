from odoo import models, fields, api

class QMSDocumentType(models.Model):
    _name = 'qms.document.type'
    _description = 'QMS Document Type'
    _order = 'sequence, name'
    
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    sequence = fields.Integer('Sequence', default=10)
    description = fields.Text('Description')
    
    approval_required = fields.Boolean('Requires Approval', default=True)
    review_required = fields.Boolean('Requires Review', default=True)
    revision_control = fields.Boolean('Revision Control', default=True)
    
    reviewer_group_id = fields.Many2one('res.groups', string='Reviewer Group')
    approver_group_id = fields.Many2one('res.groups', string='Approver Group')
    
    template_id = fields.Many2one('ir.ui.view', string='Document Template')
    numbering_sequence_id = fields.Many2one('ir.sequence', string='Numbering Sequence')
    
    retention_period = fields.Integer('Retention Period (months)')
    active = fields.Boolean('Active', default=True)
    
    document_ids = fields.One2many('qms.document', 'document_type_id', string='Documents')