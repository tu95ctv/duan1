# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions
import xlrd
import base64
import re
from odoo.osv import expression    
from odoo.exceptions import UserError
class TuyenCap(models.Model):
    _name = 'tuyen_cap'
    name = fields.Char(required=True)
    soi_ids = fields.One2many('dai_tgg.soi','tuyen_cap')
class PortThietBi(models.Model):
    _name = 'port.thiet_bi'
    name = fields.Char(compute = '_name_compute',store=True)
    port_name = fields.Char()
    thiet_bi_id = fields.Many2one('thietbi')
    port_thiet_bi_id = fields.Many2one('port.thiet_bi')
    ada_ids = fields.One2many('ada','port_thiet_bi')
    ada_id = fields.Many2one('ada',compute=  'ada_id_',store = True)
    @api.depends('ada_ids')
    def ada_id_(self):
        for r in self:
            if r.ada_ids:
                r.ada_id = r.ada_ids[0]
                
    @api.depends('port_name','thiet_bi_id')
    def _name_compute(self):
        for r in self:
            name = (r.port_name if r.port_name else '') + ('/' + r.thiet_bi_id.name if r.thiet_bi_id else '')
            r.name = name
class ParticularReport1(models.AbstractModel):
    _name = 'report.dai_tgg.port_thiet_bi_print'
    @api.noguess
    def get_action(self, docids, report_name, data=None):
        """Return an action of type ir.actions.report.xml.

        :param docids: id/ids/browserecord of the records to print (if not used, pass an empty list)
        :param report_name: Name of the template to generate an action for
        """
        context = self.env.context
        if docids:
            if isinstance(docids, models.Model):
                active_ids = docids.ids
            elif isinstance(docids, int):
                active_ids = [docids]
            elif isinstance(docids, list):
                active_ids = docids
            context = dict(self.env.context, active_ids=active_ids)

        report = self.env['ir.actions.report.xml'].with_context(context).search([('report_name', '=', report_name)])
        if not report:
            raise UserError(_("Bad Report Reference") + _("This report is not loaded into the database: %s.") % report_name)
        
        return_d  ={
            'context': context,
            'data': data,
            'type': 'ir.actions.report.xml',
            'report_name': report.report_name,
            'report_type': report.report_type,
            'report_file': report.report_file,
            'name': report.name,
        }
        print "return_d"*23,return_d
        return {
            'context': context,
            'data': data,
            'type': 'ir.actions.report.xml',
            'report_name': report.report_name,
            'report_type': report.report_type,
            'report_file': report.report_file,
            'name': report.name,
        }
        
        
    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('dai_tgg.port_thiet_bi_print')
        docs = self.env[report.model].browse(docids)
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': docs,
        }
        print 'docargs'*33,docargs
        return report_obj.render('dai_tgg.port_thiet_bi_print', docargs)
class ThietBi(models.Model):
    _name = 'thietbi'
    name = fields.Char()
    test = fields.Char()
#Phuong an va du phong
class PADP(models.Model):# moi phuong an chi ung voi 1 soi
    _name='padp'
    name = fields.Char(compute='_name_compute',store = True)
    #name = fields.Char()
    huong_id =  fields.Many2one('huong', string = u'Hướng')
    soi_id = fields.Many2one('dai_tgg.soi',string = u'Sợi')
    thiet_bi_id = fields.Many2one('thietbi',compute = '_thiet_bi_compute',store = True)
    soi_ids = fields.Many2many('dai_tgg.soi','soi_padp_relate','padp_id','soi_id')
    soi_ids_lay_soi_ve_dai =  fields.Many2many('dai_tgg.soi',compute ='_soi_ids_lay_soi_ve_dai' )
    soi_ids_char = fields.Char(compute='_soi_ids_char_compute',store = True)
    ada_ids_char = fields.Char(compute='_ada_ids_char_compute',store = True)
    ada_ids = fields.Many2many('ada',compute='_ada_ids_for_padp_compute')
    pa_hay_dp_n = fields.Selection(string=u'Phương án hay dự phòng',
                                   selection = [(u'PA',u'Phương án'),(u'DP1',u'Dự phòng 1'),
                                                (u'DP2',u'Dự phòng 2'),(u'DP3',u'Dự phòng 3'),
                                                (u'DP4',u'Dự phòng 4')],
                                   required = True
                                   )
    lich_su_hay_hien_tai = fields.Selection(selection=[(u'lịch sử',u'Lịch Sử'),(u'hiện tại',u'Hiện tại')])
    odf_dau_xa = fields.Char(compute='_odf_dau_xa_compute',store=True)
