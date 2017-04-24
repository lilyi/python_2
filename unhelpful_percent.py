# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 15:52:41 2017

@author: Lily
"""


import MySQLdb
import statistics
import csv

def main():
    type_name = ['tutorial', 'faq']
    for each in type_name:
        try:
            db = MySQLdb.connect(host="10.8.2.125",user="marketing_query",passwd="WStFfFDSrzzdEQFW",db="web_analytics")
            sql = "SELECT page_type, page_id, count(*) as total_votes FROM `page_helpful` where page_type='%s' group by `page_id` order by total_votes desc" % each
            cursor = db.cursor()
            cursor.execute(sql)        
#            撈取多筆資料
            all_results = cursor.fetchall()   
            total_votes = []
            all_data = []
            all_dict = {}
            for record in all_results: 
                all_data.append(record[:])
                all_dict[str(record[1])] = record[0], record[2]
                total_votes.append(record[2]) 
            med = statistics.median(total_votes)
            all_pID = []
            for i in all_data:
                if i[2] >= med:
                   all_pID.append(str(i[1]))
            all_pID2 = ','.join(all_pID)
            sql2 = "SELECT page_id, count(*) as unhelpful_count FROM `page_helpful` WHERE `page_type` = '%s' AND `page_id` IN (%s) AND helpful = 0 group by page_id" % (each, all_pID2)
            cursor.execute(sql2)
            unhelpful_results = cursor.fetchall()
            if each == 'tutorial':
                TYPE = 'trade_teach'
            else:
                TYPE = 'qa'
            unhelpful_pID = []
            unfelpful_count = []
            percent = []
            unhelpful_data = []
            result = []         
            for i in unhelpful_results:
                unhelpful_data.append(i[:])
                unhelpful_pID.append(str(i[0]))
                unfelpful_count.append(i[1])
                per = round(100*(i[1]/all_dict[str(i[0])][1]),2)
                percent.append(per)
                url = 'https://www.qnap.com/en/how-to/%s/con_show.php?cid=%s' % (each, str(i[0]))
                db2 = MySQLdb.connect(host="10.8.2.125",user="marketing_query",passwd="WStFfFDSrzzdEQFW",db="yen_nas", charset='utf8')
                cursor = db2.cursor()
                sql3 = "SELECT title FROM `%s` WHERE `cid` = %s AND `lang_set` = 'en'" % (TYPE, str(i[0]))
                cursor.execute(sql3)
                title_result = cursor.fetchall()
                result.append([str(title_result[0][0]), url, per, all_dict[str(i[0])][1]])
            top10 = sorted(result, key = lambda x : (x[2], x[3]), reverse=True)[:10]
            with open('unhelpful_%s.csv' % each, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['title', 'page','unhelpful (%)', 'total_votes'])
                writer.writerows(top10)
#            關閉連線
            db.close()
            db2.close()
            print('Saved!')
        except MySQLdb.Error as e:
            print ("Error %d: %s" % (e.args[0], e.args[1]))
  
if __name__ == '__main__':
    main()