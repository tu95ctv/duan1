 # -*- coding: utf-8 -*-
 
import re
import xlrd
import time
import datetime
from odoo.exceptions import UserError
import logging
from odoo import  fields
import base64
from copy import deepcopy
def get_merged_cell_val(sheet,row,col_index,is_return_primary_or_secondary=False):
    is_merge_cell = False
    for  crange in sheet.merged_cells:
        rlo, rhi, clo, chi = crange
        if clo ==col_index and chi == col_index + 1 and row == rlo:
            readed_xl_val = sheet.cell_value(row,col_index)
            is_merge_cell = True
            if is_return_primary_or_secondary:
                primary_cell_or_secondary_cell = 1
            break
        elif clo ==col_index and chi == col_index + 1 and row > rlo and row <rhi :
            readed_xl_val = sheet.cell_value(rlo,col_index)
            is_merge_cell = True
            if is_return_primary_or_secondary:
                primary_cell_or_secondary_cell = 2
            break
    if not is_merge_cell:
            readed_xl_val = sheet.cell_value(row,col_index)
            if is_return_primary_or_secondary:
                primary_cell_or_secondary_cell = False
    if is_return_primary_or_secondary:
                return readed_xl_val,primary_cell_or_secondary_cell
    else:
        return readed_xl_val
    
    
def get_id_of_object(mess_object):
#     if isinstance(mess_object, list):
#         mess_object_id =mess_object[0]
#     elif isinstance(mess_object,int):
#         mess_object_id = mess_object
#     else:#mess_object được tạo từ wizard
#         mess_object_id = mess_object.id
    return mess_object.id

def convert_object(self,class_name,mess_object):# mac dinh la mess_object ton tai
    if isinstance(mess_object, list):
        mess_object_id =mess_object[0]
    elif isinstance(mess_object,int):
        mess_object_id = mess_object
    else:
        return mess_object
    mess_object = self.env[class_name].browse(mess_object_id)
    return mess_object
    
def get_or_create_object(self,class_name,search_dict,create_write_dict ={},is_must_update=True):
    domain_list = []
    for i in search_dict:
        tuple_in = (i,'=',search_dict[i])
        domain_list.append(tuple_in)
    searched_object  = self.env[class_name].search(domain_list)
    if not searched_object:
        current_number = create_number_dict.setdefault(class_name,0)
        create_number_dict[class_name] = current_number +  1
        search_dict.update(create_write_dict)
        update_search_dict = search_dict
        created_object = self.env[class_name].create(update_search_dict)
        created_object = convert_object(self,class_name,created_object)
        return created_object
    else:
        searched_object = convert_object(self,class_name,searched_object)
        is_write = False
        for attr in create_write_dict:
            domain_val = create_write_dict[attr]
            exit_val = getattr(searched_object,attr)
            exit_val = getattr(exit_val,'id',exit_val)
            if exit_val ==None: #recorderset.id ==None when recorder sset = ()
                exit_val=False
            if unicode(exit_val) !=unicode(domain_val):
                is_write = True
                break
        if is_write or is_must_update:
            current_number = update_number_dict.setdefault(class_name,0)
            update_number_dict[class_name] = current_number +  1
            searched_object.write(create_write_dict)
        else:
            current_number = get_number_dict.setdefault(class_name,0)
            get_number_dict[class_name] = current_number +  1
    return searched_object #re turn a object recorders

choose_between(sheet,row,master_col_index,replace_col_index,avail_val =None):
    if replace_col_index !=None:
        second_name_replace = sheet.cell_value(row,replace_col_index)
        if check_variable_is_not_empty_string(second_name_replace):
            master_name = second_name_replace
            return master_name
    if avail_val ==None:
        master_name = get_merged_cell_val(sheet,row,master_col_index)
    else:
        return avail_val
    return master_name
EMPTY_CHAR = [u'',u' ',u'\xa0' ]
def check_variable_is_not_empty_string(readed_xl_value):
    if  isinstance(readed_xl_value,unicode) :
        if readed_xl_value  in EMPTY_CHAR:
            return False
        rs = re.search('\S',readed_xl_value)
        if not rs:
            return False
    return True
            
