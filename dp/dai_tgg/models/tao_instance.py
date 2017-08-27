 # -*- coding: utf-8 -*-
import re
import xlrd
import datetime
#from models import Model
# Prepare the connection to the server
from odoorpc import models
def get_merged_cell_val(sheet,row,thiet_bi_index,is_return_primary_or_secondary=False):
    is_merge_cell = False
    for  crange in sheet.merged_cells:
        rlo, rhi, clo, chi = crange
        if clo ==thiet_bi_index and chi == thiet_bi_index + 1 and row == rlo:
            thiet_bi_txt = sheet.cell_value(row,thiet_bi_index)
            is_merge_cell = True
            if is_return_primary_or_secondary:
                primary_cell_or_secondary_cell = 1
            break
        elif clo ==thiet_bi_index and chi == thiet_bi_index + 1 and row > rlo and row <rhi :
            thiet_bi_txt = sheet.cell_value(rlo,thiet_bi_index)
            is_merge_cell = True
            if is_return_primary_or_secondary:
                primary_cell_or_secondary_cell = 2
            break
    if not is_merge_cell:
            thiet_bi_txt = sheet.cell_value(row,thiet_bi_index)
            if is_return_primary_or_secondary:
                primary_cell_or_secondary_cell = False
    if is_return_primary_or_secondary:
                return thiet_bi_txt,primary_cell_or_secondary_cell
    else:
        return thiet_bi_txt
def get_id_of_object(tuyen_cap_chinh):
    if isinstance(tuyen_cap_chinh, list):
        tuyen_cap_chinh_id =tuyen_cap_chinh[0]
    elif isinstance(tuyen_cap_chinh,int):
        tuyen_cap_chinh_id = tuyen_cap_chinh
    else:#tuyen_cap_chinh được tạo từ wizard
        tuyen_cap_chinh_id = tuyen_cap_chinh.id
    return tuyen_cap_chinh_id
def covert_object(self,class_name,tuyen_cap_chinh):# mac dinh la tuyen_cap_chinh ton tai
    if isinstance(tuyen_cap_chinh, list):
        tuyen_cap_chinh_id =tuyen_cap_chinh[0]
    elif isinstance(tuyen_cap_chinh,int):
        tuyen_cap_chinh_id = tuyen_cap_chinh
    else:
        return tuyen_cap_chinh
    tuyen_cap_chinh = self.env[class_name].browse(tuyen_cap_chinh_id)
    return tuyen_cap_chinh
    
def get_or_create_object(self,class_name,search_dict,domain_ada_create_write ={}):
    domain_list = []
    for i in search_dict:
        tuple_in = (i,'=',search_dict[i])
        domain_list.append(tuple_in)
    tuyen_cap_chinh  = self.env[class_name].search(domain_list)
    if not tuyen_cap_chinh:
        current_number = create_number_dict.setdefault(class_name,0)
        create_number_dict[class_name] = current_number +  1
        search_dict.update(domain_ada_create_write)
        tuyen_cap_chinh = self.env[class_name].create(search_dict)
    else:
        tuyen_cap_chinh = covert_object(self,class_name,tuyen_cap_chinh)
        is_write = False
        for attr in domain_ada_create_write:
            domain_val = domain_ada_create_write[attr]
            exit_val = getattr(tuyen_cap_chinh,attr)
            exit_val = getattr(exit_val,'id',exit_val)
            if exit_val ==None: #recorderset.id ==None when recorder sset = ()
                exit_val=False
            print attr,exit_val,domain_val,domain_val==exit_val,type(domain_val),type(exit_val)
#             if type(exit_val) ==unicode and type(domain_val) ==float:
#                 domain_val = unicode(domain_val)
            domain_val = list(domain_val) if isinstance(domain_val,tuple) else domain_val
            #print unicode(exit_val),unicode(domain_val),domain_val,unicode(domain_val)==unicode(exit_val)
            if unicode(exit_val) !=unicode(domain_val):
                #raise ValueError('sdfdf')
                is_write = True
                break
        if is_write:
            current_number = update_number_dict.setdefault(class_name,0)
            update_number_dict[class_name] = current_number +  1
            tuyen_cap_chinh.write(domain_ada_create_write)
        else:
            current_number = get_number_dict.setdefault(class_name,0)
            get_number_dict[class_name] = current_number +  1
    return tuyen_cap_chinh #re turn a object recorders
