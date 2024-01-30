# -*- coding: utf-8 -*-
# from odoo import http


# class ReportTemplate(http.Controller):
#     @http.route('/tritel_report_template/tritel_report_template', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tritel_report_template/tritel_report_template/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tritel_report_template.listing', {
#             'root': '/tritel_report_template/tritel_report_template',
#             'objects': http.request.env['tritel_report_template.tritel_report_template'].search([]),
#         })

#     @http.route('/tritel_report_template/tritel_report_template/objects/<model("tritel_report_template.tritel_report_template"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tritel_report_template.object', {
#             'object': obj
#         })
