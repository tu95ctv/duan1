# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions
import xlrd
import base64
import re
from odoo.osv import expression
from odoo.http import request
from odoo.tools.misc import xlwt
from copy import deepcopy
from cStringIO import StringIO
#from odoo.exceptions import UserError
import logging
from tao_instance import import_bd
from tao_instance import import_bd_tuan
_logger = logging.getLogger(__name__)
import psycopg2
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
class Import(models.TransientModel):
    _inherit = 'base_import.import'
    @api.multi
    def do(self, fields, options, dryrun=False):
        """ Actual execution of the import

        :param fields: import mapping: maps each column to a field,
                       ``False`` for the columns to ignore
        :type fields: list(str|bool)
        :param dict options:
        :param bool dryrun: performs all import operations (and
                            validations) but rollbacks writes, allows
                            getting as much errors as possible without
                            the risk of clobbering the database.
        :returns: A list of errors. If the list is empty the import
                  executed fully and correctly. If the list is
                  non-empty it contains dicts with 3 keys ``type`` the
                  type of error (``error|warning``); ``message`` the
                  error message associated with the error (a string)
                  and ``record`` the data which failed to import (or
                  ``false`` if that data isn't available or provided)
        :rtype: list({type, message, record})
        """
        self.ensure_one()
        self._cr.execute('SAVEPOINT import')

        try:
            data, import_fields = self._convert_import_data(fields, options)
            # Parse date and float field
            data = self._parse_import_data(data, import_fields, options)
        except ValueError, error:
            return [{
                'type': 'error',
                'message': unicode(error),
                'record': False,
            }]
        print 'import_fields, options',import_fields, options
        #print 'ahhah**'*33,data
        _logger.info('importing %d rows...', len(data))
        import_result = self.env[self.res_model].with_context(import_file=True).load(import_fields, data)
        _logger.info('done')

        # If transaction aborted, RELEASE SAVEPOINT is going to raise
        # an InternalError (ROLLBACK should work, maybe). Ignore that.
        # TODO: to handle multiple errors, create savepoint around
        #       write and release it in case of write error (after
        #       adding error to errors array) => can keep on trying to
        #       import stuff, and rollback at the end if there is any
        #       error in the results.
        try:
            if dryrun:
                self._cr.execute('ROLLBACK TO SAVEPOINT import')
            else:
                self._cr.execute('RELEASE SAVEPOINT import')
        except psycopg2.InternalError:
            pass

        return import_result['messages']
    
class ImportBaoDuong(models.Model):
    _name = 'importbd' 
    file = fields.Binary()
    import_2g_or_3g = fields.Selection([('2G','2G'),('3G','3G')])
    @api.multi
    def importbd_old(self):
        return {
             'type' : 'ir.actions.act_url',
             'url': '/web/binary/download_document?model=importbd&field=file&id=%s&filename=product_stock.xls'%(self.id),
             'target': 'self',
 }
    @api.multi
    def importbd(self):
        import_bd(self)
        return True
    @api.multi
    def importbd1(self):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1',cell_overwrite_ok=True)
#         worksheet.col(3).width =int(13*260)
#         worksheet.col(4).width =int(13*260)
#         worksheet.col(5).width =int(13*260)
        worksheet.write_merge(0, 1, 0 , 0,u"Thiết bị",title_format_style)
        worksheet.write_merge(0, 1, 1 ,1,u"Hướng",title_format_style)
        worksheet.write_merge(0, 0, 2 ,3,u"PHƯƠNG ÁN",title_format_style)
        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
    
    
        
        return request.make_response(
            data,
            #self.from_data(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % 'test'),
               
            ],
           
        )
