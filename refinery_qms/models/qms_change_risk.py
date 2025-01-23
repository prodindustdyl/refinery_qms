from odoo import models, fields, api

class QMSChangeRisk(models.Model):
    _name = 'qms.change.risk'
    _description = 'Change Risk Assessment'
    
    change_id = fields.Many2one('qms.change', string='Change Request', required=True)
    name = fields.Char('Risk Description', required=True)
    
    likelihood = fields.Selection([
        ('1', 'Rare'),
        ('2', 'Unlikely'),
        ('3', 'Possible'),
        ('4', 'Likely'),
        ('5', 'Almost Certain'),
    ], required=True)
    
    impact = fields.Selection([
        ('1', 'Negligible'),
        ('2', 'Minor'),
        ('3', 'Moderate'),
        ('4', 'Major'),
        ('5', 'Severe'),
    ], required=True)
    
    risk_level = fields.Integer('Risk Level', compute='_compute_risk_level', store=True)
    
    mitigation_plan = fields.Text('Mitigation Plan')
    responsible_id = fields.Many2one('res.users', string='Responsible')
    
    @api.depends('likelihood', 'impact')
    def _compute_risk_level(self):
        for risk in self:
            if risk.likelihood and risk.impact:
                risk.risk_level = int(risk.likelihood) * int(risk.impact)
            else:
                risk.risk_level = 0