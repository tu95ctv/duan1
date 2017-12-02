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
_logger = logging.getLogger(__name__)


def get_or_create_object_sosanh(self,class_name,search_dict,
                                create_write_dict ={},is_must_update=False,noti_dict=None,not_active_item_search = False):
    #print 'in get_or create fnc','search_dict',search_dict,'create_write_dict',create_write_dict
    if not_active_item_search:
        domain_list = ['|',('active','=',True),('active','=',False)]
    else:
        domain_list = []
    if noti_dict =={}:
        noti_dict['create'] = 0
        noti_dict['update'] = 0
        noti_dict['skipupdate'] = 0
    for i in search_dict:
        tuple_in = (i,'=',search_dict[i])
        domain_list.append(tuple_in)
    print '***domain_list***',domain_list,'**create_write_dict**',create_write_dict
    #print 'domain_list 1',domain_list
    searched_object  = self.env[class_name].search(domain_list)
    print 'searched_object',searched_object
    if not searched_object:
        search_dict.update(create_write_dict)
        print
        created_object = self.env[class_name].sudo().create(search_dict)
        if noti_dict !=None:
            noti_dict['create'] = noti_dict['create'] + 1
        return_obj =  created_object
        print 'created_object 1',created_object
    else:
        if not is_must_update:
            is_write = False
            for attr in create_write_dict:
                domain_val = create_write_dict[attr]
                exit_val = getattr(searched_object,attr)
                try:
                    exit_val = getattr(exit_val,'id',exit_val)
                    if exit_val ==None: #recorderset.id ==None when recorder sset = ()
                        exit_val=False
                except:#singelton
                    pass
                if isinstance(domain_val, datetime.date):
                    exit_val = fields.Date.from_string(exit_val)
                if exit_val !=domain_val:
                    #print 'exit_val','domain_val',exit_val,domain_val
                    is_write = True
                    break
            
        else:
            is_write = True
        if is_write:
            searched_object.sudo().write(create_write_dict)
            if noti_dict !=None:
                noti_dict['update'] = noti_dict['update'] + 1
            #print 'searched_object 2'

        else:#'update'
            if noti_dict !=None:
                noti_dict['skipupdate'] = noti_dict['skipupdate'] + 1
        #print 'is_write***',is_write,'class_name',class_name,'noti_dict',noti_dict
        return_obj = searched_object
    #print 'domain_list 2',domain_list
    return return_obj
    
EMPTY_CHAR = [u'',u' ',u'\xa0' ]
def check_variable_is_not_empty_string(readed_xl_value):
    if  isinstance(readed_xl_value,unicode) :
        if readed_xl_value  in EMPTY_CHAR:
            return False
        rs = re.search('\S',readed_xl_value)
        if not rs:
            return False
    return True        
  
def print_diem(val):
    #print 'diem',val,type(val)
    return val
def ham_tao_tvcvlines():
    pass
INVALIDS = ['No serial','N/A','NA','--','-','BUILTIN','0','1']
#INVALIDS=map(lambda i:i.lower(),INVALIDS)
def valid_sn_pn(sn_pn):
    if isinstance(sn_pn, unicode):
        if sn_pn in INVALIDS:
            return False
    return sn_pn
        #sn_pn = sn_pn.lower()
def sn_bi_false(sn_pn):
    if isinstance(sn_pn, unicode):
        if sn_pn in INVALIDS:
            return sn_pn
    return False

def sn_map(val):
    rs = re.findall('Serial number.*?(\w+)',val)
    if rs:
        return rs[0]
