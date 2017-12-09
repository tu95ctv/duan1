# -*- coding: utf-8 -*-
from odoo import http

# class Kiemke(http.Controller):
#     @http.route('/kiemke/kiemke/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kiemke/kiemke/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kiemke.listing', {
#             'root': '/kiemke/kiemke',
#             'objects': http.request.env['kiemke.kiemke'].search([]),
#         })

#     @http.route('/kiemke/kiemke/objects/<model("kiemke.kiemke"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kiemke.object', {
#             'object': obj
#         })