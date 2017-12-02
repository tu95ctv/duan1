# -*- coding: utf-8 -*-

from odoo import models, fields, api,sql_db
from fetch import fetch
from fetch import get_quan_list_in_big_page
from fetch import update_phuong_or_quan_for_url_id,import_contact


import logging
import threading
import time
from threading import current_thread
from fetch import get_or_create_object
import base64
import urllib2
import re
from fetch import create_or_get_quan_for_chotot
import datetime
# from fetch import page_handle_for_thread

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

def worker():
    print 'current_thread',current_thread().name
    logging.debug('Starting')
    time.sleep(1)
    logging.debug('Exiting')
    
    
class QuanHuyen(models.Model):
    _name = 'bds.quan'
    name = fields.Char()
    name_unidecode = fields.Char()
    name_without_quan = fields.Char()
class Phuong(models.Model):
    _name = 'bds.phuong'
    name = fields.Char(compute='name_',store=True)
    name_phuong = fields.Char()
    quan_id = fields.Many2one('bds.quan')
    name_unidecode = fields.Char()
    @api.depends('name_phuong','quan_id')
    def name_(self):
        self.name = ( self.name_phuong if self.name_phuong else '' )+ ('-' + self.quan_id.name) if self.quan_id.name else ''
    @api.multi
    def name_get(self):
        #return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]
        res = []
        for r in self:
            new_name = u'phường ' + r.name
            res.append((r.id,new_name))
        return res
class bds(models.Model):
    _name = 'bds.bds'
    name = fields.Char(compute = 'name_',store = True)
    present_image_link = fields.Char()
#     present_image_link_show = fields.Binary(compute="present_image_link_show_",store=True,attachment=True)
    present_image_link_show = fields.Binary()   
    title = fields.Char()
    gia = fields.Float()
    area = fields.Float(digits=(32,1))
    address=fields.Char()
    parameters = fields.Text()
    quan_id = fields.Many2one('bds.quan')
    phuong_id = fields.Many2one('bds.phuong')
    link = fields.Char()
    cho_tot_link_fake = fields.Char(compute='cho_tot_link_fake_')
    ngay_dang = fields.Datetime()
    quan_tam = fields.Datetime()
    gia_chat = fields.Datetime()
    goi_dien_cho_co = fields.Datetime()
    hen_di_xem_time = fields.Datetime()
    da_xem_time = fields.Datetime()
    ghi_chu = fields.Text()
    html = fields.Html()
    poster_id = fields.Many2one('res.users')
    url_cate = fields.Char()
    fetch_ids = fields.Many2many('bds.fetch','fetch_bds_relate','bds_id','fetch_id')
    #count_post_of_poster = fields.Integer(compute='count_post_of_poster_ct_',store=True,string=u'count_post_of_poster chotot')
    count_post_of_poster = fields.Integer(related= 'poster_id.count_post_of_poster_chotot',store=True,string=u'count_post_of_poster chotot')
    count_post_of_poster_bds = fields.Integer(related= 'poster_id.count_post_of_poster_bds',store=True)
    count_post_all_site = fields.Integer(related= 'poster_id.count_post_all_site',store=True)
    post_ids_of_user  = fields.One2many('bds.bds','poster_id',related='poster_id.post_ids')
    
    #count_post_of_poster_bds = fields.Integer(compute='count_post_of_poster_',store=True)
    user_name = fields.Char(related='poster_id.username_in_site_ids.username_in_site' )
    name_tong_hop = fields.Char(related = 'poster_id.name_tong_hop')
    data = fields.Text()
    user_name_poster = fields.Char()
    phone_poster = fields.Char()
    siteleech_id = fields.Many2one('bds.siteleech')
    
    @api.multi
    def cho_tot_link_fake_(self):
        for r in self:
            if 'chotot' in r.link:
                rs = re.search('/(\d*)$',r.link)
                id_link = rs.group(1)
                r.cho_tot_link_fake = 'https://nha.chotot.com/quan-10/mua-ban-nha-dat/' + 'xxx-' + id_link+ '.htm'
    
    
#     @api.depends('write_date')
#     def count_post_of_poster_(self):
#         for r in self:
#             count_post_of_poster = self.env['bds.bds'].search([('poster_id','=',r.poster_id.id),('link','like','chotot')])
#             count_post_of_poster_bds = self.env['bds.bds'].search([('poster_id','=',r.poster_id.id),('link','like','batdongsan')])
#             r.count_post_of_poster = len(count_post_of_poster)
#             r.count_post_of_poster_bds = len(count_post_of_poster_bds)

    #fetch_ids = fields.Many2many('bds.fetch')
    @api.depends('present_image_link')
    def present_image_link_show_(self):
        for r in self:
            if r.present_image_link:
                photo = base64.encodestring(urllib2.urlopen(r.present_image_link).read())
                r.present_image_link_show = photo 

    @api.depends('title')
    def name_(self):
        self.name = self.title
class LinkNhaMinhLines(models.Model):
    _name = 'bds.linknhaminh'
    name = fields.Char()
    nha_minh_id = fields.Many2one('bds.nhaminh')
class NhaMinh(models.Model):
    _name = 'bds.nhaminh'
    name = fields.Char()
    link_nha_minh_ids = fields.One2many('bds.linknhaminh','nha_minh_id')
class Khach(models.Model):
    _name = 'bds.khach'
    name = fields.Char()
    mo_gioi_dau_tien_gioi_thieu_id = fields.Many2one('res.users')
    ghi_chu=fields.Text()
