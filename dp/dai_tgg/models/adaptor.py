# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions
import xlrd
import base64
import re
from odoo.osv import expression    
class TuyenCap(models.Model):
    _name = 'tuyen_cap'
    name = fields.Char(required=True)
    soi_ids = fields.One2many('dai_tgg.soi','tuyen_cap')
class PortThietBi(models.Model):
    _name = 'port.thiet_bi'
    name = fields.Char(compute = '_name_compute',store=True)
    port_name = fields.Char()
    thiet_bi_id = fields.Many2one('thietbi')
    @api.depends('port_name','thiet_bi_id')
    def _name_compute(self):
        for r in self:
            name = (r.port_name if r.port_name else '') + ('/' + r.thiet_bi_id.name if r.thiet_bi_id else '')
            r.name = name

class ThietBi(models.Model):
    _name = 'thietbi'
    name = fields.Char()
    test = fields.Char()
#Phuong an va du phong
class PADP(models.Model):# moi phuong an chi ung voi 1 soi
    _name='padp'
    name = fields.Char(compute='_name_compute',store = True)
    huong_id =  fields.Many2one('huong', string = u'Hướng')
    soi_id = fields.Many2one('dai_tgg.soi',string = u'Sợi')
    #soi_id = fields.Many2many('dai_tgg.soi','soi_padp_relate','padp_id','soi_id')
    pa_hay_dp_n = fields.Selection(string=u'Phương án hay dự phòng',selection = [(u'phương án',u'Phương án'),(u'dự phòng 1',u'Dự phòng 1'),(u'dự phòng 2',u'Dự phòng 2'),(u'dự phòng 3',u'Dự phòng 3')])
    lich_su_hay_hien_tai = fields.Selection(selection=[(u'lịch sử',u'Lịch Sử'),(u'hiện tại',u'Hiện tại')])
    @api.depends('soi_id','pa_hay_dp_n')
    def _name_compute(self):
        for r in self:
            r.name = r.pa_hay_dp_n +'-' +r.soi_id.name
class Huong(models.Model):
    _name = "huong"
    name = fields.Char(compute='_name_compute',string = u'Tên(hướng + thiết bị)',store=True)
    name_theo_huong = fields.Char(string = u'hướng',required = True)
    thiet_bi_id = fields.Many2one('thietbi', string = u'Thiết bị',required = True)
    soi_ids = fields.One2many('dai_tgg.soi','huong_id',string = u'Sợi') #compute='_soi_compute'
    soi_name = fields.Char(related='soi_ids.name',string=u'Tên Sợi',help = u'related soi_ids.name')
    pa_hay_dp_n = fields.Selection(related='soi_ids.pa_hay_dp_n',string=u'Phương án or dp',selection = [(u'phương án',u'Phương án'),(u'dự phòng 1',u'Dự phòng 1'),(u'dự phòng 2',u'Dự phòng 2'),(u'dự phòng 3',u'Dự phòng 3')])

    @api.depends('name_theo_huong','thiet_bi_id')
    def _name_compute(self):
        for r in self:
            names = []
            if r.name_theo_huong:
                names.append(r.name_theo_huong)
            if  r.thiet_bi_id:
                names.append(r.thiet_bi_id.name)
            if names:
                r.name = u'-'.join(names)
class Log(models.Model):
    _name = 'dai.log'
    sheet_name = fields.Char()
    create_number_dict = fields.Char()
    get_number_dict = fields.Char()
    update_number_dict = fields.Char()

    
    
