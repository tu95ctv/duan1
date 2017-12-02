# -*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import datetime
import re
from unidecode import unidecode
import xlrd
import base64
import json
from time import sleep
import pytz
import logging
_logger = logging.getLogger(__name__)

create_number_dict = {}
update_number_dict ={}
get_number_dict = {}
def convert_object(self,class_name,mess_object):# mac dinh la mess_object ton tai
    if isinstance(mess_object, list):
        mess_object_id =mess_object[0]
    elif isinstance(mess_object,int):
        mess_object_id = mess_object
    else:
        return mess_object
    mess_object = self.env[class_name].browse(mess_object_id)
    return mess_object

def get_or_create_object(self,class_name,search_dict,create_write_dict ={},is_must_update=True,create_or_get_return = False,has_write_m2x=True):
    domain_list = []
    for i in search_dict:
        tuple_in = (i,'=',search_dict[i])
        domain_list.append(tuple_in)
    searched_object  = self.env[class_name].search(domain_list)
    if not searched_object:
        current_number = create_number_dict.setdefault(class_name,0)
        create_number_dict[class_name] = current_number +  1
        
        if not has_write_m2x:
            search_dict.update(create_write_dict)
            update_search_dict = search_dict
            
        else:
            update_search_dict = search_dict
        created_object = self.env[class_name].create(update_search_dict)
        created_object = convert_object(self,class_name,created_object)
        if  has_write_m2x:
            created_object.write(create_write_dict)
        if create_or_get_return:
            return created_object,'create'
        else:
            return created_object
    else:
        searched_object = convert_object(self,class_name,searched_object)
        is_write = False
#         for attr in create_write_dict:
#             domain_val = create_write_dict[attr]
#             exit_val = getattr(searched_object,attr)
#             exit_val = getattr(exit_val,'id',exit_val)
#             if exit_val ==None: #recorderset.id ==None when recorder sset = ()
#                 exit_val=False
#             if unicode(exit_val) !=unicode(domain_val):
#                 is_write = True
#                 break
        if is_write or is_must_update:
            current_number = update_number_dict.setdefault(class_name,0)
            update_number_dict[class_name] = current_number +  1
            searched_object.write(create_write_dict)
        else:
            current_number = get_number_dict.setdefault(class_name,0)
            get_number_dict[class_name] = current_number +  1
            
        if create_or_get_return:
            return searched_object,'get'
        else:
            return searched_object

def request_html(url):
    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36' }
    req = urllib2.Request(url, None, headers)
    html = urllib2.urlopen(req).read()
    return html
def get_ngay_dang(soup):
    select = soup.select('div.prd-more-info > div:nth-of-type(3)')#[0].contents[0]
    ngay_dang_str = select[0].contents[2]
    ngay_dang_str = ngay_dang_str.replace('\r','').replace('\n','')
    ngay_dang_str = re.sub('\s*', '', ngay_dang_str)
    ngay_dang = datetime.datetime.strptime(ngay_dang_str,"%d-%m-%Y")
    return ngay_dang
def get_product_detail(soup):
    select = soup.select('div#product-detail')[0]
    return select
def get_quan_list_in_big_page(self,column_name='bds_bds.phuong_id'):
    product_category_query = '''select  count(%s), %s from fetch_bds_relate inner join bds_bds on fetch_bds_relate.bds_id = bds_bds.id where fetch_id = %s group by %s'''%(column_name,column_name,self.id,column_name)
    self.env.cr.execute(product_category_query)
    product_category = self.env.cr.fetchall()
    phuong_list = reduce(lambda y,x:([x[1]]+y) if x[1]!=None else y,product_category,[] )
    return phuong_list
def update_phuong_or_quan_for_url_id(self,quan_list=[],phuong_list=[],url_id=None):
    #phuong_list = get_quan_list_in_big_page(self)
    #quan_list = get_quan_list_in_big_page(self,column_name='bds_bds.quan_id')
    if len(phuong_list) == 1:
        url_id.phuong_id = phuong_list[0]
        url_id.quan_id = False
    elif len(quan_list) ==1:
        url_id.quan_id = quan_list[0]
        url_id.phuong_id =False