class KhachTungNha(models.Model):
    _name = 'bds.khachtungnhalines'
    khach_id = fields.Many2one('bds.khach'
                               )
class NhaGuiChoMoGioiLine(models.Model):
    _name = 'bds.nhaguimogioi_lines'
    nha_minh_id = fields.Many2one('bds.nhaminh')
    thoi_gian_goi_so_tren_zalo = fields.Datetime()
    thoi_gian_goi_so_tren_viber = fields.Datetime()
    thoi_gian_goi_so_giay = fields.Datetime()
    mo_gioi_id = fields.Many2one('res.users')
    khach_thich_so_luong = fields.Integer()
    khac_che = fields.Integer()
    khach_dang_suy_nghi = fields.Integer()
    khach_dang_tra_gia = fields.Integer()
    
class SiteDuocLeech(models.Model):
    _name = 'bds.siteleech'
    name = fields.Char()
class PosterNameLines(models.Model):
    _name = 'bds.posternamelines'
    username_in_site = fields.Char()
    site_id = fields.Many2one('bds.siteleech')
    poster_id = fields.Many2one('res.users')
class QuanOfPoster(models.Model):
    _name = 'bds.quanofposter'
    name = fields.Char(compute='name_',store=True)
    quan_id = fields.Many2one('bds.quan')
    siteleech_id = fields.Many2one('bds.siteleech')
    quantity = fields.Integer()
    min_price = fields.Float(digits=(32,1))
    avg_price = fields.Float(digits=(32,1))
    max_price = fields.Float(digits=(32,1))
    poster_id = fields.Many2one('res.users')
    @api.depends('quan_id','quantity') 
    def name_(self):
        for r in self:
            r.name = r.quan_id.name + ':' + str(r.quantity)
            

    
class SMS(models.Model):
    _name= 'bds.sms'
    name=  fields.Char()
    noi_dung = fields.Text()
    getphoneposter_ids = fields.One2many('bds.getphoneposter','sms_id')
#     poster_ids = fields.Many2many('res.users','sms_poster_relate','sms_id','poster_id',compute='poster_ids_',store=True)
    poster_ids = fields.Many2many('res.users','sms_poster_relate','sms_id','poster_id',related="getphoneposter_ids.poster_ids",store=True)#compute='poster_ids_',store=True#,related="getphoneposter_ids.poster_ids",store=True
    test_depend_through = fields.Char(compute='last_name_of_that_model_',store=True)#
    
    @api.depends('getphoneposter_ids','getphoneposter_ids.poster_ids')
    def last_name_of_that_model_(self):
        for r in self:
            pass
            #r.test_depend_through = ','.join(map(str,r.getphoneposter_ids.mapped('name')))
    
    @api.depends('getphoneposter_ids','getphoneposter_ids.poster_ids')
    def poster_ids_(self):
        for r in self:
            getphoneposter_ids = r.getphoneposter_ids.mapped('poster_ids.id')
            print 'getphoneposter_ids*33',getphoneposter_ids
            #r.write({'poster_ids':[(6,0,getphoneposter_ids)]})
            r.poster_ids = getphoneposter_ids
class GetPhonePoster(models.Model):
    _name = 'bds.getphoneposter'
    
    is_report_for_poster = fields.Boolean()
    filter_sms_or_filter_sql = fields.Selection([('sms_ids','sms_ids'),('by_sql','by_sql')],default='sms_ids')
    name = fields.Char()
    sms_id = fields.Many2one('bds.sms')
    nha_mang = fields.Selection([('vina','vina'),('mobi','mobi'),('viettel','viettel'),('khac','khac')],default='vina')
    post_count_min = fields.Integer(default=10)
    len_poster = fields.Integer()
    exclude_poster_ids = fields.Many2many('res.users')#,inverse="exclude_poster_inverse_")
    len_posters_of_sms = fields.Integer()
    test1 = fields.Char()
    kq = fields.Char(compute="kq_")
    danh_sach_doi_tac = fields.Html()
#     min_loc_less = fields.Float(digits=(32,1))
    avg_loc_less = fields.Float(digits=(32,1))
    phuong_loc_ids = fields.Many2many('bds.phuong')

    @api.onchange('poster_ids')
    def danh_sach_doi_tac_(self):
        for r in self:
            x = r.poster_ids.mapped('name')
            r.danh_sach_doi_tac = '\r\n'.join(x)
    @api.depends('test1')
    def kq_(self):
        for r in self:
            kq = []
            if r.test1:
                int_list = map(int,r.test1.split(','))
                rs = self.search([('exclude_poster_ids','=',int_list[0])])
                print "self.search([('exclude_poster_ids','=',int_list[0])])",rs
                kq.append(True if rs else False)
                rs = self.search([('exclude_poster_ids','in',int_list)])
                kq.append(True if rs else False)
                r.kq = kq
                print "self.search([('exclude_poster_ids','=',int_list[0])])",rs

#     
#     @api.onchange()
#     def  oc_for_exclude_poster(self):
        
#     @api.multi
#     def write(self,vals):
#         self.poster_ids.write({'sms_ids':[(4,self.sms_id.id)]})
#         res = super(GetPhonePoster, self).write(vals)
#         return res
#      
#     @api.model
#     def create(self,vals):
#         self.poster_ids.write({'sms_ids':[(4,self.sms_id.id)]})
#         res = super(GetPhonePoster, self).create(vals)
#         return res
    
    def default_quan(self):
        quan_10 = self.env['bds.quan'].search([('name','=',u'Quận 10')])
        return quan_10.id
    quan_id = fields.Many2one('bds.quan',default=default_quan)
    phone_list = fields.Text(compute='phone_list_',store=True)
    poster_ids = fields.Many2many('res.users','getphone_poster_relate','getphone_id','poster_id')#,compute='poster_ids_',store=True)
    