def fix_import_export_id_paths(fieldname):
    """
    Fixes the id fields in import and exports, and splits field paths
    on '/'.

    :param str fieldname: name of the field to import/export
    :return: split field name
    :rtype: list of str
    """
    fixed_db_id = re.sub(r'([^/])\.id', r'\1/.id', fieldname)
    fixed_external_id = re.sub(r'([^/]):id', r'\1/id', fixed_db_id)
    return fixed_external_id.split('/')        
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
    @api.model
    def load(self, fields, data):
        """
        Attempts to load the data matrix, and returns a list of ids (or
        ``False`` if there was an error and no id could be generated) and a
        list of messages.

        The ids are those of the records created and saved (in database), in
        the same order they were extracted from the file. They can be passed
        directly to :meth:`~read`

        :param fields: list of fields to import, at the same index as the corresponding data
        :type fields: list(str)
        :param data: row-major matrix of data to import
        :type data: list(list(str))
        :returns: {ids: list(int)|False, messages: [Message]}
        """
        # determine values of mode, current_module and noupdate
        mode = self._context.get('mode', 'init')
        current_module = self._context.get('module', '')
        noupdate = self._context.get('noupdate', False)

        # add current module in context for the conversion of xml ids
        self = self.with_context(_import_current_module=current_module)
        print 'self._context',self._context
        cr = self._cr
        cr.execute('SAVEPOINT model_load')

        fields = map(fix_import_export_id_paths, fields)
        fg = self.fields_get()

        ids = []
        messages = []
        ModelData = self.env['ir.model.data']
        ModelData.clear_caches()
        extracted = self._extract_records(fields, data, log=messages.append)
        converted = self._convert_records(extracted, log=messages.append)
        for id, xid, record, info in converted:
            try:
                cr.execute('SAVEPOINT model_load_save')
            except psycopg2.InternalError as e:
                # broken transaction, exit and hope the source error was
                # already logged
                if not any(message['type'] == 'error' for message in messages):
                    messages.append(dict(info, type='error',message=u"Unknown database error: '%s'" % e))
                break
            try:
                ids.append(ModelData._update(self._name, current_module, record, mode=mode,
                                             xml_id=xid, noupdate=noupdate, res_id=id))
                cr.execute('RELEASE SAVEPOINT model_load_save')
            except psycopg2.Warning as e:
                messages.append(dict(info, type='warning', message=str(e)))
                cr.execute('ROLLBACK TO SAVEPOINT model_load_save')
            except psycopg2.Error as e:
                messages.append(dict(info, type='error', **PGERROR_TO_OE[e.pgcode](self, fg, info, e)))
                # Failed to write, log to messages, rollback savepoint (to
                # avoid broken transaction) and keep going
                cr.execute('ROLLBACK TO SAVEPOINT model_load_save')
            except Exception as e:
                message = (_('Unknown error during import:') + ' %s: %s' % (type(e), unicode(e)))
                moreinfo = _('Resolve other errors first')
                messages.append(dict(info, type='error', message=message, moreinfo=moreinfo))
                # Failed for some reason, perhaps due to invalid data supplied,
                # rollback savepoint and keep going
                cr.execute('ROLLBACK TO SAVEPOINT model_load_save')
        if any(message['type'] == 'error' for message in messages):
            cr.execute('ROLLBACK TO SAVEPOINT model_load')
            ids = False

        if ids and self._context.get('defer_parent_store_computation'):
            self._parent_store_compute()

        return {'ids': ids, 'messages': messages}
class NodeB (models.Model):
    _name = 'nodeb'
    name = fields.Char()
    code = fields.Char()
    ngay_bao_duong = fields.Date()
class Tram(models.Model):
    _name = 'tram'
    name = fields.Char()
    address =fields.Char()
    soi_ids = fields.Many2many('dai_tgg.soi','soi_tram_relate','tram_id','soi_id')
class User(models.Model):
    _inherit = 'res.users'
    catruc_ids = fields.Many2many('trucca', 'trucca_res_users_rel_d4','res_users_id','trucca_id',string=u'Ca truc')
    tram_id = fields.Many2one('tram', string=u'Trạm')
def convert_memebers_to_str(member_ids):
    return u','.join(member_ids.mapped('name'))
