# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
import re
from odoo.osv import expression
from odoo.tools.misc import xlwt
from copy import deepcopy
import pytz
from odoo.exceptions import ValidationError,UserError
from tao_instance import importthuvien
from tao_instance import import_strect
import datetime
import json
from lxml import etree

### ngày 05/10/2017 ##
############### BEGIN DAI HCM ##################
def name_compute(r,adict=None,join_char = u' - '):
    names = []
#     adict = [('cate_cvi',{'pr':''}),('noi_dung',{'pr':''}),('id',{'pr':''})]
    for fname,attr_dict in adict:
        val = getattr(r,fname)
        fnc = attr_dict.get('fnc',None)
        if fnc:
            val = fnc(val)
        if  not val:# Cho có trường hợp New ID
#         if val ==False:
            if attr_dict.get('skip_if_False',False):
                continue
            if  fname=='id' :
                val ='New'
            else:
                val ='_'
        if attr_dict.get('pr',None):
            item =  attr_dict['pr'] + u': ' + unicode(val)
        else:
            item = unicode (val)
        names.append(item)
    if names:
        name = join_char.join(names)
    else:
        name = False
    return name
def convert_memebers_to_str(member_ids):
    return u','.join(member_ids.mapped('name'))
def Convert_date_orm_to_str(date_orm_str):
    if date_orm_str:
        date_obj = fields.Date.from_string(date_orm_str)
        return date_obj.strftime('%d/%m/%y')
    else:
        return False
def convert_utc_to_gmt_7(utc_datetime_inputs):
    local = pytz.timezone('Etc/GMT-7')
    utc_tz =pytz.utc
    gio_bat_dau_utc_native = utc_datetime_inputs#fields.Datetime.from_string(self.gio_bat_dau)
    gio_bat_dau_utc = utc_tz.localize(gio_bat_dau_utc_native, is_dst=None)
    gio_bat_dau_vn = gio_bat_dau_utc.astimezone (local)
    return gio_bat_dau_vn
def convert_odoo_datetime_to_vn_datetime(odoo_datetime):
        utc_datetime_inputs = fields.Datetime.from_string(odoo_datetime)
        vn_time = convert_utc_to_gmt_7(utc_datetime_inputs)
        return vn_time
  
def convert_vn_datetime_to_utc_datetime(native_ca_gio_in_vn):
            local = pytz.timezone('Etc/GMT-7')
            utc_tz =pytz.utc
            gio_bat_dau_in_vn = local.localize(native_ca_gio_in_vn, is_dst=None)
            gio_bat_dau_in_utc = gio_bat_dau_in_vn.astimezone (utc_tz)
            return gio_bat_dau_in_utc
        
def convert_odoo_datetime_to_vn_str(odoo_datetime):
    if odoo_datetime:
        utc_datetime_inputs = fields.Datetime.from_string(odoo_datetime)
        vn_time = convert_utc_to_gmt_7(utc_datetime_inputs)
        vn_time_str = vn_time.strftime('%d/%m/%Y %H:%M')
        return vn_time_str
    else:
        return False
    
################ CA TRỰC ##############
class CaTruc(models.Model):
    _name = 'ctr'
    name = fields.Char(compute = '_name_truc_ca_compute', store=True)
    ca = fields.Selection([(u'Sáng',u'Sáng'), (u'Chiều',u'Chiều'), (u'Đêm',u'Đêm')],string=u'Buổi ca',default = lambda self: self.buoi_ca_now_default_())
    date = fields.Date(string=u'Ngày',compute='date_',store=True)#readonly = True
    gio_bat_dau = fields.Datetime(u'Giờ bắt đầu ca ',default=lambda self: self.gio_bat_dau_defaut_or_ket_thuc_())
    gio_ket_thuc = fields.Datetime(u'Giờ Kết Thúc ca',default=lambda self: self.gio_bat_dau_defaut_or_ket_thuc_(is_tinh_gio_bat_dau_or_ket_thuc = 'gio_ket_thuc'))#
    cty_id = fields.Many2one('congty',string=u'Đơn vị',default=lambda self:self.env.user.cty_id, readonly=True,required=True)
    member_ids = fields.Many2many('res.users', string=u'Những thành viên trực')
    cvi_ids = fields.Many2many('cvi','ctr_cvi_relate','ctr_id','cvi_id',string=u'Công Việc')
    su_co_ids = fields.Many2many('suco','ctr_suco_rel','ctr_id','suco_id',string=u'Sự Cố')
    su_vu_ids = fields.Many2many('suvu','ctr_suvu_rel','ctr_id','suvu_id',string=u'Sự Vụ')
#     @api.model
#     def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
#         res = super(CaTruc, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         if view_type =='form':
#             id_you_want = self._context.get('active_id')
#             fields = res.get('fields')
#             fields['date']['string'] =u'anh con no'# ['|',('ctr_ids','=','active_id'),'&',('ctr_ids','!=',False),('gio_ket_thuc','=',False)]
#             fields['loai_su_co']['domain'] ='''[('l','!=',False)]'''
#         return res
    @api.depends('date','ca','member_ids')
    def _name_truc_ca_compute(self):
        for r in self:
            adict=[('id',{'pr':u'Ca Trực, id'}),('ca',{'pr':u'Buổi'}),('date',{'pr':u'Ngày','fnc':Convert_date_orm_to_str}),('member_ids',{'pr':u'Người Trực','fnc':convert_memebers_to_str})]
            ret =  name_compute(r, adict)
            r.name = ret
    @api.depends('gio_bat_dau')
    def date_(self):
        for r in self:
            if r.gio_bat_dau:
                r.date = convert_odoo_datetime_to_vn_datetime(r.gio_bat_dau).date()
    def buoi_ca_now_default_(self,gio_bat_dau_vn_return = False):
        now_vn_datetime = convert_utc_to_gmt_7(datetime.datetime.now())
        now_hour = now_vn_datetime.hour
        alist = [(u'Sáng',7),(u'Chiều',14),(u'Đêm',22)]
        new_list= map(lambda i:abs(now_hour-i[1]),alist)
        index =  new_list.index(min (new_list))
        buoi_ca = alist[index][0]
        if gio_bat_dau_vn_return:
            return buoi_ca,now_vn_datetime
        else:
            return buoi_ca
    def gio_bat_dau_defaut_or_ket_thuc_(self,is_tinh_gio_bat_dau_or_ket_thuc = 'gio_bat_dau'):#dd/mm/Y 14:00:00
        adict = {u'Sáng':'sang',u'Chiều':'chieu',u'Đêm':'dem'}
        buoi_ca,now_vn_datetime =  self.buoi_ca_now_default_(gio_bat_dau_vn_return = True)
        ca_x_bat_dau_key = 'ca_' + adict[buoi_ca] + '_bat_dau'
        get_ca_x_bat_dau_from_congty = getattr(self.env.user.cty_id,ca_x_bat_dau_key)
        if get_ca_x_bat_dau_from_congty==False:
            return datetime.datetime.now()
        x =  now_vn_datetime.strftime('%d-%m-%Y')
        x = x + ' ' +get_ca_x_bat_dau_from_congty
        native_ca_gio_in_vn  = datetime.datetime.strptime(x,'%d-%m-%Y %H:%M:%S')
        gio_bat_dau_in_utc = convert_vn_datetime_to_utc_datetime(native_ca_gio_in_vn)
        if is_tinh_gio_bat_dau_or_ket_thuc == 'gio_bat_dau':
            return gio_bat_dau_in_utc   
        else:
            ca_x_duration_key = 'ca_' + adict[buoi_ca] + '_duration'
            duration_hours = getattr(self.env.user.cty_id,ca_x_duration_key)
            if duration_hours:
                gio_ket_thuc_utc = gio_bat_dau_in_utc + datetime.timedelta(hours=duration_hours,seconds=-1)
                return gio_ket_thuc_utc
            else:
                return False
    @api.model
    def default_get(self, fields):
        res = super(CaTruc, self).default_get(fields)
        adict = {'cvi_ids':{'model':'cvi','add_domain':[('ctr_ids','!=',False)]},
                 'su_co_ids':{'model':'suco','add_domain':[('ctr_ids','!=',False)]},
                 'su_vu_ids':{'model':'suvu','add_domain':[('ctr_ids','!=',False)]}
              
                 }
        #def afunc(atuple):
        for field,attr_field_dict in adict.items():
            model = attr_field_dict['model']
            domain = [('gio_ket_thuc','=',False)]
            if 'add_domain' in attr_field_dict:
                domain.extend(attr_field_dict['add_domain'])
            empty_ket_thuc_comments = self.env[ model].search(domain)
            if empty_ket_thuc_comments:
                res[field] = empty_ket_thuc_comments.mapped('id')
        res['member_ids']  = [self.env.user.id]
        return res           
#     @api.depends('create_uid')
#     def cong_ty_(self):
#         for r in self:
#             r.cty_id = r.create_uid.cty_id
            
########################SỰ CỐ####################
#SUCO_SUVU_LIST = ('su_co',u'Sự Cố'),('su_vu',u'Sự Vụ')
SUCO_SUVU_DICT = {'su_co':u'Sự Cố','su_vu':u'Sự Vụ'}

class LTKSetting(models.TransientModel):
    _name = 'ltk.config.settings'
    _inherit = 'res.config.settings'
    
    allow_edit_time = fields.Integer(string = u'Thời gian cho phép để sửa record (giây)',default=20)
    group_time_allow_field_edit_group = fields.Selection([
        (0, u'Không gán cho nhân viên quyền cho sửa fields'),
        (1, u'Gán cho nhân viên quyền cho sửa fields')
        ], u"Gán quyền sửa fields cho nhân viên", implied_group='dai_tgg.time_allow_field_edit_group')
    is_cam_sua_do_time  =fields.Boolean(string=u'Có cấm sửa do quá thời gian?')
    is_cam_sua_truoc_ngay =fields.Boolean(string=u'Có cấm sửa trước ngày?')
    cam_sua_truoc_ngay = fields.Date(string=u'Cấm sửa trước ngày')
    
    @api.multi
    def set_is_cam_sua_truoc_ngay(self):
        self.env['ir.values'].sudo().set_default(
            'ltk.config.settings', 'is_cam_sua_truoc_ngay', self.is_cam_sua_truoc_ngay)
        self.env['ir.values'].sudo().set_default(
            'ltk.config.settings', 'cam_sua_truoc_ngay', self.cam_sua_truoc_ngay)
    @api.multi
    def set_deposit_product_id_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'ltk.config.settings', 'allow_edit_time', self.allow_edit_time)
    @api.multi
    def set_is_cam_sua_do_time(self):
        return self.env['ir.values'].sudo().set_default(
            'ltk.config.settings', 'is_cam_sua_do_time', self.is_cam_sua_do_time)