#     @api.multi
#     def exclude_poster_inverse_(self):
#         for r in self:
#             r.poster_ids = r.poster_ids.filtered(lambda l:l.id not in r.exclude_poster_ids.ids ).mapped('id')
    @api.depends('poster_ids')
    def phone_list_(self):
        for r in self:
            phone_lists = filter(lambda l: not isinstance(l,bool),r.poster_ids.mapped('phone'))
            r.phone_list = ','.join(phone_lists)
    @api.depends('quan_id','post_count_min','nha_mang','sms_id')
    def poster_ids1_(self):
        for r in self:
            if not r.sms_id:
                pass
            else:
                verbose_quan = r.quan_id.name_unidecode.replace('-','_')
                verbose_quan = 'count_' + verbose_quan
                product_category_query =\
                 '''select distinct u.id,c.sms_id from res_users as u
    left join getphone_poster_relate as r
    on u.id  = r.poster_id
    left  join bds_getphoneposter as c
    on  r.getphone_id= c.id
    where  u.%(verbose_quan)s > %(post_count_min)s
    and u.nha_mang like '%(nha_mang)s'
    and (c.sms_id is null or c.sms_id <>%(sms_id)s)
    '''%{'verbose_quan':verbose_quan,
         "nha_mang":  r.nha_mang,
         'post_count_min':r.post_count_min,
         'sms_id':r.sms_id.id
         }
                print product_category_query
                self.env.cr.execute(product_category_query)
                product_category = self.env.cr.fetchall()
                print product_category  
                product_category = map(lambda x:x[0], product_category)
                r.poster_ids = product_category
                r.len_poster = len(product_category)
                
                #raise ValueError(product_category)         
    @api.onchange('quan_id','post_count_min','nha_mang','sms_id','exclude_poster_ids','poster_ids.exclude_sms_ids','phuong_loc_ids','is_report_for_poster')
    def poster_ids_(self):
        def filter_for_poster(l):
            if l.id in r.exclude_poster_ids.ids:
                return False
            if r.sms_id.id in l.exclude_sms_ids.ids:
                return False
            if r.is_report_for_poster or r.filter_sms_or_filter_sql =='sms_ids':
                return True
            elif r.filter_sms_or_filter_sql =='by_sql':
                product_category_query =\
                         '''select distinct u.id,c.sms_id from res_users as u
            inner join getphone_poster_relate as r
            on u.id  = r.poster_id
            inner join bds_getphoneposter as c
            on  r.getphone_id= c.id
            where  u.id = %(r_id)s
            and c.sms_id =  %(sms_id)s
            '''%{'r_id':l.id,
                 'sms_id':r.sms_id.id
                 }
                self.env.cr.execute(product_category_query)
                product_category = self.env.cr.fetchall()
                if product_category:
                    return False
                else:
                    return True  
        for r in self:
            if not r.sms_id:
                pass
            else:
            #quan_10 = self.env['bds.quan'].search([('name','=',u'Quận 10')])
                domain_tong = []
                if r.nha_mang:
                    nha_mang_domain = ('nha_mang','=',r.nha_mang)
                    domain_tong.append(nha_mang_domain)
               
#                 if r.quan_id and r.post_count_min:
#                     verbose_quan = r.quan_id.name_unidecode.replace('-','_')
#                     count_quan_domain = ( 'count_' + verbose_quan,'>=',r.post_count_min)
#                     domain_tong.append(count_quan_domain)
#                     if r.avg_loc_less:
#                         count_quan_domain = ('avg_' + verbose_quan,'<',r.avg_loc_less)
#                         domain_tong.append(count_quan_domain)
                
                
                if r.quan_id and r.post_count_min:
                    count_quan_domain = ( 'quanofposter_ids.quan_id','=',r.quan_id.id)
                    domain_tong.append(count_quan_domain)
                    domain_tong.append(('quanofposter_ids.quantity','>=',r.post_count_min))
                        
#                     if r.avg_loc_less:
#                         count_quan_domain = ('avg_' + verbose_quan,'<',r.avg_loc_less)
#                         domain_tong.append(count_quan_domain)


                if r.phuong_loc_ids:
                    count_quan_domain = ('phuong_id' ,'in',r.phuong_loc_ids.mapped('id'))
                    domain_tong.append(count_quan_domain)
                    
                if r.filter_sms_or_filter_sql =='sms_ids' and not r.is_report_for_poster:
                    domain_tong.append(('sms_ids','!=',r.sms_id.id))
                poster_quan10_greater_10 = self.env['res.users'].search(domain_tong)
#                 if r.is_report_for_poster:
#                     pass
#                 else:
                poster_quan10_greater_10 = poster_quan10_greater_10.filtered(filter_for_poster )
                #alist= poster_quan10_greater_10.mapped('id')
                
                r.poster_ids =poster_quan10_greater_10
                r.len_poster = len(poster_quan10_greater_10)
    
    
    
                
    
#                 r.len_posters_of_sms = len(r.sms_id.getphoneposter_ids.poster_ids)
              
