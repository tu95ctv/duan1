# -*- coding: utf-8 -*-

from odoo import models, fields, api
from fetch import fetch

class QuanHuyen(models.Model):
    _name = 'bds.quan'
    name = fields.Char()
    name_unidecode = fields.Char()
class Phuong(models.Model):
    _name = 'bds.phuong'
    name = fields.Char(compute='name_',store=True)
    name_phuong = fields.Char()
    quan_id = fields.Many2one('bds.quan')
    name_unidecode = fields.Char()
    @api.depends('name_phuong','quan_id')
    def name_(self):
        self.name = ( self.name_phuong if self.name_phuong else '' )+ ('-' + self.quan_id.name) if self.quan_id.name else ''
    
class bds(models.Model):
    _name = 'bds.bds'
    name = fields.Char(compute = 'name_',store = True)
    title = fields.Char()
    gia = fields.Float()
    area = fields.Float()
    quan_id = fields.Many2one('bds.quan')
    phuong_id = fields.Many2one('bds.phuong')
    link = fields.Char()
    ngay_dang = fields.Date()
    html = fields.Html()
    poster_id = fields.Many2one('res.users')
    url_cate = fields.Char()
    fetch_ids = fields.Many2many('bds.fetch','fetch_bds_relate','bds_id','fetch_id')
    #fetch_ids = fields.Many2many('bds.fetch')
    @api.depends('title')
    def name_(self):
        self.name = self.title
class Poster(models.Model):
    _inherit = 'res.users'
    post_ids = fields.One2many('bds.bds','poster_id')
class UrlCate(models.Model):
    _name = 'bds.urlcate'
    name = fields.Char()
class Fetch(models.Model):
    _name = 'bds.fetch'
    url = fields.Char(default = 'https://batdongsan.com.vn/ban-nha-rieng-quan-10/-1/2500-3500/-1/-1')
    url_id = fields.Many2one('bds.urlcate')
    quan_id = fields.Many2one('bds.quan')
    name = fields.Char(compute='name_',store=True)
    link = fields.Char()
    page_end = fields.Integer()
    link_number = fields.Integer()
    update_link_number = fields.Integer()
    create_link_number = fields.Integer()
    phuong_ids =  fields.Many2many('bds.phuong')
    bds_ids = fields.Many2many('bds.bds','fetch_bds_relate','fetch_id','bds_id')
    #bds_ids = fields.Many2many('bds.bds')
    
    @api.depends('write_date')
    def name_(self):
        write_date = fields.Datetime.from_string(self.write_date)
        write_date_str =write_date.strftime( "%d-%m-%Y")
        self.name = write_date_str 
    @api.multi
    def group_quan(self):
        product_category_query = '''select count(bds_bds.quan_id),bds_bds.phuong_id from fetch_bds_relate inner join bds_bds on fetch_bds_relate.bds_id = bds_bds.id where fetch_id = %s group by bds_bds.phuong_id'''%self.id
        self.env.cr.execute(product_category_query)
        product_category = self.env.cr.fetchall()
        phuong_list = reduce(lambda y,x:([x[1]]+y) if x[1]!=None else y,product_category,[] )
        self.phuong_ids = phuong_list
        #self.write({'phuong_ids':[(6,0,phuong_list)]})
#         raise ValueError ('aaaa',product_category)
    @api.multi
    def fetch(self):
        page_end = self.page_end
        create_link_number,update_link_number,link_number = fetch(self,page_end)
        self.create_link_number=create_link_number
        self.update_link_number =update_link_number
        self.link_number = link_number
    
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100