# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Megha K (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


TRANSPORT_MODES = [('land', 'Land'), ('air', 'Air'), ('sea', 'Sea'), ('rail', 'Rail')]


class FreightOrder(models.Model):
    _name = 'freight.order'
    _description = 'Freight Order'

    name = fields.Char('Name', default='New', readonly=True)
    shipper_id = fields.Many2one('res.partner', 'Partner', required=True, help="Customer's Details")
    consignee_id = fields.Many2one('res.partner', 'Shipper Name', help="Details of consignee")
    ship_to_id = fields.Many2one('res.partner', string='Ship To', domain=[('type', '=', 'delivery')])
    type = fields.Selection([('import', 'Import'), ('export', 'Export')],
                            'Import/Export', required=True, help="Type of freight operation")
    transport_type = fields.Selection(TRANSPORT_MODES, "Cargo", help='Type of transportation', required=True)
    land_type = fields.Selection([('ltl', 'LTL'), ('ftl', 'FTL')],
                                 'Land Shipping', help="Types of shipment movement involved in Land")
    sea_type = fields.Selection([('fcl', 'FCL'), ('lcl', 'LCL')],
                                'Sea Shipping', help="Types of shipment movement involved in Sea")
    rail_type = fields.Selection(
        [('dhr', 'Double-headed Rail'),
         ('bhr', 'Bull-headed Rail'),
         ('ffr', 'Flat-footed Rail')],
        'Rail Shipping', help="Types of shipment movement involved in Rail")
    order_date = fields.Date('Shipping Date', default=fields.Date.today(), help="Date of order")
    loading_port_id = fields.Many2one('freight.port', string="Loading Port",
                                      required=True, help="Loading port of the freight order")
    discharging_port_id = fields.Many2one('freight.port', string="Discharging Port",
                                          required=True, help="Discharging port of freight order")
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submitted'),
                              ('confirm', 'Confirmed'),
                              ('invoice', 'Invoiced'), ('done', 'Done'),
                              ('cancel', 'Cancel')], default='draft')
    clearance = fields.Boolean("Clearance")
    clearance_count = fields.Integer(compute='compute_moves_count')
    invoice_count = fields.Integer(compute='compute_moves_count')
    bills_count = fields.Integer(compute='compute_moves_count')
    total_order_price = fields.Float('Total', compute='_compute_total_order_price')
    total_volume = fields.Float('Total Volume', compute='_compute_total_order_price')
    total_weight = fields.Float('Total Weight', compute='_compute_total_order_price')
    order_ids = fields.One2many('freight.order.line', 'order_id')
    route_ids = fields.One2many('freight.order.routes.line', 'route_id')
    total_route_sale = fields.Float('Total Sale', compute="_compute_total_route_cost")
    service_ids = fields.One2many('freight.order.service', 'line_id')
    total_service_sale = fields.Float('Service Total Sale', compute="_compute_total_service_cost")
    agent_id = fields.Many2one('res.partner', 'Agent', required=True, help="Details of agent")
    company_id = fields.Many2one('res.company', string='Company', default=lambda s: s.env.company.id)
    company_currency_id = fields.Many2one(related='company_id.currency_id')
    expected_date = fields.Date('Expected Date')
    track_ids = fields.One2many('freight.track', 'track_id')
    awb_number = fields.Char(string='AWB Number')
    bl_number = fields.Char(string='BL Number')
    custom_entry = fields.Char(string='Custom Entry No')
    inv_number = fields.Char(string='INV Number')
    idf_number = fields.Char(string='IDF Number')
    status = fields.Text('Status Description')

    @api.depends('order_ids.total_price', 'order_ids.volume', 'order_ids.weight')
    def _compute_total_order_price(self):
        """Computing the price of the order"""
        for rec in self:
            rec.total_order_price = sum(rec.order_ids.mapped('total_price'))
            rec.total_volume = sum(rec.order_ids.mapped('volume'))
            rec.total_weight = sum(rec.order_ids.mapped('weight'))

    @api.depends('route_ids.sale')
    def _compute_total_route_cost(self):
        """Computing the total cost of route operation"""
        for rec in self:
            rec.total_route_sale = sum(rec.route_ids.mapped('sale'))

    @api.depends('service_ids.total_sale')
    def _compute_total_service_cost(self):
        """Computing the total cost of services"""
        for rec in self:
            rec.total_service_sale = sum(rec.service_ids.mapped('total_sale'))

    @api.model
    def create(self, vals):
        """Create Sequence"""
        sequence_code = 'freight.order.sequence'
        vals['name'] = self.env['ir.sequence'].next_by_code(sequence_code)
        return super(FreightOrder, self).create(vals)

    def create_custom_clearance(self):
        """Create custom clearance"""
        clearance = self.env['custom.clearance'].create({
            'name': 'CC - ' + self.name,
            'freight_id': self.id,
            'date': self.order_date,
            'loading_port_id': self.loading_port_id.id,
            'discharging_port_id': self.discharging_port_id.id,
            'agent_id': self.agent_id.id,
        })
        result = {
            'name': 'action.name',
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'target': 'current',
            'res_id': clearance.id,
            'res_model': 'custom.clearance',
        }
        self.clearance = True
        return result

    def get_custom_clearance(self):
        """Get custom clearance"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Clearance',
            'view_mode': 'tree,form',
            'res_model': 'custom.clearance',
            'domain': [('freight_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def track_order(self):
        """Track the order"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Received/Delivered',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'freight.order.track',
            'context': {
                'default_freight_id': self.id
            }
        }

    def create_service_bills(self):
        partner_group = {}
        for service in self.service_ids.filtered(
                lambda s: s.partner_id.id != self.company_id.partner_id.
                id and s.partner_id.id not in self.company_id.partner_id.child_ids.ids):
            product_id =service.service_id.product_id
            account_id = product_id.property_account_expense_id or product_id.categ_id.property_account_expense_categ_id
            
            value = (0, 0, {
                'product_id': product_id.id,
                'account_id': account_id.id,
                'name': service.service_id.name,
                'price_unit': service.cost,
                'quantity': service.qty
            })
            if partner_group.get(service.partner_id.id):
                partner_group[service.partner_id.id].append(value)
            else:
                partner_group[service.partner_id.id] = [value]

        for group, group_values in partner_group.items():
            invoice = {
                'move_type': 'in_invoice',
                'partner_id': group,
                'invoice_user_id': self.env.user.id,
                'invoice_origin': self.name,
                'ref': self.name,
                'company_id': self.company_id.id,
                'invoice_line_ids': group_values,
            }
            self.env['account.move'].create(invoice)

    def create_invoice(self):
        """Create invoice"""
        lines = []
        if self.order_ids:
            for order in self.order_ids:
                value = (0, 0, {
                    'name': order.product_id.name,
                    'price_unit': order.price,
                    'quantity': order.volume + order.weight,
                })
                lines.append(value)

        if self.route_ids:
            for route in self.route_ids:
                value = (0, 0, {
                    'name': route.operation_id.name,
                    'price_unit': route.sale,
                })
                lines.append(value)

        if self.service_ids:
            for service in self.service_ids:
                product_id =service.service_id.product_id
                account_id = product_id.property_account_income_id or product_id.categ_id.property_account_income_categ_id
                value = (0, 0, {
                    'product_id': product_id.id,
                    'account_id': account_id.id,
                    'name': service.service_id.name,
                    'price_unit': service.sale,
                    'quantity': service.qty
                })
                lines.append(value)

        invoice = {
            'move_type': 'out_invoice',
            'partner_id': self.shipper_id.id,
            'invoice_user_id': self.env.user.id,
            'invoice_origin': self.name,
            'ref': self.name,
            'transport_type': self.transport_type,
            'awb_number': self.awb_number,
            'bl_number': self.bl_number,
            'consignee_id': self.consignee_id.id,
            'ship_date': self.order_date,
            'ship_to_id': self.ship_to_id.id,
            'custom_entry': self.custom_entry,
            'invoice_line_ids': lines,
        }
        inv = self.env['account.move'].create(invoice)
        result = {
            'name': 'action.name',
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'target': 'current',
            'res_id': inv.id,
            'res_model': 'account.move',
        }
        self.state = 'invoice'
        return result

    def action_cancel(self):
        """Cancel the record"""
        if self.state == 'draft' and self.state == 'submit':
            self.state = 'cancel'
        else:
            raise ValidationError("You can't cancel this order")

    def get_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} Invoices',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('ref', '=', self.name), ('move_type', 'in', ('out_invoice', 'out_refund'))],
            'context': "{'create': False}"
        }

    def get_bills(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} Bills',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('ref', '=', self.name), ('move_type', 'in', ('in_invoice', 'in_refund'))],
            'context': "{'create': False}"
        }

    @api.depends('name')
    def compute_moves_count(self):
        """Compute custom clearance and account move's count"""
        for rec in self:
            if rec.env['custom.clearance'].search([('freight_id', '=', rec.id)]):
                rec.clearance_count = rec.env['custom.clearance'].search_count(
                    [('freight_id', '=', rec.id)])
            else:
                rec.clearance_count = 0

            invoice_domain = [('ref', '=', rec.name), ('move_type', 'in', ('out_invoice', 'out_refund'))]
            rec.invoice_count = self.env['account.move'].search_count(invoice_domain)

            bills_domain = [('ref', '=', rec.name), ('move_type', 'in', ('in_invoice', 'in_refund'))]
            rec.bills_count = self.env['account.move'].search_count(bills_domain)

    def action_submit(self):
        """Submitting order"""
        for rec in self:
            rec.state = 'submit'
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            Urls = urls.url_join(base_url, 'web#id=%(id)s&model=freight.order&view_type=form' % {'id': self.id})

            mail_content = _('Hi %s,<br>'
                             'The Freight Order %s is Submitted'
                             '<div style = "text-align: center; '
                             'margin-top: 16px;"><a href = "%s"'
                             'style = "padding: 5px 10px; font-size: 12px; '
                             'line-height: 18px; color: #FFFFFF; '
                             'border-color:#875A7B;text-decoration: none; '
                             'display: inline-block; margin-bottom: 0px; '
                             'font-weight: 400;text-align: center; '
                             'vertical-align: middle; cursor: pointer; '
                             'white-space: nowrap; background-image: none; '
                             'background-color: #875A7B; '
                             'border: 1px solid #875A7B; border-radius:3px;">'
                             'View %s</a></div>'
                             ) % (rec.agent_id.name, rec.name, Urls, rec.name)
            email_to = self.env['res.partner'].search([
                ('id', 'in', (self.shipper_id.id, self.consignee_id.id,
                              self.agent_id.id))])
            for mail in email_to:
                main_content = {
                    'subject': _('Freight Order %s is Submitted') % self.name,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': mail.email
                }
                mail_id = self.env['mail.mail'].create(main_content)
                mail_id.mail_message_id.body = mail_content
                mail_id.send()

    def action_confirm(self):
        """Confirm order"""
        for rec in self:
            clearance = self.env['custom.clearance'].search([
                ('freight_id', '=', self.id)])
            if clearance:
                if clearance.state == 'confirm':
                    rec.state = 'confirm'
                    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    Urls = urls.url_join(base_url, 'web#id=%(id)s&model=freight.order&view_type=form' % {'id': self.id})
                    mail_content = _('Hi %s,<br> '
                                     'The Freight Order %s is Confirmed '
                                     '<div style = "text-align: center; '
                                     'margin-top: 16px;"><a href = "%s"'
                                     'style = "padding: 5px 10px; '
                                     'font-size: 12px; line-height: 18px; '
                                     'color: #FFFFFF; border-color:#875A7B; '
                                     'text-decoration: none; '
                                     'display: inline-block; '
                                     'margin-bottom: 0px; font-weight: 400;'
                                     'text-align: center; '
                                     'vertical-align: middle; '
                                     'cursor: pointer; white-space: nowrap; '
                                     'background-image: none; '
                                     'background-color: #875A7B; '
                                     'border: 1px solid #875A7B; '
                                     'border-radius:3px;">'
                                     'View %s</a></div>'
                                     ) % (rec.agent_id.name, rec.name,
                                          Urls, rec.name)
                    email_to = self.env['res.partner'].search([
                        ('id', 'in', (self.shipper_id.id,
                                      self.consignee_id.id, self.agent_id.id))])
                    for mail in email_to:
                        main_content = {
                            'subject': _('Freight Order %s is Confirmed') % self.name,
                            'author_id': self.env.user.partner_id.id,
                            'body_html': mail_content,
                            'email_to': mail.email
                        }
                        mail_id = self.env['mail.mail'].create(main_content)
                        mail_id.mail_message_id.body = mail_content
                        mail_id.send()
                elif clearance.state == 'draft':
                    raise ValidationError("the custom clearance ' %s ' is "
                                          "not confirmed" % clearance.name)
            else:
                raise ValidationError("Create a custom clearance for %s" % rec.name)

            for line in rec.order_ids:
                line.container_id.state = 'reserve'
            rec.create_service_bills()

    def action_done(self):
        """Mark order as done"""
        for rec in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            Urls = urls.url_join(base_url, 'web#id=%(id)s&model=freight.order&view_type=form' % {'id': self.id})

            mail_content = _('Hi %s,<br>'
                             'The Freight Order %s is Completed'
                             '<div style = "text-align: center; '
                             'margin-top: 16px;"><a href = "%s"'
                             'style = "padding: 5px 10px; font-size: 12px; '
                             'line-height: 18px; color: #FFFFFF; '
                             'border-color:#875A7B;text-decoration: none; '
                             'display: inline-block; '
                             'margin-bottom: 0px; font-weight: 400;'
                             'text-align: center; vertical-align: middle; '
                             'cursor: pointer; white-space: nowrap; '
                             'background-image: none; '
                             'background-color: #875A7B; '
                             'border: 1px solid #875A7B; border-radius:3px;">'
                             'View %s</a></div>'
                             ) % (rec.agent_id.name, rec.name, Urls, rec.name)
            email_to = self.env['res.partner'].search([
                ('id', 'in', (self.shipper_id.id, self.consignee_id.id,
                              self.agent_id.id))])
            for mail in email_to:
                main_content = {
                    'subject': _('Freight Order %s is completed') % self.name,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': mail.email
                }
                mail_id = self.env['mail.mail'].create(main_content)
                mail_id.mail_message_id.body = mail_content
                mail_id.send()
            self.state = 'done'

            for line in rec.order_ids:
                line.container_id.state = 'available'


