# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 10:57:25 2017

@author: Lily
"""

import html, MySQLdb, time, datetime


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
        #`ean` int(100) DEFAULT NULL,
        #`upc` int(100) DEFAULT NULL,
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

# locale dic
def mk_lan_dic():
    lan_list = ['en', 'zh-cn', 'de-de', 'fr-fr', 'it-it', 'zh-tw', 'nl-nl', 'ja-jp', 'en-uk', 'en-us', 'es-es', 'pt-pt', 'ru']
    code = ['en', 'cn', 'de-DE', 'fr', 'it', 'tw', 'nl', 'jp', 'UKE', 'USE', 'es', 'pt-br', 'ru']
    lan_dic = {}
    for idx in range(len(code)):
        lan_dic[code[idx]] = lan_list[idx]
    return lan_dic

# table 2
tStart = time.time()
try:
    db1 = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
    db2 = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
    cursor1 = db1.cursor()
    cursor2 = db2.cursor()
    for each_product in product_accessory:
        sql2 = "SELECT `language_id`, `name`, `description` FROM `product_description` WHERE `product_id` = {}".format(each_product[0])
        cursor2.execute(sql2)
        results = cursor2.fetchall()
        sql3 = "SELECT `id` FROM `new_product_accessory` WHERE `sku` = '{}' AND `image` = '{}'".format(each_product[1].strip(), each_product[2].strip())
        cursor1.execute(sql3)
        accessory_id = cursor1.fetchall()
        for each_lan in results:
            sql4 = "SELECT `language_id`, `code` FROM `language` WHERE `language_id` = {}".format(each_lan[0])
            cursor2.execute(sql4)
            lan_detail = cursor2.fetchall()
            lan_dic = mk_lan_dic()
            locale = lan_dic[lan_detail[0][1]]
            print(locale)
            sql5 = 'INSERT INTO NEW_PRODUCT_ACCESSORY_DETAIL(accessory_id, \
                locale, name, description, created_at, updated_at, deleted_at)\
                VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}") \
                ON DUPLICATE KEY UPDATE name="{}", description = "{}", updated_at="{}"'\
               .format(accessory_id[0][0], str(locale), str(each_lan[1]), str(each_lan[2]), \
                       int(time.time()), int(time.time()), "0", str(each_lan[1]), str(each_lan[2]), int(time.time()))
            cursor1.execute(sql5)
            db1.commit()
except MySQLdb.Error as e:
        print ("Error %d: %s" % (e.args[0], e.args[1]))
        db1.rollback()
        db2.rollback()
db1.close()
db2.close()
tStop = time.time()
taken = round(tStop - tStart)
print("Done!\n")
print("Time taken: ", round(taken//60), "(m)", round(taken%60), "(s)")

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
    print("Done!\n")
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
print(TSSET)

