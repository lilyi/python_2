# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 10:57:25 2017

@author: Lily
"""

import os, MySQLdb, time, datetime

#file_path = os.path.dirname(__file__)
A = "SP-1BAY-STAND-SILVER"
B = "data/QNAP/SP-1BAY-STAND-SILVER.jpg"
# write-in DB
db = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas")
cursor = db.cursor()
sql = "INSERT INTO NEW_PRODUCT_ACCESSORY(sku, \
    image, published_at, created_at, updated_at, deleted_at)\
    VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(str(A), str(B), int(time.time()), int(time.time()), int(time.time()), "0")
# REPLACE can be INSERT
cursor.execute(sql)
db.commit()
db.close()

# get DB data
#db = MySQLdb.connect(host="10.8.2.125", user=" ", passwd=" ", db="yen_nas", charset='utf8')

# fetch product as a table
db = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
sql = "SELECT `product_id`, `model`, `image`, `date_available` FROM `product`"
cursor = db.cursor()
cursor.execute(sql)
product_accessory = cursor.fetchall()
db.close()
#A = "SS"
try:
    db = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
    cursor = db.cursor()
    sql = '''
        CREATE TABLE IF NOT EXISTS `new_product_accessory` (
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
        ) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
        '''
    cursor.execute(sql)
    db.commit()
except MySQLdb.Error as e:
    print ("Error %d: %s" % (e.args[0], e.args[1]))
    db.rollback()
db.close()
    
try:
    db = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
    cursor = db.cursor()
    for each_product in product_accessory:
#        sku = each_product[1].strip()
#        image = each_product[2].strip()
        published_date = time.mktime(datetime.datetime.strptime(str(each_product[3]), "%Y-%m-%d").timetuple())
        sql_check = "SELECT `sku`, `image` FROM `new_product_accessory` WHERE sku = '{}'".format(str(each_product[1]))
        check = cursor.execute(sql_check)
        res = cursor.fetchall()
        if check == 1:
            if [res[0][0], res[0][1]] != [str(each_product[1]), str(each_product[2])]:
                sql = "UPDATE `new_product_accessory` SET image = '{}', updated_at = '{}' WHERE sku = '{}'".format(str(each_product[2].strip()), int(time.time()), str(each_product[1].strip()))
                cursor.execute(sql)
                db.commit()
                print("update")
        else:
            sql = "INSERT INTO NEW_PRODUCT_ACCESSORY(sku, image, published_at, created_at, updated_at, deleted_at)\
               VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(str(each_product[1].strip()), str(each_product[2].strip()), int(published_date), int(time.time()), int(time.time()), "0")
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

tStart = time.time()
try:
    db1 = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
    db2 = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
    cursor1 = db1.cursor()
    cursor2 = db2.cursor()
    for each_product in product_accessory:
        sql2 = "SELECT `language_id`, `name`, `description` FROM `product_description` WHERE `product_id` = {}".format(each_product[0])
        cursor2.execute(sql2)
#        print(sql2)
        results = cursor2.fetchall()
        sql3 = "SELECT `id` FROM `new_product_accessory` WHERE `sku` = '{}' AND `image` = '{}'".format(each_product[1], each_product[2])
        cursor1.execute(sql3)
#        print(sql3)
        accessory_id = cursor1.fetchall()
        for each_lan in results:
            sql4 = "SELECT `language_id`, `code` FROM `language` WHERE `language_id` = {}".format(each_lan[0])
            cursor2.execute(sql4)
#            print(sql4)
            lan_detail = cursor2.fetchall()
            lan_dic = mk_lan_dic()
            locale = lan_dic[lan_detail[0][1]]
            print(locale)
            sql5 = 'INSERT INTO NEW_PRODUCT_ACCESSORY(accessory_id, \
                locale, name, description, created_at, updated_at, deleted_at)\
                VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}") \
                ON DUPLICATE KEY UPDATE name="{}", description = "{}", updated_at="{}"'\
               .format(accessory_id[0][0], str(locale), str(each_lan[1]), str(each_lan[2]), \
                       int(time.time()), int(time.time()), "0", str(each_lan[1]), str(each_lan[2]), int(time.time()))
#==============================================================================
#             sql5 = 'REPLACE INTO NEW_PRODUCT_ACCESSORY_DETAIL(accessory_id, \
#                 locale, name, description, created_at, updated_at, deleted_at)\
#                 VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(accessory_id[0][0], str(locale), str(each_lan[1]), str(each_lan[2]), int(time.time()), int(time.time()), "0")
# #            print(sql5)
#==============================================================================
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
try:
    db1 = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
    db2 = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
    cursor1 = db1.cursor()
    cursor2 = db2.cursor()
    sql1 = "SELECT `id`, `sku` FROM `new_product_accessory`"
    cursor1.execute(sql1)
    accessory = cursor1.fetchall()
    c = 0
    c_each_cate = 0
    CHECK = []
    CHECK2 = []
    for each_access in accessory:
        c += 1
        sql2 = "SELECT `product_id` FROM `product` WHERE `model` = '{}'".format(each_access[1]) # 用 access sku 找到對應 id
        print("HERE!1")
        cursor2.execute(sql2)
        product_id = cursor2.fetchall()
        print("HERE!2")
        sql3 = "SELECT `category_id` FROM `product_to_category` WHERE `product_id` = {}".format(product_id[0][0]) # 用 product_id 找到對應的 category_id 通常不只一筆
        print("HERE!3")
        cursor2.execute(sql3)
        category_ids = cursor2.fetchall()
#        print("len(category_ids)={}".format(category_ids))
        # 用 category_ids 跑回圈
        for each_cate in category_ids:
            if len(each_cate) == 0:
                c_each_cate += 1
                each_cate = 0
                sql4 = "SELECT `name` FROM `category_description` WHERE `category_id` = {}".format(each_cate) # 用 category_id 找對應 name (此處為 NAS/NVR name)
            else:
                sql4 = "SELECT `name` FROM `category_description` WHERE `category_id` = {}".format(each_cate[0])
            print("HERE!5")
            cursor2.execute(sql4)
            NAS_name = cursor2.fetchall() # 會包含 NVR 和 XXX Series 等以下與官網 nas 的 temp_name 對不上的名稱，多語，所以有好幾個
            print("HERE!6")
            each_nas = NAS_name[0][0].strip().lower()
            #

            #
            if len(NAS_name) == 0: # 基本上不會進來這個條件下
                CHECK.append(each_cate[0])
                NAS_name = ''
                sql5 = "SELECT `ItemID` FROM `product_items` WHERE `temp_name` = '{}'".format(NAS_name)
#            elif NAS_name[0][0][-1] == ' ':
#                sql5 = "SELECT `ItemID` FROM `PRODUCT_ITEMS` WHERE `temp_name` = '{}'".format(NAS_name[0][0][:-1])
            else:
                sql5 = "SELECT `ItemID` FROM `product_items` WHERE `temp_name` = '{}'".format(each_nas) # 用 NAS name 找機種 ID
            print(sql5)
            cursor1.execute(sql5)
            item_id = cursor1.fetchall()
            #
            print(item_id)
            if len(item_id) == 0:
                CHECK2.append(each_nas)
                item_id = 0
                print(item_id)
                sql6 = "INSERT IGNORE INTO NEW_PRODUCT_ACCESSORY_RELATED(accessory_id, product_id,\
                created_at, updated_at, deleted_at) VALUES ('{}', '{}', '{}', '{}', '{}')".format(each_access[0], item_id, int(time.time()), int(time.time()), "0")
            else:
                sql6 = "INSERT IGNORE INTO NEW_PRODUCT_ACCESSORY_RELATED(accessory_id, product_id,\
                created_at, updated_at, deleted_at) VALUES ('{}', '{}', '{}', '{}', '{}')".format(each_access[0], item_id[0][0], int(time.time()), int(time.time()), "0")
            print("sql6: {}".format(sql6))
            cursor1.execute(sql6)
            db1.commit()
            print("HERE!9")

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
print(c)
print("c_each_cate = {}".format(c_each_cate))
print("CHECK = {}".format(CHECK))
print("CHECK2 = {}".format(len(set(CHECK2))))

VS = []
TS = []
for i in set(CHECK2):
    l = i.split('-')[0]
    if l == 'vs':
        VS.append(i)
    else:
        TS.append(i)
print(TS.sort())
# 找出 65 個 0 來自何處
# 針對每個 TS 去找所有的 accessory_name
#db1 = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
Accessory = []
db2 = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
cursor2 = db2.cursor()
for each_TS in TS:

    sql = "SELECT `category_id` FROM `category_description` WHERE `name` = '{}'".format(each_TS.upper())
    cursor2.execute(sql)
    resu = cursor2.fetchall()
    Accessory.append(resu)
db2.close()
count=0
for each in Accessory:
    count += len(each)
    if len(each) == 0:
        print("E")
# SELECT `category_id` FROM `category_description` WHERE `name` = 'TS-109 Series' => 10 筆
# count=187  共197個 access (有重複)
Hey = [] #category_id
for each in Accessory:
    if len(each) != 0:
        Hey.append(each[0])
    set(Hey)
db2 = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
cursor2 = db2.cursor()
All_access_ids = []
for i in Hey:
    sql = "SELECT `product_id` FROM `product_to_category` WHERE `category_id` = '{}'".format(i[0])
    cursor2.execute(sql)
    res = cursor2.fetchall()
    for j in res:
        All_access_ids.append(j[0])
db2.close()


db2 = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart", charset='utf8')
cursor2 = db2.cursor()
sql = "SELECT DISTINCT `category_id` FROM `product_to_category`"
cursor2.execute(sql)
product_items1 = cursor2.fetchall()
db2.close()
q = []
p = []
res = []
for each in product_items2:
#    l = each[0].strip()
#    res.append(l)
    q.append(each[0])

for i in p:
    for j in res:
        if i != j:
            print (i)


    #    print(published_date)
#        sql = "INSERT INTO NEW_PRODUCT_ACCESSORY(sku, \
#        image, published_at, created_at, updated_at, deleted_at)\
#        VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(str(each_product[1]), str(each_product[2]), int(published_date), int(time.time()), int(time.time()), "0")
        sql = "INSERT INTO NEW_PRODUCT_ACCESSORY(sku, \
        image, published_at, created_at, updated_at, deleted_at)\
        VALUES ('{}', '{}', '{}', '{}', '{}', '{}') ON DUPLICATE KEY UPDATE image='{}', updated_at='{}'"\
               .format(str(each_product[1]), str(each_product[2]), int(published_date), \
                       int(time.time()), int(time.time()), "0", str(each_product[2]), int(time.time()))

    #    print(sql)
        cursor.execute(sql)
        db.commit()