import os, MySQLdb, time, datetime
import csv
import sys
# file_path = os.getcwd()
try:
    # db_yen = MySQLdb.connect(host="10.8.2.125", user="marketing_query", passwd="WStFfFDSrzzdEQFW", db="yen_nas", charset='utf8')
    # db_web_analytics = MySQLdb.connect(host="10.8.2.125", user="marketing_query", passwd="WStFfFDSrzzdEQFW", db="web_analytics", charset='utf8')
    db_web_analytics = MySQLdb.connect(host="localhost", user="root", passwd="root", db="web_analytics", charset='utf8')
    # cursor_yen = db_yen.cursor()
    cursor_web_analytics = db_web_analytics.cursor()
    sql_newTables = ['''CREATE TABLE IF NOT EXISTS `tray_table` (
    `part_no` varchar(100) NOT NULL,
      `sku` varchar(100) NOT NULL,
      `created_at` int(10) NOT NULL DEFAULT '0',
      `updated_at` int(10) NOT NULL DEFAULT '0',
      PRIMARY KEY (`part_no`)
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8;''',
    '''
    CREATE TABLE IF NOT EXISTS `customer_table` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
      `name` varchar(100) NOT NULL,
      `address` varchar(100) NOT NULL,
      `part_no` varchar(100) NOT NULL,
      `created_at` int(10) NOT NULL DEFAULT '0',
      `updated_at` int(10) NOT NULL DEFAULT '0',
      PRIMARY KEY (`id`)
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8;''']

    for i in sql_newTables:
        cursor_web_analytics.execute(i)
        db_web_analytics.commit()

    file_path = 'C:\\Users\\Lily\\Documents\\GitHub\\python_2'
    os.chdir(file_path)

    if os.getcwd() != file_path:
        print("EEROR: the file path incorrect.")
        sys.exit()

    with open(file_path + '\\sn.csv', 'r') as input_file:
        reader = csv.reader(input_file)
        next(reader, None)
        for row in reader:
            # print(row)
            # break
            sql_check = "SELECT * FROM `tray_table` WHERE `part_no` = '{}' AND `sku` = '{}'".format(str(row[1]), str(row[4]))
            check = cursor_web_analytics.execute(sql_check)
            if check == 1:
                sql_update = "UPDATE `tray_table` SET `part_no` = '{a}', `sku` = '{b}', updated_at = '{c}' WHERE `part_no` = '{a}' AND `sku` = '{b}'" \
                    .format(a=str(row[1]), b=str(row[4]), c=int(time.time()))
                cursor_web_analytics.execute(sql_update)
                db_web_analytics.commit()
            else:
                sql_insert = "INSERT INTO tray_table(part_no, sku, created_at, updated_at)" \
                             "VALUES ('{}', '{}', '{}', '{}')".format(
                    str(row[1]), str(row[4]), int(time.time()), int(time.time()))
                cursor_web_analytics.execute(sql_insert)
                db_web_analytics.commit()
    print("Table created")
    # sql = "SELECT `slug`, `lang_set`, `cid` FROM `knowledge_base`"
    # cursor_yen.execute(sql)
    # KB_table = cursor_yen.fetchall()


except MySQLdb.Error as e:
    print("Error %d: %s" % (e.args[0], e.args[1]))
    # db_yen.rollback()
    db_web_analytics.rollback()
# db_yen.close()
db_web_analytics.close()

def part_no_check(part_no):
    sql_find = "SELECT * FROM `tray_table` WHERE `part_no` = '{}'".format(str(part_no))
    check = cursor_web_analytics.execute(sql_find)
    if check == 1:
        cursor_web_analytics.execute(sql_find)
        product = cursor_web_analytics.fetchall()