class Poster(models.Model):
    _inherit = 'res.users'
    getphoneposter_ids = fields.Many2many('bds.getphoneposter','getphone_poster_relate','poster_id','getphone_id')
    sms_ids = fields.Many2many('bds.sms','sms_poster_relate','poster_id','sms_id')
    post_ids = fields.One2many('bds.bds','poster_id')
    phuong_id = fields.Many2one('bds.phuong',related='post_ids.phuong_id')
    ten_luu_trong_danh_ba = fields.Char()
    mycontact_id = fields.Many2one('bds.mycontact',compute='mycontact_id_',store=True)
    dan_bac_ky = fields.Boolean()
    ngat_may_giua_chung = fields.Boolean()
    nghi_ngo_minh_la_mo_gioi = fields.Integer()
    da_ket_ban_zalo = fields.Boolean()
    do_nhiet_tinh = fields.Integer()
    do_tuoi = fields.Integer()
    cong_ty = fields.Char()
    nhaGuiChoMoGioiLine_ids = fields.One2many('bds.nhaguimogioi_lines','mo_gioi_id')
    ghi_chu = fields.Char()
    username_in_site_ids = fields.One2many('bds.posternamelines','poster_id')
    site_count_of_poster = fields.Integer(compute='site_count_of_poster_',store=True)
    name_tong_hop = fields.Char(compute='name_tong_hop_',store=True)
    count_post_of_poster_chotot = fields.Integer(compute='count_post_of_poster_',store=True,string=u'count_post_of_poster chotot')
    count_post_of_poster_bds = fields.Integer(compute='count_post_of_poster_',store=True)
    count_post_all_site = fields.Integer(compute='count_post_of_poster_',store=True)
    nhan_xet = fields.Char()
    nha_mang = fields.Selection([('vina','vina'),('mobi','mobi'),('viettel','viettel'),('khac','khac')],compute='nha_mang_',store=True)
    log_text = fields.Char()
    min_price = fields.Float(digits=(32,1))
    avg_price = fields.Float(digits=(32,1))
    max_price = fields.Float(digits=(32,1))
    count_quan_1 = fields.Integer()
    count_quan_3 = fields.Integer()
    count_quan_5 = fields.Integer()
    count_quan_10 = fields.Integer()
    count_tan_binh = fields.Integer(compute='quanofposter_ids_tanbinh',store=True)
    avg_quan_1 = fields.Float()
    avg_quan_3 = fields.Float()
    avg_quan_5 = fields.Float()
    avg_quan_10 = fields.Float()
    avg_tan_binh = fields.Float(compute='quanofposter_ids_tanbinh',store=True)
    quan_quantity = fields.Integer(compute='quan_quantity_',store=True)
    quanofposter_ids = fields.One2many('bds.quanofposter','poster_id',compute='quanofposter_ids_',store = True)#,compute='quanofposter_ids_',store = True
    quan_id_for_search = fields.Many2one('bds.quan',related = 'quanofposter_ids.quan_id')
    quanofposter_ids_show = fields.Char(compute='quanofposter_ids_show_')
    trang_thai_lien_lac = fields.Selection([(u'chờ request zalo',u'chờ request zalo'),(u'request zalo',u'request zalo'),(u'added zalo',u'added zalo'),
                                            (u'Đã gửi sổ',u'Đã gửi sổ'),(u'Đã xem nhà',u'Đã xem nhà'),(u'Đã dẫn khách',u'Đã Dẫn khách')])
    da_goi_dien_hay_chua = fields.Selection([(u'Chưa gọi điện',u'Chưa gọi điện'),(u'Đã liên lạc',u'Đã liên lạc'),(u'Không bắt máy',u'Không đổ chuông')],
                                            default = u'Chưa gọi điện')
    co_khach_368 = fields.Integer()
    co_khach_353 = fields.Integer()
    is_recent = fields.Boolean(compute=  'is_recent_')
    exclude_sms_ids = fields.Many2many('bds.sms','poster_sms_relate','poster_id','sms_id')
    
    @api.multi
    def is_recent_(self):
        for r in self:
            print fields.Date.from_string(r.create_date)
            print datetime.date.today() - datetime.timedelta(days=1)
            try:
                if fields.Date.from_string(r.create_date) >=  (datetime.date.today() - datetime.timedelta(days=1)):
                    r.is_recent = True
            except TypeError:
                pass

    
#     @api.multi
#     def name_get(self):
#         rs=[]
#         for r in self:
#             new_name = r.name + u' chợ tốt (%s)'%r.count_post_of_poster_chotot \
#             + u'bds: (%s)'%r.count_post_of_poster_bds
#             rs.append((r.id,new_name))
#         return rs
#             
    
    @api.depends('phone')
    def nha_mang_(self):
        for r in self:
            patterns = {'vina':'(^091|^094|^0123|^0124|^0125|^0127|^0129|^088)',
                        'mobi':'(^090|^093|^089|^0120|^0121|^0122|^0126|^0128)',
                       'viettel': '(^098|^097|^096|^0169|^0168|^0167|^0166|^0165|^0164|^0163|^0162|^086)'}
            if r.phone:
                for nha_mang,pattern in patterns.iteritems():
                    rs = re.search(pattern, r.phone)
                    if rs:
                        r.nha_mang = nha_mang
                        break
                if not rs:
                    r.nha_mang = 'khac'
    @api.depends('post_ids','post_ids.gia')
    def quanofposter_ids_tanbinh(self):
        self.quanofposter_ids_common(u'Tân Bình')
    def quanofposter_ids_common(self,quan_name):
        for r in self:
            product_category_query =\
             '''select count(quan_id),quan_id,min(gia),avg(gia),max(gia) from bds_bds where poster_id = %s group by quan_id'''%r.id
            self.env.cr.execute(product_category_query)
            product_category = self.env.cr.fetchall()
            print product_category
            quanofposter_ids_lists= []
            for  tuple_count_quan in product_category:
                quan_id = int(tuple_count_quan[1])
                #quantity = int(tuple_count_quan[0].replace('L',''))
                quan = self.env['bds.quan'].browse(quan_id)
                if quan.name in [quan_name]:#u'Quận 1',u'Quận 3',u'Quận 5',u'Quận 10',u'Tân Bình'
                    for key1 in ['count','avg']:
                        if key1 =='count':
                            value = tuple_count_quan[0]
                        elif key1 =='avg':
                            value = tuple_count_quan[3]
                        name = quan.name_unidecode.replace('-','_')
                        name = key1+'_'+name
                        setattr(r, name, value)
                        print 'set attr',name,value
                        