class FreightOrderLine(models.Model):
    _name = 'freight.order.line'

    order_id = fields.Many2one('freight.order')
    container_id = fields.Many2one('freight.container', string='Container Size',
                                   domain="[('state', '=', 'available')]")
    total_containers = fields.Integer(string='Quantity')    
    packages = fields.Integer(string='Packages')    
    product_id = fields.Many2one('product.product', string='Goods / Description')
    billing_type = fields.Selection([('weight', 'Weight'),
                                     ('volume', 'Volume')], string="Billing On")
    pricing_id = fields.Many2one('freight.price', string='Pricing')
    price = fields.Float('Unit Price')
    total_price = fields.Float('Total Price')
    volume = fields.Float('Volume')
    weight = fields.Float('Weight')

    @api.constrains('weight')
    def _check_weight(self):
        """Checking the weight of containers"""
        for rec in self:
            if rec.container_id and rec.billing_type:
                if rec.billing_type == 'weight':
                    if rec.container_id.weight < rec.weight:
                        raise ValidationError(
                            'The weight is must be less '
                            'than or equal to %s' % (rec.container_id.weight))

    @api.constrains('volume')
    def _check_volume(self):
        """Checking the volume of containers"""
        for rec in self:
            if rec.container_id and rec.billing_type:
                if rec.billing_type == 'volume':
                    if rec.container_id.volume < rec.volume:
                        raise ValidationError(
                            'The volume is must be less '
                            'than or equal to %s' % (rec.container_id.volume))

    @api.onchange('pricing_id', 'billing_type')
    def onchange_price(self):
        """Calculate the weight and volume of container"""
        for rec in self:
            if rec.billing_type == 'weight':
                rec.volume = 0.00
                rec.price = rec.pricing_id.weight
            elif rec.billing_type == 'volume':
                rec.weight = 0.00
                rec.price = rec.pricing_id.volume

    @api.onchange('pricing_id', 'billing_type', 'volume', 'weight')
    def onchange_total_price(self):
        """Calculate sub total price"""
        for rec in self:
            if rec.billing_type and rec.pricing_id:
                if rec.billing_type == 'weight':
                    rec.total_price = rec.weight * rec.price
                elif rec.billing_type == 'volume':
                    rec.total_price = rec.volume * rec.price


