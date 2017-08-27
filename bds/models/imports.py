# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions
from fetch import import_quan_data
class ImportQuan(models.TransientModel):
    _name = "bds.import_quan"
    so_quan = fields.Integer()
    #data = fields.Binary('File')
    @api.multi
    def import_quan(self):
        so_quan=import_quan_data (self)
        self.so_quan = so_quan
