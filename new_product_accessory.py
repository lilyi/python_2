# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 10:57:25 2017

@author: Lily
"""
from subprocess import check_output
check_output("pip install -r requirements.txt", shell=True)

import html, MySQLdb, time, datetime, re
from html.parser import HTMLParser

tStart = time.time()

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
        rep = {"\n":"\\n", "\t": "\\t", "\xa0": " "}
        AA = replace_all(C, rep) + "\\n"
        regex1 = r"(Description..|EAN:|UPC:|NOTICE:)(.*?[A-z \/\\<>0-9].)(\\t|\\n|<\/p>)"
        regex2 = r"(描述..|EAN.:|UPC.:|NOTICE:)(.*?[A-z \/\\<>0-9].)(\\t|\\n)"
        regex3 = r"(Description..|EAN:|UPC:|EAN / UPC:|EAN/UPC:|NOTICE:)(.*?[A-z \/\\<>0-9].)(\\t|\\n)"
        regex4 = r"(Description..|EAN :|UPC :|NOTICE:)(.*?[A-z \/\\<>0-9].)(\\t|\\n)"
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
            ean = str1.split('EAN:')[1].split('\\n')[0].strip()
            upc = str1.split('\\nUPC:')[1].split('\\n')[0].strip()
        elif ('EAN :' in str1) or ('\\nUPC :' in str1):
            ean = str1.split('EAN :')[1].split('\\n')[0].strip()
            upc = str1.split('\\nUPC :')[1].split('\\n')[0].strip()
        elif ('EAN' not in str1) and ('UPC' not in str1):
            ean, upc = 0, 0
        else:
            ean = str1.split('UPC:')[1].split('/')[0].strip()
            upc = str1.split('UPC:')[1].split('/')[1].split('\r')[0].strip()
    return ean, upc

def NOTICE(parsedList):
    temp = parsedList[:]
    str1 = ''.join(temp)
    if parsedList == "":
        return ""
    else:
        if "NOTICE" in str1:
            notice = str1.split("NOTICE:")[1].split("\\n")[0].strip()
        else:
            notice = ""
        return notice

# create 3 tables

try:
    print("Connecting database...")
    db_yen = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
    db_cart = MySQLdb.connect(host="10.8.2.125", user="marketing_query", passwd="WStFfFDSrzzdEQFW", db="opencart", charset='utf8')
    cursor_yen = db_yen.cursor()
    cursor_cart = db_cart.cursor()
    # create 3 tables if not exits
    print("Creating 3 tables...")
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
        cursor_yen.execute(i)
        db_yen.commit()
    print("Updating table 1...")
    sql = "SELECT `product_id`, `model`, `image`, `date_available` FROM `product`"
    cursor_cart.execute(sql)
    product_accessory = cursor_cart.fetchall() # fetch product as a table
    # table1
    for each_product in product_accessory:
        sql_des = "SELECT `description` FROM `product_description` WHERE product_id = {}".format(each_product[0])
        cursor_cart.execute(sql_des)
        pre_description = cursor_cart.fetchall()
        parsed_des = parse(pre_description[0][0])
        ean = EAN_UPC(parsed_des)[0]
        upc = EAN_UPC(parsed_des)[1]
        published_date = time.mktime(datetime.datetime.strptime(str(each_product[3]), "%Y-%m-%d").timetuple())
        sql_check = "SELECT `shop_id`, `sku`, `image` FROM `new_product_accessory` WHERE sku = '{}'".format(str(each_product[1].strip()))
        check = cursor_yen.execute(sql_check)
        res = cursor_yen.fetchall()
        if check == 1:
            sql_update = "UPDATE `new_product_accessory` SET image = '{}', ean = '{}', upc = '{}', updated_at = '{}' WHERE sku = '{}'".format(str(each_product[2].strip()), int(ean), int(upc), int(time.time()), str(each_product[1].strip()))
            cursor_yen.execute(sql_update)
            db_yen.commit()
        else:
            sql_insert = "INSERT INTO new_product_accessory(shop_id, sku, image, ean, upc, published_at, created_at, updated_at, deleted_at)\
               VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(each_product[0], str(each_product[1].strip().upper()), str(each_product[2].strip()), int(ean), int(upc), int(published_date), int(time.time()), int(time.time()), "0")
            cursor_yen.execute(sql_insert)
            db_yen.commit()
    # table2
    print("Updating table 2...")
    sql1 = "SELECT `product_id`, `language_id`, `name`, `description` FROM `product_description` ORDER BY `product_id`, `language_id`"
    cursor_cart.execute(sql1)
    product_description = cursor_cart.fetchall()
    sql_check = "SHOW COLUMNS FROM `new_product_accessory_detail` LIKE 'notice';"
    check = cursor_yen.execute(sql_check)
    res_check = cursor_yen.fetchall()
    if res_check == (): # add colume `notice` if not exit
        sql_add = "ALTER TABLE `new_product_accessory_detail` ADD `notice` varchar(255) DEFAULT NULL AFTER `description`"
        cursor_yen.execute(sql_add)
        db_yen.commit()
    lan_dic = mk_lan_dic()
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
        locale = lan_dic[lanCode[0][0]] # locale
        parsed = parse(descrip_cart)
        description = descript(parsed) # description
        notice = NOTICE(parsed) # important notice
        model_front = model[0][0].strip().upper().split("-")[0]
        notNeed = ["SP", "BBU", "SCR", "FIXER", "PWR", "KIT", "KEY", "TRAY"]         
        if description == "no":
            if model_front in notNeed:
                description = ""
            else:
                sql5 = "SELECT `description` FROM `new_product_accessory_detail` \
                WHERE `locale` = 'en' AND `accessory_id` = {}".format(accessID[0][0])
                cursor_yen.execute(sql5)
                pre_description = cursor_yen.fetchall()    
                description = pre_description[0][0]       
        if description == "" and pID != 144 and model_front not in notNeed:
            sql7 = "SELECT `description` FROM `new_product_accessory_detail` \
            WHERE `locale` = 'en' AND `accessory_id` = {}".format(accessID[0][0])
            cursor_yen.execute(sql7)
            pre_description = cursor_yen.fetchall()    
            description = pre_description[0][0]        
        if name == "" and pID != 144:
            sql6 = "SELECT `name` FROM `new_product_accessory_detail` \
            WHERE `locale` = 'en' AND `accessory_id` = {}".format(accessID[0][0])
            cursor_yen.execute(sql6)
            pre_name = cursor_yen.fetchall()    
            name = pre_name[0][0]
        sql_insert = "INSERT INTO new_product_accessory_detail(accessory_id, \
                locale, name, description, notice, created_at, updated_at, deleted_at)\
                VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}') \
                ON DUPLICATE KEY UPDATE name='{}', description = '{}', notice = '{}',  updated_at='{}'"\
               .format(accessID[0][0], str(locale), str(name), str(description), str(notice), \
                       int(time.time()), int(time.time()), "0", str(name), str(description), str(notice), int(time.time()))
        cursor_yen.execute(sql_insert)
        db_yen.commit()
        
    # table3
    print("Updating table 3...")
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
            sql_insert = "INSERT INTO new_product_accessory_related(accessory_id, product_id, created_at, updated_at, deleted_at)\
             VALUES ('{}', '{}', '{}', '{}', '{}') ON DUPLICATE KEY UPDATE accessory_id ='{}', product_id = '{}', updated_at='{}'"\
                    .format(access_id[0][0], ItemID[0][0], int(time.time()), int(time.time()), "0", access_id[0][0], ItemID[0][0], int(time.time()))
            cursor_yen.execute(sql_insert)
            db_yen.commit()
      
except MySQLdb.Error as e:
    print("Error %d: %s" % (e.args[0], e.args[1]))
    db_yen.rollback()
    db_cart.rollback()
db_yen.close()
db_cart.close()

tStop = time.time()
taken = round(tStop - tStart)
print("Done!\n")
print("Time taken: ", round(taken//60), "(m)", round(taken%60), "(s)")