# def replace_name(sheet,row,tuyen_cap_chinh_name,tuyen_cap_chinh_col_maybe_replace_index):
#     if tuyen_cap_chinh_col_maybe_replace_index:
#         tuyen_cap_chinh_col_maybe_replace = sheet.cell_value(row,tuyen_cap_chinh_col_maybe_replace_index)
#         if len(tuyen_cap_chinh_col_maybe_replace)>2:
#             tuyen_cap_chinh_name = tuyen_cap_chinh_col_maybe_replace
#     return  tuyen_cap_chinh_name              
def  choose_between(sheet,row,tuyen_cap_goc_index,tuyen_cap_goc_replace_index,avail_val =None):
    if tuyen_cap_goc_replace_index !=None:
        tuyen_cap_goc_name_replace = sheet.cell_value(row,tuyen_cap_goc_replace_index)
        if isinstance(tuyen_cap_goc_name_replace,unicode) and (tuyen_cap_goc_name_replace!=u'' and tuyen_cap_goc_name_replace!=u'\xa0' ) or \
        isinstance(tuyen_cap_goc_name_replace,float):
            tuyen_cap_goc_name = tuyen_cap_goc_name_replace
            return tuyen_cap_goc_name
    if avail_val ==None:
        tuyen_cap_goc_name = get_merged_cell_val(sheet,row,tuyen_cap_goc_index,is_return_primary_or_secondary= False)
    else:
        return avail_val
    return tuyen_cap_goc_name
EMPTY_CHAR = [u'',u' ',u'\xa0' ]
def check_variable_is_not_empty_string(tuyen_cap_goc_name_replace):
    if  isinstance(tuyen_cap_goc_name_replace,unicode) and (tuyen_cap_goc_name_replace not in EMPTY_CHAR ) or \
        isinstance(tuyen_cap_goc_name_replace,float) or isinstance(tuyen_cap_goc_name_replace,int):
        return True
    else:
        return False
def check_name_after_get_or_create_and_return_id(self,sheet,row,class_name,col_index,col_replace_index,
                                                 key_main = 'name',more_search={},update_dict={},avail_val=None):
    thiet_bi_name = choose_between(sheet,row,col_index,col_replace_index,avail_val=avail_val)
    if check_variable_is_not_empty_string(thiet_bi_name):
        more_search.update({key_main:thiet_bi_name})
        thiet_bi =  get_or_create_object(self,class_name,more_search,update_dict )
        thiet_bi_id = get_id_of_object(thiet_bi)
    else:
        thiet_bi_id = False
    return thiet_bi_id
create_number_dict = {}
update_number_dict = {}     
get_number_dict = {}                                    
                               
def import_ada_prc(self):
        global create_number_dict
        global update_number_dict
        global get_number_dict
        Kieu_2_odf = False
        #raise ValueError(self.env.context)
        #raise ValueError (self.os_choose)
        os_choose = getattr(self,'os_choose',u'linux')
        #os_choose =u'win'
        if os_choose ==u'win':
            path = 'E:\SO DO LUONG\T6-2017\SO DO ODF.xls'#'D:\luong_TGG\O1T1.xls'
        else:
            path = '/media/sf_E_DRIVE/SO DO LUONG/T6-2017/' +  'SO DO ODF.xls'
        excel = xlrd.open_workbook(path,formatting_info=True)#,formatting_info=True
        #raise ValueError( excel.sheet_names())
        sheet_names = excel.sheet_names()
        excute = False
        only_sheet_mode = 0
        sheet_name_choose = 'O.8-T1'
        sheet_name_choose =None
        #file = open("/media/sf_E_DRIVE/SO DO LUONG/log.txt",'w')
        #file.write(str(datetime.datetime.now()))
        #file.write('somethingsss')
        #file.close()
        #raise ValueError('dffd')
        for count_s,sheet_name in enumerate(sheet_names):
            print '***sheet_name***',sheet_name
            create_number_dict = {}
            update_number_dict = {}
            get_number_dict = {}
#             file.write(sheet_name) 
#             file.flush()
            if only_sheet_mode:
                if sheet_name ==sheet_name_choose :
                    excute = True
                else:
                    excute = False
            else:
                if sheet_name_choose ==None:
                    excute = True
                elif sheet_name == sheet_name_choose :
                    excute = True
            if excute:
                pass
            else:
                continue
            sheet = excel.sheet_by_name(sheet_name)
            #raise ValueError(sheet.merged_cells)
            state = 'begin'
