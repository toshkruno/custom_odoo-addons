# -*- coding: utf-8 -*-
# from odoo import http


# class TenderTracker(http.Controller):
#     @http.route('/tender_tracker/tender_tracker', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tender_tracker/tender_tracker/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tender_tracker.listing', {
#             'root': '/tender_tracker/tender_tracker',
#             'objects': http.request.env['tender_tracker.tender_tracker'].search([]),
#         })

#     @http.route('/tender_tracker/tender_tracker/objects/<model("tender_tracker.tender_tracker"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tender_tracker.object', {
#             'object': obj
#         })