#     lichsuchuyen_ids  =fields.One2many('lichsuchuyen','padp_id')
    @api.depends('soi_ids')#,'soi_ids.soi_ve_dai'
    def _soi_ids_lay_soi_ve_dai(self):
        for r in self:
            r.soi_ids_lay_soi_ve_dai = r.soi_ids.mapped('soi_ve_dai')
    
    @api.depends('soi_ids')
    def _odf_dau_xa_compute(self):
        for r in self:
            odf_dau_xas = r.soi_ids.mapped('ada_out_id.odf_dau_xa')
            r.odf_dau_xa = reduce(lambda x,y:x or y, odf_dau_xas,False)   
    @api.depends('soi_ids')
    def _soi_ids_char_compute(self):
        for r in self:
            adict_tuye_cap_sois = {}
            for soi in r.soi_ids.mapped('soi_duoc_chon_id'):
                soi_lists = adict_tuye_cap_sois.setdefault(soi.tuyen_cap.name,[])
                soi_lists.append(str(soi.stt_soi))
            ret_vals= []
            for tc,soi_lists in adict_tuye_cap_sois.iteritems():
                once = u','.join(soi_lists ) +u' ' + tc
                ret_vals.append(once)
            r.soi_ids_char = u'-'.join(ret_vals)
            
    @api.depends('soi_ids.ada_out_id','soi_ids.soi_ve_dai.ada_out_id')
    def _ada_ids_char_compute(self):
        for r in self:
            adict_tuye_cap_sois = {}
            soi_ids_co_out = r.soi_ids.mapped('soi_ve_dai') or r.soi_ids
            print 'soi_ids_co_out**',soi_ids_co_out
            for ada in soi_ids_co_out.mapped('ada_out_id'):
                odf_tu = str(ada.odf_number )+ '/' + str(ada.tu_number)
                soi_lists = adict_tuye_cap_sois.setdefault(odf_tu,[])
                soi_lists.append(str(ada.adaptor_number))
            ret_vals= []
            for tc,soi_lists in adict_tuye_cap_sois.iteritems():
                once = u','.join(soi_lists ) +u' /' + tc
                ret_vals.append(once)
            r.ada_ids_char = u'-'.join(ret_vals)
                
    @api.depends('soi_ids')
    def _ada_ids_for_padp_compute(self):
        for r in self:
            ada_ids = r.soi_ids.mapped('ada_id')
            r.ada_ids = ada_ids
    
    @api.depends('huong_id','pa_hay_dp_n')
    def _thiet_bi_compute(self):
        for r in self:
            r.thiet_bi_id = r.huong_id.thiet_bi_id

    @api.depends('soi_id','pa_hay_dp_n')
    def _name_compute(self):
        for r in self:
            names = []
            if r.huong_id.name:
                names.append(r.huong_id.name)
            if r.pa_hay_dp_n:
                names.append(r.pa_hay_dp_n)
            if names:
                r.name = u'-'.join(names)
            else:
                r.name =  False
                
class Huong(models.Model):
    _name = "huong"
    name = fields.Char(compute='_name_compute',string = u'Tên(hướng + thiết bị)',store=True)
    name_theo_huong = fields.Char(string = u'hướng',required = True)
    thiet_bi_id = fields.Many2one('thietbi', string = u'Thiết bị',required = True)
    dang_chay_id = fields.Many2one('padp',compute='_dang_chay_id',store=True) #moi them
    lichsuchay_ids = fields.One2many('lichsuchay','huong_id')
    
#     soi_ids = fields.One2many('dai_tgg.soi','huong_id',string = u'Sợi') #compute='_soi_compute'
#     soi_name = fields.Char(related='soi_ids.name',string=u'Tên Sợi',help = u'related soi_ids.name')
    @api.depends('lichsuchay_ids')
    def _dang_chay_id(self):
        for r in self:
            lichsuchays = r.lichsuchay_ids.search([('huong_id','=',self.id)],order="id desc")
            if lichsuchays:
                r.dang_chay_id = lichsuchays[0].padp_id
            else:
                r.dang_chay_id = False
            
    
    
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
class LichSuChay(models.Model):
    _name = 'lichsuchay'
    name = fields.Char(compute = 'name_for_lichsuchay_',store=True)
    padp_id =  fields.Many2one('padp')
    huong_id = fields.Many2one('huong',compute='huong_id_compute_for_lsc_',store = True)
    su_kien_id = fields.Many2one('sukien')
    ghi_chu = fields.Char()
    
    @api.depends('padp_id','create_date')
    def name_for_lichsuchay_(self):
        adict = {u'chuyển qua':self.padp_id.name,u'vào lúc':self.write_date}
        lists = []
        for k,v in adict.iteritems():
            if v:
                lists.append (k +u' ' + v)
        self.name = u','.join(lists)
        
