from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    bill_landing = fields.Char(string='Bill of Landing')
    custom_entry = fields.Char(string='Custom Entry')