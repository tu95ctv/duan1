# -*- coding: utf-8 -*-
from odoo import http

# class DaiTgg(http.Controller):
#     @http.route('/dai_tgg/dai_tgg/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dai_tgg/dai_tgg/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dai_tgg.listing', {
#             'root': '/dai_tgg/dai_tgg',
#             'objects': http.request.env['dai_tgg.dai_tgg'].search([]),
#         })

#     @http.route('/dai_tgg/dai_tgg/objects/<model("dai_tgg.dai_tgg"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dai_tgg.object', {
#             'object': obj
#         })