# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 10:57:25 2017

@author: Lily
"""

import html, MySQLdb, time, datetime, re
from html.parser import HTMLParser

# get DB data
#db = MySQLdb.connect(host="10.8.2.125", user=" ", passwd=" ", db="yen_nas", charset='utf8')
# create 3 tables
try:
    db = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
#    db = MySQLdb.connect(host="10.8.2.125", user="marketing_query", passwd="WStFfFDSrzzdEQFW", db="yen_nas", charset='utf8')    
    cursor = db.cursor()
    sqls = ['''CREATE TABLE IF NOT EXISTS `new_product_accessory` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `shop_id` INT(11)  NOT NULL,
        `sku` varchar(64) DEFAULT NULL,
        `image` varchar(255) DEFAULT NULL,
        `ean` bigint(100) DEFAULT NULL,
        `upc` bigint(100) DEFAULT NULL,
        `published_at` int(11) NOT NULL DEFAULT '0',
        `created_at` int(11) NOT NULL DEFAULT '0',
        `updated_at` int(11) NOT NULL DEFAULT '0',
        `deleted_at` int(11) NOT NULL DEFAULT '0',
        PRIMARY KEY (`id`),
        UNIQUE KEY (`sku`, `shop_id`)
        ) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;''',
        '''CREATE TABLE IF NOT EXISTS `new_product_accessory_detail` (
        `accessory_id` int(11) NOT NULL,
        `locale` varchar(5) DEFAULT NULL, #zh-tw/en-us/de-de...
        `name` varchar(255) DEFAULT NULL,
        `description` varchar(255) DEFAULT NULL,
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

def mk_lan_dic():
    lan_list = ['en', 'zh-cn', 'de-de', 'fr-fr', 'it-it', 'zh-tw', 'nl-nl', 'ja-jp', 'en-uk', 'en-us', 'es-es', 'pt-pt', 'ru']
    code = ['en', 'cn', 'de-DE', 'fr', 'it', 'tw', 'nl', 'jp', 'UKE', 'USE', 'es', 'pt-br', 'ru']
    lan_dic = {}
    for idx in range(len(code)):
        lan_dic[code[idx]] = lan_list[idx]
    return lan_dic


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


def parse(text):
    '''input: encoded html
       output: a stripped and parsed list  
    '''
    if text == "":
        return ""
    else:
        B = html.unescape(text)
        C = strip_tags(B)
#        if ("Description" not in C) and ("EAN" in C): # 若沒有描述的標頭則加上標頭 (此處中文內容也會加上，但在後續不影響結果)
#            C = "Description: " + C
#        else:
#            C = C
        rep = {"\n":"\\n", "\t": "\\t", "\xa0": " "}
        AA = replace_all(C, rep)
        regex1 = r"(Description..|EAN:|UPC:)(.*?[A-z \/\\<>0-9].)(\\t|\\n)"
        regex2 = r"(描述..|EAN.:|UPC.:)(.*?[A-z \/\\<>0-9].)(\\t|\\n)"
        regex3 = r"(Description..|EAN:|UPC:|EAN / UPC:|EAN/UPC:)(.*?[A-z \/\\<>0-9].)(\\t|\\n)"
        regex4 = r"(Description..|EAN :|UPC :)(.*?[A-z \/\\<>0-9].)(\\t|\\n)"
        if ("描述" in text) or ("國際條碼" in text) or ("統一商品條碼" in text):
            regex = regex2
        elif ("EAN / UPC" in text) or ("EAN/UPC" in text):
            regex = regex3
        elif ('EAN :' in text) or ('UPC :' in text):
            regex = regex4
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

def descript(parsedList): # description
    temp = parsedList[:]
    str1 = ''.join(temp)
    if parsedList == '': # 原本 Description 欄位中就沒有內容者回傳 ''
        return ''
    else:
        if "描述" in str1:
            des = str1.split("描述:")[1].split("\\n")[0].strip()
        elif "Description:" in str1:
            des = str1.split("Description:")[1].split("\\n")[0].strip()
        elif "Description :" in str1:
            des = str1.split("Description :")[1].split("\\n")[0].strip()
        else:
            des = "no"
        return des

def EAN_UPC(parsedList):
    temp = parsedList[:]
    str1 = ''.join(temp)
    if parsedList == '':
        ean, upc = 0, 0
    else:     
        if ('EAN:' in str1) or ('\\nUPC:' in str1):
            print("HERE1")
            ean = str1.split('EAN:')[1].split('\\n')[0].strip()
            upc = str1.split('\\nUPC:')[1].split('\\n')[0].strip()
        elif ('EAN :' in str1) or ('\\nUPC :' in str1):
            print("HERE4")
            ean = str1.split('EAN :')[1].split('\\n')[0].strip()
            upc = str1.split('\\nUPC :')[1].split('\\n')[0].strip()
        elif ('EAN' not in str1) and ('UPC' not in str1):
            print("HERE2")
            ean, upc = 0, 0
        else:
            print("HERE3")
            ean = str1.split('UPC:')[1].split('/')[0].strip()
            upc = str1.split('UPC:')[1].split('/')[1].strip().strip('\\n')
    return ean, upc

# fetch product as a table
try:
#    db = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
    db = MySQLdb.connect(host="10.8.2.125", user="marketing_query", passwd="WStFfFDSrzzdEQFW", db="opencart", charset='utf8')
    sql = "SELECT `product_id`, `model`, `image`, `date_available` FROM `product`"
    cursor = db.cursor()
    cursor.execute(sql)
    product_accessory = cursor.fetchall() # product_accessory table from product
except MySQLdb.Error as e:
    print ("Error %d: %s" % (e.args[0], e.args[1]))
    db.rollback()
db.close()
            
# table 1 NEW_PRODUCT_ACCESSORY
try:
    db_yen = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
#    db_yen = MySQLdb.connect(host="10.8.2.125", user="marketing_query", passwd="WStFfFDSrzzdEQFW", db="yen_nas", charset='utf8')
#    db_cart = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
    db_cart = MySQLdb.connect(host="10.8.2.125", user="marketing_query", passwd="WStFfFDSrzzdEQFW", db="opencart", charset='utf8')
    cursor_yen = db_yen.cursor()
    cursor_cart = db_cart.cursor()
    for each_product in product_accessory:
        sql_des = "SELECT `description` FROM `product_description` WHERE product_id = {}".format(each_product[0])
        cursor_cart.execute(sql_des)
        pre_description = cursor_cart.fetchall()
        parsed_des = parse(pre_description[0][0])
        ean = EAN_UPC(parsed_des)[0]
#        print(ean)
        upc = EAN_UPC(parsed_des)[1]
#        print(upc)
#        sku = each_product[1].strip()
#        image = each_product[2].strip()
        published_date = time.mktime(datetime.datetime.strptime(str(each_product[3]), "%Y-%m-%d").timetuple())
        sql_check = "SELECT `shop_id`, `sku`, `image` FROM `new_product_accessory` WHERE sku = '{}'".format(str(each_product[1].strip()))
        print(each_product[1])
        check = cursor_yen.execute(sql_check)
        res = cursor_yen.fetchall()
        if check == 1:
#            if res[0][0].strip() != str(each_product[1].strip()):
            sql_update = "UPDATE `new_product_accessory` SET image = '{}', ean = '{}', upc = '{}', updated_at = '{}' WHERE sku = '{}'".format(str(each_product[2].strip()), int(ean), int(upc), int(time.time()), str(each_product[1].strip()))
            cursor_yen.execute(sql_update)
            db_yen.commit()
            print("update")
        else:
            sql_insert = "INSERT INTO NEW_PRODUCT_ACCESSORY(shop_id, sku, image, ean, upc, published_at, created_at, updated_at, deleted_at)\
               VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(each_product[0], str(each_product[1].strip().upper()), str(each_product[2].strip()), int(ean), int(upc), int(published_date), int(time.time()), int(time.time()), "0")
            print("insert")
            cursor_yen.execute(sql_insert)
            db_yen.commit()

except MySQLdb.Error as e:
        print ("Error %d: %s" % (e.args[0], e.args[1]))
        db_yen.rollback()
        db_cart.rollback()
db_yen.close()
db_cart.close() 

#==============================================================================
# INSERT INTO def (catid, title, page, publish)
# SELECT catid, title, 'page','yes' from `abc`
# 一次 query 多筆和每個迴圈都多 query 一次
#==============================================================================
 # 透過 product 的 id 去撈 product_description 的內容
#==============================================================================
# db_yen = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
# db_cart = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
# cursor_yen = db_yen.cursor()
# cursor_cart = db_cart.cursor()
# sql01 = "SELECT ``"
#==============================================================================

# table 2

def table2():
    check_des = []
    check_parsed = []
    check_accessID = []
    try:
        db_yen = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
#        db_yen = MySQLdb.connect(host="10.8.2.125", user="marketing_query", passwd="WStFfFDSrzzdEQFW", db="yen_nas", charset='utf8')
#        db_cart = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
        db_cart = MySQLdb.connect(host="10.8.2.125", user="marketing_query", passwd="WStFfFDSrzzdEQFW", db="opencart", charset='utf8')
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
            if parsed == "": # 驗證所以""的描述都來自於資料庫本身沒有資料 經過 parse function 的 else 出來的都是 list
                check_parsed.append(descrip_cart)
            description = descript(parsed) # description
            if description == "": 
                check_des.append(descrip_cart)
            if description == "no":
                check_accessID.append(accessID)
                sql5 = "SELECT `description` FROM `new_product_accessory_detail` \
                WHERE `locale` = 'en' AND `accessory_id` = {}".format(accessID[0][0])
                cursor_yen.execute(sql5)
                pre_description = cursor_yen.fetchall()    
                description = pre_description[0][0]
            if description == "":
#                check_accessID.append(accessID)
                sql7 = "SELECT `description` FROM `new_product_accessory_detail` \
                WHERE `locale` = 'en' AND `accessory_id` = {}".format(accessID[0][0])
                cursor_yen.execute(sql7)
                pre_description = cursor_yen.fetchall()    
                description = pre_description[0][0]
            if name == "":
                sql6 = "SELECT `name` FROM `new_product_accessory_detail` \
                WHERE `locale` = 'en' AND `accessory_id` = {}".format(accessID[0][0])
                cursor_yen.execute(sql6)
                pre_name = cursor_yen.fetchall()    
                name = pre_name[0][0]
                print("pre_name: " + pre_name[0][0])
            sql_insert = "INSERT INTO NEW_PRODUCT_ACCESSORY_DETAIL(accessory_id, \
                    locale, name, description, created_at, updated_at, deleted_at)\
                    VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}') \
                    ON DUPLICATE KEY UPDATE name='{}', description = '{}',  updated_at='{}'"\
                   .format(accessID[0][0], str(locale), str(name), str(description), \
                           int(time.time()), int(time.time()), "0", str(name), str(description), int(time.time()))
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

#==============================================================================
# result = []
# for text in check_des:
#     B = html.unescape(text)
#     C = strip_tags(B)
#     rep = {"\n":"\\n", "\t": "\\t", "\xa0": " "}
#     AA = replace_all(C, rep)
#     str2 = ''.join(AA)
#     result.append(str2)
#==============================================================================

# table 3
tStart = time.time()
no_match = []
TS = []
TS_SET = []
VS = []
VS_SET = []
search_sku_list = []
try:
    db_yen = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
#    db_yen = MySQLdb.connect(host="10.8.2.125", user="marketing_query", passwd="WStFfFDSrzzdEQFW", db="yen_nas", charset='utf8')
#    db_cart = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
    db_cart = MySQLdb.connect(host="10.8.2.125", user="marketing_query", passwd="WStFfFDSrzzdEQFW", db="opencart", charset='utf8')
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
                TS_SET = []
                for i in TS:
                    TS_SET.append(i[0])
                TSSET = set(TS_SET)
#==============================================================================
#                 if "420/421" in sku_name[0][0]:
#                     print("420/421")
#                     search_sku = [[sku_name[0][0].split("/")[0], "TS-" + sku_name[0][0].split("/")[1]]]
#                     break;
#                 elif "/" in sku_name[0][0]:
#                     search_sku = [sku_name[0][0].split("/")[0].strip()]
#                 elif "Series" in sku_name[0][0]:
#                     search_sku = [sku_name[0][0].split(" ")[0].strip()]
#                 else:
#                     search_sku = [sku_name[0][0].split("U")[0].strip() + "U"]
#                 search_sku_list.append(search_sku)
#                 for each_sku in search_sku:
#                     sql6 = "SELECT `ItemID` FROM `product_items` WHERE `temp_name` LIKE '%{}%'".format(each_sku) # 可能找不到對應 temp_name
#                     cursor_yen.execute(sql6)
#                     ItemIDs = cursor_yen.fetchall() # 
#                     for ID in ItemIDs:
#                         print(ID)
#                         sql_insert = "INSERT INTO NEW_PRODUCT_ACCESSORY_RELATED(accessory_id, product_id, created_at, updated_at, deleted_at)\
#                          VALUES ('{}', '{}', '{}', '{}', '{}') ON DUPLICATE KEY UPDATE accessory_id ='{}', product_id = '{}', updated_at='{}'"\
#                             .format(access_id[0][0], ID[0], int(time.time()), int(time.time()), "0", access_id[0][0], ID[0], int(time.time()))
#                         cursor_yen.execute(sql_insert)
#                         db_yen.commit()
#==============================================================================
            
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

#==============================================================================
# product_items = ["HS-251", "HS-251+", "TS-109 II", "TS-109 Pro II", "TS-109", "TS-109 Pro", "TS-112", "TS-112P", "TS-212", "TS-212P", "TS-212-E", "TS-239H", "TS-239 Pro", "TS-239 Pro II", "TS-239 Pro II+", "TS-420U", "TS-420", "TS-420-D", "TS-421U", "TS-421", "TS-439U-RP/ SP", "TS-459U-RP/SP", "TS-459U-RP+/SP+", "TS-469U-RP", "TS-469U-SP", "TS-470U-RP", "TS-470U-SP", "TS-EC1280U", "TS-EC1280U R2", "TS-EC1680U", "TS-EC1680U R2", "TS-EC2480U R2", "TS-EC2480U", "TS-EC880U", "TS-EC880U R2", "TVS-882ST2", "TVS-882ST3"]
# len(product_items)
# 
# db_yen = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
# #    db_yen = MySQLdb.connect(host="10.8.2.125", user="marketing_query", passwd="WStFfFDSrzzdEQFW", db="yen_nas", charset='utf8')
# db_cart = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
# #    db = MySQLdb.connect(host="10.8.2.125", user="marketing_query", passwd="WStFfFDSrzzdEQFW", db="open_cart", charset='utf8')
# cursor_yen = db_yen.cursor()
# cursor_cart = db_cart.cursor()
# sql1 = "SELECT `id`, `shop_id`, `sku`, `image`, `ean`, `upc` FROM `new_product_accessory` WHERE `sku` = ''"
# sql2 = "SELECT `id`, `shop_id`, `sku`, `image`, `ean`, `upc` FROM `new_product_accessory` WHERE `image` = ''"
# cursor_yen.execute(sql1)
# cursor_yen.execute(sql2)
# noSku = cursor_yen.fetchall()
# noImage = cursor_yen.fetchall()
# db_yen.close()
# db_cart.close()
# 
# db_yen = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
# cursor_yen = db_yen.cursor()
# sql3 = "SELECT DISTINCT `accessory_id` FROM `new_product_accessory_detail` WHERE `description` = ''"
#==============================================================================