class FreightOrderRouteLine(models.Model):
    _name = 'freight.order.routes.line'

    route_id = fields.Many2one('freight.order')
    operation_id = fields.Many2one('freight.routes', required=True)
    source_loc = fields.Many2one('freight.port', 'Source Location')
    destination_loc = fields.Many2one('freight.port', 'Destination Location')
    transport_type = fields.Selection(TRANSPORT_MODES, "Transport", required=True)
    sale = fields.Float('Sale')

    @api.onchange('operation_id', 'transport_type')
    def _onchange_operation_id(self):
        """calculate the price of route operation"""
        for rec in self:
            if rec.operation_id and rec.transport_type:
                if rec.transport_type == 'land':
                    rec.sale = rec.operation_id.land_sale
                elif rec.transport_type == 'air':
                    rec.sale = rec.operation_id.air_sale
                elif rec.transport_type == 'sea':
                    rec.sale = rec.operation_id.sea_sale
                elif rec.transport_type == 'rail':
                    rec.sale = rec.operation_id.rail_sale


class FreightOrderServiceLine(models.Model):
    _name = 'freight.order.service'
    _description = 'Manage fleet services'

            
    line_id = fields.Many2one('freight.order')
    service_id = fields.Many2one('freight.service', required=True)
    partner_id = fields.Many2one('res.partner', string="Vendor")
    qty = fields.Float('Quantity', default=1.0)
    cost = fields.Float('Cost')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    currency_rate = fields.Float(string='Currency Rate', default=1.0)
    sale = fields.Float('Sale')
    total_sale = fields.Float('Total Sale (Ksh)', compute='_compute_total_sale')

    @api.depends('currency_rate', 'sale')
    def _compute_total_sale(self):
        for rec in self:
            rec.total_sale = rec.sale * rec.currency_rate
    
    @api.onchange('service_id')
    def _onchange_service_id(self):
        for rec in self:
            rec.cost = rec.service_id.product_id.standard_price
            
    @api.onchange('service_id', 'partner_id')
    def _onchange_partner_id(self):
        """Calculate the price of services"""
        for rec in self:
            if rec.service_id:
                if rec.partner_id:
                    if rec.service_id.line_ids:
                        for service in rec.service_id.line_ids:
                            if rec.partner_id == service.partner_id:
                                rec.sale = service.sale
                            else:
                                rec.sale = rec.service_id.sale_price
                    else:
                        rec.sale = rec.service_id.sale_price
                else:
                    rec.sale = rec.service_id.sale_price

    @api.onchange('qty', 'sale')
    def _onchange_qty(self):
        """Calculate the subtotal of route operation"""
        for rec in self:
            rec.total_sale = rec.qty * rec.sale


class Tracking(models.Model):
    _name = 'freight.track'

    source_loc = fields.Many2one('freight.port', 'Source Location')
    destination_loc = fields.Many2one('freight.port', 'Destination Location')
    transport_type = fields.Selection(TRANSPORT_MODES, "Transport")
    track_id = fields.Many2one('freight.order')
    date = fields.Date('Date')
    type = fields.Selection([('received', 'Received'), ('delivered', 'Delivered')], 'Received/Delivered')
