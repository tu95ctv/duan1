# -*- coding: utf-8 -*-
# Copyright 2016 Henry Zhou (http://www.maxodoo.com)
# Copyright 2016 Rodney (http://clearcorp.cr/)
# Copyright 2012 Agile Business Group
# Copyright 2012 Therp BV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import odoo.http as http
from odoo.http import request
from odoo.addons.web.controllers.main import ExcelExport
from odoo import api
from odoo.tools.misc import xlwt
import re
import datetime
from cStringIO import StringIO
from copy import deepcopy

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


def style_something(cell_value,base_style=base_style):
    cell_style = base_style

    if isinstance(cell_value, basestring):
        cell_value = re.sub("\r", " ", cell_value)
    elif isinstance(cell_value, datetime.datetime):
        cell_style = xlwt.easyxf(base_style, num_format_str='YYYY-MM-DD HH:mm:SS')
    elif isinstance(cell_value, datetime.date):
        date_style = xlwt.easyxf(base_style, num_format_str='YYYY-MM-DD')
        cell_style = date_style
    return cell_value,cell_style
def write_soi_or_ada_to_cell(worksheet,r,row_index,col_begin = 0,attr = 'soi_ids_char',delta_between_soi_and_ada = 0):
    if 'PA' in r.name:
        col_index=col_begin + 2 + delta_between_soi_and_ada
    elif 'DP1' in r.name:
        col_index=col_begin + 5 + delta_between_soi_and_ada
    elif 'DP2' in r.name:
        col_index = col_begin + 7 + delta_between_soi_and_ada
    elif 'DP3' in r.name:
        col_index = col_begin + 9 + delta_between_soi_and_ada
    else:
        return 'continue'
    cell_value = getattr(r,attr)
    if attr=='odf_dau_xa':
        ALIGN_BORDER_ada = deepcopy(ALIGN_BORDER_dict)
        ALIGN_BORDER_ada['align'].update({'horiz':"right"})
        ada_style = xlwt.easyxf(adict_flat(ALIGN_BORDER_ada))
        style = ada_style
    else:
        style = base_style
    cell_value,cell_style = style_something(cell_value,base_style=style)
    if attr =='soi_ids_char':
        worksheet.write_merge(row_index, row_index+1, col_index , col_index,
                                              cell_value,cell_style)
    else:
        worksheet.write(row_index , col_index, cell_value, cell_style,) 
        worksheet.row(row_index).height_mismatch = True
        worksheet.row(row_index).height = 256* 2
    return 'ok'          
class ExcelExportView(ExcelExport):
    def __getattribute__(self, name):
        if name == 'fmt':
            raise AttributeError()
        return super(ExcelExportView, self).__getattribute__(name)
    @api.multi
    @http.route('/web/export/xls_view', type='http', auth='user')
    def export_xls_view(self, data, token):
        data = json.loads(data)
        model = data.get('model', [])
        columns_headers = data.get('headers', [])
        rows = data.get('rows', [])
        model_class = request.env[model]
        recs = model_class.search([],order='thiet_bi_id asc, name asc')
       
        columns_headers = ['name','adaptor_number','odf_number']
        columns_headers=['name','soi_ids_char','ada_ids_char']

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1',cell_overwrite_ok=True)
#         worksheet.col(3).width =int(13*260)
#         worksheet.col(4).width =int(13*260)
#         worksheet.col(5).width =int(13*260)
        worksheet.write_merge(0, 1, 0 , 0,u"Thiết bị",title_format_style)
        worksheet.write_merge(0, 1, 1 ,1,u"Hướng",title_format_style)
        worksheet.write_merge(0, 0, 2 ,3,u"PHƯƠNG ÁN",title_format_style)
        worksheet.write(1 , 2, u'Sợi', title_format_style)
        worksheet.write(1 , 3, u'STT TRÊN ODF', title_format_style)
        worksheet.write_merge(0, 1, 4 ,4,u"Đang chạy",title_format_style)
        
        worksheet.write_merge(0, 0, 5 ,6,u"DP1",title_format_style)
        worksheet.write(1 , 5, u'Sợi', title_format_style)
        worksheet.write(1 , 6, u'STT TRÊN ODF', title_format_style)
        
        worksheet.write_merge(0, 0, 7 ,8,u"DP2",title_format_style)
        worksheet.write(1 , 7, u'Sợi', title_format_style)
        worksheet.write(1 , 8, u'STT TRÊN ODF', title_format_style)
        
        worksheet.write_merge(0, 0,9 ,10,u"DP3",title_format_style)
        worksheet.write(1 , 9, u'Sợi', title_format_style)
        worksheet.write(1 , 10, u'STT TRÊN ODF', title_format_style)
        
        
        
        
        huong_id_truoc = None
        row_index =0
        col_begin=0
        thiet_bi_id_truoc_name = None
        for count,r in enumerate(recs):
            if r.huong_id !=huong_id_truoc:
                row_index +=2
                huong_id_truoc =r.huong_id
                huong_id_first_col_write = True # huong thi write 1 lan thoi
                if r.thiet_bi_id.name != thiet_bi_id_truoc_name or count ==len(recs)-1 :
                    if thiet_bi_id_truoc_name!=None:
                        if count == len(recs) - 1:
                            end_thiet_bi_row = row_index + 1
                        else:
                            end_thiet_bi_row = row_index -1 # lấy cái ô trước khi thay đổi rồi merge
                        worksheet.write_merge(begin_row_thietbi, end_thiet_bi_row, col_begin , col_begin,
                                              thiet_bi_id_truoc_name,thiet_bi_style)
                    begin_row_thietbi = row_index
                    thiet_bi_id_truoc_name = r.thiet_bi_id.name
            if  huong_id_first_col_write:
                cell_value = r.huong_id.name
                cell_value,cell_style = style_something(r.huong_id.name)
                worksheet.write_merge(row_index, row_index+1, col_begin+1 , col_begin+1,
                                              cell_value,cell_style)
#                 worksheet.row(row_index).height_mismatch = True
#                 worksheet.row(row_index).height = 256* 3

                for empty_col_index in range(2 + col_begin,10 + col_begin):
                    worksheet.write(row_index,empty_col_index,'', base_style)
                huong_id_first_col_write = False
            write_soi_or_ada_to_cell(worksheet,r,row_index,attr = 'soi_ids_char',delta_between_soi_and_ada = 0)
            write_soi_or_ada_to_cell(worksheet,r,row_index,attr = 'ada_ids_char',delta_between_soi_and_ada = 1)
            write_soi_or_ada_to_cell(worksheet,r,row_index+1,attr = 'odf_dau_xa',delta_between_soi_and_ada = 1)



        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        #return data
    
    
        
        return request.make_response(
            data,
            #self.from_data(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