#     if  isinstance(readed_xl_value,unicode) and (readed_xl_value not in EMPTY_CHAR ) or \
#         isinstance(readed_xl_value,float) or isinstance(readed_xl_value,int):
#         
#         rs = re.search('\S',readed_xl_value)
#         if not rs:
#             return False
#         else:
#             return True
#     else:
#         return False
    
def choose_between_check_name_and_get_or_create_and_return_id(self,sheet,row,class_name,col_index,col_replace_index,
                                                 key_main = 'name',more_search={},update_dict={},avail_val=None,change_name_function = None):
    thiet_bi_name = choose_between(sheet,row,col_index,col_replace_index,avail_val=avail_val)
    
    if check_variable_is_not_empty_string(thiet_bi_name):
        if change_name_function:
            thiet_bi_name = change_name_function (thiet_bi_name)
        more_search.update({key_main:thiet_bi_name})
        thiet_bi =  get_or_create_object(self,class_name,more_search,update_dict )
        thiet_bi_id = get_id_of_object(thiet_bi)
    else:
        thiet_bi_id = False
    return thiet_bi_id
create_number_dict = {}
update_number_dict = {}     
get_number_dict = {}  


def read_cell_and_check_false(sheet,row,more_padp_soi_index):
    if more_padp_soi_index != None:
        padp_soi_txt = sheet.cell_value(row,more_padp_soi_index)
        if check_variable_is_not_empty_string(padp_soi_txt):
            return padp_soi_txt
        else:
            return False
    else:
        return False
    
                              
def simple_get_odf_dau_xa_and_ghi_chu(sheet,row,odf_dau_xa_index,ghi_chu_index):
    odf_dau_xa = get_merged_cell_val(sheet,row,odf_dau_xa_index)
    if check_variable_is_not_empty_string(odf_dau_xa):
        odf_dau_xa = unicode(odf_dau_xa)
    else:
        odf_dau_xa = False
    ghi_chu = get_merged_cell_val(sheet,row,ghi_chu_index)
    if check_variable_is_not_empty_string(ghi_chu):
        pass
    else:
        ghi_chu = False
    return odf_dau_xa,ghi_chu

def create_connect_ada_id(self,thiet_bi_txt,primary_cell_or_secondary_cell,create_write_dict):
    if thiet_bi_txt:
        connect_ada_khac_reg_rs = re.findall(r'((\d{1,2}),\s*(\d{1,2}) O\.{0,1}(\d{1,2}).{0,3}T.{0,2}(\d{1,2}))',thiet_bi_txt,re.I)
        if connect_ada_khac_reg_rs:
            ada_khac_findall_rs = connect_ada_khac_reg_rs[0]
        else:
            ada_khac_findall_rs = False
    else:
        return False
    if ada_khac_findall_rs:
        if primary_cell_or_secondary_cell==2:
            connect_adaptor_number = ada_khac_findall_rs[2]
        elif primary_cell_or_secondary_cell==1:
            connect_adaptor_number = ada_khac_findall_rs[1]
        else:
            connect_adaptor_number = ada_khac_findall_rs[1]
        connect_ada_data = {'tu_number':ada_khac_findall_rs[4],'adaptor_number':connect_adaptor_number,'odf_number':ada_khac_findall_rs[3]}
        connect_ada = get_or_create_object(self,'ada', connect_ada_data, create_write_dict={})
        connect_ada_id = get_id_of_object(connect_ada)
        create_write_dict['ada_khac_id'] = connect_ada_id
        if 'phia_sau_odf_la' in create_write_dict:
            create_write_dict.update({'phia_truoc_odf_la':'ada'})
        else:
            create_write_dict.update({'phia_sau_odf_la':'ada'})
    else:
        connect_ada_id = False
    return connect_ada_id

def tram_ids_compute_for_soi(self,thiet_bi_txt,odf_dau_xa,soi_id,more_padp_txt):      
    if soi_id:
        find_tram_list =   []
        if more_padp_txt:
            find_tram_list.append(more_padp_txt)
        elif thiet_bi_txt:
            find_tram_list.append(thiet_bi_txt)
        if odf_dau_xa:
            find_tram_list.append(odf_dau_xa)
        
        tram_list = []
        for x in find_tram_list:
            huong_name_reg_rs = re.findall('LAN|PTR|LTK|DTP|CLH|VLG|CTO|HPU|TVH|BTE|TTI',x,re.I)
            if huong_name_reg_rs:
                for i in huong_name_reg_rs:
                    tram_list.append(i)
        tram_list_filter = []        
        for huong_name in tram_list:   
            if huong_name== u'ĐTP' or huong_name ==u'DTP' or huong_name == u'CLH':
                huong_name = u'CLH'
            huong_name = huong_name.upper()
            if huong_name not in tram_list_filter:
                tram_list_filter.append(huong_name)
                tram = get_or_create_object(self,'tram',
                                                 {'name':huong_name})
                tram.write({'soi_ids':[(4,soi_id)]})