def Convert_date_orm_to_str(date_orm_str):
    date_obj = fields.Date.from_string(date_orm_str)
    return date_obj.strftime('%d/%m/%y')
class TrucCa(models.Model):
    _name = 'trucca'
    
    dien_ap_a = fields.Float()
    dong_dien_a = fields.Float()
    dien_ap_b = fields.Float()
    dong_dien_b = fields.Float()

    co_toilet = fields.Boolean()
    quet_nha = fields.Boolean()
    chui_nha = fields.Boolean()
    name = fields.Char(string=u'Ca Trực',compute = '_name_truc_ca_compute', store=True)
    ca = fields.Selection([(u'Sáng',u'Sáng'), (u'Chiều',u'Chiều'), (u'Đêm',u'Đêm')],string = u'Buổi ca') 
    date = fields.Date(default=fields.Date.today, string = u'Ngày')
    truong_ca = fields.Many2one('res.users' , default=lambda self: self._truongca_default_get())
    member_ids = fields.Many2many('res.users', string=u'Những thành viên trực')
    nguoi_truc = fields.Many2one('res.users')
    sk_id = fields.Many2one('sukien')
    
    gio_bat_dau = fields.Datetime(u'Giờ bắt đầu ca ',default=fields.Datetime.now)
    gio_ket_thuc = fields.Datetime(u'Giờ Kết Thúc ca')
    #second_su_kien_ids = fields.Many2many('sukien',related = 'su_kien_ids.su_kien_id')
    su_kien_ids = fields.Many2many('sukien','trucca_sukien_relate','trucca_id','su_kien_id',string = u'sự kiện')
    su_kien_tu_ids = fields.Many2many('sukien',
                    compute = 'skt_',store=True
                     )
    tram_id = fields.Many2one('tram',compute='tram_',store=True)
    @api.depends('name')
    def tram_(self):
        for r in self:
            r.tram_id = r.env.user.tram_id
    @api.depends('su_kien_ids.su_kien_id')
    def skt_(self):
        su_kien_id_list = self.su_kien_ids.mapped('su_kien_id')
        self.su_kien_tu_ids = su_kien_id_list
    
    @api.model
    def _truongca_default_get(self):
        return self.env.user
    
    def common(self,vals,created_object=None):
        pass
#         trucca_obj = created_object or self
#         for r in trucca_obj:
# #             if 'su_kien_ids' in vals:
# #                 su_kien_ids = self.env['sukien'].browse(vals['su_kien_ids'])
#                 su_kien_ids = r.su_kien_ids
#                 su_kien_s = su_kien_ids.mapped('su_kien_id')
#                 #raise ValueError(su_kien_s)
#                 su_kien_s.write({'catruc_ids':[(4, r.id, 0)]})
        
        #raise ValueError(vals)
    @api.model
    def create(self,vals):
        res = super(TrucCa, self).create(vals)
        self.common(vals,res)
        return res
    @api.multi
    def write(self,vals):
        
        res =  super(TrucCa, self).write(vals)
        self.common(vals)
        return res
    
    @api.depends('date','ca','member_ids')
    def _name_truc_ca_compute(self):
        for r in self:
            #ret = self.truc_ca_name(r)
            adict=[('ca',{'pr':u'Ca'}),('date',{'pr':u'Ngày','fnc':Convert_date_orm_to_str}),('id',{'pr':u'id'}),('member_ids',{'pr':u'Người Trực','fnc':convert_memebers_to_str})]
            ret =  name_compute(r, adict)
            r.name = ret
                
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

def name_compute(r,adict=None):
    names = []
#     adict = [('cate_sukien',{'pr':''}),('content',{'pr':''}),('id',{'pr':''})]
    for a,b in adict:
        val = getattr(r,a)
        if val:
            fnc = b.get('fnc',None)
            if fnc:
                val = fnc(val)
            if b.get('pr',None):
                item =  b['pr'] + u': ' + unicode(val)
            else:
                item = unicode (val)
            names.append(item)
    if names:
        name = u'-'.join(names)
    else:
        name = False
    return name
