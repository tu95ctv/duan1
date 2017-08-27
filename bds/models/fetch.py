# -*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import datetime
import re
from unidecode import unidecode
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
        is_write = True
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
            print 'searched_object',searched_object
            print 'create_write_dict',create_write_dict
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
    print 'select[0].contents',select[0].contents
    ngay_dang_str = select[0].contents[2]
    ngay_dang_str = ngay_dang_str.replace('\r','').replace('\n','')
    ngay_dang_str = re.sub('\s*', '', ngay_dang_str)
    ngay_dang = datetime.datetime.strptime(ngay_dang_str,"%d-%m-%Y")
    return ngay_dang
def get_product_detail(soup):
    select = soup.select('div#product-detail')[0]
    print select
    return select
    raise ValueError('select')
def fetch(self,page_end,save_db=True):
    #url_imput = 'https://batdongsan.com.vn/ban-nha-rieng-quan-10/-1/2500-3500/-1/-1'
    if self.url_id:
        url_imput=self.url_id.name
    else:
        if self.url:
            url_imput= self.url
            url_id = get_or_create_object(self,'bds.urlcate', {'name': url_imput}, {}, True)
            self.url_id = url_id.id
        else:
            raise ValueError('khong de bo trong url hoạc url id')
    html = request_html(url_imput)
    html_doc = html
    soup = BeautifulSoup(html_doc, 'html.parser')
    if not page_end:
        last_pages = soup.select('div.background-pager-right-controls > a')
        print last_pages
        print last_pages[-1]
        last_page =  last_pages[-1]['href']
        last_page_int = int(last_page[-1])
    else:
        last_page_int = page_end
    link_number = 0
    update_link_number = 0
    create_link_number = 0
        
    for page_int in range(1,last_page_int+1):
        url = url_imput + '/' + 'p' +str(page_int)
        html = request_html(url)
        html_doc = html
        soup = BeautifulSoup(html_doc, 'html.parser')
        kqs = soup.find_all("div", class_="p-title")
        links = []
        for div in kqs:
            for a in div.find_all('a', href=True):
                links.append(a['href'])
        if links:
            self.write({'bds_ids':[(5,0,0)]})
        for l in links:
            link_number +=1
            search_dict = {}
            update_dict = {}
            link = 'https://batdongsan.com.vn' + l
            search_dict['link'] = link
            html = request_html(link)
            soup = BeautifulSoup(html, 'html.parser')
            update_dict['ngay_dang'] = get_ngay_dang(soup)
            update_dict['html'] = get_product_detail(soup)
            try:
                update_dict['gia'] = get_price(soup)
            except:
                pass
            try:
                update_dict['area'] = get_dientich(soup)
            except:
                pass
            quan_id= get_quan_from_topic(self,soup)
            update_dict['quan_id'] = quan_id
            update_dict['phuong_id'] = get_phuong_xa_from_topic(self,soup,quan_id)
            get_all_phuong_xa_of_quan_from_topic(self,soup,quan_id)
            title = soup.select('div.pm-title > h1')[0].contents[0]
            update_dict['title']=title
            print '*'*334,self.id
            #update_dict['fetch_ids']=[(4,self.id)]
            print 'title',title,page_int
            user = get_or_create_user(self,soup,save_db)
            update_dict['poster_id'] = user.id
            update_dict.update({'fetch_ids':[(4,self.id)]})
            if save_db:
                bds_obj,create_or_get = get_or_create_object(self,'bds.bds',search_dict,update_dict,is_must_update=True,create_or_get_return=True)
                if create_or_get =='create':
                    create_link_number += 1
                else:
                    update_link_number +=1
                print 'self.id,obj.id',self.id,bds_obj.id
                #bds_obj.write({'fetch_ids':[(4,self.id)]})
                #self.write({'bds_ids':[(4,obj.id)]})
    if save_db:
        return create_link_number,update_link_number,link_number
    
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
def get_or_create_user(self,soup,save_db):
    search_dict = {}
    update_dict = {}
    mobile = get_mobile_user(soup)
    search_dict['phone'] = mobile
    search_dict['login'] = str(mobile)+'@gmail.com'
    try:
        name = get_name_user(soup)
    except:
        name = str(mobile)
    search_dict['name'] = name
    update_dict['name'] = name
    if save_db:
        user = get_or_create_object(self,'res.users', search_dict, update_dict, is_must_update=False)
        return user