def get_mobile_name_for_batdongsan(soup):
    mobile = get_mobile_user(soup)
    try:
        name = get_name_user(soup)
    except:
        name = 'no name bds'
    return mobile,name
    
# def get_or_create_user(self,soup,save_db):
#     search_dict = {}
#     update_dict = {}
#     
#     
#     search_dict['phone'] = mobile
#     search_dict['login'] = str(mobile)+'@gmail.com'
#     try:
#         name = get_name_user(soup)
#     except:
#         name = str(mobile)
#     update_dict['name'] = name
#     if save_db:
#         user = get_or_create_object(self,'res.users', search_dict, update_dict, is_must_update=False,has_write_m2x=False)
#         return user



def get_update_dict_in_topic(self,update_dict,html,siteleech_id,only_return_price=False):
    update_dict['data'] = html
    soup = BeautifulSoup(html, 'html.parser')
    try:
        gia = get_price(soup)
    except:
        gia =0
    update_dict['gia'] = gia
    if  only_return_price:
        return gia
    
    update_dict['ngay_dang'] = get_ngay_dang(soup)
    update_dict['html'] = get_product_detail(soup)
    update_dict['siteleech_id'] = siteleech_id.id
    try:
        update_dict['area'] = get_dientich(soup)
    except:
        pass
    quan_id= get_quan_from_topic(self,soup)
    update_dict['quan_id'] = quan_id
    update_dict['phuong_id'] = get_phuong_xa_from_topic(self,soup,quan_id)
    #get_all_phuong_xa_of_quan_from_topic(self,soup,quan_id)
    title = soup.select('div.pm-title > h1')[0].contents[0]
    update_dict['title']=title
    #print 'title',title
    mobile,name = get_mobile_name_for_batdongsan(soup)
    user = get_or_create_user_cho_tot_batdongsan(self,mobile,name,siteleech_id.name)
    update_dict['user_name_poster']=name
    update_dict['phone_poster']=mobile
    update_dict['poster_id'] = user.id
def get_mobile_name_cho_tot(html):
    mobile = html['phone']
    name = html['account_name']
    return mobile,name
def get_or_create_user_cho_tot_batdongsan(self,mobile,name,type_site):
    search_dict = {}
    update_dict = {}
    search_dict['phone'] = mobile
    search_dict['login'] = str(mobile)+'@gmail.com'
    search_dict['name'] = mobile
    update_dict['ghi_chu'] = 'created by %s'%type_site
    user =  self.env['res.users'].search([('phone','=',mobile)])
    site_id = get_or_create_object(self,'bds.siteleech', {'name':type_site}, {}, False, False, False)
    if user:
        posternamelines_id = get_or_create_object(self,'bds.posternamelines',
                                               {'username_in_site':name,'site_id':site_id.id,'poster_id':user.id}, {}, False, False, False)
    else:
        search_dict.update({'ghi_chu':'created by %s'%type_site})
        user =  self.env['res.users'].create(search_dict)
        self.env['bds.posternamelines'].create( {'username_in_site':name,'site_id':site_id.id,'poster_id':user.id})
    #update_dict['username_in_site_ids'] =[(4,posternamelines_id.id)]
    #user = get_or_create_object(self,'res.users', search_dict, update_dict, is_must_update=True,has_write_m2x=True)
    return user
def create_or_get_quan_for_chotot(self,quan):
    name_without_quan_huyen = quan.replace(u'Quận ','').replace(u'Huyện','')
    rs = self.env['bds.quan'].search([('name_without_quan','=',name_without_quan_huyen)])
    if not rs:
        name_unidecode  = unidecode(quan).lower().replace(' ','-')
        rs = self.env['bds.quan'].create({'name':quan,'name_unidecode':name_unidecode,'name_without_quan':name_without_quan_huyen})
    return rs        
