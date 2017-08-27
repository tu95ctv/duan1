# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions
import xlrd
import base64
import re
from odoo.osv import expression    
from tao_instance import import_ada_prc,import_user

class WordPrint(models.TransientModel):
    _name = "wordprint"
    #data = fields.Binary('File')
    @api.multi
    def wordprint(self):
        raise ValueError(len(self._context.get('active_ids', [])))

class ADAExport(models.TransientModel):
    _name = "ada.export"
    _description = "ada Ex"
    #data = fields.Binary('File')
    @api.multi
    def export(self):
        raise ValueError(len(self._context.get('active_ids', [])))

class IDAImport(models.TransientModel):
    _name = "dai_tgg.ada_import"
    _description = "ada Import"
    os_choose = fields.Selection(selection=[(u'win',u'win'),(u'linux',u'linux')],default=u'linux')
    only_sheet_mode = fields.Boolean()
    sheet_name_choose = fields.Char(default = u'O.4-T1')
    @api.multi
    def import_user(self):
        import_user(self)
        
    #data = fields.Binary('File')
    @api.multi
    def import_thiet_bi(self):
        path = '/media/d4/Data/luong_TGG/MTO-CQ dang su dung va DP 30-04-2017-BC.xlsx'
        excel = xlrd.open_workbook(path)
        sheet = excel.sheet_by_name('Thiet bi')
        for row in range(2,sheet.nrows):
            print 'row'*20,row
            huong = sheet.cell_value(row,1)
            if not huong:
                state = 'second'
            else:
                state = 'first'
            if state == 'first':  
                huong_name = sheet.cell_value(row,1) 
                tuyen_cap = sheet.cell_value(row,2)
                so_tt_tren_odf = sheet.cell_value(row,3)
            else:
                odf_xa_1 = sheet.cell_value(row,3)
            print 'tuyen_cap',tuyen_cap
            rs  = re.search(r'(.*?)/(.*?)$', tuyen_cap,re.DOTALL)
            
            tuyen_cap_name = rs.group(2)
            tuyen_cap_obj = self.env['tuyen_cap'].search([('name','=',tuyen_cap_name)])
            if not tuyen_cap_obj:
                tuyen_cap_obj = self.env['tuyen_cap'].create({'name':tuyen_cap_name})
            soi_1_name,soi_2_name = rs.group(1).split(',')
            soi_1 = self.env['dai_tgg.soi'].search([('name','=',soi_1_name),('tuyen_cap','=',tuyen_cap_obj.id)])
            if not soi_1:
                soi_1 = self.env['dai_tgg.soi'].create({'name':soi_1_name,'tuyen_cap':tuyen_cap_obj.id})
            soi_2 = self.env['dai_tgg.soi'].search([('name','=',soi_2_name),('tuyen_cap','=',tuyen_cap_obj.id)])
            if not soi_2:
                soi_2 = self.env['dai_tgg.soi'].create({'name':soi_2_name,'tuyen_cap':tuyen_cap_obj.id})
            huong_obj = self.env['huong'].search([('name','=',huong_name)])
            if not huong_obj:
                huong_obj = self.env['huong'].create({'name':huong_name,
                                                      'soi_cap_phuong_an_ids':[soi_1.id,soi_1.id]
                                                      })
            else:
                huong_obj.write({'name':huong_name,
                                                      'soi_cap_phuong_an_ids':[(6,0, [soi_1.id,soi_2.id])]
                                                      })
                
                print '***'*20,[soi_1.id,soi_1.id]
                
    @api.multi
    def import_ada(self):
        import_ada_prc(self)
    @api.multi
    def import_ada_1(self):
        path = 'E:\SO DO LUONG\T6-2017\SO DO ODF.xlsx'#'D:\luong_TGG\O1T1.xls'
        path = '/media/sf_E_DRIVE/SO DO LUONG/T6-2017/' +  'SO DO ODF.xls'
        excel = xlrd.open_workbook(path,formatting_info=True)#,formatting_info=True
        sheet = excel.sheet_by_name('O.7-T1')
        #raise ValueError(sheet.merged_cells)
        state = 'begin'
        for row in range(2,sheet.nrows):
            if state == 'begin':
                for col in range(0,sheet.ncols):
                    if state == 'begin':
                        #pattern = u'BẢNG PHÂN BỐ SỢI QUANG O\.(\d+)[\s–]+T\.(\d+)'
                        pattern = u'O\.(\d+)[\s-]+T\.(\d+)' 
                        #raise ValueError(sheet.cell_value(row,col),type(sheet.cell_value(row,col)))
                        rs = re.search(pattern, sheet.cell_value(row,col))
                        if rs:
                            o_value,t_value = int(rs.group(1)),int(rs.group(2))
                            state = 'title row'
                            continue
            elif state == 'title row':
                for col in range(0,sheet.ncols):
                    if  u'ADA' in sheet.cell_value(row,col):
                        state = 'data'
                        offset = col
                        if offset == 2:
                            tuyen_cap_chinh_col_index = 0
                            ada_index = 2
                            soi_index = 1
                            thiet_bi_index = 3
                            odf_dau_xa_index = 4
                            ghi_chu_index = 5 
                        continue
            elif state == 'data':
                ada_data = {}
                ada_data['odf_number'] = o_value
                ada_data['tu_number'] = t_value
                adaptor_number = sheet.cell_value(row,ada_index)
                try:
                    adaptor_number = str(int(adaptor_number))
                except ValueError: #invalid literal for int() with base 10: ''
                    continue
                ada_data['adaptor_number'] = adaptor_number
                ada = self.env['ada'].search([('adaptor_number','=',adaptor_number),('odf_number','=',o_value),('tu_number','=',t_value)])
