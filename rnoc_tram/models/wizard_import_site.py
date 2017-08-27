# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
import xlrd
import base64
from odoo.exceptions import UserError
class BaseLanguageImport(models.TransientModel):
    _name = "rnoc.tram.import.site"
    _description = "Site Import"
    data = fields.Binary('File', required=True)
    #filename = fields.Char('File Name', required=True)
    is_existing_file = fields.Boolean('is_existing_file in server',
                               help="Neu import tu file co trong server tick vao day")
    @api.multi
    def import_site(self):
#         try:
            data = base64.decodestring(self.data)
            #excel = xlrd.open_workbook(file_contents = data)
            excel = xlrd.open_workbook('/home/d4/duan/custom_addon/rnoc_import/document/Ericsson_Database_Ver_161 - fortest.xlsx')
            sh = excel.sheet_by_index(0)
            #for row in range(1,sh.nrows):
            print 'sh.ncols'*200,sh.ncols
            cols = []
            for col in range(0,sh.ncols):
                col_val = str(sh.cell_value(0, col)) 
                
                cols.append(col_val)
            raise ValueError('cols',cols)
            #sheet_by_name
#         except Exception, e:
#             raise UserError(_('Error %s') % (e))
#     
class Tram3g(models.Model):
    _name = 'site3g'
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "Tram 3g title must be unique"),
    ]
    
    name = fields.Char(required = True)
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100