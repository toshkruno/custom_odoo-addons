# -*- coding: utf-8 -*-

import uuid

from odoo import api, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        if not vals.get('access_token'):
            vals['access_token'] = uuid.uuid4().hex
        return super().create(vals)
