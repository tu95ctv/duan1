# -*- coding: utf-8 -*-
from odoo import http
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception,content_disposition
import base64
# from openpyxl import load_workbook
from cStringIO import StringIO
from odoo.tools.misc import xlwt
from copy import deepcopy
from odoo import api,fields
import datetime
def adict_flat(adict,item_seperate=';',k_v_separate = ':'):
    alist = []
    for k,v in adict.iteritems():
        if isinstance(v,dict):
            v = adict_flat(v,item_seperate=',',k_v_separate = ' ')
        alist.append(k + k_v_separate + v)
    return item_seperate.join(alist)     
        

class Binary(http.Controller):
    
    @api.multi
    @http.route('/web/binary/download_tuantra',type='http', auth="public")
    @serialize_exception
    def download_tuantra(self,id, **kw):
        
        
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1',cell_overwrite_ok=True)
        
        ALIGN_BORDER_dict = {'align':{'horiz': 'left','vert':'centre','wrap':'yes'},
                     "borders":{'left':'thin', 'right': 'thin', 'top': 'thin', 'bottom': 'thin'}
                     }

        title_format_dict = deepcopy(ALIGN_BORDER_dict)
        title_format_dict['align']['horiz'] = 'centre'
        title_format_dict['font'] = {"bold":"on"}
        title_format_txt = adict_flat(title_format_dict)
        title_format_style = xlwt.easyxf(title_format_txt)
        normal_txt = adict_flat(ALIGN_BORDER_dict)
        normal_style = xlwt.easyxf(normal_txt)
        
        
        worksheet.write_merge(0, 0, 0 , 15,u"BÁO CÁO TUẦN TRA NGÀY 20/09/2017",title_format_style)
        worksheet.write_merge(1, 2, 0 ,0,u"STT",title_format_style)
        worksheet.write_merge(1, 2, 1 ,1,u"Trạm",title_format_style)
        worksheet.write_merge(1, 2, 2 ,2,u"Hướng Tuyến",title_format_style)
        worksheet.write_merge(1, 2, 3 ,3,u"TTV – GSV",title_format_style)
        worksheet.write_merge(1, 2, 4 ,4,u"GPS",title_format_style)        
        worksheet.write_merge(1, 1, 5 ,6,u"LƯỢT ĐI",title_format_style)  
        worksheet.write_merge(2, 2, 5 ,5,u"GIỜ ĐI",title_format_style)  
        worksheet.write_merge(2, 2, 6 ,6,u"GIỜ ĐẾN",title_format_style)  

        worksheet.write_merge(1, 1, 7 ,8,u"LƯỢT VỀ",title_format_style)  
        worksheet.write_merge(2, 2, 7 ,7,u"GIỜ ĐI",title_format_style)  
        worksheet.write_merge(2, 2, 8 ,8,u"GIỜ ĐẾN",title_format_style) 
        
        worksheet.write_merge(1, 1, 9 ,10,u"SỐ ĐIỆN THOẠI",title_format_style)  
        worksheet.write_merge(2, 2, 9 ,9,u"ĐẦU TUYẾN",title_format_style)  
        worksheet.write_merge(2, 2, 10 ,10,u"CUỐI TUYẾN",title_format_style)  
         
        worksheet.write_merge(1, 2, 11 ,11,u"nội dung",title_format_style)

        worksheet.write_merge(1, 1, 12 ,14,u"KẾ HOẠCH NGÀY HÔM SAU",title_format_style)  
        worksheet.write_merge(2, 2, 12 ,12,u"Tuần tra",title_format_style)  
        worksheet.write_merge(2, 2, 13 ,13,u"Giám sát",title_format_style)  
        worksheet.write_merge(2, 2, 14,14,u"Bảo dưỡng – Xử Lý",title_format_style)  
        
        worksheet.write_merge(1, 2, 15 ,15,u"ghi chú",title_format_style)
        worksheet.write_merge(1, 2, 16 ,16,u"kiến nghị",title_format_style)
        
        
        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        
        return request.make_response(
            data,
            #self.from_data(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="bao_cao_tuan_tra_cq.xls"'),
                ('Content-Type', 'application/octet-stream')
            ],
            #cookies={'fileToken': token}
        )
        
        
        
        
    @api.multi
    @http.route('/web/binary/download_document',type='http', auth="public")
    @serialize_exception
    def download_document(self,id, **kw):
        
        sitetype = kw['sitetype']
        if 'mode_1900' in kw:
            mode_1900 = True
        else:
            mode_1900 = False
            
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1',cell_overwrite_ok=True)
        
        ALIGN_BORDER_dict = {'align':{'horiz': 'left','vert':'centre','wrap':'yes'},
                     "borders":{'left':'thin', 'right': 'thin', 'top': 'thin', 'bottom': 'thin'}
                     }

        title_format_dict = deepcopy(ALIGN_BORDER_dict)
        title_format_dict['align']['horiz'] = 'centre'
        title_format_dict['font'] = {"bold":"on"}
        title_format_txt = adict_flat(title_format_dict)
        title_format_style = xlwt.easyxf(title_format_txt)
        normal_txt = adict_flat(ALIGN_BORDER_dict)
        normal_style = xlwt.easyxf(normal_txt)
        date_style = xlwt.easyxf(normal_txt, num_format_str='DD/MM/YYYY')
        worksheet.write_merge(0, 0, 0 , 4,u"Danh sách Update thông tin đối tượng",title_format_style)
        worksheet.write(1, 0,u"STT",title_format_style)
    
        worksheet.write(1, 1,u"Mã đối tượng",title_format_style)
        worksheet.write(1, 2,u"Thuộc Tính",title_format_style)
        worksheet.write(1, 3,u"Giá trị cập nhật",title_format_style)
        worksheet.write(1, 4,u"Ghi chú",title_format_style)
        row_index = 1
        
        
        worksheet.col(1).width =int(20*260)
        worksheet.col(2).width =int(25*260)
        worksheet.col(3).width =int(20*260)
            
            
        if mode_1900:
            if sitetype=='3G':
                env = 'nodeb'
            elif sitetype =='4G':
                env = 'enodeb'
            elif sitetype=='2G':
                env='bts'
            
            for i in request.env[env].search([('ngay_bao_duong','=',False)]):
                row_index+=1
                worksheet.write(row_index, 1,i.ma_tram,normal_style)
                worksheet.write(row_index, 2, u'Thời gian bảo dưỡng',normal_style)
                worksheet.write(row_index, 3,datetime.date(1900, 1, 1),date_style)
                worksheet.write(row_index, 4, u'',normal_style)

                row_index+=1
                worksheet.write(row_index, 1,i.ma_tram,normal_style)
                worksheet.write(row_index, 2, u'Đơn vị thực hiện',normal_style)
                worksheet.write(row_index, 3,u'Đài VT TGG',normal_style)
                worksheet.write(row_index, 4, u'',normal_style)
        else:
            import_tuan_id = id
            model_class = request.env['importbdtuan']
            import_tuan = model_class.browse(int(import_tuan_id))
            lineimports = import_tuan.lineimports
            loop = lineimports
            for line in loop:
                if import_tuan.tuan_export and line.week_number !=import_tuan.tuan_export:
                        continue
                if sitetype =='2G':
                    ma_doi_tuong = line.bts_id.ma_tram
                elif sitetype=='3G':
                    ma_doi_tuong = line.nodeb_id.ma_tram
                date_bd  = fields.Datetime.from_string(line.date)
                if ma_doi_tuong:
                    row_index+=1
                    worksheet.write(row_index, 1,ma_doi_tuong,normal_style)
                    worksheet.write(row_index, 2, u'Thời gian bảo dưỡng',normal_style)
                    worksheet.write(row_index, 3,date_bd,date_style)
                    worksheet.write(row_index, 4, u'',normal_style)
        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        
        return request.make_response(
            data,
            #self.from_data(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="import_rnas_%s.xls"'%sitetype),
                ('Content-Type', 'application/octet-stream')
            ],
            #cookies={'fileToken': token}
        )


        
