# See LICENSE file for full copyright and licensing details.
"""This Module Contain information related to freight Configuration."""

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FreightPort(models.Model):
    """Ports Details."""

    _name = "freight.port"
    _description = "Ports Details"

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    country_id = fields.Many2one("res.country", string="Country")
    state_id = fields.Many2one(
        "res.country.state", string="State", domain="[('country_id', '=', country_id)]"
    )
    is_land = fields.Boolean(string="Land", default=True)
    is_ocean = fields.Boolean(string="Ocean", default=True)
    is_air = fields.Boolean(string="Air", default=True)
    active = fields.Boolean(string="Active", default=True)

    @api.constrains("is_land", "is_ocean", "is_air")
    def _check_port(self):
        for port in self:
            if not port.is_land and not port.is_ocean and not port.is_air:
                raise UserError(_("Please Check at least one port !!"))


class FreightVessels(models.Model):
    """Vessels Details."""

    _name = "freight.vessels"
    _description = "Vessels(Boat) Details."

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    country_id = fields.Many2one("res.country", string="Country")
    note = fields.Text(string="Note")
    active = fields.Boolean(string="Active", default=True)
    transport = fields.Selection(
        [("land", "Land"), ("ocean", "Ocean"), ("air", "Air")], default="land"
    )


class FreightAirline(models.Model):
    """Model for Airlines Details."""

    _name = "freight.airline"
    _description = "Airline Details"

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    country_id = fields.Many2one("res.country", string="Country")
    icao = fields.Char(string="ICAO", help="International Civil Aviation Organization")
    active = fields.Boolean(string="Active", default=True)


class FreightContainers(models.Model):
    """Container Details."""

    _name = "freight.container"
    _description = "Container Details"

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    container_number = fields.Char(string="Container Number", copy=False)
    state = fields.Selection(
        [("available", "Available"), ("reserve", "Reserve")], default="available"
    )
    size = fields.Float(string="Size", help="Maximum Size Handling Capacity")
    size_uom_id = fields.Many2one("uom.uom", string="Size UOM")
    volume = fields.Float(string="Volume", help="Maximum Volume(M3) Handling Capacity")
    weight = fields.Float(string="Weight", help="Maximum Weight(KG) Handling Capacity")
    is_container = fields.Boolean(string="Is Container?", default=True)

    @api.constrains("size", "volume", "weight")
    def _check_container_capacity(self):
        for cont in self:
            if cont.size < 0.0 or cont.volume < 0.0 or cont.weight < 0.0:
                raise UserError(_("You can't enter negative value!!"))

    @api.model
    def create(self, vals):
        """Overridden create method to add container number."""
        if vals and not vals.get("container_number", False):
            vals.update(
                {
                    "container_number": self.env["ir.sequence"].next_by_code(
                        "freight.container.sequence"
                    )
                }
            )
        return super(FreightContainers, self).create(vals)

    def write(self, vals):
        """Overridden write Method to add container number."""
        res = super(FreightContainers, self).write(vals)
        for container in self:
            if not container.container_number:
                container.container_number = self.env["ir.sequence"].next_by_code(
                    "freight.container.sequence"
                )
        return res


class OperationPriceList(models.Model):
    """Operation PriceListing."""

    _name = "operation.price.list"
    _description = "Operation Price Listing"

    name = fields.Char("Name")
    volume_price = fields.Float("Volume Price", help="Per m3 Volume Price")
    weight_price = fields.Float("Weight Price", help="Per KG Weight Price")
    service_price = fields.Float("Service Price")

    @api.constrains("volume_price", "weight_price")
    def _check_price(self):
        for price_list in self:
            if price_list.volume_price < 0.0 or price_list.weight_price < 0.0:
                raise UserError(_("You can't enter the negative price !!"))


class Category(models.Model):
    _name = 'freight.category'
    _rec_name = 'name'

    name = fields.Char(string="Name", copy=False)
    is_company = fields.Boolean(string="Company")
    is_logistic = fields.Boolean(string="Logistic")
    is_operation = fields.Boolean(string="Freight")
    is_transport = fields.Boolean(string="Transport TM")
    is_vessel = fields.Boolean(string="Vessel agency")
    is_warehouse = fields.Boolean(string="Warehousing")


class Incoterm(models.Model):
    _name = 'freight.incoterm'
    _rec_name = 'acronym'

    acronym = fields.Char(string="Acronym", required=True)
    name = fields.Char(string="Name", required=True)
    description = fields.Char(string="Description")
    is_source = fields.Boolean(string="Source")
    is_destination = fields.Boolean(string="Destination")


class CustomType(models.Model):
    _name = 'freight.custom.type'

    name = fields.Char(string="Code", required=True)
    description = fields.Text(string="Description")
    operation_type = fields.Selection([('import', 'Importation'), ('export', 'Exportation')], string="Operation type", required=True)
    temporary_admission = fields.Boolean(string="Temporary admission?")
    re_export = fields.Boolean(string="Re-export?")