class Soi(models.Model):
    _name = 'dai_tgg.soi'
    
    _sql_constraints = [
    ('ada_id', 'unique("ada_id")', 'Field ada_id in soi table must be unique.'),
  ]
    name = fields.Char(compute = '_name_soi_compute',store = True)
    stt_soi = fields.Integer(required=True, string = u'Số thứ tự sợi')
    tuyen_cap = fields.Many2one('tuyen_cap',required = True)
    #tuyen_cap_thuong_goi = fields.Many2one('tuyen_cap')
    pa_hay_dp_n = fields.Selection(string=u'Phương án hay dự phòng',
                                   compute = '_pa_hay_dp_n',
                                   selection = [(u'phương án',u'Phương án'),(u'dự phòng 1',u'Dự phòng 1'),
                                                (u'dự phòng 2',u'Dự phòng 2'),(u'dự phòng 3',u'Dự phòng 3')])
    huong_id =  fields.Many2one('huong', string = u'Hướng Chính')
    thiet_bi_id = fields.Many2one('thietbi',string = u'Thiết bị',related='huong_id.thiet_bi_id')
    ada_id = fields.Many2one('ada', u'Adaptor liên kết')
    #port_thiet_bi = fields.Many2one('port.thiet_bi',string = u"Port thiết bị",related="ada_id.ada_map_id.port_thiet_bi")
    padp_ids = fields.One2many('padp','soi_id')
    tach_det_txt = fields.Char()
    soi_goc_id = fields.Many2one('dai_tgg.soi')
    soi_ve_dai = fields.Many2one('dai_tgg.soi')
    soi_duoc_chon_id = fields.Many2one('dai_tgg.soi',compute='_soi_duoc_chon_compute',store=True)
#     x = fields.function(_get_work_order_codes, method=True, type='char', string='Work orders', store=False)
    #test_field = fields.Integer(compute = '_ada_id_depend')
    @api.depends('soi_goc_id')
    def _soi_duoc_chon_compute(self):
        for r in self:
            if not r.soi_goc_id:
                r.soi_duoc_chon_id = r
            else:
                r.soi_duoc_chon_id =  r.soi_goc_id
    @api.multi
    def write(self,vals):
        ret = super(Soi,self).write(vals)
        for r in self:
            soi_goc_id =vals.get('soi_goc_id',False)
            if soi_goc_id:
                soi_goc = self.env['dai_tgg.soi'].browse(soi_goc_id)
                soi_goc.write({'soi_ve_dai':r.id})
        return ret
    @api.depends('padp_ids')
    def _pa_hay_dp_n(self):
        for r in self:
            try:
                last_padp = r.padp_ids[-1]
                r.pa_hay_dp_n = last_padp.pa_hay_dp_n
                for x in r.padp_ids[:-1]:
                    x.lich_su_hay_hien_tai = u'lịch sử'
            except IndexError:
                pass

                
    @api.depends('ada_id')
    def _ada_id_depend(self):
        for r in self:
            if r.ada_id:
                if r.ada_id.soi_id.id !=r.id:
                    r.ada_id.write({'soi_id':r.id})
            else:#r.soi_id = soi() empty
                if isinstance(r.id, int):
                    ada_olds = self.env['ada'].search([('soi_id','=',r.id)])
                    ada_olds.write({'soi_id':False})

    @api.depends('stt_soi','tuyen_cap','soi_goc_id')
    def _name_soi_compute(self):
        for r in self:
            names = []
            if r.stt_soi:
                names.append(u'' + str(r.stt_soi))
            if  r.tuyen_cap:
                names.append(u'' + r.tuyen_cap.name)
            if names:
                name = u'/'.join(names)
            if r.soi_goc_id:
                name = name +  u'['+r.soi_goc_id.name + u']'
            r.name = name
            
        
    @api.multi
    def name_get(self):
        res = []
        for x in self:
            name = x.name +  (u' ,' + x.huong_id.name  if x.huong_id else u'' ) +  (', ' +  x.pa_hay_dp_n if x.pa_hay_dp_n else '' )
            res.append((x.id, name))
        return res
    def name_create(self):
        for r in self:
            return u'Sợi: ' +  r.name + (u', Tuyến cáp: '  + r.tuyen_cap.name ) if r.tuyen_cap else ''
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
class OneFaceADA(models.Model):
    _name = 'ada'
   # _inherits = {'dai_tgg.soi':'soi_id'}
    _sql_constraints = [
      ('soi_id', 'unique("soi_id")', u'Field soi_id must be unique.'),]