#                 quanofposter = get_or_create_object(self,'bds.quanofposter', {'quan_id':quan_id,
#                                                              'poster_id':r.id}, {'quantity':tuple_count_quan[0],
#                                                                                 'min_price':tuple_count_quan[2],
#                                                                                 'avg_price':tuple_count_quan[3],
#                                                                                 'max_price':tuple_count_quan[4],
#                                                                                  }, True, False, False)
#                 quanofposter_ids_lists.append(quanofposter.id)
#             r.quanofposter_ids = quanofposter_ids_lists
            
    
    @api.depends('post_ids','post_ids.gia')
    def quanofposter_ids_(self):
        for r in self:
            quanofposter_ids_lists= []
            product_category_query_siteleech =\
             '''select count(quan_id),quan_id,min(gia),avg(gia),max(gia),siteleech_id from bds_bds where poster_id = %s group by quan_id,siteleech_id'''%r.id
            product_category_query_no_siteleech = \
            '''select count(quan_id),quan_id,min(gia),avg(gia),max(gia) from bds_bds where poster_id = %s group by quan_id'''%r.id
            a = {'product_category_query_siteleech':product_category_query_siteleech,
                 'product_category_query_no_siteleech':product_category_query_no_siteleech
                 }
            for k,product_category_query in a.iteritems():
                self.env.cr.execute(product_category_query)
                product_category = self.env.cr.fetchall()
                print product_category
                for  tuple_count_quan in product_category:
                    quan_id = int(tuple_count_quan[1])
                    if k =='product_category_query_no_siteleech':
                        siteleech_id =False
                    else:
                        siteleech_id = int(tuple_count_quan[5])
                        
                    quanofposter = get_or_create_object(self,'bds.quanofposter', {'quan_id':quan_id,
                                                                 'poster_id':r.id,'siteleech_id':siteleech_id}, {'quantity':tuple_count_quan[0],
                                                                                    'min_price':tuple_count_quan[2],
                                                                                    'avg_price':tuple_count_quan[3],
                                                                                    'max_price':tuple_count_quan[4],
                                                                                     }, True, False, False)
                    quanofposter_ids_lists.append(quanofposter.id)#why????
            r.quanofposter_ids = quanofposter_ids_lists
                    
                    
    
    
    @api.depends('post_ids')
    def quanofposter_ids_old_(self):
        for r in self:
            product_category_query =\
             '''select count(quan_id),quan_id,min(gia),avg(gia),max(gia) from bds_bds where poster_id = %s group by quan_id'''%r.id
            self.env.cr.execute(product_category_query)
            product_category = self.env.cr.fetchall()
            print product_category
            quanofposter_ids_lists= []
            for  tuple_count_quan in product_category:
                quan_id = int(tuple_count_quan[1])
                #quantity = int(tuple_count_quan[0].replace('L',''))
                quan = self.env['bds.quan'].browse(quan_id)
                if quan.name in [u'Quận 1',u'Quận 3',u'Quận 5',u'Quận 10',u'Tân Bình']:
                    for key1 in ['count','avg']:
                        if key1 =='count':
                            value = tuple_count_quan[0]
                        elif key1 =='avg':
                            value = tuple_count_quan[3]
                        name = quan.name_unidecode.replace('-','_')
                        name = key1+'_'+name
                        setattr(r, name, value)
                        print 'set attr',name,value
                        
                quanofposter = get_or_create_object(self,'bds.quanofposter', {'quan_id':quan_id,
                                                             'poster_id':r.id}, {'quantity':tuple_count_quan[0],
                                                                                'min_price':tuple_count_quan[2],
                                                                                'avg_price':tuple_count_quan[3],
                                                                                'max_price':tuple_count_quan[4],
                                                                                 }, True, False, False)
                quanofposter_ids_lists.append(quanofposter.id)
            r.quanofposter_ids = quanofposter_ids_lists
    @api.depends('quanofposter_ids')
    def quanofposter_ids_show_(self):
        for r in self:
            value =','.join(r.quanofposter_ids.mapped('name'))
            r.quanofposter_ids_show = value
    
    @api.depends('quanofposter_ids')
    def quan_quantity_(self):
        for r in self:
      
            r.quan_quantity = len(r.quanofposter_ids)