class CamSua(models.Model):
    _name = 'camsua'
    _auto = False
    cam_sua = fields.Boolean(compute='cam_sua_',string=u'cấm sửa')
    cam_sua_do_chot =  fields.Boolean(compute='cam_sua_do_time_')
    cam_sua_do_time =  fields.Boolean(compute='cam_sua_do_time_')
    ly_do_cam_sua_do_time = fields.Char(compute='cam_sua_do_time_')
    cam_sua_do_diff_user =  fields.Boolean(compute='cam_sua_do_diff_user_')
    ly_do_cam_sua_do_diff_user = fields.Char(compute='cam_sua_do_diff_user_')
    is_admin = fields.Boolean(compute='is_admin_')
    ALLOW_WRITE_FIELDS_TIME = ['gio_ket_thuc','comment_ids']
    ALLOW_WRITE_FIELDS_DIFF_USER = ['gio_ket_thuc','comment_ids','percent_diemtt']
    ALLOW_WRITE_FIELDS_CHOT=[]
    IS_CAM_SUA_DO_CHOT = False
    @api.multi
    def unlink(self):
        for r in self:
            if r.cam_sua:
                raise UserError(u'Không được delete  do  qua thời gian qui định hoặc bạn ko phải là chủ thread')
        res = super(CamSua, self).unlink()
        return res
    @api.multi
    def is_admin_(self):
        for r in self:
            if self.user_has_groups('base.group_erp_manager'):
                r.is_admin = True
    @api.multi
    def cam_sua_(self):
        for r in self:
            r.cam_sua = r.cam_sua_do_time or r.cam_sua_do_diff_user
        
#     @api.model
#     def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
#         res =  super(CamSua, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         fields = res.get('fields')
#         #print 'res',res
#         if view_type=='form':
#             for field in fields:
#                 if field in ['cam_sua','cam_sua_do_time','cam_sua_do_diff_user']:#.ALLOW_WRITE_FIELDS_TIME:
#                     #print 'field name',field
#     #                 fields[field]['invisible'] = "1"
#     #                 fields[field]['string'] = 'ccc'
#                     doc = etree.XML(res['arch'])
#                     node = doc.xpath("//field[@name='%s']"%field)[0]
#                     node.set('invisible', '1')
#         return res
#  
#     @api.multi
#     def is_user_in_edit_group_(self):
#         for r in self:
#             r.is_user_in_edit_group = self.user_has_groups('dai_tgg.time_allow_field_edit_group') or self.user_has_groups('base.group_erp_manager')
    @api.multi
    def cam_sua_do_time_(self):
        for r in self:
            if not r.id:
                r.ly_do_cam_sua_do_time = u'Không cấm sửa do new'
                r.cam_sua_do_time = False
            if self.user_has_groups('dai_tgg.time_allow_field_edit_group') or self.user_has_groups('base.group_erp_manager'):
                r.ly_do_cam_sua_do_time = u'Không cấm sửa do nằm trong group hoặc edmin'
                r.cam_sua_do_time = False
            elif self.env['ir.values'].get_default('ltk.config.settings', 'is_cam_sua_truoc_ngay'):
                cam_sua_truoc_ngay = self.env['ir.values'].get_default('ltk.config.settings', 'cam_sua_truoc_ngay')
                if fields.Date.from_string(r.ngay_bat_dau) < fields.Date.from_string(cam_sua_truoc_ngay):
                    r.cam_sua_do_time = True
                    r.ly_do_cam_sua_do_time = u'cấm sửa do trước ngày'
                    r.cam_sua_do_chot = True
            elif not self.env['ir.values'].get_default('ltk.config.settings', 'is_cam_sua_do_time'):
                r.ly_do_cam_sua_do_time = u'Không cấm sửa do is_cam_sua_do_time = False'
           
            else:
                TIME_ALLOW_SECONDS = self.env['ir.values'].get_default('ltk.config.settings', 'allow_edit_time')
                cam_sua = het_time(r,TIME_ALLOW_SECONDS)
                r.cam_sua_do_time =  cam_sua
                if cam_sua:
                    r.ly_do_cam_sua_do_time = u'cấm sửa do hết thời gian' 
                else:
                    r.ly_do_cam_sua_do_time = u'Không cấm sửa do chưa hết thời gian' 
    @api.multi
    def cam_sua_do_diff_user_(self):
        for r in self:
            if not r.id:
                r.ly_do_cam_sua_do_diff_user = u'Ko Cấm do new'
            elif self.user_has_groups('base.group_erp_manager'):
                r.ly_do_cam_sua_do_diff_user = u'Ko Cấm do user là admin'
                cam_sua =  False
            else:
                cam_sua = r.create_uid != self.env.user
                if cam_sua:
                    r.ly_do_cam_sua_do_diff_user = u'Cấm do khác user'
                else:
                    r.ly_do_cam_sua_do_diff_user = u'Không cấm do cùng User'
            r.cam_sua_do_diff_user =  cam_sua
    @api.multi
    def write(self,vals):
#         #print 'vals  cam_sua',vals
#         #print '**self._name',self._name
#         for r in self:
# #             if r.cam_sua and not  (key in self.ALLOW_WRITE_FIELDS for key in vals) :
# #                 raise UserError(u'Cấm sửa do: ' + r.ly_do_cam_sua_do_time )
#             if r.cam_sua_do_time and not  all(key in self.ALLOW_WRITE_FIELDS_TIME for key in vals) :
#                 raise UserError(u'Cấm sửa do time: ' + r.ly_do_cam_sua_do_time)
#             if r.cam_sua_do_diff_user and not  all(key in self.ALLOW_WRITE_FIELDS_DIFF_USER for key in vals) :
#                 raise UserError(u'Cấm sửa do diff user' )
#             if r.IS_CAM_SUA_DO_CHOT and r.cam_sua_do_chot and not  all(key in self.ALLOW_WRITE_FIELDS_CHOT for key in vals):
#                 raise UserError(u'Cấm sửa do Chốt' )
        res = super(CamSua,self).write(vals)
        return res

class SuCoSuVu(models.Model):
    _name = 'sucosuvu'   
    _auto = False
    name = fields.Char(compute='name_',store=True)
    ngay_bat_dau =  fields.Date(compute='ngay_bat_dau_',store=True,string=u'Ngày')
    gio_bat_dau = fields.Datetime(u'Giờ bắt đầu ', default=fields.Datetime.now)
    gio_ket_thuc = fields.Datetime(u'Giờ Kết Thúc')
    duration = fields.Float(digits=(6, 1), help='Duration in Hours',compute = '_get_duration', store = True,string=u'Thời lượng (giờ)')
    noi_dung = fields.Text(string=u'Nội dung') 
    ctr_ids  = fields.Many2many('ctr',string=u'Ca Trực',required=True)
    file_ids = fields.Many2many('dai_tgg.file',string=u'Files đính kèm')
    cty_id = fields.Many2one('congty',string=u'Đơn vị',default=lambda self:self.env.user.cty_id.id, readonly=True,required=True)
    cty_ids = fields.Many2many('congty',string=u'Đơn vị Liên quan', default=lambda self: [self.env.user.cty_id.id],required=True)
    doitac_ids = fields.Many2many('doitac',string=u'Đối Tác')
#     cam_sua = fields.Boolean(compute='cam_sua_')
#     is_user_in_edit_group = fields.Boolean(compute='is_user_in_edit_group_')
#     def is_user_in_edit_group_(self):
#         for r in self:
#             r.is_user_in_edit_group = self.user_has_groups('base.group_erp_manager')
#     def cam_sua_(self):
#         for r in self:
#             if self.user_has_groups('base.group_erp_manager') or r.admin_cho_sua:
#                 r.cam_sua =  False
#             else:
#                 TIME_ALLOW_SECONDS = 20
#                 TIME_ALLOW = datetime.timedelta(seconds=TIME_ALLOW_SECONDS)
#                 r.cam_sua = het_time(r,TIME_ALLOW)
                
#     def het_time_sua_(self):
#         TIME_ALLOW_SECONDS=20
#         het_time_sua_compute(self,TIME_ALLOW_SECONDS)
    @api.depends('gio_bat_dau')
    def ngay_bat_dau_(self):#trong su kien
        for r in self:
            if r.gio_bat_dau:
                gio_bat_dau_vn = convert_odoo_datetime_to_vn_datetime(r.gio_bat_dau)
                r.ngay_bat_dau = gio_bat_dau_vn.date()
    @api.depends('noi_dung')
    def name_(self,su_co_hay_su_vu=u'Sự Cố'):
        for r in self:
            name  = name_compute(r,adict=[
                                            #('type_su_co_or_su_vu',{'fnc':lambda su_co:SUCO_SUVU_DICT[su_co]}),
                                            ('id',{'pr':u'%s, id'%su_co_hay_su_vu}),
                                           # ('loai_su_co_id',{'pr':u'Loại','fnc':lambda r: r.name,'skip_if_False':True}),
                                          #('noi_dung',{'pr':u'Nội dung'}),
                                          ])
            r.name = name
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
                hour = secs / 3600
                r.duration = hour    
class LoaiSuCo(models.Model):
    _name= 'loaisuco'
    name = fields.Char()


                
class SuCo(models.Model):
    _name = 'suco'   
    _auto = True
    _inherit = ['sucosuvu','camsua']
    loai_su_co_id = fields.Many2one('loaisuco',string=u'Loại Sự Cố')
    comment_ids = fields.One2many('comment','su_co_id',string=u'Comments/Ghi Chú')
#     @api.model
#     def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
#         result = super(SuCo, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         if view_type =='form':
#             fields = result.get('fields')
# #             result['fields']['line_ids']['views']['tree']['fields']['tax_line_id']['domain'] = [('tag_ids', 'in', [self.env.ref(self._context.get('vat_domain')).id])]
# #             fields['loai_su_co_id']['string'] =u'anh con no'# ['|',('ctr_ids','=','active_id'),'&',('ctr_ids','!=',False),('gio_ket_thuc','=',False)]
# #             fields['loai_su_co_id']['domain'] ='''[('name','!=','Đứt FO')]'''
#             doc = etree.XML(result['arch'])
#             node = doc.xpath("//field[@name='noi_dung']")[0]
# #             node.set('invisible', '1')
#             node.set('attrs', "{'invisible':[('loai_su_co_id','!=',False)]}")
# 
#             result['arch'] = etree.tostring(doc)
#         return result
    @api.multi
    def write(self, vals):
        res = super(SuCo,self).write(vals)
        return res
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        active_ctr_id = context.get('active_ctr_id',False)
        if active_ctr_id != False:
            new_args = ['|',('ctr_ids','=',active_ctr_id)]
            new_args.extend(args)
            args = new_args
        return super(SuCo, self).search(args, offset, limit, order, count=count)
   