def create_padp(self,soi_id,thiet_bi_txt,sheet,row,more_padp_soi_index=None):
    thiet_bi_txt_add_padp_soi_s = []
    if  SOI_OR_ODF_PADP_MODE =='soi' :
        if soi_id !=False:
            if more_padp_soi_index != None:
                padp_soi_txt = sheet.cell_value(row,more_padp_soi_index)
                if check_variable_is_not_empty_string(padp_soi_txt):
                    thiet_bi_txt_add_padp_soi_s.extend(padp_soi_txt.split(';;'))
#             if thiet_bi_txt:
#                 thiet_bi_txts = thiet_bi_txt.split(';;')
#                 thiet_bi_txt_add_padp_soi_s.extend(thiet_bi_txts)
        else:
            return None
    if thiet_bi_txt:
        thiet_bi_txts = thiet_bi_txt.split(u';;')
        thiet_bi_txt_add_padp_soi_s.extend(thiet_bi_txts)
    for count, thiet_bi_txt in enumerate( thiet_bi_txt_add_padp_soi_s):
        thiet_bi_reg_rs = re.findall('240G|BB2|330G|ALU|HW|8800|Fujitsu|RN3',thiet_bi_txt,re.I)
        if thiet_bi_reg_rs:
            thiet_bi_name = thiet_bi_reg_rs[0]
            if thiet_bi_name in ['BB2','330G','ALU']:
                thiet_bi_name = 'BB2 ALU 330G'
            elif thiet_bi_name in ['HW','8800']:
                thiet_bi_name = 'HW 8800'
            elif thiet_bi_name =='240G':
                thiet_bi_name= 'Ciena 240G'
            elif thiet_bi_name=='RN3':
                thiet_bi_name = 'Ciena Ring Nam 3'
            else:
                thiet_bi_name = 'Fujitsu'
            thiet_bi_id_object = get_or_create_object(self,'thietbi',
                                                 {'name':thiet_bi_name,})
            thiet_bi_id_id = get_id_of_object(thiet_bi_id_object)
            
            huong_name_reg_rs = re.findall(u'((PTR - CLH|LAN|PTR|LTK|DTP|ĐTP|CLH|DVLG|CTO|HPU|TVH|BTE|TTI)\s*#\s*\d{0,1})',thiet_bi_txt,re.I)
            if not huong_name_reg_rs:
                huong_name_reg_rs = re.findall('((PTR - CLH|LAN|PTR|LTK|DTP|CLH|VLG|CTO|HPU|TVH|BTE|TTI)\s*\d{0,1})',thiet_bi_txt,re.I)
            if huong_name_reg_rs:
                huong_name =  huong_name_reg_rs[0][0].strip()
                huong_name = huong_name.replace('#',' ')
                if huong_name== u'ĐTP' or huong_name ==u'DTP':
                    huong_name = u'CLH'
                huong_name = huong_name.upper()
#                 if '-' not in huong_name:
#                     huong_name = 'MTO - ' + huong_name
                huong_id = get_or_create_object(self,'huong',
                                                 {'name_theo_huong':huong_name,'thiet_bi_id':thiet_bi_id_id})
                huong_id_id = get_id_of_object(huong_id)
                
                dp_reg_rs = re.findall('dp\s*\d',thiet_bi_txt,re.I)
                if dp_reg_rs:
                    dp_char = dp_reg_rs[0].upper()
                else:
                    dp_char = u'PA'
                padp =  get_or_create_object(self,'padp', {'huong_id':huong_id_id,
                                                         'pa_hay_dp_n':dp_char},{'pa_hay_dp_n':dp_char},is_must_update = True)