#     @api.depends('post_ids')
#     def count_post_of_all_site_(self):
#         for r in self:
#             r.count_post_all_site = len(r.post_ids)
    @api.depends('post_ids','post_ids.gia')
    def count_post_of_poster_(self):
        for r in self:
            post_of_poster_cho_tot = self.env['bds.bds'].search([('poster_id','=',r.id),('link','like','chotot')])
            count_post_of_poster_bds = self.env['bds.bds'].search([('poster_id','=',r.id),('link','like','batdongsan')])
            r.count_post_of_poster_chotot = len(post_of_poster_cho_tot)
            r.count_post_of_poster_bds = len(count_post_of_poster_bds)
            r.count_post_all_site = len(r.post_ids)
    @api.depends('username_in_site_ids')
    def  site_count_of_poster_(self):
        for r in self:
            r.site_count_of_poster = len(r.username_in_site_ids)
    @api.depends('phone')
    def mycontact_id_(self):
        for r in self:
            r.mycontact_id = self.env['bds.mycontact'].search([('phone','=',r.phone)])
            
    @api.depends('username_in_site_ids')
    def name_tong_hop_(self):
        for r in self:
            alist = r.name_get()
#             raise ValueError('alist',alist)
            r.name_tong_hop = alist[0][1]
#     @api.multi
#     def name_get(self):
#         #return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]
#         res = []
#         for r in self:
#             #new_name = r.name + (' - ' +  r.phone ) if r.phone else ''
#             
#             a= []
#             for i in r.username_in_site_ids:
#                 a.append(i.username_in_site + '(' + i.site_id.name + ')')
#             a = '|'.join(a)
#             #new_name =r.phone  if r.phone else ''
#             new_name = a + (' - ' +  r.phone ) if r.phone else ''
#             
#             new_name = new_name + u' chợ tốt (%s)'%r.count_post_of_poster_chotot \
#             + u' bds: (%s)'%r.count_post_of_poster_bds
#             new_name = new_name + (('**'  + r.mycontact_id.name) if  r.mycontact_id else  '')
#             res.append((r.id,new_name))
#         return res
    def avg(self):
        product_category_query = '''select min(gia),avg(gia),max(gia) from bds_bds  where poster_id = %s and gia > 0'''%self.id
        self.env.cr.execute(product_category_query)
        product_category = self.env.cr.fetchall()
        print product_category
        self.log_text = product_category
        