def local_a_native_time(datetime_input):
    local = pytz.timezone("Etc/GMT-7")
    local_dt = local.localize(datetime_input, is_dst=None)
    utc_dt = local_dt.astimezone (pytz.utc)
    return utc_dt#utc_dt
def get_date_cho_tot(string):  
    try:
        print 'ngay dang from cho tot',string
        if u'hôm nay' in string:
            new = string.replace(u'hôm nay',datetime.date.today().strftime('%d/%m/%Y'))
        elif u'hôm qua' in string:
            hom_qua_date = datetime.date.today() -  datetime.timedelta(days=1)
            new = string.replace(u'hôm qua',hom_qua_date.strftime('%d/%m/%Y'))
        else:
            new=string.replace(u'ngày ','').replace(u' tháng ','/').replace(' ','/2017 ')
        new_date =  datetime.datetime.strptime(new,'%d/%m/%Y %H:%M')     
        return local_a_native_time(new_date)
    except:
        return False
def get_update_dict_in_topic_cho_tot(self,update_dict,html_big,siteleech_id,only_return_price=False):
    html=html_big['ad']
    try:
        price = float(html['price'])/1000000000
        
    except KeyError:
        price = 0
    date = html['date']
    date_obj = get_date_cho_tot(date)
    update_dict['ngay_dang']=date_obj
    update_dict['siteleech_id'] = siteleech_id.id
    
    if only_return_price:
        return price
    try:
        images = html['images']
        try:
            present_image_link = images[0]
        except IndexError:
            present_image_link = False
        update_dict['present_image_link'] = present_image_link  
    except KeyError:
        pass
    update_dict['data'] = html
    try:
        address = html['address']
        update_dict['address'] = address
    except KeyError:
        pass
    
    try:
        quan = html_big['ad_params']['area']['value']
        update_dict['parameters'] = quan
        
        rs = create_or_get_quan_for_chotot(self,quan)
        update_dict['quan_id'] = rs.id
    except KeyError:
        pass
    
    
    update_dict['gia'] = price
    
    mobile,name = get_mobile_name_cho_tot(html)
    user = get_or_create_user_cho_tot_batdongsan(self,mobile,name ,siteleech_id.name)
    update_dict['user_name_poster']=name
    update_dict['phone_poster']=mobile
    update_dict['poster_id'] = user.id
    try:
        update_dict['html'] = html['body']
    except KeyError:
        pass
    
    update_dict['area']=html.get('size',0)
    update_dict['title']=html['subject']
def deal_a_link(self,link,number_notice_dict,siteleech_id):
    #link_number +=1
    search_dict = {}
    update_dict = {}
#     is_link_exist = False
   
#         is_link_exist = True
#         self.write({'bds_ids':[(4,search_link_existing[0].id)]})
#         return None

    search_dict['link'] = link
    print link
    html = request_html(link)
    #raise ValueError(html)
    if siteleech_id.name =='batdongsan':
        pass
    elif siteleech_id.name =='chotot':
        html = json.loads(html)
        
    if siteleech_id.name =='batdongsan':    
        price = get_update_dict_in_topic(self,update_dict,html,siteleech_id,only_return_price=True)
    elif siteleech_id.name =='chotot':
        price = get_update_dict_in_topic_cho_tot(self,update_dict,html,siteleech_id,only_return_price=True)
    
    search_link_existing= self.env['bds.bds'].search([('link','=',link)])
    if search_link_existing:
        number_notice_dict["existing_link_number"] = number_notice_dict["existing_link_number"] + 1
        if self.update_field_of_existing_recorder ==u'giá':
            search_link_and_price_existing= self.env['bds.bds'].search([('link','=',link),('gia','=',price)])
            if search_link_and_price_existing:
                return None
            else:
                search_link_existing.write({'gia':price})
                number_notice_dict['update_link_number'] = number_notice_dict['update_link_number'] + 1
        elif self.update_field_of_existing_recorder ==u'all':
            if siteleech_id.name =='batdongsan':    
                get_update_dict_in_topic(self,update_dict,html,siteleech_id)
            elif siteleech_id.name =='chotot':
                get_update_dict_in_topic_cho_tot(self,update_dict,html,siteleech_id)
            update_dict.update({'fetch_ids':[(4,self.id)]})
            search_link_existing.write(update_dict)
            number_notice_dict['update_link_number'] = number_notice_dict['update_link_number'] + 1
            print 'update all field a link' 
        else:
            print 'khong update existing linnk'
    else:
        if siteleech_id.name =='batdongsan':    
            get_update_dict_in_topic(self,update_dict,html,siteleech_id)
        elif siteleech_id.name  =='chotot':
            get_update_dict_in_topic_cho_tot(self,update_dict,html,siteleech_id)
        update_dict['link'] = link
        update_dict.update({'fetch_ids':[(4,self.id)]})
        self.env['bds.bds'].create(update_dict)
        number_notice_dict['create_link_number'] = number_notice_dict['create_link_number'] + 1    
