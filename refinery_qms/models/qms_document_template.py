from odoo import models, fields, api

class QMSDocumentTemplate(models.Model):
    _name = 'qms.document.template'
    _description = 'QMS Document Template'
    
    name = fields.Char('Template Name', required=True)
    document_type_id = fields.Many2one('qms.document.type', string='Document Type', 
                                     required=True)
    description = fields.Text('Description')
    
    content = fields.Html('Template Content', required=True)
    header = fields.Html('Header Content')
    footer = fields.Html('Footer Content')
    
    field_ids = fields.One2many('qms.document.template.field', 'template_id', 
                               string='Template Fields')
    active = fields.Boolean('Active', default=True)
    
    def generate_document(self, values=None):
        """Generate a new document from this template"""
        self.ensure_one()
        if not values:
            values = {}
            
        # Create new document
        document_vals = {
            'name': values.get('name', 'New Document'),
            'document_type_id': self.document_type_id.id,
            'template_id': self.id,
        }
        
        # Process template content
        content = self.content
        for field in self.field_ids:
            placeholder = f"[{field.name}]"
            value = values.get(field.name, field.default_value or '')
            content = content.replace(placeholder, str(value))
            
        document_vals['content'] = content
        return self.env['qms.document'].create(document_vals)

class QMSDocumentTemplateField(models.Model):
    _name = 'qms.document.template.field'
    _description = 'QMS Document Template Field'
    _order = 'sequence, id'
    
    template_id = fields.Many2one('qms.document.template', string='Template', 
                                 required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    
    name = fields.Char('Field Name', required=True)
    description = fields.Text('Description')
    field_type = fields.Selection([
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('selection', 'Selection'),
    ], string='Field Type', required=True, default='text')
    
    required = fields.Boolean('Required')
    default_value = fields.Char('Default Value')
    selection_options = fields.Text('Selection Options', 
                                  help='One option per line for selection fields')