class Importcontact(models.Model):
    _name = 'bds.importcontact'
    file = fields.Binary()
    land_contact_saved_number = fields.Integer()
    @api.multi
    def import_contact(self):
        import_contact(self)
        
  
    @api.multi
    def count_post_of_poster(self):
        for r in self.env['res.users'].search([]):
            post_of_poster_cho_tot = self.env['mbds.bds'].search([('poster_id','=',r.id),('link','like','chotot')])
            count_post_of_poster_bds = self.env['bds.bds'].search([('poster_id','=',r.id),('link','like','batdongsan')])
            r.count_post_of_poster_chotot = len(post_of_poster_cho_tot)
            r.count_post_of_poster_bds = len(count_post_of_poster_bds)
            count_post_of_poster_bds = self.env['bds.bds'].search([('poster_id','=',r.id)])
            r.count_post_all_site = len(count_post_of_poster_bds)
            
    @api.multi
    def insert_count_by_sql(self):
        product_category_query = '''UPDATE res_users 
SET count_post_all_site = i.count
FROM (
    SELECT count(id),poster_id
    FROM bds_bds group by poster_id)  i
WHERE 
    i.poster_id = res_users.ID

'''    
        
        #self.env.cr.execute(product_category_query)
        
        bds_site = self.env['bds.siteleech'].search([('name','like','batdongsan')]).id
        chotot_site = self.env['bds.siteleech'].search([('name','like','chotot')]).id
        for x in [bds_site,chotot_site]:
            if x ==bds_site:
                name = 'bds'
            else:
                name ='chotot'
            product_category_query = '''UPDATE res_users 
    SET count_post_of_poster_%s = i.count
    FROM (
        SELECT count(id),poster_id,siteleech_id
        FROM bds_bds group by poster_id,siteleech_id)  i
    WHERE 
        i.poster_id = res_users.ID and i.siteleech_id=%s'''%(name,x)
        
            self.env.cr.execute(product_category_query) 
        #product_category = self.env.cr.fetchall()
        #print product_category
    @api.multi
    def add_nha_mang(self):
        for r in self.env['res.users'].search([]):
            print 'handling...',r.name
            patterns = {'vina':'(^091|^094|^0123|^0124|^0125|^0127|^0129|^088)',
                        'mobi':'(^090|^093|^089|^0120|^0121|^0122|^0126|^0128)',
                       'viettel': '(^098|^097|^096|^0169|^0168|^0167|^0166|^0165|^0164|^0163|^0162|^086)'}
            if r.phone:
                for nha_mang,pattern in patterns.iteritems():
                    rs = re.search(pattern, r.phone)
                    if rs:
                        r.nha_mang = nha_mang
                        break
                if not rs:
                    r.nha_mang = 'khac'
    @api.multi
    def add_quan_id_for_cho_tot(self):
        for r in self.env['bds.bds'].search([('link','ilike','chotot')]):
            if r.parameters:
                rs = create_or_get_quan_for_chotot(self,r.parameters)
                if r.quan_id.id !=rs.id:
                    r.quan_id = rs.id
                    print 'updating quan vao 1 topic'
    @api.multi
    def add_site_leech_tobds(self):
        chotot_site = self.env['bds.siteleech'].search([('name','ilike','chotot')])
        ctbds = self.env['bds.bds'].search([('link','ilike','chotot')])
        ctbds.write({'siteleech_id':chotot_site.id})
        
        chotot_site = self.env['bds.siteleech'].search([('name','ilike','batdongsan')])
        ctbds = self.env['bds.bds'].search([('link','ilike','batdongsan')])
        ctbds.write({'siteleech_id':chotot_site.id})
        
    
    @api.multi
    def add_name_tong_hop(self):
        for r in self.env['res.users'].search([]):
            print 'hadling...one usee'
            r.name_tong_hop = r.name_get()[0][1]
    @api.multi
    def add_min_max_avg_for_user(self):
        for c,r in enumerate(self.env['res.users'].search([])):
            print 'hadling...one usee' ,c
            r.name_tong_hop = r.name_get()[0][1]
            product_category_query = '''select min(gia),avg(gia),max(gia) from bds_bds  where poster_id = %s and gia > 0'''%r.id
            self.env.cr.execute(product_category_query)
            product_category = self.env.cr.fetchall()
            r.min_price = product_category[0][0]
            r.avg_price = product_category[0][1]
            r.max_price = product_category[0][2]
            print' min,avg,max', product_category
            
    @api.multi
    def add_quan_lines_ids_to_poster(self):
        for c,r in enumerate(self.env['res.users'].search([])):
            print 'hadling...one usee' ,c
            product_category_query =\
             '''select count(quan_id),quan_id,min(gia),avg(gia),max(gia) from bds_bds where poster_id = %s group by quan_id'''%r.id
            self.env.cr.execute(product_category_query)
            product_category = self.env.cr.fetchall()
            print product_category
            for  tuple_count_quan in product_category:
                quan_id = int(tuple_count_quan[1])
                #quantity = int(tuple_count_quan[0].replace('L',''))
                quan = self.env['bds.quan'].browse(quan_id)
                if quan.name in [u'Quận 1',u'Quận 3',u'Quận 5',u'Quận 10',u'Tân Bình']:
                    for key1 in ['count','avg']:
                        if key1 =='count':
                            value = tuple_count_quan[0]
                        elif key1 =='avg':
                            value = tuple_count_quan[3]
                        name = quan.name_unidecode.replace('-','_')
                        name = key1+'_'+name
                        setattr(r, name, value)
                        print 'set attr',name,value
                get_or_create_object(self,'bds.quanofposter', {'quan_id':quan_id,
                                                             'poster_id':r.id}, {'quantity':tuple_count_quan[0],
                                                                                'min_price':tuple_count_quan[2],
                                                                                'avg_price':tuple_count_quan[3],
                                                                                'max_price':tuple_count_quan[4],
                                                                                 }, True, False, False)
                
                
    @api.multi
    def add_quan_lines_ids_to_poster_theo_siteleech_id(self):
        for c,r in enumerate(self.env['res.users'].search([])):
            
            product_category_query_siteleech =\
             '''select count(quan_id),quan_id,min(gia),avg(gia),max(gia),siteleech_id from bds_bds where poster_id = %s group by quan_id,siteleech_id'''%r.id
            product_category_query_no_siteleech = \
            '''select count(quan_id),quan_id,min(gia),avg(gia),max(gia) from bds_bds where poster_id = %s group by quan_id'''%r.id
            a = {'product_category_query_siteleech':product_category_query_siteleech,
                 'product_category_query_no_siteleech':product_category_query_no_siteleech
                 }
            for k,product_category_query in a.iteritems():
                self.env.cr.execute(product_category_query)
                product_category = self.env.cr.fetchall()
                print product_category
                for  tuple_count_quan in product_category:
                    quan_id = int(tuple_count_quan[1])
                    if k =='product_category_query_no_siteleech':
                        siteleech_id =False
                    else:
                        siteleech_id = int(tuple_count_quan[5])
                    get_or_create_object(self,'bds.quanofposter', {'quan_id':quan_id,
                                                                 'poster_id':r.id,'siteleech_id':siteleech_id}, {'quantity':tuple_count_quan[0],
                                                                                    'min_price':tuple_count_quan[2],
                                                                                    'avg_price':tuple_count_quan[3],
                                                                                    'max_price':tuple_count_quan[4],
                                                                                     }, True, False, False)
                
            
    @api.multi
    def add_site_leech_to_urlcate(self):
        for r in self.env['bds.urlcate'].search([]):
            r.url = r.url
            
        
                          
class Errors(models.Model):
    _name = 'bds.error'
    url = fields.Char()
    code = fields.Char()
class Luong(models.Model):
    _name = 'bds.luong'
    threadname = fields.Char()
    urlcate_id = fields.Many2one('bds.urlcate')
    current_page = fields.Integer()
class UrlCate(models.Model):
    _name = 'bds.urlcate'
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(url)',
         "The url must be unique"),
    ]
    name = fields.Char(compute='name_',store = True)
    url = fields.Char()
    description = fields.Char()    
    siteleech_id = fields.Many2one('bds.siteleech',compute='siteleech_id_',store=True)
    web_last_page_number = fields.Integer()
    quan_id = fields.Many2one('bds.quan')
    phuong_id = fields.Many2one('bds.phuong')
    current_page = fields.Integer()
    so_luong_luong = fields.Integer()
    luong_ids = fields.One2many('bds.luong','urlcate_id')
    @api.depends('url')
    def siteleech_id_(self):
        for r in self:
            if 'chotot' in r.url:
                name = 'chotot'
            elif 'batdongsan' in r.url:
                name = 'batdongsan'
                
            chottot_site = get_or_create_object(self,'bds.siteleech', {'name':name})
            r.siteleech_id = chottot_site.id
            
    @api.depends('url','quan_id','phuong_id')
    def name_(self):
        surfix =  self.phuong_id.name or  self.quan_id.name  
        self.name = self.url + ((' ' +  surfix ) if surfix else '')
    @api.multi
    def name_get(self):
        #return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]
        res = []
        for r in self:
            surfix =  r.quan_id.name or r.phuong_id.name
            new_name = r.url + ((' ' +  surfix ) if surfix else '' )+' current_page: %s'%r. current_page
            res.append((r.id,new_name))
        return res
    