#     elif type_site =='chotot':
#         html = json.loads(html)
#         html=html['ad']
#         price = get_update_dict_in_topic_cho_tot(self,update_dict,html,type_site,only_return_price=True)
#         get_update_dict_in_topic_cho_tot(self,update_dict,html,type_site)
        
#     update_dict.update({'fetch_ids':[(4,self.id)]})
#     bds_obj,create_or_get = get_or_create_object(self,'bds.bds',search_dict,update_dict,is_must_update=True,create_or_get_return=True)
#     if create_or_get =='create':
#         create_link_number += 1
#     else:
#         update_link_number +=1
        
        

def page_handle(self, page_int, url_id, number_notice_dict):
    links_per_page = []
    url_imput = url_id.url
    siteleech_id = url_id.siteleech_id
    if siteleech_id.name=='batdongsan':
        url = url_imput + '/' + 'p' +str(page_int)
        html = request_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        title_soups = soup.select("div.p-title  a")
        for a in title_soups:
            l =a['href']
            link = 'https://batdongsan.com.vn' + l
            links_per_page.append(link)
    elif siteleech_id.name =='chotot':
        repl = 'o=%s'%(20*(page_int-1))
        url_imput = re.sub('o=\d+',repl,url_imput)
        url = url_imput +  '&page=' +str(page_int)
        print 'handling....page',url
        html = request_html(url)
        html = json.loads(html)
        html = html['ads']
        for i in html:
            url = 'https://gateway.chotot.com/v1/public/ad-listing/' + str(i['list_id'])
            links_per_page.append(url)
    for link in links_per_page:
        number_notice_dict["link_number"] = number_notice_dict["link_number"] + 1
        #deal_a_link(self,link,type_site,number_notice_dict)
        while (True):
            try:
                deal_a_link(self,link,number_notice_dict,siteleech_id)
                break
            except Exception as e:
                #raise ValueError(str(e))
                self.env['bds.error'].create({'code':str(e),'url':link})
                print 'url','sleep....because error'
                sleep(5)
                 
def get_last_page_from_bdsvn_website(url_imput):
    
    html = request_html(url_imput)
    soup = BeautifulSoup(html, 'html.parser')
    range_pages = soup.select('div.background-pager-right-controls > a')
    if range_pages:
        last_page_href =  range_pages[-1]['href']
        #end_page = int(last_page_href[-1])
        kq= re.search('\d+$',last_page_href)
        last_page_from_website =  int(kq.group(0))
    else:
        last_page_from_website = 1
    return last_page_from_website