#             thiet_bi_txt_truoc=None
#             tuyen_cap_goc_name_bf = False
#             soi_or_thiet_bi_name_before=False
#             tuyen_cap_chinh_name_before = None
#             adaptor_number_before = False
#             thiet_bi_name_before = False
#             tuyen_cap_goc_name_check_count = 0
            tuyen_cap_chinh_col_maybe_replace_index= None
            tuyen_cap_goc_replace_index = None
            soi_goc_index = None
            thiet_bi_replace_index = None
            tach_index= None
    #         already_check_ada_in_col_title = False
    #         already_check_ada_in_col_title = False
            #print sheet.cell_value(3,6)
            #raise ValueError(sheet.cell_value(7,9),type(sheet.cell_value(7,9)),sheet.cell_value(8,9),bool(sheet.cell_value(8,9)))
            #print re.search('\S+','anh yeu em . em co yeu anh khong').group(0)
            #print 'ket qua ne',re.search('\S+',u' ').group(0)
            #raise ValueError(sheet.cell_value(31,2),sheet.cell_value(31,2)==u'\xa0',sheet.cell_value(30,2),sheet.cell_value(30,2)==u'')
            
            
            for row in range(2,sheet.nrows):
                #mat_sau_mode =None
                if state == 'begin':
                    for col in range(0,sheet.ncols):
                        if state == 'begin':
                            pattern = u'O\.(\d+)[\s-]+T\.(\d+)' 
                            rs = re.search(pattern, sheet.cell_value(row,col))
                            if rs:
                                o_value,t_value = int(rs.group(1)),int(rs.group(2))
                                state = 'title row'
                                continue
                elif state == 'title row':
                    for col in range(0,sheet.ncols):
                        if  u'ADA' in sheet.cell_value(row,col):
                            state = 'data'
                            data_row = row + 1
                            if col == 2:
                                offset = 0
                                tuyen_cap_goc_index = None
                            elif col ==3:
                                offset =1
                                tuyen_cap_goc_index = 1
                            
                            tuyen_cap_chinh_col_index = 0
                            ada_index = 2 + offset
                            soi_index = 1 + offset
                            thiet_bi_index = 3 + offset
                            odf_dau_xa_index = 4 + offset
                            ghi_chu_index = 5 + offset
                            #continue
                        if u'tc' in sheet.cell_value(row,col):
                            tuyen_cap_chinh_col_maybe_replace_index = col
                        if u'cap goc' in sheet.cell_value(row,col):
                            tuyen_cap_goc_replace_index = col
                        if u'soi goc' in sheet.cell_value(row,col):
                            soi_goc_index = col
                        if u'thiet_bi_replace' in sheet.cell_value(row,col):
                            thiet_bi_replace_index = col
                        if u'tach' in sheet.cell_value(row,col):
                            tach_index = col
                elif state == 'data':
                    print '<row>',row
                    ada_data = {}
                    domain_ada_create_write = {}
                    ada_data['odf_number'] = o_value
                    ada_data['tu_number'] = t_value
                    adaptor_number = sheet.cell_value(row,ada_index)
                    adaptor_val = get_merged_cell_val(sheet,row,ada_index)
                    if row> data_row + 47:
                        break
                    if check_variable_is_not_empty_string(adaptor_val):
                        pass
                    else:
                        continue
                    adaptor_number = str(int(adaptor_val))
                    ada_data['adaptor_number'] = adaptor_number
#                     if  Kieu_2_odf:
#                         ada_data['truoc_hay_sau'] = u'sau'
                    
                    
                    