def import_strect(odoo_or_self_of_wizard):
    self = odoo_or_self_of_wizard
    for r in self:
            noti_dict = {}
            recordlist = base64.decodestring(r.file)
            xl_workbook = xlrd.open_workbook(file_contents = recordlist)
            begin_row_offset = 0
            if r.type_choose==u'640':
                sheet_names = xl_workbook.sheet_names()
                #sheet_names = ['VTN-137P-4-2']
            for sheet_name in sheet_names:
                sheet = xl_workbook.sheet_by_name(sheet_name)
                if r.type_choose ==u'640':
                    model_name = 'kknoc'
                    field_dict= (
                            ('sn',{'func':sn_map,'contain':u'Serial number','key':'Both','col_index':7}),
                            
#                             ('stt',{'func':None,'xl_title':u'stt','key':True}),
#                             ('so_the',{'func':None,'xl_title':u'Số thẻ','key':True}),
#                             ('pn',{'func':valid_sn_pn,'xl_title':u'Part-Number','key':True}),
#                             ('pn_id',{'model':'pn','func':valid_sn_pn,'xl_title':u'Part-Number','key':False}),
#                             ('sn_false',{'func':sn_bi_false,'xl_title':None,'key':False,'col_index':7}),
                            
                            )
                column_number = 0
                key_search_dict = {}
                update_dict = {}
                data=''
                for row in range(begin_row_offset,sheet.nrows):
                        #print 'row',row
                        read_value = sheet.cell_value(row,column_number)
                        if read_value:
                            if read_value:
                                data = data + '\n' + read_value
                            for field,field_attr in field_dict:
                                func = field_attr['func']
                                val = func (read_value)
                                if val != None:
                                    if field_attr['key']==True:
                                        key_search_dict[field] = val
                                    elif  field_attr['key']=='Both':
                                        key_search_dict[field] = val
                                        update_dict[field] = val
                                    else:
                                        update_dict[field] = val
                                    break
                        else:
                            if key_search_dict:
                                update_dict['sheet_name'] = sheet_name
                                update_dict['file_name'] = r.type_choose
                                update_dict['data'] = data
                                get_or_create_object_sosanh(self,model_name,key_search_dict,update_dict,True,noti_dict=noti_dict )
                                key_search_dict = {}
                                update_dict = {}
                                data = ''
                    
                     
                    
                 
            r.create_number = noti_dict['create']
            r.update_number = noti_dict['update']
            r.skipupdate_number = noti_dict['skipupdate']
        