def get_page_lists(self,url_id,is_fetch_in_cron):
    if url_id.siteleech_id.name ==  'batdongsan':
        last_page_from_website =  get_last_page_from_bdsvn_website(url_id.url)
        self.web_last_page_number = last_page_from_website
    elif url_id.siteleech_id.name=='chotot':
        last_page_from_website =6000
    if is_fetch_in_cron:
        set_page_end = False
    else:
        set_page_end  =self.set_page_end
        
    if not set_page_end:
        end_page = last_page_from_website
    else:
        end_page = set_page_end if set_page_end <= last_page_from_website else last_page_from_website
    if is_fetch_in_cron:
        current_page = url_id.current_page
        if  self.set_number_of_page_once_fetch ==0 or self.number_of_page_once_fetch==1:
            if end_page <2:
                page_lists = [1]
                last_page_in_once_fetch=1
            else:
                last_page_in_once_fetch = current_page +  1
                if last_page_in_once_fetch > end_page:
                    last_page_in_once_fetch = 2
                page_lists = [1,last_page_in_once_fetch]
        else:
            begin = current_page + 1
            end = current_page   + self.number_of_page_once_fetch
            if begin>end_page:
                begin  = 1
                end = self.number_of_page_once_fetch
            else:
                if end > end_page:
                    end =  end_page
            last_page_in_once_fetch =end
            page_lists = range(begin,end+1)
    else:
        begin = url_id.current_page + 1
        end = url_id.current_page   + self.number_of_page_once_fetch
        if begin>end_page:
            begin  = 1
            end = self.number_of_page_once_fetch
        else:
            if end > end_page:
                end =  end_page
        last_page_in_once_fetch =end
        page_lists = range(begin,end+1)
    return last_page_in_once_fetch,page_lists

def fetch(self,note=False,is_fetch_in_cron = False):
    fetch1(self,note,is_fetch_in_cron)
#     count_fault =0
#     while 1:
#         
#         try:
#             
#             fetch1(self,note,is_fetch_in_cron)
#             count_fault=0
#             break
#         except Exception as e:
#             count_fault +=1
#             if count_fault==1:
#                 break
#             self.env['bds.error'].create({'code':str(e),'url':'fech page not link'})
#             _logger.debug('loi ban oi',str(e))
#             print 'url','sleep....because on page'
#             sleep(5)
                
def fetch1(self,note=False,is_fetch_in_cron = False):
#     if not self.is_fetch_circle:
#         url_imput = get_url(self)
#     
#     if not self.is_fetch_circle:
#         url_id = self.url_id
#         current_url_id_circle_fetch = None
#     else:
    url_ids = self.url_ids.sorted(lambda l:l.id)
    url_ids_id_lists = url_ids.mapped('id')
    if not self.current_url_id_circle_fetch:
        new_index = 0
    else:
        index_of_current_url_id_circle_fetch = url_ids_id_lists.index(self.current_url_id_circle_fetch)
        new_index =  index_of_current_url_id_circle_fetch+1
        if new_index > len(url_ids_id_lists)-1:
            new_index = 0
    url_id = url_ids[new_index]
    current_url_id_circle_fetch = url_ids_id_lists[new_index]
  
    last_page_in_once_fetch, int_page_lists = get_page_lists (self, url_id, is_fetch_in_cron)
    number_notice_dict = {
    'link_number' : 0,
    'update_link_number' : 0,
    'create_link_number' : 0,
    'existing_link_number' : 0
    }
    for page_int in int_page_lists:
        page_handle(self, page_int, url_id, number_notice_dict)
    url_id.write({'current_page':last_page_in_once_fetch})
    if self.is_fetch_circle:
        self.current_url_id_circle_fetch = current_url_id_circle_fetch
        
    self.create_link_number=number_notice_dict['create_link_number']
    self.update_link_number =number_notice_dict["update_link_number"]
    self.link_number = number_notice_dict["link_number"]
    self.existing_link_number = number_notice_dict["existing_link_number"]
    if url_id.siteleech_id.name ==  'batdongsan':
        phuong_list = get_quan_list_in_big_page(self)
        quan_list = get_quan_list_in_big_page(self,column_name='bds_bds.quan_id')
        self.write({'phuong_ids':[(6,0,phuong_list)],'quan_ids':[(6,0,quan_list)]})#'quan_ids':[(6,0,quan_list)]
        url_id.web_last_page_number= self.web_last_page_number
        update_phuong_or_quan_for_url_id(self,quan_list,phuong_list,url_id)
    else:
        quan_list = get_quan_list_in_big_page(self,column_name='bds_bds.quan_id')
        self.write({'quan_ids':[(6,0,quan_list)]})#'quan_ids':[(6,0,quan_list)]
    self.note = note
    return None
    