class LoaiSuVu(models.Model):
    _name= 'loaisuvu'
    name = fields.Char()
class SuVu(models.Model):
    _name='suvu'
    _auto = True
    _inherit = ['sucosuvu','camsua']
    loai_su_vu_id = fields.Many2one('loaisuvu',string=u'Loại Sự Vụ')
    comment_ids = fields.One2many('comment','su_vu_id',string=u'Comments/Ghi Chú')
    noi_dung = fields.Char()
#     field_1 = fields.Char(compute='field_1_',store=True)
#     field_2 = fields.Char(compute='field_2_',store=True)
#     field_3 = fields.Char(compute='field_3_',store=True)
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        active_ctr_id = context.get('active_ctr_id',False)
        if active_ctr_id != False:
            new_args = ['|',('ctr_ids','=',active_ctr_id)]
            new_args.extend(args)
            args = new_args
        return super(SuVu, self).search(args, offset, limit, order, count=count)
    
    @api.multi
    def write(self,vals):
        res = super(SuVu,self).write(vals)
        return res
    def name_(self):
        super(SuVu, self).name_(su_co_hay_su_vu=u'Sự Vụ')

class Comment(models.Model):
    _name = 'comment'
    name = fields.Char(compute='name_',store=True)
    noi_dung = fields.Text(string=u'Nội dung comment')
    cvi_id = fields.Many2one('cvi')
    su_co_id = fields.Many2one('suco')
    su_vu_id = fields.Many2one('suvu')
    file_ids = fields.Many2many('dai_tgg.file','comment_file_relate','comment_id','file_id',string=u'Files đính kèm')
    doitac_ids = fields.Many2many('doitac',string=u'Đối Tác')
    @api.depends('noi_dung','create_uid','create_date')
    def name_(self):
        def noi_dung_trim(noi_dung):
            if noi_dung:
                if len(noi_dung) > 10:
                    name = noi_dung[:10] + u'...'
                    return name
                else:
                    return noi_dung
        
        for r in self:
            name = name_compute(r, adict=[
                ('noi_dung',{'fnc':noi_dung_trim,'skip_if_False':True}),
                ('create_uid',{'pr':u'Người comment','skip_if_False':True,'fnc': lambda u:u.name}),
                ('create_date',{'fnc':convert_odoo_datetime_to_vn_str,'skip_if_False':True}),
                ] )
            r.name = name
            
class DoiTac(models.Model):
    _name = 'doitac'
    name = fields.Char(string=u'Tên đối tác')
    cty_id = fields.Many2one('congty',string=u'Đơn vị')
    chuc_vu = fields.Char(string=u'Chức vụ')
class User(models.Model):
    _inherit = 'res.users'
    ctr_ids = fields.Many2many('ctr', 'ctr_res_users_rel_d4','res_users_id','ctr_id',string=u'Các ca đã trực')
    cty_id = fields.Many2one('congty',string=u'Đơn vị')
    cac_sep_ids = fields.Many2many('res.users','user_sep_relate','user_id','sep_id', string=u'Các Lãnh Đạo')
    cac_linh_ids = fields.Many2many('res.users','user_sep_relate','sep_id', 'user_id',string=u'Các Nhân Viên')
#     is_admin = fields.Boolean(compute='is_admin_',store=True)
#     @api.multi
#     def is_admin_(self):
#         for r in self:
#             if self.user_has_groups('base.group_erp_manager'):
#                 r.is_admin = True
#             else:
#                 r.is_admin = False
        