#                 if ada :
#                     continue
                try:
                    stt_soi = int(sheet.cell_value(row,soi_index))
                except:
                    stt_soi = False
                print ('adaptor_number',adaptor_number,'stt_soi',stt_soi)
                if stt_soi:
                    tuyen_cap_chinh_name =   sheet.cell_value(row,tuyen_cap_chinh_col_index)
                    if tuyen_cap_chinh_name == '':
                        tuyen_cap_chinh_name = tuyen_cap_chinh_name_before
                    tuyen_cap_chinh_name_before = tuyen_cap_chinh_name
                    tuyen_cap_chinh  = self.env['tuyen_cap'].search([('name','=',tuyen_cap_chinh_name)])
                    if not tuyen_cap_chinh:
                        tuyen_cap_chinh = self.env['tuyen_cap'].create({'name':tuyen_cap_chinh_name})
                    soi = self.env['dai_tgg.soi'].search([('stt_soi','=',stt_soi),('tuyen_cap','=',tuyen_cap_chinh.id)])
                    if not soi:
                        soi = self.env['dai_tgg.soi'].create({'stt_soi':stt_soi,'tuyen_cap':tuyen_cap_chinh.id})
                    ada_data['soi_id'] = soi.id
                ada_data['truoc_hay_sau'] = u'sau'
                is_merge_cell = False
                for  crange in sheet.merged_cells:
                    rlo, rhi, clo, chi = crange
                    if clo ==thiet_bi_index and chi == thiet_bi_index + 1 and row == rlo:
                        thiet_bi_txt = sheet.cell_value(row,thiet_bi_index)
                        thiet_bi_txt_truoc = thiet_bi_txt
                        is_merge_cell = True
                    elif clo ==thiet_bi_index and chi == thiet_bi_index + 1 and row > rlo and row <rhi :
                        thiet_bi_txt = thiet_bi_txt_truoc
                        is_merge_cell = True
                if  is_merge_cell == False:
                        thiet_bi_txt = sheet.cell_value(row,thiet_bi_index)
                ada_data['thietbi_char'] = thiet_bi_txt
                
                    
                    
                    
                
                
                #create this_ref