def get_price(soup):
    kqs = soup.find_all("span", class_="gia-title")
    gia = kqs[0].find_all("strong")
    gia = gia[0].get_text()
    if u'tỷ' in gia:
        int_gia = gia.replace(u'tỷ','').rstrip()
        int_gia = float(int_gia)
    return int_gia
def get_dientich(soup):
    kqs = soup.find_all("span", class_="gia-title")
    gia = kqs[1].find_all("strong")
    gia = gia[0].get_text()
    rs = re.search(ur'(\d+)', gia)
    gia = rs.group(1)
    int_gia = float(gia)
    return int_gia
def get_mobile_user(soup,id_select = 'div#LeftMainContent__productDetail_contactMobile'):
    select = soup.select(id_select)[0]
    mobile =  select.contents[3].contents[0]
    mobile =  mobile.strip()
    if not mobile:
        raise ValueError('sao khong co phone')
    return mobile
def get_name_user(soup):
    name = get_mobile_user(soup,id_select = 'div#LeftMainContent__productDetail_contactName')
    return name

    
    
    
def detect_number():
    string = 'Liên hệ: 0903006436 - 0989089751 Mr Đại.'
    pattern = '\d{10,11}'
    kq = re.findall(pattern,string)
quan_huyen_data = '''<ul class="advance-options" style="min-width: 218px;">
<li vl="0" class="advance-options current" style="min-width: 186px;">--Chọn Quận/Huyện--</li><li vl="72" class="advance-options" style="min-width: 186px;">Bình Chánh</li><li vl="65" class="advance-options" style="min-width: 186px;">Bình Tân</li><li vl="66" class="advance-options" style="min-width: 186px;">Bình Thạnh</li><li vl="73" class="advance-options" style="min-width: 186px;">Cần Giờ</li><li vl="74" class="advance-options" style="min-width: 186px;">Củ Chi</li><li vl="67" class="advance-options" style="min-width: 186px;">Gò Vấp</li><li vl="75" class="advance-options" style="min-width: 186px;">Hóc Môn</li><li vl="76" class="advance-options" style="min-width: 186px;">Nhà Bè</li><li vl="68" class="advance-options" style="min-width: 186px;">Phú Nhuận</li><li vl="53" class="advance-options" style="min-width: 186px;">Quận 1</li><li vl="62" class="advance-options" style="min-width: 186px;">Quận 10</li><li vl="63" class="advance-options" style="min-width: 186px;">Quận 11</li><li vl="64" class="advance-options" style="min-width: 186px;">Quận 12</li><li vl="54" class="advance-options" style="min-width: 186px;">Quận 2</li><li vl="55" class="advance-options" style="min-width: 186px;">Quận 3</li><li vl="56" class="advance-options" style="min-width: 186px;">Quận 4</li><li vl="57" class="advance-options" style="min-width: 186px;">Quận 5</li><li vl="58" class="advance-options" style="min-width: 186px;">Quận 6</li><li vl="59" class="advance-options" style="min-width: 186px;">Quận 7</li><li vl="60" class="advance-options" style="min-width: 186px;">Quận 8</li><li vl="61" class="advance-options" style="min-width: 186px;">Quận 9</li><li vl="69" class="advance-options" style="min-width: 186px;">Tân Bình</li><li vl="70" class="advance-options" style="min-width: 186px;">Tân Phú</li><li vl="71" class="advance-options" style="min-width: 186px;">Thủ Đức</li>
</ul>'''
def import_quan_data(self):
    soup = BeautifulSoup(quan_huyen_data, 'html.parser')
    lis =  soup.select('li')
    for li in lis:
        quan =  li.get_text()
        name_without_quan = quan.replace(u'Quận ','')
        quan_unidecode = unidecode(quan).lower().replace(' ','-')
        get_or_create_object(self,'bds.quan', {'name':quan}, {'name_unidecode':quan_unidecode,'name_without_quan':name_without_quan}, True)
    return len(lis)
