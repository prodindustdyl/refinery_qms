from odoo import models, fields, api

class QMSDocumentCategory(models.Model):
    _name = 'qms.document.category'
    _description = 'QMS Document Category'
    _parent_store = True
    _order = 'complete_name'
    
    name = fields.Char('Name', required=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True)
    parent_id = fields.Many2one('qms.document.category', string='Parent Category', 
                               ondelete='restrict', index=True)
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many('qms.document.category', 'parent_id', string='Child Categories')
    
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True)
    
    document_ids = fields.One2many('qms.document', 'category_id', string='Documents')
    document_count = fields.Integer('Document Count', compute='_compute_document_count')
    
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name
    
    @api.depends('document_ids')
    def _compute_document_count(self):
        for category in self:
            category.document_count = len(category.document_ids)