#                 this_ref = self.env['ada.reference'].search([('soi_id','=',soi.id)])
#                 if this_ref:
#                     pass
#                 else:
#                     this_ref = self.env['ada.reference'].create({
#                         'soi_id':soi.id
#                         })
#                 ada_data['phia_sau_odf_selection_id'] = this_ref.id
#                 ada_data ['thiet_bi'] = sheet.cell_value(row,thiet_bi_index)
#                 ada_data ['odf_dau_xa'] = sheet.cell_value(row,odf_dau_xa_index)
                if not ada:
                    rt = self.env['ada'].create(ada_data)
                    print 'ada duoc tao',rt.id
                else:
                    ada.write(ada_data)
                    
                    
                    
    @api.multi
    def import_site(self):
        path = '/media/d4/Data/luong_TGG/O1T1.xls'#'D:\luong_TGG\O1T1.xls'
        excel = xlrd.open_workbook(path,formatting_info=True)
        sheet = excel.sheet_by_name('O9-T1')
        state = 'begin'
        for row in range(0,sheet.nrows):
            if state == 'begin':
                for col in range(0,sheet.ncols):
                    if state == 'begin':
                        #pattern = u'BẢNG PHÂN BỐ SỢI QUANG O\.(\d+)[\s–]+T\.(\d+)'
                        pattern = u'O\.(\d+)[\s–]+T\.(\d+)'
                        rs = re.search(pattern, sheet.cell_value(row,col))
                        if rs:
                            o_value,t_value = int(rs.group(1)),int(rs.group(2))
                            state = 'title row'
            elif state == 'title row':
                for col in range(0,sheet.ncols):
                    if  sheet.cell_value(row,col) =='ADA':
                        state = 'data'
                        offset = col
                        if offset == 2:
                            tuyen_cap_chinh_col_index = 0
                            ada_index = 2
                            soi_index = 1
                            thiet_bi_index = 3
                            odf_dau_xa_index = 4
                            ghi_chu_index = 5 
                        continue
            elif state == 'data':
                ada_data = {}
                ada_data['odf_number'] = o_value
                ada_data['tu_number'] = t_value
                ada_name = sheet.cell_value(row,ada_index)
                print 'ada_name',ada_name
                try:
                    ada_name = str(int(ada_name))
                except ValueError: #invalid literal for int() with base 10: ''
                    continue
                ada = self.env['dai_tgg.ada'].search([('name','=',ada_name),('odf_number','=',o_value),('tu_number','=',t_value)])
#                 if ada :
#                     continue
                ada_data['name'] = ada_name
                print 'row','col',row,tuyen_cap_chinh_col_index
                
                tuyen_cap_chinh_name =   sheet.cell_value(row,tuyen_cap_chinh_col_index)
                if tuyen_cap_chinh_name == '':
                    tuyen_cap_chinh_name = tuyen_cap_chinh_name_before
                tuyen_cap_chinh_name_before = tuyen_cap_chinh_name
                tuyen_cap_chinh  = self.env['tuyen_cap'].search([('name','=',tuyen_cap_chinh_name)])
                if not tuyen_cap_chinh:
                    tuyen_cap_chinh = self.env['tuyen_cap'].create({'name':tuyen_cap_chinh_name})
                #ada_data['tuyen_cap_chinh'] = tuyen_cap_chinh.id
                soi_name = int(sheet.cell_value(row,soi_index))
                soi = self.env['dai_tgg.soi'].search([('name','=',soi_name),('tuyen_cap','=',tuyen_cap_chinh.id)])
                if not soi:
                    soi = self.env['dai_tgg.soi'].create({'name':soi_name,'tuyen_cap':tuyen_cap_chinh.id})
                ada_data['soi'] = soi.id 
                
                #create this_ref
                this_ref = self.env['ada.reference'].search([('soi_id','=',soi.id)])
                if this_ref:
                    pass
                else:
                    this_ref = self.env['ada.reference'].create({
                        'soi_id':soi.id
                        })
                ada_data['phia_sau_odf_selection_id'] = this_ref.id
                ada_data ['thiet_bi'] = sheet.cell_value(row,thiet_bi_index)
                ada_data ['odf_dau_xa'] = sheet.cell_value(row,odf_dau_xa_index)
                if not ada:
                    self.env['dai_tgg.ada'].create(ada_data)
                else:
                    ada.write(ada_data)
            #reads.append(rows)
            #raise ValueError ('reads',sheet.merged_cells,reads) 
                    