#                     ada = self.env['ada'].search([('adaptor_number','=',adaptor_number),
#                                                   ('odf_number','=',o_value),('tu_number','=',t_value),
#                                                   ('truoc_hay_sau','=',u'sau'),
#                                                   ])
                    soi_or_thiet_bi_name = get_merged_cell_val(sheet,row,soi_index)
                    try:#kiem tra interge hay khong
                        stt_soi = int(soi_or_thiet_bi_name)
                        mat_sau_mode = 'soi'
                    except:
                        if check_variable_is_not_empty_string(soi_or_thiet_bi_name):
                            mat_sau_mode = 'port thiet bi'
                        else:# con lai la rong 
                            mat_sau_mode = None
                            stt_soi=None
                    if mat_sau_mode == 'port thiet bi':
                        
                        thiet_bi_id = check_name_after_get_or_create_and_return_id(self,sheet,row,'thietbi',0,thiet_bi_replace_index,
                                                 key_main = 'name',more_search={},update_dict={})
                        
                        name_port_thiet_bi = soi_or_thiet_bi_name
                        port_tb = get_or_create_object(self,'port.thiet_bi', {'port_name':name_port_thiet_bi,'thiet_bi_id':thiet_bi_id})
                        port_thiet_bi_id = get_id_of_object(port_tb)
                        domain_ada_create_write['port_thiet_bi'] = port_thiet_bi_id
                        if port_thiet_bi_id !=False:
                            #raise ValueError('adfd',port_thiet_bi_id)
                            domain_ada_create_write['phia_sau_odf_la'] = 'port.thiet_bi'
                    elif mat_sau_mode == 'soi':
                        #raise ValueError('soi')
                        tuyen_cap_chinh_id = check_name_after_get_or_create_and_return_id(self,sheet,row,'tuyen_cap',tuyen_cap_chinh_col_index,tuyen_cap_chinh_col_maybe_replace_index,
                                                 key_main = 'name',more_search={},update_dict={})
                        if tuyen_cap_chinh_id:
                            soi_goc_id=False
                            if tuyen_cap_goc_index !=None:
                                tuyen_cap_goc_id = \
                                check_name_after_get_or_create_and_return_id(self,sheet,row,'tuyen_cap',
                                                tuyen_cap_goc_index,tuyen_cap_goc_replace_index,key_main = 'name'  )    
                                if tuyen_cap_goc_id: 
                                    soi_goc_id = check_name_after_get_or_create_and_return_id(self,sheet,row,'dai_tgg.soi',
                                                None,soi_goc_index,
                                                 key_main = 'stt_soi',
                                                 more_search = {'tuyen_cap':tuyen_cap_goc_id}, 
                                                 avail_val=stt_soi
                                              )
                            if tach_index:
                                is_tach = sheet.cell_value(row,tach_index)
                                is_tach = check_variable_is_not_empty_string(is_tach)
                            else:
                                is_tach = False
                            soi_id = check_name_after_get_or_create_and_return_id(self,sheet,row,'dai_tgg.soi',None,None,
                                                 key_main = 'stt_soi',
                                                 more_search={'tuyen_cap':tuyen_cap_chinh_id},
                                                 update_dict={'soi_goc_id':soi_goc_id},
                                                 avail_val=stt_soi)
                            if is_tach:
                                soi_id = False
                            domain_ada_create_write['soi_id'] = soi_id
                            if soi_id !=False:
                                domain_ada_create_write['phia_sau_odf_la'] = 'dai_tgg.soi'
                    rs = get_merged_cell_val(sheet,row,thiet_bi_index,is_return_primary_or_secondary=True)
                    thiet_bi_txt = rs[0]
                    primary_cell_or_secondary_cell = rs[1]
                    if check_variable_is_not_empty_string(thiet_bi_txt):
                        rs = re.findall(r'((\d{1,2}),\s*(\d{1,2}) O\.{0,1}(\d{1,2}).{0,3}T(\d{1,2}))',thiet_bi_txt)
                        if rs:
                            odf_duoc_tach = rs