#     @api.constrains('soi_id')
#     def _constrains_set_a_id(self):
#         if len(self.soi_id) > 1:
#             raise exceptions.ValidationError('Additional linkage failed.')

    name = fields.Char( string = u'Tên adaptor' ,compute = '_name_compute',store=True)
    truoc_hay_sau= fields.Selection(selection=[(u'trước',u'Trước'),(u'sau',u'Sau')], string=u'Trước hay sau' )
    adaptor_number = fields.Integer(required = True,string = u'Port',default=1)
    odf_number = fields.Integer(required = True, string = u'O',default=1)
    tu_number = fields.Integer(required = True,default=1,string = u'T')
    ada_ref = fields.Reference(selection=[('dai_tgg.soi',u'Sợi'),('port.thiet_bi',u'Port thiết bị'),('ada',u'ODF khác')], string = u'link toi')
    ada_tuong_duong = fields.Many2one('ada',compute='_ada_tuong_duong',store=True,string=u'Adaptor đối mặt')
    soi_id = fields.Many2one('dai_tgg.soi',u"Sợi")
    port_thiet_bi = fields.Many2one('port.thiet_bi',u"Port thiết bị")
    ada_khac_id = fields.Many2one('ada',u"Adaptor nối nhau")
    thietbi_char = fields.Char(string = u'xxxx')
    odf_duoc_tach = fields.Char()
    phia_sau_odf_la = fields.Selection([('dai_tgg.soi',u'Sợi'),('port.thiet_bi',u'Port thiết bị'),('ada',u'adaptor')])
    phia_truoc_odf_la = fields.Selection([('dai_tgg.soi',u'Sợi'),('port.thiet_bi',u'Port thiết bị'),('ada',u'adaptor')])
    odf_dau_xa = fields.Char(string = u'odf đầu xa')
    ghi_chu = fields.Char(string = u'ghi chú')
    soi_1_hay_soi_2 = fields.Selection([(1,'in'),(2,'out')])
    couple_ada_id = fields.Many2one('ada')
    padp_ids = fields.One2many('padp','soi_id',related='soi_id.padp_ids')
    padp_ids_compute = fields.Char(compute = '_padp_ids_compute')
    #pa_hay_dp_n = fields.Selection(string=u'Phương án hay dự phòng',selection = [(u'phương án',u'Phương án'),(u'dự phòng 1',u'Dự phòng 1'),(u'dự phòng 2',u'Dự phòng 2'),(u'dự phòng 3',u'Dự phòng 3')])

    search_phuong_an = fields.Selection(related='soi_id.padp_ids.pa_hay_dp_n',
                                        selection = [(u'phương án',u'Phương án'),(u'dự phòng 1',u'Dự phòng 1'),(u'dự phòng 2',u'Dự phòng 2'),(u'dự phòng 3',u'Dự phòng 3')])
    port_thiet_bi_cua_ada_khac_id = fields.Many2one('port.thiet_bi',
                                                    u"Port thiết bị ada khác",related='ada_khac_id.port_thiet_bi')
    soi_cua_ada_khac_id = fields.Many2one('dai_tgg.soi',
                                                    u"Sợi của ada khác",related='ada_khac_id.soi_id')
    soi_goc_id = fields.Many2one('dai_tgg.soi',related="soi_id.soi_goc_id")
    @api.multi
    def _padp_ids_compute(self):
        for r in self:
                padp_ids_compute = ''
                for padp in r.padp_ids:
                    padp_ids_compute = padp_ids_compute + ' ' + padp.name
                r.padp_ids_compute = padp_ids_compute
                    
                

        
    @api.depends('odf_number','tu_number','adaptor_number')
    def _name_compute(self):
        #raise ValueError('fuck here name compute')
        prefix_dict = (('adaptor_number',''), ('odf_number',''), ('tu_number',''))
        for r in self:
            r_names = []
            for i in prefix_dict:
                if getattr(r, i[0]) != False:
                    r_names.append(i[1]  +  str(getattr(r, i[0])))
            if r.truoc_hay_sau != False:
                r_names.append(r.truoc_hay_sau)
            if r_names:
                name =  '/'.join(r_names)
                r.test_field_name = name
                r.name = name

            
    @api.model
    def create(self,vals):
        id_new = self.id
        tu_number = self.tu_number
        this_ada  =  super(OneFaceADA, self).create(vals)
        
        soi_id = vals.get('soi_id',False)
        if soi_id:
