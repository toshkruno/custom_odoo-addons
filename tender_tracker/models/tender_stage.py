import PyPDF2
import re
import io
from odoo import api, Command, fields, models, tools, SUPERUSER_ID, _, _lt



STATUS_COLOR = {
    'on_track': 20,  # green / success
    'at_risk': 2,  # orange
    'off_track': 23,  # red / danger
    'on_hold': 4,  # light blue
    False: 0,  # default grey -- for studio
}
class TenderStage(models.Model):
    _name = 'tender.stage'
    _description = 'Tender Stage'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Stage Name', required=True, tracking=True)
    sequence = fields.Integer(string='Sequence', default=10, help="Gives the sequence order when displaying a list of tenders.")
    description = fields.Text(translate=True, tracking=True)
    color = fields.Integer(compute='_compute_color', default=0)

    status = fields.Selection(selection=[
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('off_track', 'Off Track'),
        ('on_hold', 'On Hold')
    ], required=True, tracking=True)

    legend_new = fields.Char(
        'Red Kanban Label', default=lambda s: _('New'), translate=True, required=True,
        help='Override the default value displayed for the new state for kanban selection when the tender is in that stage.')
    legend_normal = fields.Char(
        'Green Kanban Label', default=lambda s: _('Normal'), translate=True, required=True,
        help='Override the default value displayed for the compliance state for kanban selection when the tender is in that stage.')
    legend_done = fields.Char(
        'Green Kanban Label', default=lambda s: _('New'), translate=True, required=True,
        help='Override the default value displayed for the submitted state for kanban selection when the tender is in that stage.')
    legend_events = fields.Char(
        'Red Kanban Label', default=lambda s: _('Events'), translate=True, required=True,
        help='Override the default value displayed for the events state for kanban selection when the tender is in that stage.')

    @api.depends('status')
    def _compute_color(self):
        for update in self:
            update.color = STATUS_COLOR[update.status]