#         if self.padp_id.name:
#             self.name = u'chuyển qua' + self.padp_id.name + u'vào lúc' + self.create_date
    @api.depends('padp_id.huong_id')
    def huong_id_compute_for_lsc_(self):
        self.huong_id = self.padp_id.huong_id
        
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
    #ada_id = fields.Many2one('ada', u'Adaptor liên kết')
    ada_ids_butone =  fields.One2many('ada','soi_id')
    ada_id=  fields.Many2one('ada', u'Adaptor liên kết',compute='_ada_id_m2o',store = True)
    padp_ids = fields.Many2many('padp','soi_padp_relate','soi_id','padp_id')
#     padp_ids_char = fields.Char(compute ='_padp_ids_char',store = True)
    soi_goc_id = fields.Many2one('dai_tgg.soi')
    soi_ve_dai = fields.Many2one('dai_tgg.soi')
    #soi_ve_dai_ada_id = fields.Many2one('ada',related='soi_ve_dai.ada_id')
    soi_duoc_chon_id = fields.Many2one('dai_tgg.soi',compute='_soi_duoc_chon_compute',store=True)
    ada_out_id = fields.Many2one('ada',compute = '_ada_out_id_compute',store= True)
    port_thiet_bi = fields.Many2one('port.thiet_bi',compute='_port_thiet_bi_for_soi',store = True)
    soi_id = fields.Many2one('dai_tgg.soi',compute = '_soi_for_soi',store = True)
    co_xai = fields.Integer(compute = '_co_xai',store = True)
    xai_cho_gi = fields.Char(compute= '_xai_cho_gi',store= True)
    tram_ids = fields.Many2many('tram','soi_tram_relate','soi_id','tram_id')
    
#     @api.depends('padp_ids')
#     def _padp_ids_char(self):
#         for r in self:
#             r.padp_ids_char = u';'.join(r.padp_ids.mapped('name'))
    @api.depends('ada_ids_butone')
    def _ada_id_m2o(self):
        self.ada_id = self.ada_ids_butone
    @api.depends('ada_id','ada_id.ada_khac_id','ada_id.ada_khac_id.soi_id')
    def _ada_out_id_compute(self):
        for r in self:
            if r.ada_id:
                if  not r.ada_id.ada_khac_id:
                    r.ada_out_id = r.ada_id
                else:
                    if not r.ada_id.ada_khac_id.soi_id:
                        r.ada_out_id = r.ada_id.ada_khac_id
                    else:
                        r.ada_out_id = False
            else:
                r.ada_out_id = False
    
    #write nguoc lai trong ada_id vs soi_id
    @api.depends('ada_id','soi_ve_dai')
    def _port_thiet_bi_for_soi(self):
        self.port_thiet_bi = self.soi_ve_dai.port_thiet_bi or self.ada_id.port_thiet_bi or self.ada_id.ada_khac_id.port_thiet_bi
    @api.depends('ada_id','soi_ve_dai')
    def _soi_for_soi(self):
        self.soi_id =  self.soi_ve_dai.soi_id or self.ada_id.ada_khac_id.soi_id
    @api.depends('ada_id','port_thiet_bi','soi_id','padp_ids','soi_ve_dai')
    def _xai_cho_gi(self):
        
        for r in self:
            if r.soi_ve_dai.xai_cho_gi:
                r.xai_cho_gi = r.soi_ve_dai.xai_cho_gi
            else:
                xai_cho_gis = []
                padps = r.padp_ids.mapped('pa_hay_dp_n')
                xai_cho_gis.extend(padps)
                if r.port_thiet_bi:
                    xai_cho_gis.append(u'port tb')
                if r.soi_id:
                    xai_cho_gis.append(u'soi')
                r.xai_cho_gi = u','.join(xai_cho_gis)
    @api.depends('xai_cho_gi','soi_ve_dai')
    def _co_xai(self):
        for r in self:
            if r.soi_ve_dai.co_xai:
                r.co_xai = r.soi_ve_dai.co_xai
            elif r.xai_cho_gi:
                r.co_xai = 1
            
    
    @api.depends('soi_goc_id')
    def _soi_duoc_chon_compute(self):
        for r in self:
            if not r.soi_goc_id:
                r.soi_duoc_chon_id = r
            else:
                r.soi_duoc_chon_id =  r.soi_goc_id
    def _write_and_create_common_soi(self,vals,create_object = False):
        
        write_opposite(self,vals,create_object,
                   attr = 'soi_goc_id',attr_model = 'dai_tgg.soi',opposite_attr = 'soi_ve_dai')
    @api.multi
    def write(self,vals):
        ret = super(Soi,self).write(vals)
        self._write_and_create_common_soi(vals)
        return ret
    @api.model
    def create(self,vals):
        this_soi  =  super(Soi, self).create(vals)
        self._write_and_create_common_soi(vals,create_object=this_soi)
        return this_soi
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
            else:
                return False
            if r.soi_goc_id:
                name = name +  u'['+r.soi_goc_id.name + u']'
            
            r.name = name

