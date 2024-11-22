from odoo import api, models, fields

class EstatePropertyType(models.Model):
    _name =  "estate.property.type"
    _description = "Estate Property Type"
    _order = "name"

    name = fields.Char(required=True)
    property_ids = fields.One2many("estate.property", "property_type_id", string="Properties")
    sequence = fields.Integer()
    offer_ids = fields.One2many("estate.property.offer","property_type_id",string="Offres")
    offer_count = fields.Integer(compute="_compute_offer_count", string="Offers")
    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids)
    def action_sold(self):
        for rec in self:
            rec.property_ids.write({'state': 'sold'})
    def action_cancel(self):
        for rec in self:
            rec.property_ids.write({'state': 'canceled'})