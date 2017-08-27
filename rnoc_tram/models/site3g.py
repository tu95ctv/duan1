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

class Tram2g(models.Model):
    _name = 'tram2g'
    name = fields.Char()
    nha_tram_id = fields.Many2one('tram',u'Nhà Trạm')
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "Tram 2g title must be unique"),
    ]
    @api.model
    def create(self,vals):
        rs = super(Tram2g, self).create(vals)
        self.env['mixed.stuff'].create({'name': '2G' + ' ' + vals['name'],
                                      'tram_2g_id':self.id})
        return rs 
    
#     @api.multi
#     def unlink(self):
#         rs = super(Tram2g,self).unlink()
#         return rs
class Tram3g(models.Model):
    _name = 'tram3g'
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "Tram 3g title must be unique"),
    ]
    name = fields.Char(required = True)
    des = fields.Char()
    active_site = fields.Boolean()
    nha_tram_id = fields.Many2one('tram',u'Nhà Trạm')
    truc_ca_ids = fields.Many2many('truc.ca')
    #truc_ca_ids = fields.Many2many('truc.ca','truc_ca_tram3g_rel','tram3g_id','truc_ca_id')
    @api.multi
    def write(self,vals):
        #raise ValueError(vals)
        res = super(Tram3g, self).write(vals)
        return res
    @api.model
    def create(self,vals):
        #raise ValueError(vals)
        #
        rs = super(Tram3g, self).create(vals)
        #self.env['mixed.stuff'].create({'name': '3G' + ' ' + self.name,'tram_3g_id':self.id})
        return rs 
class Tram4g(models.Model):
    _name = 'tram4g'
    name = fields.Char()
    nha_tram_id = fields.Many2one('tram',u'Nhà Trạm')
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "Tram 2g title must be unique"),
    ]
class Tram(models.Model):
    _name = 'tram'
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "Tram 2g title must be unique"),
    ]
    name = fields.Char()
    tram_2g_ids = fields.One2many('tram2g','nha_tram_id')
    tram_3g_ids = fields.One2many('tram3g','nha_tram_id')
    tram_4g_ids = fields.One2many('tram4g','nha_tram_id')
class Object(models.Model):
    _name = 'rnoc.tram.object'
    name = fields.Char()
    object_relate = fields.Reference(selection=[('tram2g',u'Tram 2G'),('tram3g',u'Tram 3G'),('tram4g',u'Tram 4G')])
    #truc_ca_id = fields.Many2one('truc.ca')
class TrucCa (models.Model):
    _name = 'truc.ca'
    name = fields.Char()
    raise_time = fields.Datetime()
    tram_3g_ids = fields.Many2many('tram3g')
    
    #tram_3g_ids = fields.Many2many('tram3g','truc_ca_tram3g_rel','truc_ca_id','tram3g_id')
    #object_ids = fields.One2many('rnoc.tram.object','truc_ca_id')
    #tram_id = fields.Many2one('rnoc.tram.object', related='object_ids.name', string='Product')
    @api.model
    def create(self,vals):
        raise ValueError(vals)
class MixedStuff(models.Model):
    _name = 'mixed.stuff'
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "Tram 2g title must be unique"),
    ]
    name  = fields.Char()
    tram_2g_id = fields.Many2one('tram2g', ondelete = 'cascade')
    tram_3g_id = fields.Many2one('tram3g', ondelete = 'cascade')
    tram_4g_id = fields.Many2one('tram4g', ondelete = 'cascade')
    tram_id = fields.Many2one('tram', ondelete = 'cascade')
    