def write_opposite(self,vals,create_object,
                   attr = 'soi_id',attr_model = 'dai_tgg.soi',opposite_attr = 'ada_id',ep_write = False,write_False = True):
    this_ada = create_object or self
    if attr in vals and 'avoid_recursive_opposite' not in vals   and (write_False or vals[attr] !=False):
        if create_object==None:# write
            attr_object_old = getattr(this_ada, attr)
            id_old_soi_id = attr_object_old.id
            if id_old_soi_id != vals[attr] or ep_write == True:
                if id_old_soi_id:
                    attr_object_old.write({opposite_attr:False,'avoid_recursive_opposite':True })
            if vals[attr]:# write reserver
                soi_id = self.env[attr_model].browse(vals[attr])
                #if getattr(soi_id, opposite_attr) != this_ada.id:
                soi_id.write({opposite_attr:this_ada.id,'avoid_recursive_opposite':True})
        else:#create
            if vals[attr]:
                    soi_id = self.env[attr_model].browse(vals[attr])
                    soi_id.write({opposite_attr:this_ada.id,'avoid_recursive_opposite':True})
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
    adaptor_number = fields.Integer(required = True,string = u'Port',default=1)
    odf_number = fields.Integer(required = True, string = u'O',default=1)
    tu_number = fields.Integer(required = True,default=1,string = u'T')
    soi_id = fields.Many2one('dai_tgg.soi',u"Sợi của Adaptor này")
    soi_goc_id = fields.Many2one('dai_tgg.soi',related="soi_id.soi_goc_id",string=u'Sợi gốc')
    
    soi_out_id = fields.Many2one('dai_tgg.soi',string=u'Sợi được out ra thiết bị từ odf này',compute ='_soi_out_id' ,store = True)
    soi_out_ids = fields.One2many('dai_tgg.soi','ada_out_id')
    port_thiet_bi = fields.Many2one('port.thiet_bi',u"Port thiết bị")
    ada_khac_id = fields.Many2one('ada',u"Adaptor nối nhau")
    #ada_khac_ids = fields.One2many('ada','ada_khac_id')
    
    soi_cua_ada_khac_id = fields.Many2one('dai_tgg.soi', u"Sợi của ada khác",related='ada_khac_id.soi_id')
    port_thiet_bi_cua_ada_khac_id = fields.Many2one('port.thiet_bi',u"Port thiết bị ada khác",related='ada_khac_id.port_thiet_bi')
    padp_ids = fields.Many2many('padp',compute='_padp_compute_for_ada',store=True)
    padp_ids_relate_soi = fields.Many2many('padp',related='soi_id.padp_ids',string = u"padps của sợi id")
    thietbi_char = fields.Char(string = u'Thiết bị')
    phia_sau_odf_la = fields.Selection([('dai_tgg.soi',u'Sợi'),('port.thiet_bi',u'Port thiết bị'),('ada',u'adaptor')],string = u'Phía sau ODF là')
    phia_truoc_odf_la = fields.Selection([('dai_tgg.soi',u'Sợi'),('port.thiet_bi',u'Port thiết bị'),('ada',u'adaptor')],string = u'Phía trước ODF là')
    odf_dau_xa = fields.Char(string = u'odf đầu xa')
    ghi_chu = fields.Char(string = u'ghi chú')
    soi_1_hay_soi_2 = fields.Selection([(1,'in'),(2,'out')])
    couple_ada_id = fields.Many2one('ada')
