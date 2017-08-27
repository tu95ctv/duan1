# -*- coding: utf-8 -*-
import odoorpc
import re
print odoorpc 
import xlrd
# Prepare the connection to the server

def import_ada_prc(self):
        path = 'E:\SO DO LUONG\T6-2017\SO DO ODF.xls'#'D:\luong_TGG\O1T1.xls'
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
                        
                    #raise ValueError(tuyen_cap_chinh,type(tuyen_cap_chinh),tuyen_cap_chinh.id)
                    if isinstance(tuyen_cap_chinh, list):
                        tuyen_cap_chinh_id =tuyen_cap_chinh[0]
                    elif isinstance(tuyen_cap_chinh,int):
                        tuyen_cap_chinh_id = tuyen_cap_chinh
                    else:
                        tuyen_cap_chinh_id = tuyen_cap_chinh.id
                    soi = self.env['dai_tgg.soi'].search([('stt_soi','=',stt_soi),('tuyen_cap','=',tuyen_cap_chinh_id)])
                    if not soi:
                        soi = self.env['dai_tgg.soi'].create({'stt_soi':stt_soi,'tuyen_cap':tuyen_cap_chinh_id})
                        #raise ValueError(soi,type(soi))
                    if isinstance(soi, list):
                        soi_id =soi[0]
                    elif isinstance(soi,int):
                        soi_id = soi
                    else:
                        soi_id = soi.id    
                    ada_data['soi_id'] = soi_id
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
   
                if not ada:
                    rt = self.env['ada'].create(ada_data)
                    print 'ada duoc tao',rt
                else:
                    if isinstance(ada,list):
                        ada = self.env['ada'].browse(ada)
                        #ada_cung_soi = self.env['ada'].search([('soi_id','=',soi_id)])
                        #raise ValueError( ada.id,ada.soi_id,ada.truoc_hay_sau,ada_cung_soi )
                        #raise ValueError(ada_data['soi_id'],ada.soi_id,type(ada.soi_id),ada_data['soi_id'] ==ada.soi_id[0])
                        if  'soi_id' in ada_data and ada_data['soi_id'] ==ada.soi_id.id:
                            del ada_data['soi_id']
                            #raise ValueError(ada_data)
                            #raise ValueError(ada_data)
                    ada.write(ada_data)
                    
if __name__ =='__main__':
    odoo = odoorpc.ODOO('localhost', port=8069)
    # Check available databases
    print(odoo.db.list())
    # Login
    #odoo.login('db_name', 'user', 'passwd')
    odoo.login('2606', 'nguyenductu@gmail.com', '228787')
    #
    # Current user
    # user = odoo.env.user
    # print(user.name)            # name of the user connected
    # print(user.company_id.name) # the name of its company
    # ist = odoo.env['res.users'].create({'name':'anh','login':'new_user@yahoo.com','password':'228787'})
    # print ist
    import_ada_prc(odoo)                 