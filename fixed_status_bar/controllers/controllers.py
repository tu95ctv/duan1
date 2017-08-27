# -*- coding: utf-8 -*-
from odoo import http

# class FixedStatusBar(http.Controller):
#     @http.route('/fixed_status_bar/fixed_status_bar/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fixed_status_bar/fixed_status_bar/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fixed_status_bar.listing', {
#             'root': '/fixed_status_bar/fixed_status_bar',
#             'objects': http.request.env['fixed_status_bar.fixed_status_bar'].search([]),
#         })

#     @http.route('/fixed_status_bar/fixed_status_bar/objects/<model("fixed_status_bar.fixed_status_bar"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fixed_status_bar.object', {
#             'object': obj
#         })