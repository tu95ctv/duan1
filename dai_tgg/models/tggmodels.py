# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
import re
from odoo.osv import expression
from odoo.tools.misc import xlwt
from copy import deepcopy
import pytz
from odoo.exceptions import ValidationError
import datetime
import json
from tao_instance import import_bd_tuan
from tao_instance import importnhatram

def adict_flat(adict,item_seperate=';',k_v_separate = ':'):
    alist = []
    for k,v in adict.iteritems():
        if isinstance(v,dict):
            v = adict_flat(v,item_seperate=',',k_v_separate = ' ')
        alist.append(k + k_v_separate + v)
    return item_seperate.join(alist)   
ALIGN_BORDER_dict = {'align':{'horiz': 'left','vert':'centre','wrap':'yes'},
                     "borders":{'left':'thin', 'right': 'thin', 'top': 'thin', 'bottom': 'thin'}
                     }

ALIGN_BORDER =adict_flat(ALIGN_BORDER_dict)

ALIGN_BORDER_tb_dict = deepcopy(ALIGN_BORDER_dict)
ALIGN_BORDER_tb_dict['align'].update({'rotation':"90"})
ALIGN_BORDER_tb_dict['align'].update({'horiz':"center"})
ALIGN_BORDER_tb_dict['font'] = {"bold":"on","height" :"320"}
ALIGN_BORDER_tb = adict_flat(ALIGN_BORDER_tb_dict)

title_format_dict = deepcopy(ALIGN_BORDER_dict)
title_format_dict['align']['horiz'] = 'centre'
title_format_txt = adict_flat(title_format_dict)

base_style = xlwt.easyxf(ALIGN_BORDER)
thiet_bi_style = xlwt.easyxf(ALIGN_BORDER_tb )

title_format_style = xlwt.easyxf(title_format_txt)

    
class ImportNhaTram(models.Model):
    _name = 'importnhatram' 
    file = fields.Binary()
    import_2g_or_3g = fields.Selection([('2G','2G'),('3G','3G'),('4G','4G')],string=u'2G or 3G or 4G')
    update_number=fields.Integer()
    create_number=fields.Integer()
    skipupdate_number=fields.Integer()
    def importnhatram(self):
        importnhatram(self)
        return True
    

class BTS (models.Model):
    _name = 'bts'
    _sql_constraints = [
    ('name', 'unique("name")', 'Field name in soi table must be unique.'),
  ]
    name = fields.Char()
    #ten_cho_quan_ly = fields.Char()
    ma_tram = fields.Char()
    #code = fields.Char()
    ngay_bao_duong = fields.Date()

class eNodeB (models.Model):
    _name = 'enodeb'
    name = fields.Char()
    ma_tram = fields.Char()
    ngay_bao_duong = fields.Date()
    
class NodeB (models.Model):
    _name = 'nodeb'
    name = fields.Char()
    ma_tram = fields.Char()
    ngay_bao_duong = fields.Date()
class Tram(models.Model):
    _name = 'tram'
    name = fields.Char()
    address =fields.Char()
    soi_ids = fields.Many2many('dai_tgg.soi','soi_tram_relate','tram_id','soi_id')
    
    ca_sang_bat_dau = fields.Char(default=u'07:00:00')
    ca_chieu_bat_dau = fields.Char(default=u'14:00:00')
    ca_dem_bat_dau = fields.Char(default=u'22:30:00')


class VatTu(models.Model):
    _name = 'vattu'
    name = fields.Char()
    don_vi_tinh = fields.Many2one('product.uom', 'Unit of Measure',)
class VatTuLines(models.Model):
    _name = 'vattulines'
    name = fields.Char()
    vat_tu_id = fields.Many2one('vattu')
    to_trinh_id = fields.Many2one('totrinh')
    so_luong = fields.Integer()
    product_uom = fields.Many2one('product.uom')
class ToTrinh(models.Model): 
    _name='totrinh'
    name = fields.Char()
    location=fields.Char()
    date = fields.Date()
    kinh_trinh_id = fields.Many2one('res.partner')
    member_id = fields.Many2one('res.users')
    noi_dung = fields.Html()
    vat_tu_ids = fields.One2many('vattulines','to_trinh_id')
class HuongTuyen(models.Model):
    _name = 'huongtuyen'
    name = fields.Char()
    nguoi_thuong_di = fields.Many2one('res.users')
class TuanTraCapQuang(models.Model):
    _name = 'tuantracapquang'
    nguoi_tuan_tra = fields.Many2one('res.users')
    huong_tuyen = fields.Many2one('huongtuyen')
    gps = fields.Boolean()
    ngay = fields.Date()
    gio_di_luot_di = fields.Datetime()
    gio_den_luot_di = fields.Datetime()
    gio_di_luot_ve = fields.Datetime()
    gio_den_luot_ve = fields.Datetime()
    noidung = fields.Char()
    tuan_tra_hom_sau = fields.Char()
    giam_sat_hom_sau = fields.Char()
    xu_ly_bao_duong_hom_sau = fields.Char()

    @api.multi
    def download_tuan_tra_trong_ngay(self):
        return {
             'type' : 'ir.actions.act_url',
             #'url': '/web/binary/download_document?model=importbd&field=file&id=%s&filename=product_stock.xls'%(self.id),
             'url': '/web/binary/download_tuantra?model=tuantracapquang&id=%s&sitetype=2G'%(self.id),
             'target': 'self',
        }
    
class LoaiCongVan(models.Model):
    _name = 'loaicongvan'
    name = fields.Char()
