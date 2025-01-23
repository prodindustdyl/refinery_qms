from odoo import models, fields, api
from datetime import datetime, timedelta

class QMSDocumentRevision(models.Model):
    _name = 'qms.document.revision'
    _description = 'QMS Document Revision'
    _order = 'revision_number desc'
    
    document_id = fields.Many2one('qms.document', string='Document', required=True, 
                                 ondelete='cascade')
    revision_number = fields.Integer('Revision Number', required=True)
    revision_date = fields.Date('Revision Date', required=True, default=fields.Date.today)
    
    author_id = fields.Many2one('res.users', string='Author', required=True, 
                               default=lambda self: self.env.user)
    reviewer_ids = fields.Many2many('res.users', 'qms_doc_revision_reviewer_rel', 
                                  string='Reviewers')
    approver_id = fields.Many2one('res.users', string='Approver')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('superseded', 'Superseded')
    ], string='Status', default='draft', required=True, tracking=True)
    
    content = fields.Html('Content', required=True)
    change_description = fields.Text('Change Description', required=True)
    review_comments = fields.Text('Review Comments')
    approval_comments = fields.Text('Approval Comments')
    
    review_deadline = fields.Date('Review Deadline')
    reviewed_date = fields.Date('Reviewed Date')
    approved_date = fields.Date('Approved Date')
    
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    @api.model
    def create(self, vals):
        if vals.get('document_id') and not vals.get('revision_number'):
            document = self.env['qms.document'].browse(vals['document_id'])
            last_revision = document.revision_ids.sorted('revision_number', reverse=True)[:1]
            vals['revision_number'] = (last_revision.revision_number + 1) if last_revision else 1
        return super(QMSDocumentRevision, self).create(vals)
    
    def action_submit_review(self):
        self.ensure_one()
        self.write({
            'state': 'review',
            'review_deadline': fields.Date.today() + timedelta(days=7)
        })
    
    def action_approve(self):
        self.ensure_one()
        self.write({
            'state': 'approved',
            'approved_date': fields.Date.today()
        })
        # Mark previous revision as superseded
        previous_revisions = self.document_id.revision_ids.filtered(
            lambda r: r.id != self.id and r.state == 'approved'
        )
        previous_revisions.write({'state': 'superseded'})
    
    def action_reject(self):
        self.ensure_one()
        self.write({'state': 'draft'})