def importthuvien(odoo_or_self_of_wizard):
    self = odoo_or_self_of_wizard
    for r in self:
            noti_dict = {}
            recordlist = base64.decodestring(r.file)
            #raise ValueError(type(r.file),r.file.name)
            xl_workbook = xlrd.open_workbook(file_contents = recordlist)
            begin_row_offset = 1
            not_active_item_search  =False
            if r.type_choose ==u'User':
                sheet_names = ['Sheet1']
            elif r.type_choose ==u'Công Ty':
                sheet_names = [u'Công Ty']
            elif r.type_choose ==u'Kiểm Kê':
                sheet_names = [u'web']
                begin_row_offset = 2
            elif r.type_choose ==u'Vật Tư LTK':
                sheet_names = [u'LTK']
                begin_row_offset = 1
            elif r.type_choose ==u'INVENTORY_240G':
                sheet_names = xl_workbook.sheet_names()
                begin_row_offset = 1
            elif r.type_choose ==u'INVENTORY_RING_NAM_CIENA':
                sheet_names = xl_workbook.sheet_names()
                begin_row_offset = 1
                
            if r.type_choose==u'Thư viện công việc':
                not_active_item_search  =True
                sheet_names = xl_workbook.sheet_names()
                model_name = 'tvcv'
                def is_active_f(val):
                    return False if val ==u'na' else True
                field_dict_goc= (
                         ('name', {'func':None,'xl_title':u'Công việc','key':True,'break_when_xl_field_empty':True}),
                         ( 'code',{'func':None,'xl_title':u'Mã CV','key':False }),
                         ('do_phuc_tap',{'func':None,'xl_title':u'Độ phức tạp','key':False}),
                         ('don_vi',{'model':'donvi','func':lambda x: unicode(x).title().strip(),'xl_title':u'Đơn vị','key':False}),
                         ('thoi_gian_hoan_thanh',{'func':None,'xl_title':u'Thời gian hoàn thành','key':False}),
                         ('dot_xuat_hay_dinh_ky',{'model':'dotxuathaydinhky','func':None,'xl_title':None,'key':False,'col_index':7}),
                         ('diem',{'func':None,'xl_title':u'Điểm','key':False}),
                         ('is_active',{'func':is_active_f,'xl_title':u'active','key':False,'col_index':'skip_if_not_found_column','use_fnc_even_cell_is_False':True}),
                         ('active',{'func':is_active_f,'xl_title':u'active','key':False,'col_index':'skip_if_not_found_column','use_fnc_even_cell_is_False':True}),
                         ('children_ids',{'model':'tvcv',
                        'xl_title':u'Các công việc con',
                        'key':False,'col_index':'skip_if_not_found_column','m2m':True,'dung_ham_de_tao_val_rieng':ham_tao_tvcvlines,
                                                                                                    }),
                        )
                title_rows = range(1,4)
                
            elif r.type_choose ==u'User':
                model_name = 'res.users'
                field_dict= (
                         ('name', {'func':None,'xl_title':u'Họ và Tên','key':False,'break_when_xl_field_empty':True}),
                         ( 'login',{'func':None,'xl_title':u'Địa chỉ email','key':True ,'break_when_xl_field_empty':True}),
                         ('phone',{'func':None,'xl_title':u'Số điện thoại','key':False}),
                         #('tram_id',{'model':'tram','func':None,'xl_title':u'Trạm','key':False}),
                         #('parent_id',{'model':'res.users','func':None,'xl_title':u'Cấp trên','key':False,'key_name':'login','split_first_item_if_comma':True}),
                         ('cac_sep_ids',{'model':'res.users','func':None,'xl_title':u'Cấp trên','key':False,'key_name':'login','m2m':True}),
                        ('cty_id',{'model':'congty','func':None,'xl_title':u'Bộ Phận','key':False}),
                        )
                title_rows = [1]
            elif r.type_choose ==u'Công Ty':
                model_name = 'congty'
                field_dict= (
                        ('name',{'func':None,'xl_title':u'công ty','key':True}),
                        ('parent_id',{'model':'congty','func':None,'xl_title':u'parent_id','key':False}),
                          ('cong_ty_type',{'model':'congtytype','func':None,'xl_title':u'cong_ty_type','key':False}),
                        )
                title_rows = [1]
            elif r.type_choose ==u'Kiểm Kê':
                model_name = 'kiemke'
                field_dict= (
                        ('kiem_ke_id',{'func':None,'xl_title':u'ID - Không sửa cột này','key':True}),
                        ('ten_vat_tu',{'func':None,'xl_title':u'Tên tài sản','key':False}),
                        ('so_the',{'func':None,'xl_title':u'Số thẻ','key':False}),
                        ('pn',{'func':valid_sn_pn,'xl_title':u'Part-Number','key':False}),
                        ('pn_id',{'model':'pn','func':valid_sn_pn,'xl_title':u'Part-Number','key':False}),
                        ('sn',{'func':valid_sn_pn,'xl_title':u'Serial number','key':False}),
                        ('sn_false',{'func':sn_bi_false,'xl_title':u'Serial number','key':False}),
                        ('ma_du_an',{'func':None,'xl_title':u'Mã dự án','key':False}),
                        ('ten_du_an',{'func':None,'xl_title':u'Tên dự án','key':False}),
                        ('ma_vach',{'func':None,'xl_title':u'Mã vạch','key':False}),
                        ('trang_thai',{'func':None,'xl_title':u'Trạng thái','key':False}),
                        ('hien_trang_su_dung',{'func':None,'xl_title':u'Hiện trạng sử dụng','key':False}),
                        ('ghi_chu',{'func':None,'xl_title':u'Ghi chú','key':False}),
                        ('don_vi',{'func':None,'xl_title':u'Đơn vị','key':False}),
                        ('vi_tri_lap_dat',{'func':None,'xl_title':u'Vị trí lắp đặt','key':False}),
                        ('loai_tai_san',{'func':None,'xl_title':u'Loại tài sản','key':False}),
                        )
                title_rows = range(6,11)
                begin_row_offset = 1
            elif r.type_choose ==u'Vật Tư LTK':
                model_name = 'vattu'
                field_dict= (
#                             ('name',{'func':None,'xl_title':u'Tên tài sản','key':True}),
                      
                        ('stt',{'func':None,'xl_title':u'STT','key':True}),
                        ('phan_loai',{'func':None,'xl_title':u'Phân loại thiết bị','key':False}),
                        ('pn',{'func':valid_sn_pn,'xl_title':u'Mã card (P/N)','key':False}),
                        ('pn_id',{'model':'pn','func':valid_sn_pn,'xl_title':u'Mã card (P/N)','key':False}),
                        ('sn',{'func':valid_sn_pn,'xl_title':u'Số serial (S/N)','key':False}),
                        ('loai_card',{'func':None,'xl_title':u'Loại card','key':False}),
                        ('he_thong',{'func':None,'xl_title':u'Tên hệ thống thiết bị','key':False}),
                        ('cabinet_rack',{'func':None,'xl_title':u'Tên tủ (Cabinet / rack)','key':False}),
                        ('shelf',{'func':lambda i: str(int(i)) if isinstance(i,float)  else i,'xl_title':u'Ngăn (shelf)','key':False}),
                        ('stt_shelf',{'func':lambda i: str(int(i)) if isinstance(i,float)  else i,'xl_title':u'Số thứ tự (trong shelf)','key':False}),
                        ('slot',{'func':lambda i: str(int(i)) if isinstance(i,float) else i,'xl_title':u'Khe (Slot)','key':False}),
                        ('ghi_chu',{'func':None,'xl_title':u'Ghi chú - Mô tả thêm','key':False}),
                        ('sn_false',{'func':sn_bi_false,'xl_title':u'Số serial (S/N)','key':False}),
                        )
                title_rows = range(0,7)
            elif r.type_choose ==u'INVENTORY_240G':
                model_name = 'kknoc'
                field_dict= (
                        ('sn',{'func':None,'xl_title':[u'Serial #',u'Serial Number'],'key':True}),
#                             ('sn',{'func':None,'xl_title':[u'Serial #',u'Serial Number'],'key':True,'col_index':'skip_if_not_found_column'}),
                        
                        )
                title_rows = [0]
                
            elif r.type_choose ==u'INVENTORY_RING_NAM_CIENA':
                model_name = 'kknoc'
                field_dict= (
                        ('sn',{'func':None,'xl_title':[u'Serial No.',u'Serial Number'],'key':True}),
                        ('pn',{'func':None,'xl_title':[u'PART  NUMBER'],'key':True,'col_index':'skip_if_not_found_column'}),
                         ('sheet_name',{'func':None,'xl_title':[u'System Name',u'Network Element'],'key':True,'col_index':'skip_if_not_found_column'})
                        )
                title_rows = [0]
            elif r.type_choose ==u'Inventory-120G':
                model_name = 'kknoc'
                field_dict= (
                        ('sn',{'func':None,'xl_title':[u'Serial No',u'Serial #'],'key':True}),
                        ('clei',{'func':None,'xl_title':[u'CLEI'],'key':True,'col_index':'skip_if_not_found_column'}),
                         ('sheet_name',{'func':None,'xl_title':[u'NE Name',u'Shelf'],'key':True,'col_index':'skip_if_not_found_column'})
                        )
                title_rows = [0]
                sheet_names = xl_workbook.sheet_names()
                begin_row_offset = 1
                
            elif r.type_choose ==u'Inventory-330G':
                model_name = 'kknoc'
                field_dict= (
                        ('sn',{'func':None,'xl_title':[u'SERIAL NUMBER'],'key':True}),
                        ('pn',{'func':None,'xl_title':[u'UNIT PART NUMBER'],'key':True,'col_index':'skip_if_not_found_column'}),
                         ('sheet_name',{'func':None,'xl_title':[u'NE'],'key':True,'col_index':'skip_if_not_found_column'})
                        )
                title_rows = [0]
                sheet_names = xl_workbook.sheet_names()
                begin_row_offset = 1
            elif r.type_choose ==u'INVENTORY-FW4570':
                model_name = 'kknoc'
                field_dict= (
                        ('sn',{'func':None,'xl_title':[u'Serial Number'],'key':True}),
#                         ('pn',{'func':None,'xl_title':[u'UNIT PART NUMBER'],'key':True,'col_index':'skip_if_not_found_column'}),
#                          ('sheet_name',{'func':None,'xl_title':[u'NE'],'key':True,'col_index':'skip_if_not_found_column'})
                        )
                title_rows = [0]
                sheet_names = xl_workbook.sheet_names()
                begin_row_offset = 1
            elif r.type_choose ==u'INVETORY 1670':
                model_name = 'kknoc'
                field_dict= (
                        ('sn',{'func':None,'xl_title':[u'SERIAL NUMBER '],'key':True}),
                        ('pn',{'func':None,'xl_title':[u'PART NUMBER'],'key':True,'col_index':'skip_if_not_found_column'}),
                        ('sheet_name',{'func':None,'xl_title':[u'NODE'],'key':False,'col_index':'skip_if_not_found_column'})
                        )
                title_rows = [0]
                sheet_names = xl_workbook.sheet_names()
                begin_row_offset = 1
            elif r.type_choose ==u'iventory hw8800':
                model_name = 'kknoc'
                field_dict= (
                        ('sn',{'func':None,'xl_title':[u'Serial number'],'key':True}),
#                         ('pn',{'func':None,'xl_title':[u'PART NUMBER'],'key':True,'col_index':'skip_if_not_found_column'}),
                        ('sheet_name',{'func':None,'xl_title':[u'NE'],'key':True,'col_index':'skip_if_not_found_column'})
                        )
                title_rows = [0]
                sheet_names = xl_workbook.sheet_names()
                begin_row_offset = 1
            elif r.type_choose ==u'iventory7500':
                model_name = 'kknoc'
                field_dict= (
                        ('sn',{'func':None,'xl_title':[u'Serial No'],'key':True}),
#                         ('pn',{'func':None,'xl_title':[u'PART NUMBER'],'key':True,'col_index':'skip_if_not_found_column'}),
                        ('sheet_name',{'func':None,'xl_title':[u'TID'],'key':True,'col_index':'skip_if_not_found_column'})
                        )
                title_rows = [0]
                sheet_names = xl_workbook.sheet_names()
                begin_row_offset = 1
            
            
            
            
            for sheet_name in sheet_names:
                if r.type_choose==u'Thư viện công việc':
                    field_dict = deepcopy(field_dict_goc)
                #print 'sheet_name***',sheet_name
                sheet = xl_workbook.sheet_by_name(sheet_name)
                row_title_index =None