#                 padp_id_id = get_id_of_object(padp_id)
#                 padp = convert_object(self,'padp', padp_id)
                #padp.write({'soi_ids':[(6,0,[soi_id])]})
                if dp_char == u'PA':
                    id_padp_id =get_id_of_object(padp)
                    lichsuchay = get_or_create_object(self,'lichsuchay', {"padp_id": id_padp_id,'ghi_chu':u'Được tạo ra tự động khi import'}, #, "huong_id":huong_id_id 
                                                      create_write_dict={"padp_id":id_padp_id},is_must_update = True)
                if soi_id:
#                     if u'<-->17,18 O1-T2 dp1 VLG 240G' in thiet_bi_txt:
#                         raise ValueError('dfasdfdf',padp.name)
                    padp.write({'soi_ids':[(4,soi_id)]})
                    #padp.write({'soi_ids':[(6,0,[soi_id])]})
def change_name_function_tuyen_cap(tc_name):
    r = re.match(u'CÁP',tc_name,re.I)
    if not r:
        tc_name = u'CÁP ' +  tc_name
    return tc_name


def create_soi(self,sheet,row,create_write_dict,
               tuyen_cap_chinh_col_index,
               tuyen_cap_chinh_col_maybe_replace_index,
               tuyen_cap_goc_index,
               tuyen_cap_goc_replace_index,
               soi_goc_index,tach_index,
               stt_soi,
               ):
    tuyen_cap_chinh_id = choose_between_check_name_and_get_or_create_and_return_id(self,sheet,row,'tuyen_cap',tuyen_cap_chinh_col_index,tuyen_cap_chinh_col_maybe_replace_index,
                                                 key_main = 'name',more_search={},update_dict={},change_name_function = change_name_function_tuyen_cap)
    if tuyen_cap_chinh_id:
        soi_goc_id=False
        if tuyen_cap_goc_index !=None:
            tuyen_cap_goc_id = \
            choose_between_check_name_and_get_or_create_and_return_id(self,sheet,row,'tuyen_cap',
                            tuyen_cap_goc_index,tuyen_cap_goc_replace_index,key_main = 'name',change_name_function = change_name_function_tuyen_cap  )    
            if tuyen_cap_goc_id: 
                soi_goc_id = choose_between_check_name_and_get_or_create_and_return_id(self,sheet,row,'dai_tgg.soi',
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
        soi_id = choose_between_check_name_and_get_or_create_and_return_id(self,sheet,row,'dai_tgg.soi',None,None,
                             key_main = 'stt_soi',
                             more_search={'tuyen_cap':tuyen_cap_chinh_id},
                             update_dict={'soi_goc_id':soi_goc_id},
                             avail_val=stt_soi)
        if is_tach:
            soi_id = False
            create_write_dict['is_tach'] = True
        
    else:
        soi_id = False
        soi_goc_id = False
#     create_write_dict['soi_id'] = soi_id
    if soi_id !=False:
        create_write_dict['phia_sau_odf_la'] = 'dai_tgg.soi'
    return soi_id, soi_goc_id         
SOI_OR_ODF_PADP_MODE = 'soi'                                                               
def import_ada_prc(self):
        global create_number_dict
        global update_number_dict
        global get_number_dict
        os_choose = getattr(self,'os_choose',u'linux')
        if os_choose ==u'win':
            path = 'E:\SO DO LUONG\T6-2017\SO DO ODF.xls'#'D:\luong_TGG\O1T1.xls'
        else:
            path = '/media/sf_E_DRIVE/SO DO LUONG/T6-2017/' +  'SO DO ODF.xls'
        excel = xlrd.open_workbook(path,formatting_info=True)#,formatting_info=True
        sheet_names = excel.sheet_names()
        excute = False
        
        only_sheet_mode = self.only_sheet_mode
        sheet_name_choose = self.sheet_name_choose
#         if sheet_name_choose ==False:
#             only_sheet_mode = 0
#             sheet_name_choose = 'O.4-T1'
#             #sheet_name_choose =False
        for count_s,sheet_name in enumerate(sheet_names):
            create_number_dict = {}
            update_number_dict = {}
            get_number_dict = {}
            excute = only_sheet_mode and sheet_name ==sheet_name_choose or \
                not only_sheet_mode and (sheet_name_choose ==False or sheet_name == sheet_name_choose or excute)
            if not excute:
                continue
            
            sheet = excel.sheet_by_name(sheet_name)
            state = 'begin'
            tuyen_cap_chinh_col_maybe_replace_index= None
            tuyen_cap_goc_replace_index = None
            soi_goc_index = None
            equ_replace_index = None
            thiet_bi_replace_index = None
            tach_index= None
            more_padp_soi_index = None
            thuoc_tinh_phu_col_index  =None
            for row in range(2,sheet.nrows):
                if state == 'begin':
                    pattern = u'O\.(\d+)[\s-]+T\.(\d+)' 
                    rs = re.search(pattern, sheet.cell_value(row,0))
                    if rs:
                        o_value,t_value = int(rs.group(1)),int(rs.group(2))
                        state = 'title row'
                    else:
                        raise ValueError(u' Không đúng định dạng title (not match format title)')
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
                        if u'equ_replace' in sheet.cell_value(row,col):
                            equ_replace_index = col
                        if u'thiet_bi_replace' in sheet.cell_value(row,col):
                            thiet_bi_replace_index = col
                        if u'tach' in sheet.cell_value(row,col):
                            tach_index = col
                        if u'thuoc tinh phu' in sheet.cell_value(row,col):
                            thuoc_tinh_phu_col_index = col
                        if  SOI_OR_ODF_PADP_MODE =='soi' and u'padp soi' in sheet.cell_value(row,col):
                            more_padp_soi_index = col
                            #raise ValueError('adfdf',sheet_name)
                elif state == 'data':
                    #print '<row>',row
                    ada_data = {}
                    create_write_dict = {}
                    ada_data['odf_number'] = o_value
                    ada_data['tu_number'] = t_value
                    adaptor_val = get_merged_cell_val(sheet,row,ada_index)
                    if row> data_row + 47:
                        break
                    if not check_variable_is_not_empty_string(adaptor_val):
                        continue
                    adaptor_number = str(int(adaptor_val))
                    ada_data['adaptor_number'] = adaptor_number

                    soi_or_thiet_bi_name = get_merged_cell_val(sheet,row,soi_index)
                    try:#kiem tra interge hay khong
                        stt_soi = int(soi_or_thiet_bi_name)
                        mat_sau_mode = 'soi'
                    except:
                        if check_variable_is_not_empty_string(soi_or_thiet_bi_name):
                            mat_sau_mode = 'port thiet bi'
                        else:# con lai la rong 
                            mat_sau_mode = None
                    thuoc_tinh_phu = thuoc_tinh_phu_col_index and  sheet.cell_value(row,thuoc_tinh_phu_col_index)
                    soi_id =False
                    if mat_sau_mode == 'port thiet bi':
                        thiet_bi_id = choose_between_check_name_and_get_or_create_and_return_id(self,sheet,row,'thietbi',0,equ_replace_index,
                                                 key_main = 'name',more_search={},update_dict={})
                        name_port_thiet_bi = soi_or_thiet_bi_name
                        port_tb = get_or_create_object(self,'port.thiet_bi', {'port_name':name_port_thiet_bi,'thiet_bi_id':thiet_bi_id})
                        port_thiet_bi_id = get_id_of_object(port_tb)
                        create_write_dict['port_thiet_bi'] = port_thiet_bi_id
                        #if port_thiet_bi_id !=False:
                        create_write_dict['phia_sau_odf_la'] = 'port.thiet_bi'
                    elif mat_sau_mode == 'soi':
                        soi_id,soi_goc_id = create_soi(self,sheet,row,
                                            create_write_dict,
                                            tuyen_cap_chinh_col_index,
                                            tuyen_cap_chinh_col_maybe_replace_index,
                                            tuyen_cap_goc_index,
                                            tuyen_cap_goc_replace_index,
                                            soi_goc_index,
                                            tach_index,
                                            stt_soi,
                                            )
                    read_thiet_bi_s = get_merged_cell_val(sheet,row,thiet_bi_index,is_return_primary_or_secondary=True)
                    thiet_bi_txt = read_thiet_bi_s[0]
                    thiet_bi_txt_valid = check_variable_is_not_empty_string(thiet_bi_txt)
                    if not thiet_bi_txt_valid:
                        thiet_bi_txt = False
                    primary_cell_or_secondary_cell = read_thiet_bi_s[1]
                    if thiet_bi_replace_index:
                        thiet_bi_replace_txt = sheet.cell_value(row,thiet_bi_replace_index)
                        if check_variable_is_not_empty_string(thiet_bi_replace_txt):
                            thiet_bi_txt=thiet_bi_replace_txt
                    
                    connect_ada_id = create_connect_ada_id(self,thiet_bi_txt,primary_cell_or_secondary_cell,create_write_dict)
                    
                    odf_dau_xa,ghi_chu = simple_get_odf_dau_xa_and_ghi_chu(sheet,row,odf_dau_xa_index,ghi_chu_index)
                    
                    
                    more_padp_txt = read_cell_and_check_false(sheet,row,more_padp_soi_index)
                    tram_ids_for_soi  = tram_ids_compute_for_soi(self,thiet_bi_txt,odf_dau_xa,soi_id,more_padp_txt)
                    create_write_dict.update({
                                                        'thietbi_char':thiet_bi_txt,
                                                       'odf_dau_xa':odf_dau_xa,
                                                       'ghi_chu':ghi_chu,
                                                       'soi_id':soi_id,
#                                                        'ada_khac_id':connect_ada_id,
                                                       'soi_1_hay_soi_2':primary_cell_or_secondary_cell
                                                       })
                    
                    if primary_cell_or_secondary_cell==2:
                        create_write_dict.update({'couple_ada_id':primary_ada_id})
                    
                    ada_ret = get_or_create_object(self,'ada',ada_data,
                                 create_write_dict =create_write_dict)
                    
                    # @(soi_ids.ada_out_id) ada_ids_char ->
                    #@soi_id.ada_out_id (soi_id.ada_id,soi_id.ada_khac_id.soi_id) 
                    if thuoc_tinh_phu and 'khong du phong' in thuoc_tinh_phu:
                        pass
                    else:
                        create_padp(self,soi_goc_id or soi_id,thiet_bi_txt,sheet,row,more_padp_soi_index)
                    #@ada_khac_id,@
                                
                    if primary_cell_or_secondary_cell==1:
                        primary_ada_id = get_id_of_object(ada_ret)
                    print '</row>'
            get_or_create_object(self,'dai.log',{'sheet_name':sheet_name},
                                 create_write_dict ={'create_number_dict':create_number_dict,
                                                       'update_number_dict':update_number_dict,
                                                       'get_number_dict':get_number_dict})
        #file.close()
def import_user (odoo_or_self_of_wizard):
    self = odoo_or_self_of_wizard
    os_choose = getattr(self,'os_choose',u'linux')
    if os_choose ==u'win':
        path = 'E:\SO DO LUONG\ds.xls'#'D:\luong_TGG\O1T1.xls'
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
        ngay_sinh = sheet.cell_value(row,ngay_sinh_index)
        #print 'name',name
        if check_variable_is_not_empty_string(ngay_sinh):
            ngay_sinh =  datetime.datetime.strptime(ngay_sinh,'%d/%m/%Y')
        else:
            ngay_sinh = False
        tram_id = choose_between_check_name_and_get_or_create_and_return_id(self,sheet, row,
                                                                'tram', tram_index, None, key_main= 'name')
        print 'tram_id',tram_id
        user_id = choose_between_check_name_and_get_or_create_and_return_id(self,sheet,row,'res.users',
                                                     email_index,None,
                                                 key_main = 'login',more_search={},update_dict={'name':name,'password':'123456',
                                                                                                           'date':ngay_sinh,'tram_id':tram_id}) 
        print user_id
    
def dieu_chinh_nam_3g(name_3g):
    name_3g  = re.sub('^3G-','3G_',name_3g)
    name_3g = re.sub('-(\w{3})$',r'_\1',name_3g)  
    return name_3g

def importnhatram (odoo_or_self_of_wizard):
    
    self = odoo_or_self_of_wizard 
    for r in self:
            noti_dict = {}
            recordlist = base64.decodestring(r.file)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sheet = excel.sheet_by_index(0)
            ten_cho_quan_ly_index = None
            for row in [0,1,2]:
                for col in range(0,sheet.ncols):
                    value = sheet.cell_value(row,col)
                    if  u'Tên cho quản lý' in value or u'Tên trên hệ thống' in value:
                        ten_cho_quan_ly_index = col
                        continue
                    if  u'Mã trạm' in value:
                        ma_tram_index = col
                        continue
                    if u'Thời gian bảo dưỡng' in value:
                        thoi_gian_bd_index = col
                        continue
#                 if ten_cho_quan_ly_index !=None:
#                     begin_data_row = row + 2
#                     break
            for row in range(3,sheet.nrows):
                ten_cho_quan_ly = sheet.cell_value(row,ten_cho_quan_ly_index)
                if not ten_cho_quan_ly or len(ten_cho_quan_ly)<2 :
                    continue
                ma_tram = sheet.cell_value(row,ma_tram_index)
                thoi_gian_bd = sheet.cell_value(row,thoi_gian_bd_index)
                if check_variable_is_not_empty_string(thoi_gian_bd):
                    thoi_gian_bd =  datetime.datetime.strptime(thoi_gian_bd,'%d/%m/%Y')
                    thoi_gian_bd = thoi_gian_bd.date()
                else:
                    thoi_gian_bd = False
                ten_cho_quan_ly = dieu_chinh_nam_3g(ten_cho_quan_ly)
                #print 'ma_tram,type(ma_tram)',ma_tram,type(ma_tram)
                if isinstance(ma_tram, float):
                    continue
                if '2G' in ma_tram:
                    model = 'bts'
                    tram_type = '2G'
                elif '3G' in ma_tram:
                    model = 'nodeb'
                    tram_type = '3G'
                elif '4G' in ma_tram:
                    model = 'enodeb'
                    tram_type = '4G'
                else:
                    raise ValueError('wtf 2g, 3g not in matram')
                    #print 'wtf',ma_tram,type(ma_tram)
                get_or_create_object_sosanh(self,model,{'name':ten_cho_quan_ly}, {'ma_tram':ma_tram,'ngay_bao_duong':thoi_gian_bd},noti_dict=noti_dict )
                
            r.create_number = noti_dict['create']
            r.update_number = noti_dict['update']
            r.skipupdate_number = noti_dict['skipupdate']
            r.import_2g_or_3g = tram_type
                
def dieu_chinh_2g(name_2g):
    name_2g = re.sub('\(.+\)','',name_2g)
    name_2g = name_2g.strip()
    return name_2g                
def import_bd_tuan(odoo_or_self_of_wizard):
    import base64
    self = odoo_or_self_of_wizard 
    for r in self:
            import_file = r.file_import
            recordlist = base64.decodestring(import_file)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sheet = excel.sheet_by_index(0)
      
            for col in range(0,sheet.ncols):
                value = sheet.cell_value(0,col)
                if  u'2G' in value:
                    col_2G_index = col
                    continue
                if  u'3G' in value:
                    col_3G_index = col
                    continue
                if u'NGÀY BẢO DƯỠNG' in value:
                    thoi_gian_bd_index = col
                    continue
                if u'TUẦN BẢO DƯỠNG' in value:
                    tuan_bao_duong_col_index = col
                    continue
            col_2G_index= 6
            col_3G_index = 9
            for row in range(2,sheet.nrows):
                name_2g_edited = False
                name_2g = sheet.cell_value(row,col_2G_index)
                if check_variable_is_not_empty_string(name_2g):
                    name_2g_edited = dieu_chinh_2g(name_2g)
                else:
                    name_2g = False
                name_3g = sheet.cell_value(row,col_3G_index)
                name_3g_edited = False
                if check_variable_is_not_empty_string(name_3g):
                    name_3g = name_3g.strip()
                    name_3g = re.sub('\s+',' ',name_3g)
                    name_3gs = name_3g.split(' ')
                    name_3g_edited = False
                    match_3g_xl_with_db = False
                    for name_3g_edited in name_3gs:
                        name_3g_edited = re.sub(r'(E|K)(_\w{3})',r"\2",name_3g_edited)
                        name_3g_edited = dieu_chinh_nam_3g(name_3g_edited)
                        rs = self.env['nodeb'].search([('name','=',name_3g_edited)])
                        if rs:
                            match_3g_xl_with_db = True
                            break
                    if not match_3g_xl_with_db:
                        name_3g_edited =('3G_' + name_2g_edited) if name_2g_edited else False
                        

                else:
                    name_3g  =  False
                tuan_bao_duong_char = sheet.cell_value(row,tuan_bao_duong_col_index)
                if check_variable_is_not_empty_string(tuan_bao_duong_char):
                    tuan_bao_duong_char = re.sub('W', '', tuan_bao_duong_char,0, re.I)
                    tuan_bao_duong_char= int(tuan_bao_duong_char)
                else:
                    tuan_bao_duong_char = False
                    
                date_bd = False
                week_number = False    
                thoi_gian_bd_xl = sheet.cell_value(row,thoi_gian_bd_index)
                
                if not name_3g and not name_2g:
                    continue
                #ghi_chu = type(thoi_gian_bd)
                is_mapping_2_week =False
                if check_variable_is_not_empty_string(thoi_gian_bd_xl):
                    if isinstance(thoi_gian_bd_xl, float):
                        date_bd = xlrd.xldate.xldate_as_datetime(thoi_gian_bd_xl, excel.datemode)
                        week_number = date_bd.isocalendar()[1]
                        if week_number ==tuan_bao_duong_char \
                        or week_number ==tuan_bao_duong_char + 1\
                        or week_number ==tuan_bao_duong_char - 1 \
                        and tuan_bao_duong_char != False:
                            is_mapping_2_week = True
                    else:
                        date_bd= False
                        thoi_gian_bd_xl = re.sub('\.|\s', '', thoi_gian_bd_xl,0, re.I)
                        date_formats = ["%d-%m-%Y","%m-%d-%Y","%m/%d/%Y","%d/%m/%Y"]
                        for d_f in date_formats:
                            try:
                                date_bd = datetime.datetime.strptime(thoi_gian_bd_xl,d_f)
                                week_number = date_bd.isocalendar()[1]
                                if week_number ==tuan_bao_duong_char \
                                or week_number ==tuan_bao_duong_char + 1\
                                or week_number ==tuan_bao_duong_char - 1 \
                                and tuan_bao_duong_char != False:
                                    is_mapping_2_week = True
                                    break
                            except ValueError:
                                continue
                else:
                    date_bd = False  
                
                if self.tuan_import and week_number !=self.tuan_import:
                    continue
                    
   
                if check_variable_is_not_empty_string(name_2g):
                    get_or_create_object(self,'lineimport',{'name_2g':name_2g,'importbdtuan_id':r.id,'name_3g':name_3g},
                                          {'date_char':thoi_gian_bd_xl,
                                           'name_2g':name_2g,# 'ghi_chu':ghi_chu,
                                           'name_2g_edited':name_2g_edited,
                                           'name_3g_edited':name_3g_edited,
                                            'date':date_bd,'week_number':week_number,
                                            'week_char':tuan_bao_duong_char,
                                            'is_mapping_2_week':is_mapping_2_week
                                            },True )
                
def test_depend_onchange(odoo):       
    id_trave = odoo.env['ada'].create({'name':'dauphong','truoc_hay_sau':u'sau',
                                       'adaptor_number':2,
                                       'odf_number':2,
                                       'tu_number':2,
                                       'test_3':'coi thu test 4,5 co gi thay doi ko',
                                       #'test_2':'reassign test 2'
                                       })
    #print 'id_trave',id_trave     
def test_write_ada(odoo):
    ada = odoo.env['ada'].browse(2152)
    print ada.soi_id
    kq = ada.write({'soi_id':9})
    print kq
def test_compare_object_id_with_id(odoo):
    ada = odoo.env['ada'].search([('odf_number','=',1),('tu_number','=',2),('adaptor_number','=',1)])
    ada = convert_object(odoo,'ada', ada)
def test_map_thiet_bi_id_in_padp(odoo):
    print odoo.env['padp'].search([]).mapped('thiet_bi_id')
if __name__ =='__main__':
    import odoorpc
    odoo = odoorpc.ODOO('localhost', port=8069)
    # Check available databases
    print(odoo.db.list())
    # Login
    #odoo.login('db_name', 'user', 'passwd')
    odoo.login('2606', 'nguyenductu@gmail.com', '228787')
    #import_user(odoo)
    #import_ada_prc(odoo) 
    test_map_thiet_bi_id_in_padp(odoo)
    #test_compare_object_id_with_id(odoo)
           
    #test_write_ada(odoo)         