#     couple_ada_ids = fields.One2many('ada','couple_ada_id')
    ada_type = fields.Char(compute = '_ada_type_compute',store=True)
    is_tach = fields.Boolean()
#     @api.depends('ada_khac_ids')
#     def _ada_khac_id(self):
#         self.ada_khac_id = self.ada_khac_ids
#     @api.depends('couple_ada_ids')
#     def _couple_ada_id(self):
#         self.couple_ada_id = self.couple_ada_ids
    @api.depends('soi_out_ids')
    def _soi_out_id(self):  
        for r in self:
            if len(r.soi_out_ids)>1:
                raise ValueError(r.soi_out_ids.mapped('name'))
            r.soi_out_id = r.soi_out_ids
    def phia_sau_odf_txt(self,phia_sau_odf_la,truoc_hay_sau=None,co_tinh_ada = True, ada = None):
        ada = ada or self
        if phia_sau_odf_la =='ada' and co_tinh_ada:
            if ada.ada_khac_id:
                if self.ada_khac_id.ada_khac_id:
                    no_coexit_ada_txt = u''
                else:
                    no_coexit_ada_txt = u'no coexit ada'
                
                phia_sau_odf_la_of_ada_khac_bool = self.ada_khac_id.phia_sau_odf_la =='dai_tgg.soi' or \
                self.ada_khac_id.phia_sau_odf_la == 'port.thiet_bi'
                if phia_sau_odf_la_of_ada_khac_bool:
                    phia_cua_thiet_bi_or_soi_cua_ada_khac = u'sau'
                    phia_cua_ada_khac = u'trước'
                else:#self.ada_khac_id.phia_sau_odf_la = 'adaptor' or false
                    phia_cua_thiet_bi_or_soi_cua_ada_khac = u'trước'# co the la dp hoac pa
                    phia_cua_ada_khac = u'sau'  
                phia_sau_txt_cua_ada_khac = self.phia_sau_odf_txt(self.ada_khac_id.phia_sau_odf_la,
                                                                  truoc_hay_sau=phia_cua_thiet_bi_or_soi_cua_ada_khac,
                                                                  co_tinh_ada = False,ada =ada.ada_khac_id )
  
                phia_sau_txt = phia_sau_txt_cua_ada_khac + u'(' +  phia_cua_thiet_bi_or_soi_cua_ada_khac +u' ' + no_coexit_ada_txt+ u' ada )' 
            
            
            else:
                phia_sau_txt = u'fuck sao co ada roi lai khong co ada'
        
        elif phia_sau_odf_la =='dai_tgg.soi':
            phia_sau_txt = u'sợi'
        else:# phia truoc
            padps= ada.padp_ids.mapped('pa_hay_dp_n')
            if padps:
                phia_sau_txt = padps[0]
                if u'DP' in phia_sau_txt:
                    phia_sau_txt =u'DP'
            elif phia_sau_odf_la =='port.thiet_bi':
                phia_sau_txt = u'port thiết bị'
            else:
                if truoc_hay_sau == u'sau' and ada.is_tach:
                    phia_sau_txt = u'Tách'
                else:
                    phia_sau_txt = u'trống'
        return phia_sau_txt
    
    
       
    @api.depends('soi_id','port_thiet_bi','ada_khac_id','ada_khac_id.ada_khac_id','phia_sau_odf_la','phia_truoc_odf_la','padp_ids','is_tach')
    def _ada_type_compute(self):
        for r in self:
            phia_sau_odf_la = r.phia_sau_odf_la
            phia_sau_txt = r.phia_sau_odf_txt(phia_sau_odf_la,u'sau')
            phia_truoc_odf_la = r.phia_truoc_odf_la
            phia_truoc_txt = r.phia_sau_odf_txt(phia_truoc_odf_la,u'trước')
            r.ada_type = phia_sau_txt + u'-' + phia_truoc_txt
            
        
            
                
    @api.depends('soi_out_id.padp_ids','soi_out_id.soi_goc_id.padp_ids')
    def _padp_compute_for_ada(self):
        for r in self:
            r.padp_ids = r.soi_out_id.padp_ids or r.soi_out_id.soi_goc_id.padp_ids
    @api.depends('odf_number','tu_number','adaptor_number')
    def _name_compute(self):
        prefix_dict = (('adaptor_number',''), ('odf_number',''), ('tu_number',''))
        for r in self:
            r_names = []
            for i in prefix_dict:
                if getattr(r, i[0]) != False:
                    r_names.append(i[1]  +  str(getattr(r, i[0])))
            
            if r_names:
                name =  '/'.join(r_names)
                r.test_field_name = name
                r.name = name
    
    
    
    def _common_relate_soi(self,vals, create_object = None):
        
        write_opposite(self,vals,create_object,
                    attr ='ada_khac_id', attr_model = 'ada', opposite_attr ='ada_khac_id',write_False = False)    
        #write_opposite(self,vals,create_object,attr = 'soi_id',attr_model = 'dai_tgg.soi',opposite_attr = 'ada_id',ep_write=True)