#                 #print 'title_rows',title_rows
                for row in title_rows:
                    for col in range(0,sheet.ncols):
                        try:
                            value = unicode(sheet.cell_value(row,col))
#                             #print 'value tt',value
                        except Exception as e:
                            raise ValueError(str(e),'row',row,'col',col,sheet_name)
                        for field,field_attr in field_dict:
                            if field_attr['xl_title'] ==None:
                                continue
                            if isinstance(field_attr['xl_title'],unicode) or  isinstance(field_attr['xl_title'],str):
                                xl_title_s = [field_attr['xl_title']]
                            else:
                                xl_title_s =  field_attr['xl_title']
                            for xl_title in xl_title_s:
                                if xl_title == value:
#                                     #print 'xl_title == value',xl_title
                                    field_attr['col_index'] = col
                                    if row_title_index ==None or  row > row_title_index:
                                        row_title_index = row
                                    break
                                
                                
                for row in range(row_title_index+begin_row_offset,sheet.nrows):
                    #print 'row_number',row,'sh',sheet_name
                    key_search_dict = {}
                    update_dict = {}
                    if r.type_choose==u'Thư viện công việc':
                        cong_viec_cate_id = get_or_create_object_sosanh(self,'tvcvcate',{'name':sheet_name},{} )
                        update_dict['cong_viec_cate_id'] = cong_viec_cate_id.id
                    elif r.type_choose==u'User':
                        update_dict['password'] = '123456'
                    elif r.type_choose==u'INVENTORY_240G':
                        update_dict['sheet_name'] = sheet_name
                        update_dict['file_name'] = r.type_choose
                    elif r.type_choose==u'INVENTORY_RING_NAM_CIENA':
                        update_dict['file_name'] = r.type_choose
                    elif r.type_choose==u'Inventory-120G':
                        update_dict['file_name'] = r.type_choose
                    elif r.type_choose==u'Inventory-330G':
                        update_dict['file_name'] = r.type_choose
                    elif r.type_choose==u'INVENTORY-FW4570':
                        key_search_dict['sheet_name'] = sheet_name
                        update_dict['file_name'] = r.type_choose
                    elif r.type_choose==u'INVETORY 1670':
                        update_dict['file_name'] = r.type_choose
                    elif r.type_choose==u'iventory hw8800':
                        update_dict['file_name'] = r.type_choose
                    elif r.type_choose==u'iventory7500':
                        update_dict['file_name'] = r.type_choose
                    continue_row = False
                    for field,field_attr in field_dict:
                        try:
                            if field_attr['col_index'] =='skip_if_not_found_column':
                                continue
                        except KeyError as e:
                            raise KeyError (u'Ko co col_index của field %s'% field)
                        #print 'row,col',row,col
                        col = field_attr['col_index']
                        val = sheet.cell_value(row,col)
                        #print 'val',val
                        if isinstance(val, unicode):
                            val = val.strip()
                        if not check_variable_is_not_empty_string(val):
                            val = False
                        if 'break_when_xl_field_empty' in field_attr and val==False:
                            continue_row = True
                            break
                        if 'dung_ham_de_tao_val_rieng' in field_attr and field_attr['dung_ham_de_tao_val_rieng'] and val != False:
                            alist = val.split(',')
                            len_alist = len(alist)
                            diem_percent = 100/len(alist)
                            key_name = field_attr.get('key_name','name')
                            parent_id_name = key_search_dict['name']
                            def afunc(val):
                                i = val[0]
                                val = val[1]
                                val = val.strip().capitalize()
                                name_tv_con = val  # + u'|Công Việc Cha: '  + key_search_dict['name']
                                parent_id = get_or_create_object_sosanh (self,'tvcv',{'name':parent_id_name})
                                if i ==len_alist-1:
                                    diem_percent_l =100- (len_alist-1)*diem_percent
                                else:
                                    diem_percent_l = diem_percent
                                    
                                return get_or_create_object_sosanh(self,field_attr['model'],{key_name:name_tv_con,'parent_id':parent_id.id},{'diem_percent':diem_percent_l,
                                                                                                                                             #'diem':diem,
                                                                                                                                             'don_vi':update_dict['don_vi'],
                                                                                                                                             'cong_viec_cate_id':update_dict['cong_viec_cate_id'],
                                                                                                                                             'parent_id':parent_id.id
                                                                                                                                             } )
                            
                            a_object_list = map(afunc,enumerate(alist))
                            a_object_list = map(lambda x:x.id,a_object_list)
                            val = [(6, False, a_object_list)]
                        else:
                            if 'func' in field_attr and field_attr['func']:
                                if val !=False or field_attr.get('use_fnc_even_cell_is_False',False):
                                    val = field_attr['func'](val)
                            elif 'func_co_xai_another_field_value' in field_attr and field_attr['func_co_xai_another_field_value']:
                                if val !=False:
                                    val = field_attr['func_co_xai_another_field_value'](val,key_search_dict)
                                
                            if 'model' in field_attr  and field_attr['model'] and val !=False  :
                                key_name = field_attr.get('key_name','name')
                                if 'addtion_dict_template' in field_attr and field_attr['addtion_dict_template']:
                                    addtion_dict_template = field_attr['addtion_dict_template']
                                    addtion_dict = {}
                                    for k,v in addtion_dict_template.items():
                                        if isinstance(v, dict):
                                            func_addtion_dict = v['func_addtion_dict']
                                            value_of_k = func_addtion_dict(val)
                                            addtion_dict[k] = value_of_k
                                else:
                                    addtion_dict ={}
                                if 'm2m' not in field_attr or not field_attr['m2m']:
                                    if ',' in val and field_attr.get('split_first_item_if_comma',False):
                                        val = val.split(',')[0]
                                    any_obj = get_or_create_object_sosanh(self,field_attr['model'],{key_name:val},addtion_dict )
                                    val = any_obj.id
                                else:
                                    unicode_m2m_list = val.split(',')
                                    unicode_m2m_list = filter( lambda r: len(r)>2 and r,unicode_m2m_list)
                                    print '***unicode_m2m_list**',unicode_m2m_list
                                    def create_or_get_one_in_m2m_value(val):
                                        val = val.strip()
                                        return get_or_create_object_sosanh(self,field_attr['model'],{key_name:val},addtion_dict )
                                    
                                    object_m2m_list = map(create_or_get_one_in_m2m_value, unicode_m2m_list)
                                    m2m_ids = map(lambda x:x.id, object_m2m_list)
                                    val = [(6, False, m2m_ids)]
                                
                        
                        
                        if field_attr['key']==True:
                            key_search_dict[field] = val
                        elif  field_attr['key']=='Both':
                            key_search_dict[field] = val
                            update_dict[field] = val
                        else:
                            update_dict[field] = val
                    if continue_row:
                        continue
                    if key_search_dict:
#                         #print 'key_search_dict',key_search_dict
                        if not key_search_dict['login']:
                            continue
                        _logger.info(key_search_dict)
                        _logger.info(update_dict)
                        try:
                            get_or_create_object_sosanh(self,model_name,key_search_dict,update_dict,True,noti_dict=noti_dict,not_active_item_search  =not_active_item_search)
                        except:
                            pass
            r.create_number = noti_dict['create']
            r.update_number = noti_dict['update']
            r.skipupdate_number = noti_dict['skipupdate']
            

            
            