class Cron(models.Model):
 
    _inherit = "ir.cron"
    _logger = logging.getLogger(_inherit)
    @api.model
    def worker(self,thread_index,urlcate_id,thread_number):
        new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
        uid, context = self.env.uid, self.env.context
        with api.Environment.manage():
            self.env = api.Environment(new_cr, uid, context)
            luong = get_or_create_object(self,'bds.luong', {'threadname':str(1),'urlcate_id':urlcate_id})
            if luong[0].current_page==0:
                current_page = thread_index
            else:
                current_page = luong[0].current_page + thread_number
            luong[0].write({'current_page':current_page})
            new_cr.commit()
            self.env.cr.close()

class Fetch(models.Model):
    _name = 'bds.fetch'
#     url = fields.Char(default = 'https://batdongsan.com.vn/ban-nha-rieng-quan-10/-1/2500-3500/-1/-1')
    url_id = fields.Many2one('bds.urlcate')
    url_ids = fields.Many2many('bds.urlcate')
#     is_fetch_circle = fields.Boolean(string=u'vòng tròn link',default=True)
    current_url_id_circle_fetch = fields.Integer()#>0
    name = fields.Char()
    link = fields.Char()
    web_last_page_number = fields.Integer()
    set_page_end = fields.Integer(default=4)
    set_number_of_page_once_fetch = fields.Integer(default=5)
    thread_number = fields.Integer(default=5)
    link_number = fields.Integer()
    update_link_number = fields.Integer()
    create_link_number = fields.Integer()
    existing_link_number = fields.Integer()
    bds_ids_quantity = fields.Integer()
    
    phuong_ids =  fields.Many2many('bds.phuong')
    quan_ids =  fields.Many2many('bds.quan')
    bds_ids = fields.Many2many('bds.bds','fetch_bds_relate','fetch_id','bds_id')
    fetch_cronfield = fields.Integer()
    page_begin = fields.Integer()
    per_page = fields.Integer()
    note = fields.Char()
    update_field_of_existing_recorder = fields.Selection([(u'giá',u'giá'),(u'all',u'all')],default = u'all')
    
    @api.multi
    def thread(self):
        thread_number = 5
        url_imput = self.url_id.url
        fetch_object = self
        for i in range(1,6):
            urlcate_id = self.url_id.id
            w2 = threading.Thread(target=self.env['ir.cron'].worker,kwargs={'thread_index':i,'urlcate_id':urlcate_id,
                                                                            "thread_number" : thread_number,
                                                                            'url_imput':url_imput,
                                                                            "fetch_object":fetch_object
                                                                            })
            w2.start()

    
    @api.multi
    def fetch_cron1(self):
        fetch_id2 = self.browse(2)
        fetch_id2.fetch_cronfield +=1
    @api.multi
    def fetch_cron(self,id_fetch):
        fetch_id2 = self.browse(id_fetch)
        fetch(fetch_id2,note=u'cập nhật lúc ' +  fields.Datetime.now(),is_fetch_in_cron = True)
        #raise ValueError('dfdfdfd')
    @api.depends('write_date')
    def name_(self):
        write_date = fields.Datetime.from_string(self.write_date)
        write_date_str =write_date.strftime( "%d-%m-%Y")
        self.name = write_date_str 
#     @api.depends('write_date')
#     def bds_ids_quantity_(self):
#         for r in self:
#             r.bds_ids_quantity = len(r.bds_ids)
        
    @api.multi
    def group_quan(self):
#         product_category_query = '''select count(bds_bds.quan_id),bds_bds.phuong_id from fetch_bds_relate inner join bds_bds on fetch_bds_relate.bds_id = bds_bds.id where fetch_id = %s group by bds_bds.phuong_id'''%self.id
#         self.env.cr.execute(product_category_query)
#         product_category = self.env.cr.fetchall()
#         phuong_list = reduce(lambda y,x:([x[1]]+y) if x[1]!=None else y,product_category,[] )
        #self.phuong_ids = phuong_list
        phuong_list = get_quan_list_in_big_page(self)
        quan_list = get_quan_list_in_big_page(self,column_name='bds_bds.quan_id')
        self.write({'phuong_ids':[(6,0,phuong_list)],'quan_ids':[(6,0,quan_list)]})#'quan_ids':[(6,0,quan_list)]
        update_phuong_or_quan_for_url_id(self)
#         raise ValueError ('aaaa',product_category)
    @api.multi
    def fetch(self):
        fetch(self)
#         self.create_link_number=create_link_number
#         self.update_link_number =update_link_number
#         self.link_number = link_number
        
#         phuong_list = get_quan_list_in_big_page(self)
#         quan_list = get_quan_list_in_big_page(self,column_name='bds_bds.quan_id')
#         self.write({'phuong_ids':[(6,0,phuong_list)],'quan_ids':[(6,0,quan_list)]})#'quan_ids':[(6,0,quan_list)]
#         update_phuong_or_quan_for_url_id(self)
        
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
class Mycontact(models.Model):
    _name = 'bds.mycontact'
    name = fields.Char()
    phone = fields.Char()