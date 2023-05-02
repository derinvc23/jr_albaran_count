# -*- coding: utf-8 -*-
# from odoo import http


# class StanlitReports(http.Controller):
#     @http.route('/stanlit_reports/stanlit_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stanlit_reports/stanlit_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stanlit_reports.listing', {
#             'root': '/stanlit_reports/stanlit_reports',
#             'objects': http.request.env['stanlit_reports.stanlit_reports'].search([]),
#         })

#     @http.route('/stanlit_reports/stanlit_reports/objects/<model("stanlit_reports.stanlit_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stanlit_reports.object', {
#             'object': obj
#         })
