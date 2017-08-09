# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 10:57:25 2017

@author: Lily
"""

import os, MySQLdb, time, httplib2, webbrowser, datetime

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

try:
    db = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas", charset='utf8')
    cursor = db.cursor()
    for each_product in product_accessory:
        published_date = time.mktime(datetime.datetime.strptime(str(each_product[3]), "%Y-%m-%d").timetuple())
    #    print(published_date)    
        sql = "INSERT IGNORE INTO NEW_PRODUCT_ACCESSORY(sku, \
        image, published_at, created_at, updated_at, deleted_at)\
        VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(str(each_product[1]), str(each_product[2]), int(published_date), int(time.time()), int(time.time()), "0")
    #    print(sql)
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
        sql3 = "SELECT `id` FROM `NEW_PRODUCT_ACCESSORY` WHERE `sku` = '{}' AND `image` = '{}'".format(each_product[1], each_product[2])
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
            # INSERT IGNORE
            sql5 = 'REPLACE INTO NEW_PRODUCT_ACCESSORY_DETAIL(accessory_id, \
                locale, name, description, created_at, updated_at, deleted_at)\
                VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(accessory_id[0][0], str(locale), str(each_lan[1]), str(each_lan[2]), int(time.time()), int(time.time()), "0")
#            print(sql5)
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
    sql1 = "SELECT `id`, `sku` FROM `NEW_PRODUCT_ACCESSORY`"
    cursor1.execute(sql1)
    accessory = cursor1.fetchall()
    c = 0
    for each_access in accessory:
        c += 1
        sql2 = "SELECT `product_id` FROM `PRODUCT` WHERE `model` = '{}'".format(each_access[1])
        print("HERE!1")
        cursor2.execute(sql2)
        product_id = cursor2.fetchall()
        print("HERE!2")
        sql3 = "SELECT `category_id` FROM `PRODUCT_TO_CATEGORY` WHERE `product_id` = {}".format(product_id[0][0])
        print("HERE!3")
        cursor2.execute(sql3)
        category_id = cursor2.fetchall()
        print("HERE!4")
        for each_cate in category_id:
            if len(each_cate) == 0:
                each_cate = 0
                sql4 = "SELECT `name` FROM `CATEGORY_DESCRIPTION` WHERE `category_id` = {}".format(each_cate)
            else:
                sql4 = "SELECT `name` FROM `CATEGORY_DESCRIPTION` WHERE `category_id` = {}".format(each_cate[0])
            print("HERE!5")
            cursor2.execute(sql4)
            NAS_name = cursor2.fetchall() # 會包含 NVR 和 XXX Series 等以下與官網 nas 的 temp_name 對不上的名稱
            print("HERE!6")
            if len(NAS_name) == 0:
                NAS_name = ''
                sql5 = "SELECT `ItemID` FROM `PRODUCT_ITEMS` WHERE `temp_name` = '{}'".format(NAS_name)
            elif NAS_name[0][0][-1] == ' ':
                sql5 = "SELECT `ItemID` FROM `PRODUCT_ITEMS` WHERE `temp_name` = '{}'".format(NAS_name[0][0][:-1])
            else:
                sql5 = "SELECT `ItemID` FROM `PRODUCT_ITEMS` WHERE `temp_name` = '{}'".format(NAS_name[0][0])
            print(sql5)
            cursor1.execute(sql5)
            item_id = cursor1.fetchall()
            print(item_id)
            if len(item_id) == 0:
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