# -*- coding: utf-8 -*-
from odoo import http

# class RnocTram(http.Controller):
#     @http.route('/rnoc_tram/rnoc_tram/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rnoc_tram/rnoc_tram/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rnoc_tram.listing', {
#             'root': '/rnoc_tram/rnoc_tram',
#             'objects': http.request.env['rnoc_tram.rnoc_tram'].search([]),
#         })

#     @http.route('/rnoc_tram/rnoc_tram/objects/<model("rnoc_tram.rnoc_tram"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rnoc_tram.object', {
#             'object': obj
#         })