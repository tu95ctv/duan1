# -*- coding: utf-8 -*-

import datetime
import re
# string = u'hôm nay 10:19'
# new = string.replace(u'hôm nay',datetime.date.today().strftime('%d/%m/%Y'))
# print new
# new_date =  datetime.datetime.strptime(new,'%d/%m/%Y %H:%M')
# print new_date
string = u'hôm nay 10:19'
string= u"ngày 25 tháng 07 07:15"
string =u"hôm qua 18:59"
if u'hôm nay' in string:
    new = string.replace(u'hôm nay',datetime.date.today().strftime('%d/%m/%Y'))
elif u'hôm qua' in string:
    hom_qua_date = datetime.date.today() -  datetime.timedelta(days=1)
    new = string.replace(u'hôm qua',hom_qua_date.strftime('%d/%m/%Y'))
else:
    
    new=string.replace(u'ngày ','').replace(u' tháng ','/').replace(' ','/2017 ')
new_date =  datetime.datetime.strptime(new,'%d/%m/%Y %H:%M')
print new_date

