# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 10:57:25 2017

@author: Lily
"""

import html, MySQLdb, time, datetime, re
from html.parser import HTMLParser

#==============================================================================
# #file_path = os.path.dirname(__file__)
# A = "SP-1BAY-STAND-SILVER"
# B = "data/QNAP/SP-1BAY-STAND-SILVER.jpg"
# # write-in DB
# db = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas")
# cursor = db.cursor()
# sql = "INSERT INTO NEW_PRODUCT_ACCESSORY(sku, \
#     image, published_at, created_at, updated_at, deleted_at)\
#     VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(str(A), str(B), int(time.time()), int(time.time()), int(time.time()), "0")
# # REPLACE can be INSERT
# cursor.execute(sql)
# db.commit()
# db.close()
#==============================================================================

# get DB data
#db = MySQLdb.connect(host="10.8.2.125", user=" ", passwd=" ", db="yen_nas", charset='utf8')

# fetch product as a table
try:
    db = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
    sql = "SELECT `product_id`, `model`, `image`, `date_available` FROM `product`"
    cursor = db.cursor()
    cursor.execute(sql)
    product_accessory = cursor.fetchall()
except MySQLdb.Error as e:
    print ("Error %d: %s" % (e.args[0], e.args[1]))
    db.rollback()
db.close()

# create 3 tables
try:
    db = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
    cursor = db.cursor()
    sqls = ['''CREATE TABLE IF NOT EXISTS `new_product_accessory` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `sku` varchar(64) DEFAULT NULL,
        `image` varchar(255) DEFAULT NULL,
        `published_at` int(11) NOT NULL DEFAULT '0',
        `created_at` int(11) NOT NULL DEFAULT '0',
        `updated_at` int(11) NOT NULL DEFAULT '0',
        `deleted_at` int(11) NOT NULL DEFAULT '0',
        PRIMARY KEY (`id`),
        UNIQUE KEY (`sku`)
        ) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;''',
        '''CREATE TABLE IF NOT EXISTS `new_product_accessory_detail` (
        `accessory_id` int(11) NOT NULL,
        `locale` varchar(5) DEFAULT NULL, #zh-tw/en-us/de-de...
        `name` varchar(255) DEFAULT NULL,
        `description` varchar(255) DEFAULT NULL,
        `ean` int(100) DEFAULT NULL,
        `upc` int(100) DEFAULT NULL,
        `created_at` int(11) NOT NULL DEFAULT '0',
        `updated_at` int(11) NOT NULL DEFAULT '0',
        `deleted_at` int(11) NOT NULL DEFAULT '0',
        PRIMARY KEY (`accessory_id`, `locale`)
        ) ENGINE=MyISAM DEFAULT CHARSET=utf8;''',
        '''CREATE TABLE IF NOT EXISTS `new_product_accessory_related` (
        `accessory_id` int(11) NOT NULL DEFAULT '0',
        `product_id` int(11) NOT NULL DEFAULT '0', # 官網 nas_id
        `created_at` int(11) NOT NULL DEFAULT '0',
        `updated_at` int(11) NOT NULL DEFAULT '0',
        `deleted_at` int(11) NOT NULL DEFAULT '0',
        PRIMARY KEY (`accessory_id`,`product_id`)
        ) ENGINE=MyISAM DEFAULT CHARSET=utf8;
        ''']
    for i in sqls:
        cursor.execute(i)
        db.commit()
except MySQLdb.Error as e:
    print ("Error %d: %s" % (e.args[0], e.args[1]))
    db.rollback()
db.close()
    
# table 1 NEW_PRODUCT_ACCESSORY
try:
    db = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
    cursor = db.cursor()
    for each_product in product_accessory:
#        sku = each_product[1].strip()
#        image = each_product[2].strip()
        published_date = time.mktime(datetime.datetime.strptime(str(each_product[3]), "%Y-%m-%d").timetuple())
        sql_check = "SELECT `sku`, `image` FROM `new_product_accessory` WHERE sku = '{}'".format(str(each_product[1].strip()))
        print(each_product[1])
        check = cursor.execute(sql_check)
        res = cursor.fetchall()
        if check == 1:
#            if res[0][0].strip() != str(each_product[1].strip()):
            sql = "UPDATE `new_product_accessory` SET image = '{}', updated_at = '{}' WHERE sku = '{}'".format(str(each_product[2].strip()), int(time.time()), str(each_product[1].strip()))
            cursor.execute(sql)
            db.commit()
            print("update")
        else:
            sql = "INSERT INTO NEW_PRODUCT_ACCESSORY(sku, image, published_at, created_at, updated_at, deleted_at)\
               VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(str(each_product[1].strip().upper()), str(each_product[2].strip()), int(published_date), int(time.time()), int(time.time()), "0")
            print("insert")
            cursor.execute(sql)
            db.commit()

except MySQLdb.Error as e:
        print ("Error %d: %s" % (e.args[0], e.args[1]))
        db.rollback()
db.close()

#==============================================================================
# INSERT INTO def (catid, title, page, publish)
# SELECT catid, title, 'page','yes' from `abc`
# 一次 query 多筆和每個迴圈都多 query 一次
#==============================================================================
 # 透過 product 的 id 去撈 product_description 的內容
def mk_lan_dic():
    lan_list = ['en', 'zh-cn', 'de-de', 'fr-fr', 'it-it', 'zh-tw', 'nl-nl', 'ja-jp', 'en-uk', 'en-us', 'es-es', 'pt-pt', 'ru']
    code = ['en', 'cn', 'de-DE', 'fr', 'it', 'tw', 'nl', 'jp', 'UKE', 'USE', 'es', 'pt-br', 'ru']
    lan_dic = {}
    for idx in range(len(code)):
        lan_dic[code[idx]] = lan_list[idx]
    return lan_dic

def decode_description(descrip):
    if descrip == '':
        result = 'NULL'
    elif '描述' in descrip:
        decodeDES = html.unescape(descrip)
        EXPDES = re.findall('描述(.*?[A-z \/\\<>0-9].)<\/p>', decodeDES)[0]
        res = re.findall('<\/strong>(.*?[A-z \/\\<>0-9].)($|<\/span>)', EXPDES)
        if len(res) != 0:
            print("0':{}".format(res))
            result = res[0][0].strip()
        else:
            print("0:{}".format(res))
            result = res
    elif 'Description' in descrip:
        decodeDES = html.unescape(descrip)
        EXPDES = re.findall('Description(.*?[A-z \/\\<>0-9].)<\/p>', decodeDES)[0]
        if 'style="color: rgb(0, 0, 0);"' in EXPDES:
            res = re.findall('>&nbsp;(.*?[A-z \/\\<>0-9].)($|<\/span>)', EXPDES)
            if len(res) != 0:
                print("1':{}".format(res[0]))
                result = res[0][0].strip()
            else:
                print("1:{}".format(res))
                result = res
        elif 'font-family:' in EXPDES:
            res = re.findall('">(.*?[A-z \/\\<>0-9].)($|<\/span>)', EXPDES)
            if len(res) != 0:
                print("2':{}".format(res))
                result = res[0][0].strip()
            else:
                print("2:{}".format(res))
                result = res
        elif EXPDES[0] == ':&nbsp;</strong>':
            result = 'error'
        else:
            if '&nbsp;' in EXPDES:
                res = re.findall('&nbsp;(.*?[A-z \/\\<>0-9].)($|<\/span>)', EXPDES)
                if len(res) != 0:
                    print("3':{}".format(res))
                    result = res[0][0].strip()
                else:
                    print("3:{}".format(res))
                    result = res
            else:
                res = re.findall('(:|<\/strong>)(.*?[A-z \/\\<>0-9].)($|<\/span>)', EXPDES)
                if len(res) != 0:
                    print("4':{}".format(res))
                    result = res[0][1].strip()
                else:
                    print("4:{}".format(res))
                    result = res
    else:
        result = 'no "Description"!'
        print('no "Description"!')
    return result

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
def replace_all(text, dic):
            for i, j in dic.items():
                text = text.replace(i, j)
            return text
#==============================================================================
# def descript(text):
#     if text == "":
#         return ""
#     else:
#         B = html.unescape(text)
#         C = strip_tags(B)
#         rep = {"\n":"\\n", "\t": "\\t", "\xa0": " "}
#         AA = replace_all(C, rep)
#         regex1 = r"(Description..|EAN:|UPC:)(.*?[A-z \/\\<>0-9].)(\\t|\\n)"
#         regex2 = r"(描述..|EAN.:|UPC.:)(.*?[A-z \/\\<>0-9].)(\\t|\\n)"
#         if "描述" in text or "國際條碼" in text or "統一商品條碼" in text:
#             regex = regex2
#         else:
#             regex = regex1
#         matches = re.finditer(regex, AA)
#         res = []
#         for matchNum, match in enumerate(matches):
#             matchNum = matchNum + 1  
#             for groupNum in range(0, len(match.groups())):
#                 groupNum = groupNum + 1
#                 res.append(match.group(groupNum))
#         if res == '':
#             result = 'no'
#         elif "Description" in res[0] or "描述" in res[0]:
#             result = res[1].strip().replace("\r", "").replace("\\n", "")
#         else:
#             result = "no Description"
#         return result
#==============================================================================
#==============================================================================
# def any(iterable):
#     for element in iterable:
#         if element:
#             return True
#     return False
#==============================================================================

def parse(text):
    if text == "":
        return ""
    else:
        B = html.unescape(text)
        C = strip_tags(B)
        rep = {"\n":"\\n", "\t": "\\t", "\xa0": " "}
        AA = replace_all(C, rep)
        regex1 = r"(Description..|EAN:|UPC:)(.*?[A-z \/\\<>0-9].)(\\t|\\n)"
        regex2 = r"(描述..|EAN.:|UPC.:)(.*?[A-z \/\\<>0-9].)(\\t|\\n)"
        regex3 = r"(Description..|EAN:|UPC:|EAN / UPC:|EAN/UPC:)(.*?[A-z \/\\<>0-9].)(\\t|\\n)"
        if "描述" in text or "國際條碼" in text or "統一商品條碼" in text:
            regex = regex2
        elif "EAN / UPC" in text:
            regex = regex3
        else:
            regex = regex1
        matches = re.finditer(regex, AA)
        res = []
        for matchNum, match in enumerate(matches):
            matchNum = matchNum + 1  
            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
                res.append(match.group(groupNum))
        return res
 
def descript(parsedList):
    if parsedList == '':
        return 0
    else:
        temp = parsedList[:]
        while True:
            if ("Description" or "描述") not in temp[0]:
                temp.pop(0)
                if len(temp) == 0:
                    return 0
            else:
                return temp[1].strip().replace("\r", "").replace("\\n", "")

def EAN(parsedList):
    if parsedList == '':
        return 0
    else:
        temp = parsedList[:]
        while True:
            if ("EAN" or "國際條碼") not in temp[0]:
                temp.pop(0)
                if len(temp) == 0:
                    return 0
            else:
                return int(temp[1].strip().replace("\r", "").replace("\\n", ""))

def UPC(parsedList):
    if parsedList == '':
        return 0
    else:
        temp = parsedList[:]
        while True:
            if ("UPC" or "統一商品條碼") not in temp[0]:
                temp.pop(0)
                if len(temp) == 0:
                    return 0
            else:
                return int(temp[1].strip().replace("\r", "").replace("\\n", ""))

def EAN_UPC(parsedList):
    if parsedList == '':
        return 0
    else:
        temp = parsedList[:]
        while True:
            if ("EAN / UPC" not in temp[0]) or ("EAN/UPC" not in temp[0]):
                temp.pop(0)
                if len(temp) == 0:
                    return 0
            else:
                ean, upc = temp[1].split('/')
                return ean.strip(), upc.strip()

# table 2

def table2():
    try:
        db_yen = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
        db_cart = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
        cursor_yen = db_yen.cursor()
        cursor_cart = db_cart.cursor()
        sql1 = "SELECT `product_id`, `language_id`, `name`, `description` FROM `product_description`"
        cursor_cart.execute(sql1)
        product_description = cursor_cart.fetchall()
        for each_pd_lan in product_description:
            pID, lanID, name, descrip_cart = each_pd_lan[0], each_pd_lan[1], each_pd_lan[2], each_pd_lan[3]  # name
            sql2 = "SELECT `model` FROM `product` WHERE `product_id` = {}".format(pID)
            cursor_cart.execute(sql2)
            model = cursor_cart.fetchall()
            sql3 = "SELECT `id` FROM `new_product_accessory` WHERE `sku` = '{}'".format(model[0][0].strip().upper())
            cursor_yen.execute(sql3)
            accessID = cursor_yen.fetchall() # id
            sql4 = "SELECT `code` FROM `language` WHERE `language_id` = {}".format(lanID)
            cursor_cart.execute(sql4)
            lanCode = cursor_cart.fetchall()
            lan_dic = mk_lan_dic()
            locale = lan_dic[lanCode[0][0]] # locale
            parsed = parse(descrip_cart)
            description = descript(parsed) # description
            decode_html = html.unescape(descrip_cart)
            strip_html = strip_tags(decode_html)
            if "EAN / UPC" in strip_html or "EAN/UPC" in strip_html:
                ean = EAN_UPC(parsed)[0]
                upc = EAN_UPC(parsed)[1]
            else:
                ean = EAN(parsed)
                upc = UPC(parsed)
#            description = descript(descrip_cart) # description
            sql_insert = "INSERT INTO NEW_PRODUCT_ACCESSORY_DETAIL(accessory_id, \
                    locale, name, description, ean, upc, created_at, updated_at, deleted_at)\
                    VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}') \
                    ON DUPLICATE KEY UPDATE name='{}', description = '{}', ean = '{}', upc = '{}',  updated_at='{}'"\
                   .format(accessID[0][0], str(locale), str(name), str(description), int(ean), int(upc), \
                           int(time.time()), int(time.time()), "0", str(name), str(description), int(ean), int(upc), int(time.time()))
            cursor_yen.execute(sql_insert)
            db_yen.commit()
    except MySQLdb.Error as e:
            print ("Error %d: %s" % (e.args[0], e.args[1]))
            db_yen.rollback()
            db_cart.rollback()
    db_yen.close()
    db_cart.close() 
    
tStart = time.time()
table2()
tStop = time.time()
taken = round(tStop - tStart)
print("Done!\n")
print("Time taken: ", round(taken//60), "(m)", round(taken%60), "(s)")        
        
    
#   old 
#==============================================================================
# try:    
#     db1 = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
#     db2 = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
#     cursor1 = db1.cursor()
#     cursor2 = db2.cursor()
#     for each_product in product_accessory:
#         sql2 = "SELECT `language_id`, `name`, `description` FROM `product_description` WHERE `product_id` = {}".format(each_product[0])
#         cursor2.execute(sql2)
# #        print(sql2)
#         results = cursor2.fetchall()
#         sql3 = "SELECT `id` FROM `new_product_accessory` WHERE `sku` = '{}' AND `image` = '{}'".format(each_product[1].strip(), each_product[2].strip())
#         cursor1.execute(sql3)
# #        print(sql3)
#         accessory_id = cursor1.fetchall()
#         for each_lan in results:
#             sql4 = "SELECT `language_id`, `code` FROM `language` WHERE `language_id` = {}".format(each_lan[0])
#             cursor2.execute(sql4)
# #            print(sql4)
#             lan_detail = cursor2.fetchall()
#             lan_dic = mk_lan_dic()
#             locale = lan_dic[lan_detail[0][1]]
#             print(locale)
#             if '描述' in each_lan[2]:
# #            if locale == 'zh-cn' or locale == 'zh-tw':
#                 descrip_uncode = html.unescape(each_lan[2])
#                 pre_description = re.findall('描述(.*?[A-z \/\\<>0-9])<\/p>', descrip_uncode)[0]
#                 description = pre_description.split('</strong>')[1].split('</span>')[0].strip()
#                 if description[:6] == '&nbsp;':
#                     description = description[6:]
#                 else:
#                     description = description
#                 print('zh')
#             elif each_lan[2] == '':
#                 print('{}, no description'.format(locale))
#             elif 'Description' in each_lan[2]:
#                 print("HERE")
#                 descrip_uncode = html.unescape(each_lan[2])
#                 pre_description = re.findall('Description(.*?[A-z \/\\<>0-9])<\/p>', descrip_uncode) #一直會 parse 不出東西來 但網頁版可以
#                 if pre_description != []: 
#                     if '</strong>' in pre_description[0]:
#                         print("HERE!")
#                         description = pre_description[0].split('</strong>')[1].split('</span>')[0].strip()
#                         if description[:6] == '&nbsp;':
#                             description = description[6:]
#                         else:
#                             description = description
#                     else:
#                         print("HERE!!")
#                         description = pre_description[0].split(':')[1].split('</span>')[0].strip()
#                         if description[:6] == '&nbsp;':
#                             description = description[6:]
#                         else:
#                             description = description
#                 else:
#                     print("can't exp!")
#             else:
#                 print("no Description!")
# #                print("other")
#             sql5 = "INSERT INTO NEW_PRODUCT_ACCESSORY_DETAIL(accessory_id, \
#                 locale, name, description, created_at, updated_at, deleted_at)\
#                 VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}') \
#                 ON DUPLICATE KEY UPDATE name='{}', description = '{}', updated_at='{}'"\
#                .format(accessory_id[0][0], str(locale), str(each_lan[1]), str(description), \
#                        int(time.time()), int(time.time()), "0", str(each_lan[1]), str(description), int(time.time()))
# #            print(sql5)
# #==============================================================================
# #             sql5 = 'REPLACE INTO NEW_PRODUCT_ACCESSORY_DETAIL(accessory_id, \
# #                 locale, name, description, created_at, updated_at, deleted_at)\
# #                 VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(accessory_id[0][0], str(locale), str(each_lan[1]), str(each_lan[2]), int(time.time()), int(time.time()), "0")
# # #            print(sql5)
# #==============================================================================
#             cursor1.execute(sql5)
#             db1.commit()
# except MySQLdb.Error as e:
#         print ("Error %d: %s" % (e.args[0], e.args[1]))
#         db1.rollback()
#         db2.rollback()
# db1.close()
# db2.close()
#==============================================================================

# table 3
tStart = time.time()
no_match = []
TS = []
TS_SET = []
VS = []
VS_SET = []
try:
    db_yen = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
    db_cart = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
    cursor_yen = db_yen.cursor()
    cursor_cart = db_cart.cursor()
    sql1 = "SELECT `product_id`, `category_id` FROM `product_to_category`"
    cursor_cart.execute(sql1)
    product_to_category = cursor_cart.fetchall()
    for eachPTC in product_to_category:
        product_id = eachPTC[0]
        category_id = eachPTC[1]
        sql2 = "SELECT `model` FROM `product` WHERE `product_id` = {}".format(product_id)
        cursor_cart.execute(sql2)
        access_model = cursor_cart.fetchall()
        sql3 = "SELECT `id` FROM `new_product_accessory` WHERE `sku` = '{}'".format(access_model[0][0].strip().upper())
        cursor_yen.execute(sql3)
        access_id = cursor_yen.fetchall() # accessID
        sql4 = "SELECT `name` FROM `category_description` WHERE `category_id` = {}".format(category_id)
        cursor_cart.execute(sql4)
        sku_name = cursor_cart.fetchall()
        sql5 = "SELECT `ItemID` FROM `product_items` WHERE `temp_name` = '{}'".format(sku_name[0][0].strip()) # 可能找不到對應 temp_name
        cursor_yen.execute(sql5)
        ItemID = cursor_yen.fetchall() # productID 可能為 ''
        if len(ItemID) != 0:
            sql_insert = "INSERT INTO NEW_PRODUCT_ACCESSORY_RELATED(accessory_id, product_id, created_at, updated_at, deleted_at)\
             VALUES ('{}', '{}', '{}', '{}', '{}') ON DUPLICATE KEY UPDATE accessory_id ='{}', product_id = '{}', updated_at='{}'"\
                    .format(access_id[0][0], ItemID[0][0], int(time.time()), int(time.time()), "0", access_id[0][0], ItemID[0][0], int(time.time()))
            cursor_yen.execute(sql_insert)
            db_yen.commit()
        else: # 紀錄 match 不到的 sku_namem 與 category_id
            no_match.append([sku_name[0][0], category_id])
            if sku_name[0][0].strip().upper()[0] == 'V':
                VS.append([sku_name[0][0], category_id])
            else:
                TS.append([sku_name[0][0], category_id])
            
except MySQLdb.Error as e:
        print ("Error %d: %s" % (e.args[0], e.args[1]))
        db_yen.rollback()
        db_cart.rollback()
db_yen.close()
db_cart.close()
tStop = time.time()
taken = round(tStop - tStart)
print("Done!\n")
print("Time taken: ", round(taken//60), "(m)", round(taken%60), "(s)")
print("TS = {}".format(len(TS)))
print("VS = {}".format(len(VS)))
TS_SET = []
for i in TS:
    TS_SET.append(i[0])
TSSET = set(TS_SET)

# 驗證
#==============================================================================
# db2 = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
# cursor2 = db2.cursor()
# sql = "SELECT * FROM `product_to_category` WHERE `category_id` = 365"
# cursor2.execute(sql)
# resu = cursor2.fetchall()
# db2.close()
# 
# db1 = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
# cursor1 = db1.cursor()
# sql2 = "SELECT * FROM `new_product_accessory_related` WHERE `product_id` = 223"
# cursor1.execute(sql2)
# resu2 = cursor1.fetchall()
# db1.close()
#==============================================================================
# TVS-871
#==============================================================================
# db1 = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
# cursor1 = db1.cursor()
# sql2 = "SELECT * FROM `new_product_accessory_related` WHERE `product_id` = 160"
# cursor1.execute(sql2)
# resu2 = cursor1.fetchall()
# db1.close()
#==============================================================================