def detect_number():
    string = 'Liên hệ: 0903006436 - 0989089751 Mr Đại.'
    pattern = '\d{10,11}'
    kq = re.findall(pattern,string)
    print kq
quan_huyen_data = '''<ul class="advance-options" style="min-width: 218px;">
<li vl="0" class="advance-options current" style="min-width: 186px;">--Chọn Quận/Huyện--</li><li vl="72" class="advance-options" style="min-width: 186px;">Bình Chánh</li><li vl="65" class="advance-options" style="min-width: 186px;">Bình Tân</li><li vl="66" class="advance-options" style="min-width: 186px;">Bình Thạnh</li><li vl="73" class="advance-options" style="min-width: 186px;">Cần Giờ</li><li vl="74" class="advance-options" style="min-width: 186px;">Củ Chi</li><li vl="67" class="advance-options" style="min-width: 186px;">Gò Vấp</li><li vl="75" class="advance-options" style="min-width: 186px;">Hóc Môn</li><li vl="76" class="advance-options" style="min-width: 186px;">Nhà Bè</li><li vl="68" class="advance-options" style="min-width: 186px;">Phú Nhuận</li><li vl="53" class="advance-options" style="min-width: 186px;">Quận 1</li><li vl="62" class="advance-options" style="min-width: 186px;">Quận 10</li><li vl="63" class="advance-options" style="min-width: 186px;">Quận 11</li><li vl="64" class="advance-options" style="min-width: 186px;">Quận 12</li><li vl="54" class="advance-options" style="min-width: 186px;">Quận 2</li><li vl="55" class="advance-options" style="min-width: 186px;">Quận 3</li><li vl="56" class="advance-options" style="min-width: 186px;">Quận 4</li><li vl="57" class="advance-options" style="min-width: 186px;">Quận 5</li><li vl="58" class="advance-options" style="min-width: 186px;">Quận 6</li><li vl="59" class="advance-options" style="min-width: 186px;">Quận 7</li><li vl="60" class="advance-options" style="min-width: 186px;">Quận 8</li><li vl="61" class="advance-options" style="min-width: 186px;">Quận 9</li><li vl="69" class="advance-options" style="min-width: 186px;">Tân Bình</li><li vl="70" class="advance-options" style="min-width: 186px;">Tân Phú</li><li vl="71" class="advance-options" style="min-width: 186px;">Thủ Đức</li>
</ul>'''
def import_quan_data(self):
    soup = BeautifulSoup(quan_huyen_data, 'html.parser')
    lis =  soup.select('li')
    for li in lis:
        quan =  li.get_text()
        quan_unidecode = unidecode(quan).lower().replace(' ','-')
        get_or_create_object(self,'bds.quan', {'name':quan}, {'name_unidecode':quan_unidecode}, True)
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
        phuong = get_or_create_object(self,'bds.phuong', {'name_phuong':phuong_name,'quan_id':quan_id}, {'quan_id':quan_id}, True)
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
            phuong = get_or_create_object(self,'bds.phuong', {'name_phuong':phuong_name,'quan_id':quan_id}, {'quan_id':quan_id}, True)
    else:
        return False
    
def get_quan_from_topic(self,soup):
    sl = soup.select('div#divDistrictOptions li.current')   
    if sl:
        quan_name =  sl[0].get_text()
        quan_unidecode = unidecode(quan_name).lower().replace(' ','-')
        quan = get_or_create_object(self,'bds.quan', {'name':quan_name}, {'name_unidecode':quan_unidecode}, True)
        return quan.id
    else:
        return False
if __name__== '__main__':
    get_quan_from_topic(get_soup_from_file())

    
