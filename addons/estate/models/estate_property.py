from odoo import api, models, fields
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real estate property"
    _order='id desc'

    # FIELDS
    name = fields.Char(required=True,string="Title")
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=lambda self: (datetime.today() + timedelta(days=90)).strftime('%Y-%m-%d'), string="Available from")
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False, compute='_compute_selling_price')
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')])
    active = fields.Boolean(default=True)
    state = fields.Selection([('new', 'New'), ('offer received', 'Offer Received'), ('offer accepted', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')], default='new', required=True, copy=False)
    total_area = fields.Integer(compute='_compute_total', store=True)
    best_price = fields.Float(compute='_compute_best_price', store=True)

    # RELATIONS
    property_type_id = fields.Many2one("estate.property.type", string="Property type",ondelete="set null")
    buyer_id = fields.Many2one("res.partner", string="Buyer", compute='_compute_buyer', copy=False,ondelete="set null")
    salesperson_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user,ondelete="set null")
    property_tag_ids = fields.Many2many("estate.property.tag", string="Tags",ondelete="cascade")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price >= 0)', 'The expected price must be positive'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'The selling price must be positive')
    ]

    @api.depends('living_area', 'garden_area')
    def _compute_total(self):
        for rec in self:
            rec.total_area = rec.living_area + rec.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for rec in self:
            rec.best_price = rec.offer_ids and max(rec.offer_ids.mapped('price')) or 0

    @api.depends('offer_ids.status')
    def _compute_selling_price(self):
        for rec in self:
            accepted_offer = rec.offer_ids.filtered(lambda o: o.status == 'accepted')
            rec.selling_price = accepted_offer and accepted_offer[0].price or 0

    @api.depends('offer_ids.status')
    def _compute_buyer(self):
        for rec in self:
            accepted_offer = rec.offer_ids.filtered(lambda o: o.status == 'accepted')
            rec.buyer_id = accepted_offer and accepted_offer[0].partner_id or False
    @api.onchange('offers_ids.status')
    def _onchange_state(self):
        for rec in self:
            if rec.offer_ids and rec.state == 'new':
                rec.state = 'offer received'
    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_orientation = "north"
            self.garden_area = 10

    def action_sold(self):
        if self.state != 'canceled':
            self.state = 'sold'
        else:
            raise UserError("You can't sell a canceled property")

    def action_cancel(self):
        if self.state != 'sold':
            self.state = 'canceled'
        else:
            raise UserError("You can't cancel a sold property")

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for rec in self:
            if not float_is_zero(rec.selling_price, precision_rounding=0.01):
                if float_compare(rec.selling_price, 0.9 * rec.expected_price, precision_rounding=0.01) < 0:
                    raise ValidationError("The selling price cannot be lower than 90 percent of the expected price")