class SuKien(models.Model):
    _name = 'sukien'
    name = fields.Char(compute='name_',store=True)
    gio_bat_dau = fields.Datetime(u'Giờ bắt đầu ', default=fields.Datetime.now,required=True)
    gio_ket_thuc = fields.Datetime(u'Giờ Kết Thúc')
    cate_sukien = fields.Selection([(u'Sự cố đứt quang',u'Sự cố đứt quang'),(u'Đổi luồng',u'Đổi luồng'),(u'Đấu mới',u'Đấu mới'),(u'Khác',u'Khác')],default =u'Khác' )
    duration = fields.Float(digits=(6, 2), help="Duration in minutes",compute = '_get_duration', store = True)
    content = fields.Char(string = u"Nội dung comment đầu") 
    comment_ids = fields.One2many('comment','su_kien_id',string=u'Những comments tiếp')
    catruc_ids  = fields.Many2many('trucca','trucca_sukien_relate','su_kien_id','trucca_id',string = u'Ca Trực')
    su_kien_id = fields.Many2one('sukien')
    chuyen_luong_ids= fields.One2many('lichsuchay','su_kien_id')
    test = fields.Char()
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        print 'name'*20,name,'args',args,'operator',operator
        print 'context***',self._context
        rs  = super(SuKien, self).name_search(name, args=args, operator=operator, limit=limit)
        print 'rs'*20,rs
        return rs
    @api.depends('content','cate_sukien')
    def name_(self):
        for r in self:
            name  = name_compute(r,adict=[('cate_sukien',{'pr':u'cate'}),('content',{'pr':u'nd'}),('id',{'pr':u'id'})])
            r.name = name
#     @api.onchange('su_kien_id')
#     def catruc_ids_compute(self):
#         raise ValueError(self._context)
#         if self.su_kien_id:
#             self.catruc_ids = self.catruc_ids.append(self.su_kien_id.ca)
    def common(self,vals):
        #raise ValueError('vals',vals)
        pass
        #raise ValueError(self._context)
    @api.model
    def create(self,vals):
        self.common(vals)
        res = super(SuKien, self).create(vals)
        return res
    @api.multi
    def write(self,vals):
        self.common(vals)
        res =  super(SuKien, self).write(vals)
        return res
        
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
  
#     @api.multi
#     def name_get(self):
#         res = []
#         for x in self:
#             res.append((x.id, x.content))
#         return res
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
class MorePrint(models.Model):
    _name = 'add_more_print'
    name = fields.Char()
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
    
class LineImportBD(models.Model):
    _name = 'lineimport'
    name_2g = fields.Char()
    bts_id = fields.Many2one('bts',compute='bts_id_',store=True)
    name_3g = fields.Char()
    date_char = fields.Char()
    date = fields.Date()
    week_number = fields.Integer()
    week_char = fields.Char()
    importbdtuan_id = fields.Many2one('importbdtuan') 
    ghi_chu = fields.Char()
    is_mapping_2_week = fields.Boolean()
    @api.depends('name_2g')
    def bts_id_(self):
        rs = self.env['bts'].search([('name','=',self.name_2g)])
        self.bts_id = rs
    
    
        
class ImportBaoDuongTuan(models.Model): 
    _name='importbdtuan'
    file_import = fields.Binary()
    lineimports = fields.One2many('lineimport','importbdtuan_id')
    
    @api.multi
    def import_bd_tuan(self):
        import_bd_tuan(self)
    
    @api.multi
    def download_for_rnas(self):
        return {
             'type' : 'ir.actions.act_url',
             #'url': '/web/binary/download_document?model=importbd&field=file&id=%s&filename=product_stock.xls'%(self.id),
             'url': '/web/binary/download_importbdtuan',
             'target': 'self',
        }