class CongTy(models.Model):
    _name = 'congty'
    _parent_name = 'parent_id'
    name=fields.Char()
    parent_id = fields.Many2one('congty',string=u'Đơn vị Cha')
    child_ids = fields.One2many('congty', 'parent_id', string=u'Các đơn vị con')
    cong_ty_type = fields.Many2one('congtytype', string=u'Loại đơn vị')
    ca_sang_bat_dau = fields.Char(default=u'07:00:00')
    ca_chieu_bat_dau = fields.Char(default=u'14:00:00')
    ca_dem_bat_dau = fields.Char(default=u'22:30:00')
    ca_sang_duration = fields.Float(digits=(6,1),default=7)
    ca_chieu_duration = fields.Float(digits=(6,1),default=8.5)
    ca_dem_duration = fields.Float(digits=(6,1),default=8.5)
    nhan_vien_ids = fields.One2many('res.users','cty_id')
    @api.constrains('parent_id')
    def _check_category_recursion_check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('Error ! You cannot create recursive categories.'))
        return True
    @api.multi
    def name_get(self):
        def get_names(cat):
            ''' Return the list [cat.name, cat.parent_id.name, ...] '''
            res = []
            if cat.name != False:
                while cat:
                        res.append(cat.name)
                        cat = cat.parent_id
            return res
        return [(cat.id, ' / '.join(reversed(get_names(cat)))) for cat in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symetric to name_get
            category_names = name.split(' / ')
            parents = list(category_names)
            child = parents.pop()
            domain = [('name', operator, child)]
            if parents:
                names_ids = self.name_search(' / '.join(parents), args=args, operator='ilike', limit=limit)
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([('id', 'not in', category_ids)])
                    domain = expression.OR([[('parent_id', 'in', categories.ids)], domain])
                else:
                    domain = expression.AND([[('parent_id', 'in', category_ids)], domain])
                for i in range(1, len(category_names)):
                    domain = [[('name', operator, ' / '.join(category_names[-1 - i:]))], domain]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(expression.AND([domain, args]), limit=limit)
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()
class CongTyType(models.Model):
    _name = 'congtytype'
    name = fields.Char()   
    
###################### END CA TRỰC #################3
############FILE###########
class File(models.Model):
    _name = 'dai_tgg.file'
    name = fields.Char(string=u'File name')
    file = fields.Binary( attachment=True)
    mo_ta = fields.Text(string=u'Mô tả file')
#     cvi_id = fields.Many2one('cvi')
########END FILE############

###############  CÔNG VIỆC ###############

def het_time(r,TIME_ALLOW_SECONDS):
    TIME_ALLOW = datetime.timedelta(seconds=TIME_ALLOW_SECONDS)
    create_date =  fields.Datetime.from_string(r.create_date)
    delta_time =  datetime.datetime.now() - create_date
    return  delta_time>TIME_ALLOW


class Cvi(models.Model):
    _name = 'cvi'
    _parent_name = 'gd_parent_id'
    _inherit = ['camsua']
    _auto = True
    ALLOW_WRITE_FIELDS_TIME = ['gio_ket_thuc','comment_ids','cd_children_ids','gd_children_ids','percent_diemtt']
    ALLOW_WRITE_FIELDS_CHOT = ['gio_ket_thuc','comment_ids','cd_children_ids','gd_children_ids',]
    ALLOW_WRITE_FIELDS_DIFF_USER = ['gio_ket_thuc','comment_ids','cd_children_ids','gd_children_ids','percent_diemtc']
    IS_CAM_SUA_DO_CHOT = True
    name = fields.Char(compute='name_',store=True)
    ngay_bat_dau =  fields.Date(compute='ngay_bat_dau_',store=True,string=u'Ngày')
    gio_bat_dau = fields.Datetime(string=u'Giờ bắt đầu ', default=fields.Datetime.now)
    gio_ket_thuc = fields.Datetime(string=u'Giờ Kết Thúc')
    duration = fields.Float(digits=(6, 1), help='Duration in Hours',compute = '_get_duration', store = True,string=u'Thời lượng (giờ)')
    user_id = fields.Many2one('res.users',default =  lambda self: self.env.uid, string=u'Nhân viên tạo')   
#     cty_id = fields.Many2one('congty',string=u'Đơn vị tạo',default=lambda self:self.env.user.cty_id, readonly=True,required=True)
    cty_id = fields.Many2one('congty',string=u'Đơn vị tạo',compute='cty_id_',store=True)
    tvcv_id = fields.Many2one('tvcv', string=u'Thư Viện Công việc')
    
    diem_tvi = fields.Float(digits=(6,2),string=u'Điểm Thư Viện',related='tvcv_id.diem',store=True,readonly=True)# 
#     don_vi = fields.Many2one('donvi',related='tvcv_id.don_vi',string=u'Đơn vị tính',readonly=True)
#     diem_tv = fields.Float(digits=(6,2),string=u'Điểm Thư Viện',compute='diem_tv_',store=True)# 
    don_vi = fields.Many2one('donvi',string=u'Đơn vị tính',compute='don_vi_',store=True)
    ctr_ids  = fields.Many2many('ctr','ctr_cvi_relate','cvi_id','ctr_id',string=u'Ca Trực')
    so_luong = fields.Integer(string=u'Số Lượng',default = 1,required=True)
    so_lan = fields.Integer(string=u'Số Lần',default = 1,required=True)
    noi_dung = fields.Text(string=u'Nội dung') 
    noi_dung_trich_dan = fields.Char(compute='noi_dung_trich_dan_',store=True)
    comment_ids = fields.One2many('comment','cvi_id',string=u'Comments/Ghi Chú')
    gd_parent_id = fields.Many2one('cvi',string=u'Công Việc Giai Đoạn Cha',ondelete='cascade')
    gd_children_ids = fields.One2many('cvi','gd_parent_id',string=u'Các CV Giai Đoạn Con')
    cd_parent_id = fields.Many2one('cvi',string=u'Công Việc Chia Điểm Cha',ondelete='cascade')# ondelete='restrict' #ondelete='cascade', ondelete='set null'
    cd_children_ids = fields.One2many('cvi','cd_parent_id',string=u'Các CV Chia Điểm Con')
    diem_goc = fields.Float(digits=(6,2),string=u'Điểm Góc',compute='diem_goc_',store=True)# 
    diemtt = fields.Float(digits=(6,2),store=True,compute = 'diemtt_',string=u'Điểm Tự Tính')
    percent_diemtt = fields.Integer(default=100,string=u'Điểm Tự Chấm/Điểm Tự Tính(%)')
    diemtc = fields.Float(digits=(6,2),compute='diemtc_',string=u'Điểm Tự Chấm',store=True)
    diem_remain_gd = fields.Float(compute='diem_remain_gd_',string=u'Điểm còn lại của giai đoạn con',store=True)
    slncl = fields.Integer(compute='slncl_',store=True,string=u'Số lượng người cùng làm')
    percent_diemtc = fields.Integer(default=100,string=u'Điểm LĐ/Điểm Tự Chấm (%)')
    diemld = fields.Float(digits=(6,2),compute='diemld_',string=u'Điểm Lãnh Đạo Chấm',store=True)
    valid_diemtc = fields.Boolean(compute='valid_diemtc_', string=u'Valid Điểm Tự Chấm',store=True)#
    loai_cvi = fields.Selection([(u'Single',u'Công Việc Đơn'),(u'Chia Điểm Cha',u'Chia Điểm Cha'),
                                       (u'Chia Điểm Con',u'Chia Điểm Con'),(u'Giai Đoạn Cha',u'Giai Đoạn Cha'),
                                       (u'Giai Đoạn Con',u'Giai Đoạn Con'),
                                       (u'Giai Đoạn Con và Chia Điểm Cha',u'Giai Đoạn Con và Chia Điểm Cha'),
                                       (u'Giai Đoạn Con và Giai Đoạn Cha',u'Giai Đoạn Con và Giai Đoạn Cha')
                                        ],compute='valid_diemtc_',store=True,string=u'Loại công việc')
    valid_cd = fields.Boolean(compute='valid_cd_',store=True)    
    valid_gd = fields.Boolean(compute='valid_gd_',store=True)  
    valid_diemtc_conclusion = fields.Selection([(u'Chia điểm không đủ 100%',u'Chia điểm không đủ 100%'),
                                  (u'Thiếu giai đoạn con',u'Thiếu giai đoạn con'),
                                  (u'Thiếu giai đoạn',u'Thiếu giai đoạn'),
                                  (u'Thiếu giai đoạn và Chia điểm không đủ 100%',u'Thiếu giai đoạn và Chia điểm không đủ 100%'),
                                  (u'Kiểm tra điểm OK',u'Kiểm tra điểm OK'),         
                                                           ],compute='valid_diemtc_',store=True,string=u'Kết luận Valid')
    file_ids = fields.Many2many('dai_tgg.file','cvi_file_relate','cvi_id','file_id',string=u'Files đính kèm')
    doitac_ids = fields.Many2many('doitac',string=u'Đối Tác')
    cty_ids = fields.Many2many('congty',string=u'Đơn vị liên quan',default=lambda self:[self.env.user.cty_id.id],required=True)
    #MIDLE FIELD , Trung gian
    len_gd_child = fields.Integer(compute='len_gd_child_',store=True)
    sum_gd_con = fields.Float(digits=(6,2),compute='sum_gd_con_',store=True)
    sum_cd_con = fields.Float(digits=(6,2),compute='sum_cd_con_',store=True)

    #compute field
    is_sep = fields.Boolean(compute='is_sep_')
    is_has_tvcv_con = fields.Boolean(compute='is_has_tvcv_con_')
    thu_vien_da_chon_list = fields.Char(compute='thu_vien_da_chon_list_')   
 
    @api.depends('user_id','create_uid')
    def cty_id_(self):
        for r in self:
            if r.user_id:
                r.cty_id = r.user_id.cty_id
            else:
                r.cty_id = r.create_uid.cty_id
 
    @api.multi
    def cam_sua_do_diff_user_(self):
        for r in self:
            if not r.id:
                r.ly_do_cam_sua_do_diff_user = u'Ko Cấm do new'
                cam_sua =  False
            elif self.user_has_groups('base.group_erp_manager'):
                r.ly_do_cam_sua_do_diff_user = u'Ko Cấm do user là admin'
                cam_sua =  False
            else:
#                 cam_sua = r.create_uid != self.env.user and  r.user_id != self.env.user
                if r.user_id:
                    if r.user_id != self.env.user:
                        TIME_ALLOW_SECONDS =200
                        if r.create_uid == self.env.user:# and not het_time(r,TIME_ALLOW_SECONDS):
                            cam_sua = False
                        else:
                            cam_sua = True
                    else:
                        cam_sua = False
                else:# giai doan cha
                    cam_sua = r.create_uid != self.env.user
                
                if cam_sua:
                    r.ly_do_cam_sua_do_diff_user = u'Cấm do khác user'
                else:
                    r.ly_do_cam_sua_do_diff_user = u'Không cấm do cùng User'
            r.cam_sua_do_diff_user =  cam_sua
            
    @api.depends('tvcv_id.don_vi')
    def don_vi_(self):
        for r in self:
            r.don_vi = r.tvcv_id.don_vi
    @api.onchange('gd_children_ids')
    def thu_vien_da_chon_list_(self):
        for r in self:
            if r.gd_children_ids:
                r.thu_vien_da_chon_list = r.gd_children_ids.mapped('tvcv_id.id')
            
    
    @api.depends('tvcv_id')
    def is_has_tvcv_con_(self):
        for r in self:
            if r.tvcv_id:
                r.is_has_tvcv_con = r.tvcv_id.is_has_children
    @api.multi
    def is_sep_(self):
        for r in self:
            if self.env.uid in r.user_id.cac_sep_ids.mapped('id') +  r.user_id.cac_sep_ids.cac_sep_ids.mapped('id'):
                r.is_sep = True
            else:
                r.is_sep = False
    ################# DEPEND##########################
    @api.depends('noi_dung')
    def noi_dung_trich_dan_(self):
        for r in self:
            if r.noi_dung and len(r.noi_dung) > 30:
                r.noi_dung_trich_dan = r.noi_dung[:30] + u'...'
    
    
    @api.depends(
                'cd_children_ids',# dành cho CHIA ĐIỂM CHA
                'cd_parent_id.cd_children_ids', # Trigger cho slncl CHIA ĐIỂM CON
                'len_gd_child',#moi add
                )      # khi form thay đổi bất cứ field nào thì chắc chắn cd_children_ids thay đổi vì ta sẽ luôn thay nó trong hàm write()
    def slncl_(self):
        for r in self:
            if r.cd_children_ids:
                r.slncl = len(r.cd_children_ids) + 1
            elif r.cd_parent_id:#CHIA ĐIỂM CON
                r.slncl = len(r.cd_parent_id.cd_children_ids) + 1
#                 #print u'222CD_CON  Ở SLNCL  CON^  id:%s,r.slncl:%s  ,r.cd_parent_id.cd_children_ids:%s 222'%(r.id,r.slncl,r.cd_parent_id.cd_children_ids)
            elif r.gd_children_ids:
                r.slncl=0
            else:
                r.slncl = 1
                
    @api.depends('gd_children_ids')
    def len_gd_child_(self):
        for r in self:
            r.len_gd_child = len(r.gd_children_ids)
    @api.depends('tvcv_id.diem','so_luong','so_lan','len_gd_child')
    def diem_remain_gd_(self):
        for r in self:
            if r.len_gd_child:
#                 r.diem_remain_gd = self.diem_remain_gd_compute(r)
                all_but_not_con_lai_s = r.gd_children_ids.filtered(lambda r: r.tvcv_id.id != self.env.ref('dai_tgg.loaisuvu_viec_con_lai').id)
                all_but_not_con_lai_diem = map(lambda r: r.so_luong *r.so_lan * r.tvcv_id.diem,all_but_not_con_lai_s)
                diem_remain_gd =r.tvcv_id.diem*r.so_luong *r.so_lan -  sum(all_but_not_con_lai_diem)
                sai_so = 0.005* r.so_luong *r.so_lan*len(all_but_not_con_lai_diem)
                if abs(diem_remain_gd) < sai_so:
                    diem_remain_gd = 0
                r.diem_remain_gd = diem_remain_gd
 
    @api.depends('so_luong','so_lan', 'tvcv_id.diem','gd_parent_id.diem_remain_gd')
    def diem_goc_(self):
        for r in self:
            if r.gd_parent_id: #GD CON
                if  r.tvcv_id.id == self.env.ref('dai_tgg.loaisuvu_viec_con_lai').id:
                    diem_remain_gd = r.gd_parent_id.diem_remain_gd
                    r.diem_goc = diem_remain_gd
                else:
                    r.diem_goc = r.so_luong * r.so_lan * r.tvcv_id.diem
            elif r.cd_parent_id:#Điểm góc CHIA ĐIỂM CON
                r.diem_goc = 0#r.cd_parent_id.tvcv_id.diem *r.cd_parent_id.so_luong /r.slncl                #r.diem_goc = r.cd_parent_id.diem_goc/r.cd_parent_id.slncl
            else:
                r.diem_goc = r.so_luong * r.so_lan * r.tvcv_id.diem
     
    @api.depends( 'slncl', 'diem_goc','cd_parent_id.diem_goc','len_gd_child')
    def diemtt_(self):
        for r in self:
                if r.cd_parent_id:#cv chia diem con
                    r.diemtt = r.cd_parent_id.diem_goc/r.slncl
                elif r.slncl > 1:#CD Cha
                    r.diemtt = r.diem_goc/r.slncl
                elif r.len_gd_child:  #giai doan cha
                    r.diemtt =0
                    r.user_id = False
                else: 
                    r.diemtt = r.diem_goc           
    @api.depends('diemtt','percent_diemtt')           
    def diemtc_(self):
        for r in self:
            r.diemtc = r.diemtt * r.percent_diemtt/100
    
    @api.depends('percent_diemtt','slncl','cd_children_ids.percent_diemtt')
    def sum_cd_con_(self):
        for r in self:
            if r.slncl > 1:
                sum_phan_tram = r.percent_diemtt + sum(r.cd_children_ids.mapped('percent_diemtt'))
                r.sum_cd_con =sum_phan_tram
    def valid_cd_chung_cha_con(self,r):
        if r.sum_cd_con == 100*r.slncl:
            valid_cd = True
        else:
            valid_cd = False
        return valid_cd
    
    @api.depends('sum_cd_con','cd_parent_id.sum_cd_con')
    def valid_cd_(self):
        for r in self:
            if r.cd_parent_id:
                r.valid_cd = self.valid_cd_chung_cha_con(r.cd_parent_id)
            elif r.slncl > 1:
                r.valid_cd = self.valid_cd_chung_cha_con(r)
    #test git    
                
    @api.depends('diem_goc','len_gd_child','gd_children_ids.diem_goc')
    def sum_gd_con_(self):
        for r in self:
            if r.len_gd_child :
                r.sum_gd_con = sum(r.gd_children_ids.mapped('diem_goc'))
    
    def valid_gd_chung_cha_con(self,r):
        sai_so = abs(r.sum_gd_con - r.diem_goc )
        #sai_so_cua_tv = 0.0005
#         sai_so_cua_diem_goc_cha = 0.005
#         sai_so_diem_goc_moi_con = 0.0005*r.so_luong + 0.005
#         sai_so_cua_sum = (0.0005*r.so_luong + 0.005)*r.len_gd_child + 0.005
        sai_so_lon_nhat = 0.005*r.len_gd_child*r.so_luong*r.so_lan
        if  sai_so <= sai_so_lon_nhat:
            valid_gd = True
        else:
            valid_gd = False
        return valid_gd
    
    @api.depends('diem_goc',
                        'sum_gd_con',
                         'gd_parent_id.sum_gd_con'
                 )
    def valid_gd_(self):
        for r in self:
            if r.gd_parent_id:
                r.valid_gd = self.valid_gd_chung_cha_con(r.gd_parent_id)
            elif r.len_gd_child:
                r.valid_gd = self.valid_gd_chung_cha_con(r)
                #print '11-11 GD_Cha %s - r.valid giai doan %s ' %(r.id,r.valid_gd )
            #print '11-11 After  valid_cd %s' %r.id

    @api.depends('valid_gd','valid_cd')
    def valid_diemtc_(self):
        for r in self:
            #Chia điểm con
            if not r.id:
                pass
            else:
                if r.gd_parent_id and r.slncl> 1:
                    r.loai_cvi = u'Giai Đoạn Con và Chia Điểm Cha'
                    r.valid_diemtc = r.valid_gd &  r.valid_cd
                    if not r.valid_gd and not r.valid_cd:
                        r.valid_diemtc_conclusion = u'Thiếu giai đoạn và Chia điểm không đủ 100%'
                    elif not r.valid_gd:
                        r.valid_diemtc_conclusion =  u'Thiếu giai đoạn'
                    elif not r.valid_cd:
                        r.valid_diemtc_conclusion =  u'Chia điểm không đủ 100%'
                elif r.cd_parent_id:# CD CON
                    r.loai_cvi = u'Chia Điểm Con'
                    r.valid_diemtc = r.valid_cd
                    if not r.valid_diemtc:
                        r.valid_diemtc_conclusion =  u'Chia điểm không đủ 100%'
                elif  r.slncl > 1: # CD CHA
                    r.loai_cvi =u'Chia Điểm Cha'
                    r.valid_diemtc = r.valid_cd
                    if not r.valid_diemtc:
                        r.valid_diemtc_conclusion =  u'Chia điểm không đủ 100%'
                elif r.len_gd_child: # GD CHA
                    r.loai_cvi =u'Giai Đoạn Cha'
                    r.valid_diemtc = r.valid_gd
                    if not r.valid_diemtc:
                        r.valid_diemtc_conclusion =  u'Thiếu giai đoạn con'
                elif r.gd_parent_id:# GD CON
                    r.loai_cvi =u'Giai Đoạn Con'
                    r.valid_diemtc = r.valid_gd
                    if not r.valid_diemtc:
                        r.valid_diemtc_conclusion =  u'Thiếu giai đoạn'
                else: # SINGLE
                    r.loai_cvi = u'Single'
                    r.valid_diemtc = True
                if r.valid_diemtc ==True:
                    r.valid_diemtc_conclusion = u'Kiểm tra điểm OK'
    @api.depends('percent_diemtc',
                 'diemtc')
    def diemld_(self):
        for r in self:
            r.diemld = r.diemtc * r.percent_diemtc /100
            
    @api.depends('tvcv_id','noi_dung_trich_dan')
    def name_(self):
        for r in self:
            def tvcv_name(r):
                if r:
                    return name_compute(r,adict=[
                                        ('name',{'skip_if_False':False}),
                                        ('code',{'skip_if_False':True,'fnc':lambda name: (u'(%s)'%name) if name else False}),
                                           ],join_char=u' ')
                else:
                    return False
            name  = name_compute(r,adict=[('id',{'pr':u'Công Việc  id'}),
                                          ('tvcv_id',{'pr':u'TVCV','fnc':tvcv_name}),
                                          ('noi_dung_trich_dan',{'pr':u'Nội Dung'}),
                                          ]
                                 )
            r.name = name
            
    @api.depends('gio_bat_dau')
    def ngay_bat_dau_(self):#trong su kien
        for r in self:
            if r.gio_bat_dau:
                r.ngay_bat_dau = convert_odoo_datetime_to_vn_datetime(r.gio_bat_dau).date()
                
    
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
                hour = secs / 3600
                r.duration = hour      
                    
    ###################contrains##############
#     def get_parent_value_for_child2(self,r,update_field_list,cd_parent_id_or_gd_parent_id):
#         print '**1'
#         update_dict = {}
#         for field in update_field_list:
#             parent_id = getattr(r,cd_parent_id_or_gd_parent_id)
#             if not isinstance(field, tuple):
#                 update_dict[field] = getattr(parent_id,field)
#             else:
#                 field_ =  field[0]
#                 func = field[1]['func']
#                 val = getattr(parent_id,field_)
#                 val = func(val)
#                 update_dict[field_] = val
#         print '**end 1'
#         return update_dict
    
    def get_parent_value_for_child(self,r,update_field_list,cd_parent_id_or_gd_parent_id):
        print '**1'
        update_dict = {}
        for field in update_field_list:
            parent_id = getattr(r,cd_parent_id_or_gd_parent_id)
            fields = r._fields
            if fields[field].type=='many2one':
                update_dict[field] = getattr(parent_id,field).id
            elif fields[field].type=='many2many' or fields[field].type=='one2many':
                update_dict[field] =[(6, False,  getattr(parent_id,field).ids)]
            else:
                update_dict[field] =getattr(parent_id,field)
        return update_dict
    
    
#     def update_dict_for_child_when_update_parent2(self,r,update_field_list):
#         print '**2'
#         update_dict = {}
#         write_create_parent_dict = self._context['write_create_parent_dict']
#         for field in update_field_list:
#             if not isinstance(field, tuple) and field in write_create_parent_dict:
#                 update_dict[field] = getattr(r,field)
#             else:
#                 field_ =  field[0]
#                 if field_ in write_create_parent_dict:
#                     func = field[1]['func']
#                     val = getattr(r,field_)
#                     val = func(val)
#                     update_dict[field_] = val
#         print '**end 2'
#         return update_dict
    def update_dict_for_child_when_update_parent(self,r,update_field_list):
        update_dict = {}
        write_create_parent_dict = self._context['write_create_parent_dict']
        fields = r._fields
        for field in update_field_list:
            if field in write_create_parent_dict:
                if fields[field].type=='many2one':
                    update_dict[field] = getattr(r,field).id
                elif fields[field].type=='many2many' or fields[field].type=='one2many':
                    update_dict[field] =[(6, False,  getattr(r,field).ids)]
                else:
                    update_dict[field] =getattr(r,field)
        print '**end 2'
        return update_dict
    @api.constrains('so_luong','so_lan','cty_ids')
    def gd_parent_constrains(self):
        print '**3'
        for r in self:
            if r.gd_children_ids:
#                 {'so_luong':r.gd_parent_id.so_luong,'so_lan':r.gd_parent_id.so_lan})
#                 update_field_list = ['so_luong','so_lan',('cty_ids',{'func':lambda r: [(6, False, r.ids)]})]
                update_field_list = ['so_luong','so_lan','cty_ids']

                update_dict = self.update_dict_for_child_when_update_parent(r,update_field_list)
                for child in r.gd_children_ids:
                    child.write(update_dict)        
        print '**end 3'
    @api.constrains('gd_parent_id') # khi sinh ra
    def gd_children_constrains(self):
        print '**4'
        for r in self:
            if r.gd_parent_id:
                print 'in gd_children_constrains***'
                update_field_list = ['so_luong','so_lan', 'cty_ids']
                update_dict = self.get_parent_value_for_child(r,update_field_list,'gd_parent_id')
                print '***update_dict***',update_dict
                r.write(update_dict)
        print '**end 4'
    
    
    @api.constrains('tvcv_id','so_luong','so_lan','gio_ket_thuc','gio_bat_dau','cty_ids')
    def cd_parent_constrains(self):
        print '**5'
        for r in self:
            if r.cd_children_ids:
                update_field_list = ['tvcv_id','so_luong','gio_ket_thuc','gio_bat_dau','so_lan','cty_ids']
                update_dict_of_child = self.update_dict_for_child_when_update_parent(r,update_field_list)
                for cd_child in r.cd_children_ids:
                    cd_child.write(update_dict_of_child)

        print '**end 5'
    @api.constrains('cd_parent_id')
    def cd_children_constrains(self):
        print '**6'
        for r in self:
            if r.cd_parent_id:
                print 'in cd_children_constrains***'
                update_field_list = ['tvcv_id','so_luong','gio_ket_thuc','gio_bat_dau','so_lan', 'cty_ids']
                update_dict = self.get_parent_value_for_child(r,update_field_list,'cd_parent_id')
                r.write(update_dict)
        print '**end 6'
        
        
    def constrains_cha_con(self,r):    
        viec_con_lai = self.env.ref('dai_tgg.loaisuvu_viec_con_lai')
#         all_childs_exclude_viec_con_lais = r.gd_children_ids.filtered(lambda r: r.tvcv_id !=  viec_con_lai)
        
        check_list = map(lambda i:i.tvcv_id.parent_id !=r.tvcv_id and i.tvcv_id !=viec_con_lai,r.gd_children_ids)
        if any(check_list):
            raise ValidationError(u'Có ít nhất 1 Giai Đoạn Con có thư viện công việc không phải là con của CV Giai Đoạn Cha')
        tvcv_ids = [i.tvcv_id.id for i in  r.gd_children_ids]
        print 'tvcv_ids***',tvcv_ids
        if len(tvcv_ids) != len(set(tvcv_ids)):
            raise ValidationError(u'Giai Đoạn con có duplicate ')
    
#     @api.constrains('tvcv_id')
    @api.constrains('gd_children_ids')
    def check_thu_vien_con_in_gd_childs(self):
        for r in self:
            if r.gd_children_ids:
                self.constrains_cha_con(r)
            elif r.gd_parent_id:
                self.constrains_cha_con(r.gd_parent_id)
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        active_ctr_id = context.get('active_ctr_id',False)
        if active_ctr_id != False:
            new_args = ['|',('ctr_ids','=',active_ctr_id)]
            new_args.extend(args)
            args = new_args
        return super(Cvi, self).search(args, offset, limit, order, count=count)           
                
#                     
#     ################# !END DEPEND##########################
#                
    ################# ONCHANGE##########################

    
    

    ################# !END ONCHANGE##########################
    
    @api.model
    def create(self, vals):
        cv = super(Cvi, self.with_context({'write_create_parent_dict':vals})).create(vals)
        return cv

    @api.multi
    def write(self, vals):
        new_ctx = dict(self._context, **{'write_create_parent_dict':vals})
        
#         if self.cd_children_ids :
#             new_ctx.update({'write_from_parent_id':True})
#         elif self.cd_parent_id:
#             print 'WRITE trong cd CON, vals %s '%vals
        res = super(Cvi, self.with_context(new_ctx)).write(vals)
        return res    
#     @api.multi
#     def unlink(self):
#         for r in self:
#             if r.cam_sua:
#                 raise UserError(u'Không được delete  do  qua thời gian qui định hoặc bạn ko phải  là chủ thread')
#         res = super(Cvi, self).unlink()
#         return res
    ######################SERVER###############
    
    @api.model
    def action_dynamic_domain(self):
        action = self.env.ref('dai_tgg.cvi_action').read()[0]
        domain = ['|',('cty_id','child_of',self.env.user.cty_id.id),('cty_ids','child_of',[self.env.user.cty_id.id])]
        action['domain'] = domain
      
        return action
#    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        # TDE NOTE: WHAAAAT ??? is this because inventory_value is not stored ?
        # TDE FIXME: why not storing the inventory_value field ? company_id is required, stored, and should not create issues
        res = super(Cvi, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for c,r in enumerate(res):
            try:
                user_id_int = r['user_id'][0]
            except KeyError:
                continue
            user_id = self.env['res.users'].browse(user_id_int)
            if self.env.uid not in (user_id.cac_sep_ids.mapped('id') +  user_id.cac_sep_ids.cac_sep_ids.mapped('id')):
                r['diemld']=0
                 
#             #print r
#         if 'inventory_value' in fields:
#             for line in res:
#                 if '__domain' in line:
#                     lines = self.search(line['__domain'])
#                     inv_value = 0.0
#                     for line2 in lines:
#                         inv_value += line2.inventory_value
#                     line['inventory_value'] = inv_value
        return res   



    
     
class LoaiCvi(models.Model):
    _name = 'cvitype'
    name = fields.Char()

class ThuVienCvi(models.Model):
    _name = 'tvcv'
    _parent_name = 'parent_id'
    name = fields.Char(string=u'Tên công việc')
#     len_name = fields.Integer(compute='compute')
    code = fields.Char(string=u'Mã công việc')
    don_vi = fields.Many2one('donvi',string=u'Đơn vị tính')
    do_phuc_tap = fields.Integer(string=u'Độ Phức Tạp')
    thoi_gian_hoan_thanh = fields.Integer(string=u'Thời Gian Hoàn Thành')
    diem = fields.Float(digits=(6, 2),string=u'Điểm',implied_group='base.group_erp_manager')
    dot_xuat_hay_dinh_ky = fields.Many2one('dotxuathaydinhky',string=u'Đột xuất hay định kỳ')
    cong_viec_cate_id = fields.Many2one('tvcvcate',string=u'Phân loại TVCV')
#     diem_percent = fields.Float(digits=(6,2),string=u'Phần trăm điểm so với tvcv cha')
    diem_percent = fields.Integer(string=u'Phần trăm điểm so với TVCV cha')
    is_has_children = fields.Boolean(string=u'Có CV giai đoạn con',compute='is_has_children_',store=True)
    children_ids = fields.One2many('tvcv','parent_id',string=u'Các TVCV Giai Đoạn Con')
    parent_id = fields.Many2one('tvcv',string=u'Công Việc giai đoạn Cha')
    co_cong_viec_cha = fields.Boolean(string=u'Có công việc cha',compute='co_cong_viec_cha_',store=True)
    ghi_chu = fields.Text(u'Ghi Chú')
    valid_thu_vien = fields.Boolean(compute='valid_thu_vien_',store=True,string=u'Valid thư viện')
#     is_active = fields.Boolean(default=True)
    active = fields.Boolean(default=True)
    @api.constrains('diem')
    def parent_diem_change_children_diem(self):
        for r in self:
            if r.children_ids:
                for child in r.children_ids:
                    #print '**parent_diem_change_children_diem child.id ** ',child.id
                    child.diem =  child.diem_percent * r.diem/100
                r.children_ids = r.children_ids.ids
    @api.constrains('diem_percent','parent_id')
    def children_diem_depend_on_diem_percent(self):
        for r in self:
            if r.parent_id:
                if  r.diem_percent > 100:
                    raise UserWarning(u'Phần Trăm Điểm Không thể lớn hơn 100')
                #print 'contrains'
                r.diem = r.diem_percent * r.parent_id.diem/100
                #print 'contrains r.diem = r.diem_percent * r.parent_id.diem/100.0',r.diem,r.diem_percent,r.parent_id.diem/100.0
    @api.model
    def create(self, vals):
        cv = super(ThuVienCvi, self).create(vals)
        return cv
    @api.multi
    def write(self, vals):
        res = super(ThuVienCvi, self).write(vals)
        return res  
#     def test_common(self):
#         #print 'self._context',self._context
    def cha_con_valid(self,cha_object):
            diem_con  = sum(cha_object.children_ids.mapped('diem'))
            diem_cha = cha_object.diem
            if cha_object.diem==0:
                return False
            else:
                if abs(diem_cha - diem_con) <0.005*len(cha_object.children_ids) :
                    return True
                else:
                    return False
    @api.depends('diem',
                        'children_ids',#for parent, thay đổi bất cứ gì trong children_ids
                        'parent_id.diem',
                 )     
    def valid_thu_vien_(self):
        for r in self:
            if r.children_ids:
                r.valid_thu_vien  = self.cha_con_valid(r)
            elif r.parent_id:
                cha_object = r.parent_id
                r.valid_thu_vien  = self.cha_con_valid(cha_object)
            else:
                r.valid_thu_vien = True
            #print 'valid tv ',r.id
    @api.depends('parent_id')
    def co_cong_viec_cha_(self):
        for r in self:
            if r.parent_id:
                r.co_cong_viec_cha = True
            else:
                r.co_cong_viec_cha = False
    @api.constrains('name','parent_id')
    def _check_unique_name_per_prid(self):
        for r in self:
            if r.parent_id.id:
                rs = self.search([('name','=',r.name),('parent_id','=',r.parent_id.id)])
                if len(rs)>1:
                    raise ValidationError(u'không được trùng tên trên mỗi parent_id')
    
    @api.depends('children_ids')
    def is_has_children_(self):
        for r in self:
            r.is_has_children = bool(r.children_ids)
    @api.constrains('parent_id')
    def _check_category_recursion_check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('Error ! You cannot create recursive categories.'))
        return True
    @api.multi
    def name_get(self):
        def get_names(cat):
            ''' Return the list [cat.name, cat.parent_id.name, ...] '''
            res = []
            if cat.name != False:
                while cat:
                        res.append(cat.name)
                        cat = cat.parent_id
            return res
        res = []
        for  r in self:
            name_field = ' / '.join(get_names(r))
#             name = name_field + u' - ' + 
            name = name_compute(r,adict=[
#                                                                 ('id',{'pr':u'TVCV id'}),
                                                                ('code',{'pr':u'Mã'}),
                                                                ('name',{'fnc': lambda x:name_field}),
                                                                ('diem',{'pr':u'Điểm'}),
                                                                ('don_vi',{'pr':u'Đơn Vị','fnc':lambda r: r.name}),
                                                               #('do_phuc_tap',{'pr':u'Độ Phức Tạp'})
                                                               ])
            res.append((r.id,name))
        return res
    
#     @api.model
#     def name_search(self, name, args=None, operator='ilike', limit=100):
# #         raise ValueError('dfasdfd')
#         #print 'in name_search self.context'*100,self._context
#         res =  super(ThuVienCvi,self).name_search( name, args=None, operator='ilike', limit=100)
#         return res
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        limit =50
        try:
            id_int = int(name)
            #print 'id_int',id_int
            ma_tvcv_domain = ['|',('code','ilike',name),('id','=',id_int)]
            
        except:
            ma_tvcv_domain = [('code','ilike',name)]
        if self._context.get('you_search_at_gd_form'):
            thu_vien_da_chon_list_txt = self._context.get('thu_vien_da_chon_list')
            if thu_vien_da_chon_list_txt==False:
                thu_vien_da_chon_list = []
            else:
                thu_vien_da_chon_list = json.loads(thu_vien_da_chon_list_txt)
            thu_vien_id_of_gd_parent_id = self._context.get('thu_vien_id_of_gd_parent_id')
            gd_children_or_not_gd_children_domain = [('id','!=',thu_vien_da_chon_list),'|',('parent_id', '=',thu_vien_id_of_gd_parent_id),('id', '=',self.env.ref('dai_tgg.loaisuvu_viec_con_lai').id)]
        else:
            gd_children_or_not_gd_children_domain = [('parent_id','=',False),('id','!=',self.env.ref('dai_tgg.loaisuvu_viec_con_lai').id)]
        if not args:
            args = []
        if name:
            # Be sure name_search is symetric to name_get
            category_names = name.split(' / ')
            parents = list(category_names)
            #child = parents.pop()
            child =parents[0]
            parents = parents[1:]
            domain = [('name', operator, child)]
            if parents:
                names_ids = self.name_search(' / '.join(parents), args=args, operator='ilike', limit=limit)
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([('id', 'not in', category_ids)])
                    domain = expression.OR([[('parent_id', 'in', categories.ids)], domain])
                else:
                    domain = expression.AND([[('parent_id', 'in', category_ids)], domain])
                for i in range(1, len(category_names)):
                    domain = [[('name', operator, ' / '.join(category_names[-1 - i:]))], domain]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
#             if ma_tvcv_domain:
#                 last_domain =  expression.OR([expression.AND([domain, args]),ma_tvcv_domain])
#             else:
#                 last_domain =  expression.AND([domain, args])
            
            name_or_code_domain = expression.OR([domain, ma_tvcv_domain])
            last_domain  =  expression.AND([name_or_code_domain, gd_children_or_not_gd_children_domain,args]) 
            categories = self.search(last_domain, limit=limit)
        else:
            last_domain  =  expression.AND([gd_children_or_not_gd_children_domain,args]) 
            categories = self.search(last_domain, limit=limit)
        
        return categories.name_get()    
  
class DonVi(models.Model):
    _name = 'donvi'
    name = fields.Char()
    tvcv_ids = fields.One2many('tvcv','don_vi')
class DotXuatHayDinhKy(models.Model):
    _name = 'dotxuathaydinhky'
    name = fields.Char()
    tvcv_ids = fields.One2many('tvcv','dot_xuat_hay_dinh_ky')
class tvcvCate(models.Model):
    _name = 'tvcvcate'
    name = fields.Char()
    tvcv_ids = fields.One2many('tvcv','cong_viec_cate_id')  


               
############### END SỰ KIỆN ################
class PN(models.Model):  
    _name = 'pn'
    name = fields.Char()
    kiemke_ids = fields.One2many('kiemke','pn_id')
    vattu_ids = fields.One2many('vattu','pn_id')
M = {'LTK':['LTK'],'PTR':['pas'],'TTI':['TTI'],'BDG':['BDG'],'VTU':['VTU']}
def convert_sheetname_to_tram(sheet_name):
    if sheet_name ==False:
        return False
    else:
        for tram,key_tram_list in M.items():
            for key_tram in key_tram_list:
                rs = re.search(key_tram,sheet_name)
                if rs:
                    find_tram = tram
                    return find_tram
        return sheet_name  

class ImportThuVien(models.Model):
    _name = 'importthuvien' 
    type_choose = fields.Selection([(u'Thư viện công việc',u'Thư viện công việc'),
                                    (u'User',u'User'),(u'Công Ty',u'Công Ty')
                                    ,(u'Kiểm Kê',u'Kiểm Kê'),(u'Vật Tư LTK',u'Vật Tư LTK')
                                    ,(u'x',u'x'),(u'640',u'640G 1850 ')
                                    ,(u'INVENTORY_240G',u'INVENTORY_240G')
                                    ,(u'INVENTORY_RING_NAM_CIENA',u'INVENTORY_RING_NAM_CIENA')
                                    ,(u'Inventory-120G',u'Inventory-120G')
                                    ,(u'Inventory-330G',u'Inventory-330G')
                                    ,(u'INVENTORY-FW4570',u'INVENTORY-FW4570')
                                    ,(u'INVETORY 1670',u'INVETORY 1670')
                                    ,(u'iventory hw8800',u'iventory hw8800')
                                    ,(u'iventory7500',u'iventory7500')
                                    ],required = True)
    file = fields.Binary()
    filename = fields.Char()
    update_number=fields.Integer()
    create_number=fields.Integer()
    skipupdate_number=fields.Integer()
    thong_bao_khac = fields.Char()
    trigger_model = fields.Selection([(u'kiemke',u'kiemke'),
                                    (u'vattu',u'vattu'),(u'kknoc',u'kknoc')])
    log = fields.Text()
    def test_code(self):
#         fields= self.env['cvi']._fields
#         self.log = fields
#         for f,field  in fields.iteritems():
#             print type(field),field.type,type(field.type)
        not_active_include_search = True
        if not_active_include_search:
            domain_not_active = []
        else:
            domain_not_active = []
        domain = []
        domain = expression.AND([domain_not_active, domain])
        res = self.env['tvcv'].search(domain)
        self.log = len(res)
    def trigger(self):
        if self.trigger_model:
            count = 0
            self.env[self.trigger_model].search([]).write({'trig_field':'ok'})
#             for r in self.env[self.trigger_model].search([]):
#                 #print  count
#                 r.sn = r.sn
#                 count +=1
        else:
            raise UserWarning(u'Bạn phải chọn trigger model')
    def importthuvien(self):
        importthuvien(self)
        return True
    def import_strect(self):
        import_strect(self)
        return True
    def get_tram_from_sheet_name(self):
        M = {'LTK':['LTK'],'PTR':['PTR'],'TTI':['TTI'],'BDG':['BDG','VTU']}
        count = 0
        map_count = 0
        for r in self.env['kknoc'].search([]):
            count +=1
            #print count
            r.tram =convert_sheetname_to_tram(r.sheet_name)
            if r.tram:
                map_count +=1
        self.thong_bao_khac = 'so tram ltk, ptr %s'%map_count
                
                
    def map_kiemke_voi_noc(self):
        so_luong_mapping = 0
        count = 0
        for r in self.env['kiemke'].search([]):
            #print count
            if r.sn:
                mapping = self.env['kknoc'].search([('sn','=',r.sn)],limit=1)
                if mapping:
                    so_luong_mapping +=1
                    r.map_kknoc_id = mapping.id
            else:
                r.map_kknoc_id = False
            count +=1
        self.thong_bao_khac = u'Có %s kk mapping kknoc' %( so_luong_mapping)
        return True       
    def map_noc_voi_ltk(self):
        so_luong_mapping = 0
        count = 0
        for r in self.env['kknoc'].search([]):
            #print count
            if r.sn:
                mapping = self.env['vattu'].search([('sn','=',r.sn)],limit=1)
                if mapping:
                    so_luong_mapping +=1
                    #print 'co %s mapping'%(so_luong_mapping)
                    r.map_ltk_id = mapping.id
            else:
                r.map_ltk_id = False
            count +=1
        self.thong_bao_khac = u'Có %s noc mapping ltk' %( so_luong_mapping)
        return True   
    def map_noc_voi_kiemke(self):
        so_luong_mapping = 0
        count = 0
        for r in self.env['kknoc'].search([]):
            #print count
            if r.sn:
                mapping = self.env['kiemke'].search([('sn','=',r.sn)],limit=1)
                if mapping:
                    so_luong_mapping +=1
                    #print 'co %s mapping noc với kiểm kê'%(so_luong_mapping)
                    r.map_kiemke_id = mapping
            else:
                r.map_kiemke_id = False
            count +=1
        self.thong_bao_khac = u'Có %s noc mapping Kiểm kê' %( so_luong_mapping)
        return True   
def map_another_object(self_,val,field_map,model_map):
    self = self_
    if val:
        mappings = self.env[model_map].search([(field_map,'=ilike',val)],limit=1)
        if mappings:
            return mappings
    return False
            
                
class KiemKe(models.Model):  
    _name = 'kiemke'
    name = fields.Char(compute='name_',store=True)
    kiem_ke_id = fields.Char()
    stt = fields.Integer(string='STT')
    ten_vat_tu = fields.Char(string=u'Tên tài sản')
    so_the = fields.Char(string=u'Số Thẻ')
    ma_du_an = fields.Char(string=u'Mã dự án')
    ten_du_an = fields.Char(string=u'Tên dự án')
    pn = fields.Char(string=u'Part-Number')
    sn = fields.Char(string=u'Serial number')
    ma_vach = fields.Char(string=u'Mã vạch')
    ma_vach_thuc_te = fields.Char(string=u'Serial/Mã vạch thực tế ')
    trang_thai = fields.Char(string=u'Trạng thái')
    hien_trang_su_dung = fields.Char(string=u'Hiện trạng sử dụng')
    ghi_chu = fields.Char(string=u'Ghi chú')
    don_vi = fields.Char(string=u'Đơn vị')
    vi_tri_lap_dat = fields.Char(string=u'Vị trí lắp đặt')
    loai_tai_san = fields.Char(string=u'Loại tài sản')
    len_duplicate_sn_vat_tu_ids = fields.Integer(compute='duplicate_sn_vat_tu_ids_',store=True)
    sn_false = fields.Char()
    pn_id = fields.Many2one('pn')
    duplicate_sn_vat_tu_ids = fields.Many2many('kiemke','kiemke_kiemke_relate','kiemke_id','kiemke2_id',compute='duplicate_sn_vat_tu_ids_',store=True)
    yes_no_search = fields.Boolean(store=False)
    map_ltk_id = fields.Many2one('vattu',compute='map_ltk_id_',store=True)
   
    map_kknoc_id = fields.Many2one('kknoc',compute='map_kknoc_id_',store=True)
    tram = fields.Char(related='map_kknoc_id.tram',string=u'Trạm',store=True)
    len_sn = fields.Integer(compute='len_sn_',store=True)
    trig_field = fields.Char()
    
    ilike_map_ltk_ids = fields.Many2many('vattu',compute='ilike_map_ltk_id_',store=True)
    len_ilike_map_ltk_ids = fields.Integer(compute='ilike_map_ltk_id_',store=True)  
   
    ilike_map_kknoc_ids = fields.Many2many('kknoc',compute='ilike_map_kknoc_ids_',store=True)
    len_ilike_map_kknoc_ids = fields.Integer(compute='ilike_map_kknoc_ids_',store=True)  
    
    @api.depends('sn','trig_field','map_kknoc_id')
    def ilike_map_kknoc_ids_(self):
        for r in self:
            if not r.map_kknoc_id:
                rs = self.env['kknoc'].search([('sn','ilike',r.sn)])
                if rs:
                    r.ilike_map_kknoc_ids = rs.ids
                    r.len_ilike_map_kknoc_ids = len(rs)
                    
    
    @api.depends('sn','trig_field','map_ltk_id')
    def ilike_map_ltk_id_(self):
        for r in self:
            if not r.map_ltk_id:
                rs = self.env['vattu'].search([('sn','ilike',r.sn)])
                if rs:
                    r.ilike_map_ltk_ids = rs.ids
                    r.len_ilike_map_ltk_ids = len(rs)
                
    @api.depends('sn','trig_field')
    def len_sn_(self):
        for c,r in enumerate(self):
            #print 'len_sn',c
            if r.sn:
                r.len_sn  =len(r.sn)
    
    @api.depends('sn','trig_field')
    def map_ltk_id_(self):
        field_map = 'sn'
        model_map = 'vattu'
        for r in self:
            val = r.sn
            map_id = map_another_object(self,val,field_map,model_map)
            r.map_ltk_id = map_id
    @api.depends('sn','trig_field')
    def map_kknoc_id_(self):
        field_map = 'sn'
        model_map = 'kknoc'
        for r in self:
            val = r.sn
            map_id = map_another_object(self,val,field_map,model_map)
            r.map_kknoc_id = map_id
            
    @api.depends('sn','trig_field')
    def duplicate_sn_vat_tu_ids_(self):
        for r in self:
            if r.sn:
                mappings = self.env['kiemke'].search([('sn','=',r.sn)])
                mapping_list = mappings.ids
                if r.id:
                    mapping_list = filter(lambda i : i!=r.id,mapping_list)
                r.duplicate_sn_vat_tu_ids =mapping_list
                r.len_duplicate_sn_vat_tu_ids = len(mapping_list)
    @api.depends('sn','pn')
    def name_(self):
        for r in self:
            name  = name_compute(r,adict=[
                                            ('id',{'pr':u'vt ketoan, id'}),
                                            ('pn',{'pr':u'P/N'}),
                                            ('sn',{'pr':u'S/N'}),
                                            ]
                                 )
            r.name = name
#     @api.multi
#     def name_get(self):
#         def get_names(r):
#             name = name_compute(r,adict=[('name',{}),
#                                           ('pn',{'pr':u'P/N','skip_if_False':True},),
#                                           ('sn',{'pr':u'S/N','skip_if_False':True},),
#                                           ]
#                                  )
#             return name
#             
#         return [(r.id, get_names(r)) for r in self]
        
    


    
class Vattu(models.Model):  
    _name = 'vattu'
    name = fields.Char(compute='name_',store=True)
    stt = fields.Integer()
    phan_loai = fields.Char(string=u'Phân Loại')
    loai_card = fields.Char(string=u'Loại Card')
    he_thong = fields.Char(string=u'Hệ Thống')
    cabinet_rack = fields.Char()
    shelf = fields.Char()
    stt_shelf = fields.Char()
    slot = fields.Char()
    ghi_chu = fields.Char()
    pn = fields.Char()
    pn_id = fields.Many2one('pn')
    sn = fields.Char(string=u'SN')
    map_kiem_ke_id = fields.Many2one('kiemke',compute='map_kiem_ke_id_',store=True)
    map_kknoc_id = fields.Many2one('kknoc',compute='map_kknoc_id_',store=True)
    tram = fields.Char(related='map_kknoc_id.tram',string=u'Trạm',store=True)
    is_not_also_map_pn = fields.Boolean(compute='is_not_also_map_pn_',store=True)
    duplicate_sn_vat_tu_ids = fields.Many2many('vattu','vattu_vattu_relate','vattu_id','vattu2_id',compute='duplicate_sn_vat_tu_ids_',store=True)
    len_duplicate_sn_vat_tu_ids = fields.Integer(compute='duplicate_sn_vat_tu_ids_',store=True)
    sn_false = fields.Char()
    len_sn = fields.Integer(compute='len_sn_',store=True)
    trig_field = fields.Char()
    ilike_map_kk_ids = fields.Many2many('kiemke',compute='ilike_map_ltk_id_',store=True)
    len_ilike_map_kk_ids = fields.Integer(compute='ilike_map_ltk_id_',store=True)  
    @api.depends('sn','trig_field','map_kiem_ke_id')
    def ilike_map_ltk_id_(self):
        for c,r in enumerate(self):
            #print  'map i like _ids',c
            if not r.map_kiem_ke_id :
                rs = self.env['kiemke'].search([('sn','ilike',r.sn)])
                if rs:
                    r.ilike_map_kk_ids = rs.ids
                    r.len_ilike_map_kk_ids = len(rs)
                    
                    
                    
    @api.depends('sn','trig_field')
    def len_sn_(self):
        for r in self:
            if r.sn:
                r.len_sn  =len(r.sn)
    
    @api.depends('sn')
    def map_kknoc_id_(self):
        for r in self:
            r.map_kknoc_id = map_another_object(self,r.sn,'sn','kknoc')
    @api.depends('sn')
    def map_kiem_ke_id_(self):
        for r in self:
            r.map_kiem_ke_id = map_another_object(self,r.sn,'sn','kiemke')
    @api.depends('sn','pn')
    def name_(self):
        for r in self:
            name  = name_compute(r,adict=[
                                            ('id',{'pr':u'vt ltk, id'}),
                                            ('pn',{'pr':u'P/N'}),
                                            ('sn',{'pr':u'S/N'}),
                                            ]
                                 )
            r.name = name
    @api.multi
    def name_get(self):
        def get_names(r):
            name = name_compute(r,adict=[
                                           ('id',{'pr':u'vt ltk, id'}),
                                            ('stt',{'pr':u'STT'}),
                                            ('pn',{'pr':u'P/N'}),
                                            ('sn',{'pr':u'S/N'}),
                                          ]
                                 )
            return name
             
        return [(r.id, get_names(r)) for r in self]

    @api.depends('sn')
    def duplicate_sn_vat_tu_ids_(self):
        for r in self:
            if r.sn:
                mappings = self.env['vattu'].search([('sn','=',r.sn)])
                mapping_list = mappings.ids
                if r.id:
                    mapping_list = filter(lambda i : i!=r.id,mapping_list)
                r.duplicate_sn_vat_tu_ids =mapping_list
                r.len_duplicate_sn_vat_tu_ids = len(mapping_list)
    
    @api.depends('map_kiem_ke_id','pn')
    def is_not_also_map_pn_(self):
        for r in self:
            #print '2 Begin is_not_also_map_pn_'
            if r.map_kiem_ke_id:
                #print '2 in is_not_also_map_pn_'
                if r.pn !=r.map_kiem_ke_id.pn:
                    r.is_not_also_map_pn = True
         
    

    

class KKNoc(models.Model):  
    _name = 'kknoc'
    name = fields.Char(compute='name_',store=True)
    stt = fields.Integer()
    pn = fields.Char(string=u'P/N')
    clei = fields.Char(strin=u'CLEI')
    sn = fields.Char(string=u'S/N')
    pn_id = fields.Many2one('pn')
    len_duplicate_sn_vat_tu_ids = fields.Integer(compute='duplicate_sn_vat_tu_ids_',store=True)
    sn_false = fields.Char()
    data = fields.Text()
    duplicate_sn_vat_tu_ids = fields.Many2many('kknoc','kknoc_kknoc_relate','kknoc_id','kknoc2_id',compute='duplicate_sn_vat_tu_ids_',store=True)
    sheet_name = fields.Char()
    file_name = fields.Char(string=u'File của Noc')
    tram = fields.Char(string=u'Trạm',compute='tram_',store=True)
    map_ltk_id = fields.Many2one('vattu',compute='map_ltk_id_',store=True,string=u'Map với LTK')
    map_kiemke_id = fields.Many2one('kiemke',compute='map_kiemke_id_',store=True,string=u'Map với Kiểm Kê')
    trig_field = fields.Char()
    len_sn = fields.Integer(compute='len_sn_',store=True)
    ilike_map_kk_ids = fields.Many2many('kiemke',compute='ilike_map_kk_ids_',store=True)
    len_ilike_map_kk_ids = fields.Integer(compute='ilike_map_kk_ids_',store=True)  
    ilike_map_vattu_ids = fields.Many2many('vattu',compute='ilike_map_vattu_ids_',store=True)
    len_ilike_map_vattu_ids = fields.Integer(compute='ilike_map_vattu_ids_',store=True)  
    
    @api.depends('sn','trig_field','map_ltk_id')
    def ilike_map_vattu_ids_(self):
        for c,r in enumerate(self):
            #print '222ilike_map_vattu_ids_222',c
            if not r.map_ltk_id:
                rs = self.env['vattu'].search([('sn','ilike',r.sn)])
                if rs:
                    r.ilike_map_vattu_ids = rs.ids
                    r.len_ilike_map_vattu_ids = len(rs)
    
    @api.depends('sn','trig_field','map_kiemke_id')
    def ilike_map_kk_ids_(self):
        for c,r in enumerate(self):
            #print '333map_kiemke_id333',c
            if not r.map_kiemke_id:
                rs = self.env['kiemke'].search([('sn','ilike',r.sn)])
                if rs:
                    r.ilike_map_kk_ids = rs.ids
                    r.len_ilike_map_kk_ids = len(rs)
                    
                    
    @api.depends('sn','trig_field')
    def len_sn_(self):
        for c,r in enumerate(self):
            #print '00000 len_sn0000',c
            if r.sn:
                r.len_sn  =len(r.sn)
    @api.depends('sn','sheet_name','trig_field')
    def tram_(self):
        for c,r in enumerate(self):
            #print '1xxxtram',c
            r.tram = convert_sheetname_to_tram(r.sheet_name)
    @api.depends('sn','trig_field')
    def map_kiemke_id_(self):
        for c,r in enumerate(self):
            #print '111map_kiemke_id_111',c
            r.map_kiemke_id = map_another_object(self,r.sn,'sn','kiemke')
    @api.depends('sn','trig_field')
    def map_ltk_id_(self):
        for r in self:
            r.map_ltk_id = map_another_object(self,r.sn,'sn','vattu')
    @api.depends('sn')
    def duplicate_sn_vat_tu_ids_(self):
        for r in self:
            if r.sn:
                mappings = self.env['kknoc'].search([('sn','=',r.sn)])
                mapping_list = mappings.ids
                if r.id:
                    mapping_list = filter(lambda i : i!=r.id,mapping_list)
                r.duplicate_sn_vat_tu_ids =mapping_list
                r.len_duplicate_sn_vat_tu_ids = len(mapping_list)
    @api.depends('sn','pn')
    def name_(self):
        for r in self:
            name  = name_compute(r,adict=[
                                            ('id',{'pr':u'vt noc, id'}),
                                            ('pn',{'pr':u'P/N','skip_if_False':True}),
                                            ('sn',{'pr':u'S/N','skip_if_False':True}),
                                            ]
                                 )
            r.name = name



class GCCV(models.Model):
    _name='gccv'
    name= fields.Char()
    noi_dung=fields.Text(string=u'Nội dung') 
    thanh_cong_hay_that_bai = fields.Selection ([(u'Thành Công',u'Thành Công'),(u'Thất Bại',u'Thất Bại')],default=u'Thành Công') 
    loi_code = fields.Text(string=u'Lỗi')
    gccv_type_ids = fields.Many2many('gccvtype','gccv_gccvtype_relate','gccv_id','gccvtype_id',u'Các Loại ghi chú')
    doi_lap_id = fields.Many2one('gccv',u'Ghi chú đối lập')
    doi_lap_ids = fields.One2many('gccv','doi_lap_id',u'Những ghi chú đối lập')
    ket_qua_du_doan = fields.Text(string=u'Kết quả dự đoán')
    thac_mac =  fields.Text(string=u'Thắc Mắc')
    ket_qua_thuc_te = fields.Text(string=u'Kết quả thực tế')
    dung_voi_ket_qua_du_doan = fields.Boolean(string=u'Kết quả đúng với thực tế hay không')
    
    image_truoc_test = fields.Binary(string=u'Ảnh trước khi test')
    image_sau_test = fields.Binary(string=u'Ảnh sau khi test')
    
class GCCVType(models.Model):
    _name = 'gccvtype'
    _parent_name = 'parent_id'
    name = fields.Char()
    minh_hoa = fields.Text(string=u'Minh Họa')
    parent_id = fields.Many2one('gccvtype',string=u'Loại ghi chú Cha')
    gccv_ids=fields.Many2many('gccv','gccv_gccvtype_relate','gccvtype_id','gccv_id',u'Các Ghi chú')
    @api.constrains('parent_id')
    def _check_category_recursion_check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('Error ! You cannot create recursive categories.'))
        return True
    @api.multi
    def name_get(self):
        def get_names(cat):
            ''' Return the list [cat.name, cat.parent_id.name, ...] '''
            res = []
            if cat.name != False:
                while cat:
                        res.append(cat.name)
                        cat = cat.parent_id
            return res
        return [(cat.id, ' / '.join(reversed(get_names(cat)))) for cat in self]
 
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symetric to name_get
            category_names = name.split(' / ')
            parents = list(category_names)
            child = parents.pop()
            domain = [('name', operator, child)]
            if parents:
                names_ids = self.name_search(' / '.join(parents), args=args, operator='ilike', limit=limit)
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([('id', 'not in', category_ids)])
                    domain = expression.OR([[('parent_id', 'in', categories.ids)], domain])
                else:
                    domain = expression.AND([[('parent_id', 'in', category_ids)], domain])
                for i in range(1, len(category_names)):
                    domain = [[('name', operator, ' / '.join(category_names[-1 - i:]))], domain]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(expression.AND([domain, args]), limit=limit)
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()            

                
################### END LOAI SUCO####################                             
                
                
  
                
                
                
                





  

    

      





    



        
        
        
        





  
                
                
                
                
                
                
                
                
        
        
        
        
        