#             qk = self.env['ada'].search([('soi_id','=',soi_id)])
#             product_category_query = "SELECT * FROM ada WHERE soi_id=" + str(soi_id)
#             self.env.cr.execute(product_category_query)
#             product_category = self.env.cr.fetchall()
#             raise ValueError(id_new,qk,product_category)
            soi = self.env['dai_tgg.soi'].browse(soi_id)
            soi.write({'ada_id':this_ada.id})
        return this_ada
        
    
    @api.multi
    def write(self,vals):
        #raise ValueError('fucking here!',vals)
        ret  =  super(OneFaceADA, self).write(vals)
        for r in self:
            couple_ada_id = vals.get('couple_ada_id',False)
            if couple_ada_id and 'couple_ada_id_Not_allow_write' not in vals:
                couple_ada_object = self.env['ada'].browse(couple_ada_id)
                couple_ada_object.write({'couple_ada_id':r.id,'couple_ada_id_Not_allow_write':True})
            soi_id = vals.get('soi_id',False) 
            if soi_id :
                soi_object = self.env['dai_tgg.soi'].browse(soi_id)
                soi_object.write({'ada_id':r.id})
        return ret
                
    
#     @api.multi
#     def write(self,vals):
#         #raise ValueError('fucking here!',vals)
#         ret  =  super(OneFaceADA, self).write(vals)
#         for r in self:
#             try:#co write soi_id cua 1 ada
#                 soi_id = vals['soi_id']
#                 old_mapping_soi = self.env['dai_tgg.soi'].search([('ada_id','=',r.id)])
#                 if old_mapping_soi:
#                     if soi_id ==False:
#                         soi_update_data = {'ada_id':False}
#                         old_mapping_soi.write(soi_update_data)
#                     else:# soi_id = int
#                         soi_update_data = {'ada_id':r.id}
#                         old_mapping_soi.write(soi_update_data)
#                 else:
#                     soi = self.env['dai_tgg.soi'].browse(soi_id)
#                     soi.write({'ada_id':r.id})
#                     print 'update duoc field ada_id cua soi',soi
#             except KeyError:
#                 pass
#         return ret
        
    ####################################################################d    
