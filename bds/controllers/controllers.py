# -*- coding: utf-8 -*-
from odoo import http

# class Bds(http.Controller):
#     @http.route('/bds/bds/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bds/bds/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bds.listing', {
#             'root': '/bds/bds',
#             'objects': http.request.env['bds.bds'].search([]),
#         })

#     @http.route('/bds/bds/objects/<model("bds.bds"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bds.object', {
#             'object': obj
#         })