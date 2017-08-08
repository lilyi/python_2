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

db = MySQLdb.connect(host="localhost",user="root",passwd="root",db="open_cart")
sql = "SELECT `model`, `image`, `date_available` FROM `product`"
cursor = db.cursor()
cursor.execute(sql)
product_accessory = cursor.fetchall()
db.close()

try:
    db = MySQLdb.connect(host="localhost",user="root",passwd="root",db="yen_nas")
    cursor = db.cursor()
    for each_product in product_accessory:
        published_date = time.mktime(datetime.datetime.strptime(str(each_product[2]), "%Y-%m-%d").timetuple())
    #    print(published_date)    
        sql = "INSERT IGNORE INTO NEW_PRODUCT_ACCESSORY(sku, \
        image, published_at, created_at, updated_at, deleted_at)\
        VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(str(each_product[0]), str(each_product[1]), int(published_date), int(time.time()), int(time.time()), "0")
    #    print(sql)
        cursor.execute(sql)   
        db.commit()
except MySQLdb.Error as e:
        print ("Error %d: %s" % (e.args[0], e.args[1]))
        db.rollback()
db.close()


