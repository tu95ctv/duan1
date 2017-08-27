# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions
import xlrd
import base64
import re
from odoo.osv import expression

class User(models.Model):
    _inherit = 'res.users'
    catruc_ids = fields.Many2many('trucca', 'trucca_res_users_rel_d4','res_users_id','trucca_id',string=u'Ca truc')
class TrucCa(models.Model):
    _name = 'trucca'
    
    dien_ap_a = fields.Float()
    dong_dien_a = fields.Float()
    dien_ap_b = fields.Float()
    dong_dien_b = fields.Float()
    
    
    co_toilet = fields.Boolean()
    quet_nha = fields.Boolean()
    chui_nha = fields.Boolean()
    
#         invoice_ids = fields.Many2many('account.invoice', 'account_invoice_payment_rel', 'payment_id', 'invoice_id', string="Invoices", copy=False, readonly=True)
#     payment_ids = fields.Many2many('account.payment', 'account_invoice_payment_rel', 'invoice_id', 'payment_id', string="Payments", copy=False, readonly=True)

    name = fields.Char(string=u'Ca Trực',compute = '_name_truc_ca_compute', store=True)
    ca = fields.Selection([(u'Sáng',u'Sáng'), (u'Chiều',u'Chiều'), (u'Đêm',u'Đêm')],string = u'Buổi ca') 
    date = fields.Date(default=fields.Date.today, string = u'Ngày')
    truong_ca = fields.Many2one('res.users' , default=lambda self: self._truongca_default_get())
    member_ids = fields.Many2many('res.users', string=u'Những thành viên trực')
    truc_kem_ids = fields.Many2many('res.users', 'trucca_res_users_rel_d4','trucca_id','res_users_id',string=u'Trực kèm member')
    gio_bat_dau = fields.Datetime(u'Giờ bắt đầu ca ',default=fields.Datetime.now)
    gio_ket_thuc = fields.Datetime(u'Giờ Kết Thúc ca')
#     kiem_tra_nguon = fields.Many2one('kiemtranguon')
#     ve_sinh_cong_nghiep = fields.Many2one('vesinhcn')
    #comment_ids = fields.One2many('comment','trucca_id')
    su_kien_ids = fields.Many2many('sukien','su_kien_comment','su_kien_id','comment_id',string = u'sự kiện')
    @api.model
    def _truongca_default_get(self):
        return self.env.user
    def truc_ca_name(self,x,show_id = True, show_ca=True,show_date = True,show_member = True):
        names = []
        if x.id != False and isinstance(x.id, int):
            id_x = u'id: ' + str(x.id)
            names.append(id_x)
        if x.ca != False:
                ca = u'Ca: ' + x.ca 
                names.append(ca)
        if x.date !=False:
            date = fields.Date.from_string(x.date)
            date = u'Ngày: ' + date.strftime('%d/%m/%y')
            names.append(date)
        if x.member_ids != False:
            nguoi_trucs_str = u'Người trực: ' + u','.join(x.member_ids.mapped('name'))
            names.append(nguoi_trucs_str)
        ret = u' - '.join(names)
        return ret    
    
    
    
    @api.depends('date','ca','member_ids')
    def _name_truc_ca_compute(self):
        for x in self:
#             names = []
#             if x.id != False:
#                 id_x = u'id: ' + str(x.id)
#                 names.append(id_x)
#             if x.ca != False:
#                 ca = u'Ca: ' + x.ca 
#                 names.append(ca)
#       
#             if x.date !=False:
#                 date = fields.Date.from_string(x.date)
#                 date = u'Ngày: ' + date.strftime('%d/%m/%y')
#                 names.append(date)
#             if x.member_ids != False:
#                 nguoi_trucs_str = u'Người trực: ' + u','.join(x.member_ids.mapped('name'))
#                 names.append(nguoi_trucs_str)
#             ret = u' - '.join(names)
            ret = self.truc_ca_name(x)
            x.name = ret
                
    @api.model
    def default_get(self, fields):
        res = super(TrucCa, self).default_get(fields)
        empty_ket_thuc_comments = self.env[ 'sukien'].search([('gio_ket_thuc','=',False)])
        if empty_ket_thuc_comments:
            res['su_kien_ids'] = empty_ket_thuc_comments.mapped('id')
        res['member_ids']  = [self.env.user.id]
        return res
#     @api.multi
#     def name_get(self):
#         res = []
#         for x in self:
#             #raise ValueError('type cua date',type(self.date))
#             #date = self.date.strftime("%d/%m/%y")
#             res.append((x.id, x.date))
#         return res       

class SuKien(models.Model):
    _name = 'sukien'
    #trucca_id = fields.Many2many('trucca')
    gio_bat_dau = fields.Datetime(u'Giờ bắt đầu ', default=fields.Datetime.now,required=True)
    gio_ket_thuc = fields.Datetime(u'Giờ Kết Thúc')
    cate_sukien = fields.Selection([(u'Sự cố đứt quang',u'Sự cố đứt quang'),(u'Đổi luồng',u'Đổi luồng'),(u'Đấu mới',u'Đấu mới'),(u'Khác',u'Khác')],default =u'Khác' )
    #cate_sukien = fields.Selection([('ktn',u'Kiểm tra nguồn'),('vscn',u'Vệ sinh cn')])
#     noi_dung_lien_quan_den_cate = fields.Reference(selection=[('kiemtranguon',u'Kiểm tra nguồn reference'),('vesinhcn',u'Vệ sinh cn')])
    #ve_sinh_cn_id = fields.Many2one('vesinhcn')
    show_field_test = fields.Char(default = 'anh yeu em')
    dien_ap_a = fields.Float()
    quet_nha = fields.Boolean()
    duration = fields.Float(digits=(6, 2), help="Duration in minutes",compute = '_get_duration', store = True)
    content = fields.Char(string = u"Nội dung comment đầu") 
    comment_ids = fields.One2many('comment','su_kien_id',string=u'Những comments tiếp')
    catruc_ids  = fields.Many2many('trucca','su_kien_comment','comment_id','su_kien_id',string = u'Ca Trực')
    @api.depends('gio_ket_thuc','gio_bat_dau')
    def _get_duration(self):
        for r in self:
            if r.gio_bat_dau == False or r.gio_ket_thuc==False:
                r.duration = False
            else:
                start_date = fields.Datetime.from_string(r.gio_bat_dau)
                end_date = fields.Datetime.from_string(r.gio_ket_thuc)
                duration = (end_date - start_date)
                secs = duration.total_seconds()
                minutes = int(secs / 60)
                r.duration = minutes
    
#     @api.onchange('noi_dung_lien_quan_den_cate'):
#     def _noi_dung_lien_quan_den_cate(self):
#         if self.noi_dung_lien_quan_den_cate:
#             pass
#         else:
#             return {'co_toilet' : {'attributes':{'invisible':True}}}
#             
#     @api.onchange('catruc_ids')
#     def catruc_ids_onchange(self):
#         #raise ValueError(self._context)
#         raise  ValueError(self.id,self.cate_sukien,self.catruc_ids,self.catruc_ids.su_kien_ids)
    @api.multi
    def name_get(self):
        res = []
        for x in self:
            res.append((x.id, x.content))
        return res
class OtherComment(models.Model):
    _name = 'comment'
    comment = fields.Char(string = u"Nội dung comment  tiếp")
    su_kien_id = fields.Many2one('sukien')
    @api.multi
    def name_get(self):
        res = []
        for x in self:
            res.append((x.id, self.comment))
        return res
    
    