# class ADA(models.Model):
#     _name = 'dai_tgg.ada'
#     #image_medium = fields.Binary('Medium Image')
#     name = fields.Char( string = u'Tên adaptor', compute = '_name_compute', store = True)
#     adaptor_number = fields.Integer(u'stt Adaptor')
#     odf_number = fields.Integer(string = u'stt ODF')
#     tu_number = fields.Integer(string = u'stt Tủ')
#     
#     #thiet_bi = fields.Char()
#     odf_dau_xa = fields.Char()
#     #soi = fields.Many2one('dai_tgg.soi',compute = 'phia_sau_odf_selection_id_relate',store = True)
#     soi = fields.Many2one('dai_tgg.soi')
#     #tuyen_cap_tach_det = fields.Many2one('tuyen_cap')
#     
#     phia_truoc_odf_selection = fields.Reference(selection=[('dai_tgg.soi',u'Sợi'),('thietbi',u'Port thiết bị'),('dai_tgg.ada',u'ODF khác')], string=u'Mặt trước ODF')
#     is_another_odf_side_invisible_value= fields.Boolean(compute = '_phia_truoc_odf_onchange',string = "is_another_odf_side_invisible_value")
#     another_odf_side= fields.Selection(selection=[(u'trước',u'Trước'),(u'sau',u'Sau')], string=u'ODF khác link với mặt trước ODF này ở mặt nào?' )
#     
#     phia_sau_odf_selection = fields.Reference(selection=[('dai_tgg.soi',u'Sợi'),('thietbi',u'Port thiết bị'),('dai_tgg.ada',u'ODF khác')], string = u'Mặt sau ODF')
#     is_another_odf_side_of_behide_odf_invisible_value = fields.Boolean(compute = '_phia_sau_odf_selection_onchange')
#     another_odf_side_of_behide_odf= fields.Selection(selection=[(u'trước',u'Trước'),(u'sau',u'Sau')],string=u'Nếu phía sau ODF link tới ODF thì phía trước hay sau')
#     
#     
#     #fields.Reference(selection=[('tram2g',u'Tram 2G'),('tram3g',u'Tram 3G'),('tram4g',u'Tram 4G')])
#     #phia_sau_odf_selection_id = fields.Many2one('ada.reference',string = u'Phía sau ODF ref',)
#     #phia_truoc_odf_id = fields.Many2one('ada.reference',string = u'Phía Trước ODF ref')
#     description = fields.Char()
#     conect_adaptor_id = fields.Many2one('dai_tgg.ada',compute = 'phia_truoc_odf_id_relate',store = True)
#     @api.model
#     def create(self, vals):
#         ret  =  super(ADA, self).create(vals)
#         #raise ValueError('vals',vals)
#         phia_truoc_odf_selection_val = vals['phia_truoc_odf_selection']
#         if phia_truoc_odf_selection_val !=False:
#             phia_truoc_odf_selections = phia_truoc_odf_selection_val.split(',')
#             if 'dai_tgg.ada' ==phia_truoc_odf_selections[0]:
#                 if vals['another_odf_side']==False:
#                     raise UserWarning(u'Khi bạn đã chọn phia_truoc_odf_selections là adaptor, thì hãy chọn field another_odf_side ')
#                 else:
#                     phia_truoc_odf_selection_object = self.env['dai_tgg.ada'].browse(int(phia_truoc_odf_selections[1]))
#                     if vals['another_odf_side'] ==u'trước':
#                         update_val = {'phia_truoc_odf_selection':'dai_tgg.ada,%s'%ret.id, 'another_odf_side':u'trước'}
#                         phia_truoc_odf_selection_object.write(update_val)
#                     else:#sau
#                         update_val = {'phia_sau_odf_selection':'dai_tgg.ada,%s'%ret.id, 'another_odf_side_of_behide_odf':u'trước'}
#                         phia_truoc_odf_selection_object.write(update_val)
# #         raise ValueError('asdfdf',phia_truoc_odf_selection_object)
# #         raise ValueError('alo',vals["phia_truoc_odf_selection"])
# #         raise ValueError('alo',self.phia_truoc_odf_selection)
# #         print '****'*30,ret
#         return ret
#     @api.multi
#     def write(self, vals):
#         ret = super(ADA, self).write(vals)
#         print '****'*30,ret
#         return ret
#     
# #     @api.multi
# #     def write(self, vals):
# #         raise ValueError(self._context)
# #         return super(ADA, self).write(vals)
# #     @api.model
# #     def name_search(self, name, args=None, operator='ilike', limit=100):
# #         raise ValueError(self._context)
# #         args = args or []
# #         domain = []
# #         if name:
# #             domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
# #             if operator in expression.NEGATIVE_TERM_OPERATORS:
# #                 domain = ['&', '!'] + domain[1:]
# #         accounts = self.search(domain + args, limit=limit)
# #         return accounts.name_get()
# #     
# #     @api.depends('another_odf_side')
# #     def _another_odf_side_depends(self):
# #         for r in self:
# #             if r.another_odf_side ==u'trước':
# #                 pass
# #             elif r.another_odf_side ==u'sau':
# #                 r.another_odf_side.phia
#                  
#     
# #     @api.onchange('tu_number')
# #     def _x(self):
# #         soi = self.env['dai_tgg.soi'].search([('id','=',1)])
# #         print 'soi' * 66
# #         self.soi = soi
#         #self.phia_truoc_odf_selection = 'dai_tgg.soi,1'
#         #raise ValueError(self.id)
#     
#     @api.depends('phia_truoc_odf_selection')
#     def _phia_truoc_odf_onchange(self):
#         for  r in self:
#             if  isinstance(r.phia_truoc_odf_selection, ADA):
#                 r.is_another_odf_side_invisible_value = False
#             else:
#                 r.another_odf_side = False
#                 r.is_another_odf_side_invisible_value = True
#                 
#     @api.depends('phia_sau_odf_selection')
#     def _phia_sau_odf_selection_onchange(self):
#         for  r in self:
#             if  isinstance(r.phia_sau_odf_selection, ADA):
#                 r.is_another_odf_side_of_behide_odf_invisible_value = False
# 
#             else:
#                 r.is_another_odf_side_of_behide_odf_invisible_value = True
#                 r.another_odf_side_of_behide_odf = False
#                 
# 
# 
#     
#     
#     
#     @api.depends('image_medium')
#     def _get_file(self):
#         for r in self:
#             r.image_medium = tools.image_resize_image(r.image, size=(512,None))
#             
#     @api.depends('odf_number','tu_number','adaptor_number')
#     def _name_compute(self):
#         prefix_dict = (('adaptor_number','Port:'), ('odf_number','O:'), ('tu_number','T:'))
#         for r in self:
#             r_names = []
#             for i in prefix_dict:
#                 if getattr(r, i[0]) != False:
#                     r_names.append(i[1]  +  str(getattr(r, i[0])))
#             if r_names:
#                 r.name = ' - '.join(r_names)
#     @api.depends('phia_sau_odf_selection_id')
#     def phia_sau_odf_selection_id_relate(self):
#         for r in self:
#             this_ref = r.phia_sau_odf_selection_id
#             if this_ref:
#                 if this_ref.soi_id:
#                     r.soi = r.phia_sau_odf_selection_id.soi_id
#                     this_ref.soi_id.write({'ada_id' : self.id,'soi_dau_vao_truoc_hay_sau_odf':'sau'})
#                 else:
#                     r.soi = False
#             else:
#                 r.soi = False
    #truong hop phia truoc odf nay dau voi sau odf kia, thi ada_ref co ada_id, ada_id co phia_sau_odf_selection dau voi ada nay
