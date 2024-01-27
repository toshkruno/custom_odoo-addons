# -*- coding: utf-8 -*-
# from odoo import http


# class ReportTemplate(http.Controller):
#     @http.route('/report_template/report_template', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/report_template/report_template/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('report_template.listing', {
#             'root': '/report_template/report_template',
#             'objects': http.request.env['report_template.report_template'].search([]),
#         })

#     @http.route('/report_template/report_template/objects/<model("report_template.report_template"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('report_template.object', {
#             'object': obj
#         })
