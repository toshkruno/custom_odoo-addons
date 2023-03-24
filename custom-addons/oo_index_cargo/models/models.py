# -*- coding: utf-8 -*-

import uuid

from odoo import api, models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    po_number = fields.Char(string='PO Number')
    reference_number = fields.Char(string='Reference Number')

    @api.model
    def create(self, vals):
        if not vals.get('access_token'):
            vals['access_token'] = uuid.uuid4().hex
        return super().create(vals)


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        res.update({
            'po_number': move.po_number,
            'reference_number': move.reference_number,
        })
        return res
