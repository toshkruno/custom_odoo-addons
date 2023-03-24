from odoo import fields, models

TRANSPORT_MODES = [('land', 'Land'), ('air', 'Air'), ('sea', 'Sea'), ('rail', 'Rail')]


class AccountMove(models.Model):
    _inherit = 'account.move'

    custom_entry = fields.Char(string='Custom Entry')
    awb_number = fields.Char(string='AWB Number')
    consignee_id = fields.Many2one(comodel_name='res.partner', string='Shipper Name')
    ship_to_id = fields.Many2one(comodel_name='res.partner', string='Ship To', domain=[('type', '=', 'delivery')])
    transport = fields.Selection(string='Cargo', selection=TRANSPORT_MODES)
    ship_date = fields.Date(string='Shipping Date')