#     @api.depends('phia_truoc_odf_id')
#     def phia_truoc_odf_id_relate(self):
#         for r in self:
#             this_ada_ref = r.phia_truoc_odf_id
#             
#             if this_ada_ref:
#                 that_ada = this_ada_ref.ada_id
#                 if that_ada:# neu ada_ref la adaptor ,luu phia sau no la 1 ada_ref khac co ada_id la  r.id
#                     if this_ada_ref.ada_reference_la_truoc_hay_sau=='sau':
#                         that_ada_ref  = self.env['ada.reference'].search([('ada_id','=',self.id),('ada_reference_la_truoc_hay_sau','=','truoc')])
#                         if that_ada_ref:
#                             pass
#                         else:
#                             
#                             that_ada_ref  = self.env['ada.reference'].create({'ada_id':r.id,
#                                                                          'ada_reference_la_truoc_hay_sau':'truoc'})
#                         #raise ValueError('that_ada_ref',that_ada_ref,that_ada_id)
#                         r.conect_adaptor_id = that_ada
#                         rt = that_ada.write({'phia_sau_odf_selection_id':that_ada_ref.id})
#     @api.multi
#     def name_get(self):
#         res = []
#         for x in self:
#             if x.name != False:
#                 name = 'P ' + x.name + ' ' + 'O' + str(x.odf_number) + ' ' + 'T' + str(x.tu_number)
#                 res.append((x.id, name))
#         return res
# class ADAReference(models.Model):
#     _name = 'ada.reference'
#     name =  fields.Char(compute = '_name_create',store = True)
#     #name =  fields.Char()
#     ada_id = fields.Many2one('dai_tgg.ada')
#     soi_id= fields.Many2one('dai_tgg.soi')
#     portthiebi_id = fields.Many2one('port.thiet_bi')
#     ada_reference_la_truoc_hay_sau = fields.Selection([('truoc',u'Trước'),('sau',u'Sau')]) # danh cho ada_id
#     type = fields.Selection([('ada_id',u'Adaptor 1'),('soi_id',u'Sợi 1'),('portthiebi_id',u'port thiet bi 1')])
#     @api.multi
#     def _test_create_name(self):
#         for x in self:
#             x.name = 'fuck'
#     @api.depends('portthiebi_id','ada_id','soi_id')
#     #@api.one
#     def _name_create(self):
#             for x in self:
#                 not_empty_count = 0
#                 field_name_dict = {'portthiebi_id':'Port','ada_id':'adaptor','soi_id':u'Sợi'}
#                 for field in ['portthiebi_id','ada_id','soi_id']:
#                     ref_x = getattr(x, field)
#                     if ref_x:
#                         not_empty_count += 1
#                         field_tempt_for_check_unique = field
#                 if not_empty_count > 1:
#                     raise UserWarning('dau phong khong the co 2 field co gia tri ')
#                 elif not_empty_count ==1:
#                     if field_tempt_for_check_unique =='ada_id' and x.ada_reference_la_truoc_hay_sau:
#                         prefix = self.ada_reference_la_truoc_hay_sau
#                     else:
#                         prefix = ''
#                     #x.name = '(ref) ' + prefix + ' ' +  field_name_dict[field_tempt_for_check_unique] + ' ' +  getattr(x,field_tempt_for_check_unique).name
#                     x.name = '(ref)'  + prefix + ' ' +  getattr(x,field_tempt_for_check_unique).name_create()
#                     x.type = field_tempt_for_check_unique
#                 else:
#                     x.name = False
#                     x.type =False
#     @api.constrains('portthiebi_id','ada_id','soi_id')
#     def _check_instructor_not_in_attendees(self):
#         for x in self:
#             not_empty_count = 0
#             for field in ['portthiebi_id','ada_id','soi_id']:
#                 ref_x = getattr(x, field)
#                 if ref_x:
#                     not_empty_count += 1
#                     #field_tempt_for_check_unique = field
#             if not_empty_count > 1:
#                 raise exceptions.ValidationError('dau phong khong the co 2 field co gia tri ')
#             if x.ada_id:
#                 if x.ada_reference_la_truoc_hay_sau ==False:
#                     raise exceptions.ValidationError('ada_reference_la_truoc_hay_sau not null when ada_id ton tai')
# class DuocTachTuSoi(models.Model):
#     _name = 'duoctachtusoi'
#     soi_id = fields.Many2one('dai_tgg.soi')
#     cu_li_tach_km = fields.Float()
# class TachDetThanhSoi(models.Model):
#     _name = 'tachdetthanhsoi'
#     soi_id = fields.Many2one('dai_tgg.soi')
#     cu_li_tach_km = fields.Float()

            
#     @api.multi
#     def write(self,vals):
#         raise ValueError(vals)

