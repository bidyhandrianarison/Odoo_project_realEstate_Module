from odoo import models,fields

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real estate property tags"
    _order='name'

    name = fields.Char(required=True)
    color = fields.Integer(string="Color")
    _sql_constraints = [
        ('unique_tag_name',
        'UNIQUE(name)',
        'Tag name must be unique')

   ]