class ToTrinhSimple(models.Model):
    _name = 'totrinhsample'
    
    name =  fields.Char()
    so = fields.Integer(string=u'Số')
    ghi_chu = fields.Char(string=u'Ghi chú')
    loai_cong_van = fields.Many2one('loaicongvan',string=u'Loại công văn')
    ngay = fields.Date(string=u'Ngày soạn công văn')
    ngay_di = fields.Date(string=u'Ngày cv đi')
    ngay_ve = fields.Date(string=u'Ngày cv về')
    
class LineImportBD(models.Model):
    _name = 'lineimport'
    name_2g = fields.Char()
    bts_id = fields.Many2one('bts',compute='bts_id_',store=True)
    name_2g_edited = fields.Char()
    name_3g = fields.Char()
    name_3g_edited = fields.Char()
    nodeb_id = fields.Many2one('nodeb',compute='nodeb_id_',store=True)
    date_char = fields.Char()
    date = fields.Date()
    
    
    week_number = fields.Integer()
    week_char = fields.Char()
    importbdtuan_id = fields.Many2one('importbdtuan') 
    ghi_chu = fields.Char()
    is_mapping_2_week = fields.Boolean()
    is_site_2g_find = fields.Boolean(compute='is_site_2g_find_',store=True)
    is_site_3g_find = fields.Boolean(compute='is_site_3g_find_',store=True)
    is_right_tuan = fields.Boolean(compute='is_right_tuan_',store=True)
    @api.depends('week_char','week_number')
    def is_right_tuan_(self):
        for r in self:
            if r.week_char:
                if r.week_number !=int(r.week_char):
                    r.is_right_tuan = False
                else:
                    r.is_right_tuan = True
                    
    @api.depends('bts_id','name_2g')
    def is_site_2g_find_(self):
        for r in self:
            if r.name_2g:
                if  r.bts_id:
                    r.is_site_2g_find = True
                else:
                    r.is_site_2g_find = False
            else:
                if  r.bts_id:
                    r.is_site_2g_find = False
                else:
                    r.is_site_2g_find = True
                
    @api.depends('nodeb_id','name_3g')
    def is_site_3g_find_(self):
        for r in self:
            if r.name_3g:
                if  r.nodeb_id:
                    r.is_site_3g_find = True
                else:
                    r.is_site_3g_find = False
            else:
                if  r.nodeb_id:
                    r.is_site_3g_find = False
                else:
                    r.is_site_3g_find = True           
    
    @api.depends('name_2g_edited')
    def bts_id_(self):
        rs = self.env['bts'].search([('name','=',self.name_2g_edited)])
        self.bts_id = rs
    
    @api.depends('name_3g_edited')
    def nodeb_id_(self):
        for r in self:
            rs = self.env['nodeb'].search([('name','=',r.name_3g_edited)])
            r.nodeb_id = rs
    
        
class ImportBaoDuongTuan(models.Model): 
    _name='importbdtuan'
    file_import = fields.Binary()
    tuan_import = fields.Integer()
    tuan_export = fields.Integer()

    lineimports = fields.One2many('lineimport','importbdtuan_id')
    
    @api.multi
    def import_bd_tuan(self):
        import_bd_tuan(self)
        return True
    
    @api.multi
    def download_for_rnas(self):
        return {
             'type' : 'ir.actions.act_url',
             #'url': '/web/binary/download_document?model=importbd&field=file&id=%s&filename=product_stock.xls'%(self.id),
             'url': '/web/binary/download_document?model=xxx&id=%s&sitetype=2G'%(self.id),
             'target': 'self',
        }
    @api.multi
    def download_for_rnas_3G(self):
        return {
             'type' : 'ir.actions.act_url',
             #'url': '/web/binary/download_document?model=importbd&field=file&id=%s&filename=product_stock.xls'%(self.id),
             'url': '/web/binary/download_document?model=xxx&id=%s&sitetype=3G'%(self.id),
             'target': 'self',
        }
    @api.multi
    def download_for_rnas_3g(self):
        return {
             'type' : 'ir.actions.act_url',
             #'url': '/web/binary/download_document?model=importbd&field=file&id=%s&filename=product_stock.xls'%(self.id),
             'url': '/web/binary/download_document?model=xxx&id=%s&sitetype=3G'%(self.id),
             'target': 'self',
        }
    @api.multi
    def download_for_rnas_3g_t1900(self):
        return {
             'type' : 'ir.actions.act_url',
             #'url': '/web/binary/download_document?model=importbd&field=file&id=%s&filename=product_stock.xls'%(self.id),
             'url': '/web/binary/download_document?model=xxx&id=%s&sitetype=3G&mode_1900=True'%(self.id),
             'target': 'self',
        }
    @api.multi
    def download_for_rnas_2g_t1900(self):
        return {
             'type' : 'ir.actions.act_url',
             #'url': '/web/binary/download_document?model=importbd&field=file&id=%s&filename=product_stock.xls'%(self.id),
             'url': '/web/binary/download_document?model=xxx&id=%s&sitetype=2G&mode_1900=True'%(self.id),
             'target': 'self',
        }
        
    @api.multi
    def download_for_rnas_4g_t1900(self):
        return {
             'type' : 'ir.actions.act_url',
             #'url': '/web/binary/download_document?model=importbd&field=file&id=%s&filename=product_stock.xls'%(self.id),
             'url': '/web/binary/download_document?model=xxx&id=%s&sitetype=4G&mode_1900=True'%(self.id),
             'target': 'self',
        }
        
