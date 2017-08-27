# -*- coding: utf-8 -*-
from odoo import http

# class Testtheme(http.Controller):
#     @http.route('/testtheme/testtheme/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/testtheme/testtheme/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('testtheme.listing', {
#             'root': '/testtheme/testtheme',
#             'objects': http.request.env['testtheme.testtheme'].search([]),
#         })

#     @http.route('/testtheme/testtheme/objects/<model("testtheme.testtheme"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('testtheme.object', {
#             'object': obj
#         })