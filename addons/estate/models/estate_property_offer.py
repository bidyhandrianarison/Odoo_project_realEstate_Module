from odoo import api,models,fields
from datetime import timedelta
from odoo.exceptions import UserError
class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real estate property offers"
    _order = "price desc"

    price = fields.Float(required=True)
    status = fields.Selection([('accepted','Accepted'),('refused','Refused'),('pending','Pending')],copy=False,default='pending')
    validity = fields.Integer(default=7,string="Validity (days)")
    date_deadline = fields.Date(compute='_compute_deadline',inverse='_inverse_date',string="Deadline",store=True)
    partner_id = fields.Many2one("res.partner",string="Partner",ondelete="set null")
    property_id = fields.Many2one("estate.property",string="Property",ondelete="set null")
    property_type_id = fields.Many2one("estate.property.type",related="property_id.property_type_id",string="Property Type",store=True,ondelete="set null")

    _sql_constraints=[
        ('check_price','CHECK(price >= 0)','The price must be positive')
    ]
    @api.depends('validity')
    def _compute_deadline(self):
        for rec in self:
            if not rec.create_date:
                rec.date_deadline = fields.Date.today() + timedelta(days=rec.validity)
            else:
                rec.date_deadline = rec.create_date.date() + timedelta(days=rec.validity)
    def _inverse_date(self):
        for rec in self:
            if not rec.create_date:
                rec.validity = (rec.date_deadline - fields.Date.today()).days
            else:
                rec.validity = (rec.date_deadline - rec.create_date.date()).days
    
    def action_accept(self):
        self.status = 'accepted'
        self.property_id.state = 'offer accepted'
    
    def action_cancel(self):
        self.status = 'refused'

    @api.model
    def create(self,vals):
        property_id = self.env['estate.property'].browse(vals['property_id'])

        if vals['price'] < property_id.best_price:
            raise UserError(f"The offer price must be greater than ${property_id.best_price}")
        
        vals['state']="Offer received"
        return super().create(vals)
    @api.ondelete(at_uninstall=False)
    def _unlink_if_state_valid(self):
        for rec in self:
            if rec.state not in ['new','canceled']:
                raise UserError("You cannot delete this offer")
        