def request_and_write_to_disk(url):
    url = 'https://batdongsan.com.vn/ban-nha-rieng-duong-cao-thang-phuong-11-5/ket-tien-gap-hem-p-q-10-ngay-goc-dien-bien-phu-pr13372162'
    my_html = request_html(url)
    file = open('E:\mydata\python_data\my_html.html','w')
    file.write(my_html)
    file.close()
def get_soup_from_file():
    file = open('E:\mydata\python_data\my_html.html','r')
    my_html = file.read()
    soup = BeautifulSoup(my_html, 'html.parser')
    return soup
def get_phuong_xa_from_topic(self,soup,quan_id):
    sl = soup.select('div#divWard li.current')   
    if sl:
        phuong_name =  sl[0].get_text()
        phuong = get_or_create_object(self,'bds.phuong', {'name_phuong':phuong_name,'quan_id':quan_id}, {'quan_id':quan_id}, False)
        return phuong.id
    else:
        return False
def get_all_phuong_xa_of_quan_from_topic(self,soup,quan_id):
    sls = soup.select('div#divWard li')   
    if sls:
        for sl in sls:
            phuong_name =  sl.get_text()
            if '--' in phuong_name:
                continue
            phuong = get_or_create_object(self,'bds.phuong', {'name_phuong':phuong_name,'quan_id':quan_id}, {'quan_id':quan_id}, False)
    else:
        return False
    
def get_quan_from_topic(self,soup):
    sl = soup.select('div#divDistrictOptions li.current')   
    if sl:
        quan_name =  sl[0].get_text()
        quan_unidecode = unidecode(quan_name).lower().replace(' ','-')
        quan = get_or_create_object(self,'bds.quan', {'name':quan_name}, {'name_unidecode':quan_unidecode}, False)
        return quan.id
    else:
        return False
def import_contact(self):
    recordlist = base64.decodestring(self.file)
    excel = xlrd.open_workbook(file_contents = recordlist)
    sheet = excel.sheet_by_index(0)
    full_name_index = 2
    phone_index = 4
    
    land_contact_saved_number = 0
    for row in range(2,sheet.nrows):
        full_name = sheet.cell_value(row,full_name_index)
        phone = sheet.cell_value(row,phone_index)
        phone = phone.replace('(Mobile)','').replace('(Home)','').replace('(Other)','').replace(' ','').replace('+84','0')
        print phone,full_name
        rs_mycontact  = self.env['bds.mycontact'].search([('phone','=',phone)])
        if rs_mycontact:
            if rs_mycontact.name != full_name:
                rs_mycontact.write({'name':full_name})
        else:
            rs_mycontact = self.env['bds.mycontact'].create({'name':full_name,'phone':phone})
        rs_user = self.env['res.users'].search([('phone','=',phone)])
        if rs_user:
            land_contact_saved_number +=1
            rs_user.write({'ten_luu_trong_danh_ba':full_name,'mycontact_id':rs_mycontact.id})
    self.land_contact_saved_number = land_contact_saved_number
            
        
if __name__== '__main__':
#     get_quan_from_topic(get_soup_from_file())
    url_imput = 'https://nha.chotot.com/tp-ho-chi-minh/quan-10/mua-ban-nha-dat'
    url_imput = 'https://nha.chotot.com/quan-10/mua-ban-nha-dat/nha-hxh-duong-ly-thuong-kiet-quan-10-38471382.htm'
    #url_imput = 'https://gateway.chotot.com/v1/public/ad-listing/38471382'
    url_imput = 'https://gateway.chotot.com/v1/public/ad-listing/38483113'
    html = request_html(url_imput)
    print html

    