#          
        write_opposite(self,vals,create_object,
                    attr ='couple_ada_id',attr_model = 'ada',opposite_attr ='couple_ada_id')

                    
#     def compute_ada_out_soi_out(self,vals,create_object = None,write_case_only_update_vals = False):
#         update_dict = {}
#         this_ada_object = create_object or self
#         if "soi_id" in vals or 'ada_khac_id' in vals:
#             soi_id = vals.get('soi_id',False) or this_ada_object.soi_id.id
#             ada_khac_id = vals.get('ada_khac_id',False) or this_ada_object.ada_khac_id.id
#             if soi_id:
#                 soi_id_object = self.env['dai_tgg.soi'].browse(soi_id)
# #                 ada_khac_id = vals.get('ada_khac_id',False)
#                 if ada_khac_id:
#                     ada_khac_id_object = self.env['ada'].browse(ada_khac_id)
#                     if not ada_khac_id_object.soi_id:# ada_khac khong co soi --> ada khac la out
#                         soi_id_object .write({'ada_out_id':ada_khac_id})
#                         ada_khac_id_object.write({'soi_out_id':soi_id})
#                         if write_case_only_update_vals:
#                             vals['soi_out_id'] = False
#                             update_dict['soi_out_id'] = False
#                         else:
#                             this_ada_object.write({'soi_out_id':False})
#                     else:#cungn co soi
#                         soi_id_object .write({'ada_out_id':False})
#                         ada_khac_id_object.write({'soi_out_id':False})
#                         if write_case_only_update_vals:
#                             vals['soi_out_id'] = False
#                             update_dict['soi_out_id'] = False
#                         else:
#                             this_ada_object.write({'soi_out_id':False})
#                 else:
#                     soi_id_object.write({'ada_out_id':this_ada_object.id})
#                     if write_case_only_update_vals:
#                         vals['soi_out_id'] = soi_id
#                         update_dict['soi_out_id'] = soi_id
#                     else:
#                         this_ada_object.write({'soi_out_id':soi_id})
#                     
#             else:# kkhong co soi id
#                 if ada_khac_id:
#                     ada_khac_id_object = self.env['ada'].browse(ada_khac_id)
#                     if not ada_khac_id_object.soi_id:
#                         if write_case_only_update_vals:
#                             vals['soi_out_id'] = False
#                             update_dict['soi_out_id'] = False
#                         else:
#                             this_ada_object.write({'soi_out_id':False})
#                         ada_khac_id_object.write({'soi_out_id':False})
#                     else:#co 1 soi o ada khac
#                         if write_case_only_update_vals:
#                             vals['soi_out_id'] =  ada_khac_id_object.soi_id.id
#                             update_dict['soi_out_id'] = ada_khac_id_object.soi_id.id
#                         else:
#                             this_ada_object.write({'soi_out_id':ada_khac_id_object.soi_id.id})
#                         
#                         ada_khac_id_object.soi_id.write({'ada_out_id':self.id})
#                         ada_khac_id_object.write({'soi_out_id':False})
#                 else:
#                     if write_case_only_update_vals:
#                         vals['soi_out_id'] = False
#                         update_dict['soi_out_id'] = False
#                     else:
#                         this_ada_object.write({'soi_out_id':False})
                                
    
    @api.model
    def create(self,vals):
        this_ada  =  super(OneFaceADA, self).create(vals)
        #self.compute_ada_out_soi_out(vals,create_object = this_ada,write_case_only_update_vals = False) 
        self._common_relate_soi(vals,create_object = this_ada)
        return this_ada
    
    
    
    @api.multi
    def write(self,vals):
        #self.compute_ada_out_soi_out(vals,create_object = None,write_case_only_update_vals = True) 
        self._common_relate_soi(vals)       
        ret  =  super(OneFaceADA, self).write(vals)
        
        return ret
 