#                             ada_ref_data = {'tu_number':rs[4],'adaptor_number','odf_number':rs[3]}
#                             get_or_create_object('ada', {}, domain_ada_create_write={})
                        else:
                            odf_duoc_tach = False
                    else:
                        thiet_bi_txt = False
                        odf_duoc_tach = False

                    
                    odf_dau_xa = get_merged_cell_val(sheet,row,odf_dau_xa_index)
                    if check_variable_is_not_empty_string(odf_dau_xa):
                        pass
                    else:
                        odf_dau_xa = False
                    
                    ghi_chu = get_merged_cell_val(sheet,row,ghi_chu_index)
                    if check_variable_is_not_empty_string(ghi_chu):
                        pass
                    else:
                        ghi_chu = False
                          
                    #ada_data['thietbi_char'] = thiet_bi_txt
                    
                    
                    if odf_duoc_tach:
                        odf_duoc_tach = odf_duoc_tach[0]
                        print 'odf_duoc_tach',odf_duoc_tach
                        if primary_cell_or_secondary_cell==2:
                            connect_adaptor_number = odf_duoc_tach[2]
                        elif primary_cell_or_secondary_cell==1:
                            connect_adaptor_number = odf_duoc_tach[1]
                        else:
                            connect_adaptor_number = odf_duoc_tach[1]
                        connect_ada_data = {'tu_number':odf_duoc_tach[4],'adaptor_number':connect_adaptor_number,'odf_number':odf_duoc_tach[3]}
                        connect_ada = get_or_create_object(self,'ada', connect_ada_data, domain_ada_create_write={})
                        connect_ada_id = get_id_of_object(connect_ada)
                        domain_ada_create_write.update({'phia_truoc_odf_la':'ada'})
                    else:
                        connect_ada_id = False
                    domain_ada_create_write.update({'thietbi_char':thiet_bi_txt,
                                                       'odf_dau_xa':odf_dau_xa,
                                                       'ghi_chu':ghi_chu,
                                                       'odf_duoc_tach':odf_duoc_tach,
                                                       'ada_khac_id':connect_ada_id,
                                                       'soi_1_hay_soi_2':primary_cell_or_secondary_cell
                                                       })
                    
                    print 'primary_cell_or_secondary_cell',primary_cell_or_secondary_cell
                    if primary_cell_or_secondary_cell==2:
                        domain_ada_create_write.update({'couple_ada_id':primary_ada_id})
                    ada_ret = get_or_create_object(self,'ada',ada_data,
                                 domain_ada_create_write =domain_ada_create_write)
                    if primary_cell_or_secondary_cell==1:
                        primary_ada_id = get_id_of_object(ada_ret)
                    
                    print '</row>'
            get_or_create_object(self,'dai.log',{'sheet_name':sheet_name},
                                 domain_ada_create_write ={'create_number_dict':create_number_dict,
                                                       'update_number_dict':update_number_dict,
                                                       'get_number_dict':get_number_dict})
        #file.close()
def import_user (odoo_or_self_of_wizard):
    self = odoo_or_self_of_wizard
    os_choose = getattr(self,'os_choose',u'linux')
    if os_choose ==u'win':
        path = 'E:\SO DO LUONG\DANH SACH LĐ DAI TGG 04-2017.xls'#'D:\luong_TGG\O1T1.xls'
    else:
        path = '/media/sf_E_DRIVE/SO DO LUONG/' +  'DANH SACH LĐ DAI TGG 04-2017.xls'
    excel = xlrd.open_workbook(path,formatting_info=True)#,formatting_info=True
    sheet = excel.sheet_by_name(u'ĐÀI TGG')
    name_index = 2
    gioi_tinh_index  =3
    ngay_sinh_index = 4
    email_index = 5
    so_dt_index = 6
    tram_index = 7
    chuc_danh_index = 8
    for row in range(2,sheet.nrows):
        name = sheet.cell_value(row,name_index)
        #email = sheet.cell_value(row,email_index)
        user_id = check_name_after_get_or_create_and_return_id(self,sheet,row,'res.users',
                                                     email_index,None,
                                                 key_main = 'login',more_search={'name':name},update_dict={'password':'123456'},avail_val=None) 
        print user_id
    
    
    
    
def test_depend_onchange(odoo):       
    id_trave = odoo.env['ada'].create({'name':'dauphong','truoc_hay_sau':u'sau',
                                       'adaptor_number':2,
                                       'odf_number':2,
                                       'tu_number':2,
                                       'test_3':'coi thu test 4,5 co gi thay doi ko',
                                       #'test_2':'reassign test 2'
                                       })
    print 'id_trave',id_trave     
def test_write_ada(odoo):
    ada = odoo.env['ada'].browse(2152)
    print ada.soi_id
    kq = ada.write({'soi_id':9})
    print kq
def test_compare_object_id_with_id(odoo):
    ada = odoo.env['ada'].search([('odf_number','=',1),('tu_number','=',2),('adaptor_number','=',1)])
    ada = covert_object(odoo,'ada', ada)
    
    raise ValueError(getattr(ada.soi_id,'id',ada.soi_id )==5642)
if __name__ =='__main__':
    import odoorpc
    odoo = odoorpc.ODOO('localhost', port=8069)
    # Check available databases
    print(odoo.db.list())
    # Login
    #odoo.login('db_name', 'user', 'passwd')
    odoo.login('2606', 'nguyenductu@gmail.com', '228787')
    #import_user(odoo)
    import_ada_prc(odoo) 
    #test_compare_object_id_with_id(odoo)
           
    #test_write_ada(odoo)         