# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 16:03:36 2017

@author: Lily
"""
# -*- coding: utf-8 -*-

import argparse
from googleapiclient.errors import HttpError
from googleapiclient import sample_tools
from oauth2client.client import AccessTokenRefreshError
from oauth2client.service_account import ServiceAccountCredentials
import MySQLdb

type_name = ['tutorial', 'faq']
table_name = ['qa', 'trade_teach']
time = ['2017-03-01', '2017-03-31']
slug = '為何使用者無法登入多媒體中心只有-admin-帳號可以登入'

lan_list = ["/en/","/en-us/","/en-uk/","/en-au/","/en-in/","/de-de/","/es-es/","/es-mx/","/fr-fr/","/it-it/","/nl-nl/","/sv-se/","/zh-tw/","/zh-hk/","/pt-pt/","/pl-pl/","/ja-jp/","/ko-kr/","/cs-cz/", "/th-th/"]
dic = {}
for each in lan_list:
    l = each.split("/")[1]
    if l == 'pt-pt':
        dic['pt'] = l
    elif l == 'nl-nl':
        dic['nl'] = l
    elif l == 'ko-kr':
        dic['kr'] = l
    elif l == 'ja-jp':
        dic['jp'] = l
    elif l == 'it-it':
        dic['it'] = l
    elif l == 'fr-fr':
        dic['fr'] = l
    elif l == 'es-es':
        dic['es'] = l
    elif l == 'de-de':
        dic['de'] = l
    elif l == 'en-au':
        dic['au'] = l
    elif l == 'pl-pl':
        dic['pl'] = l
    elif l == 'cs-cz':
        dic['cz'] = l
    elif l == 'zh-hk':
        dic['hk'] = l
    else:
        dic[str(l)] = l
print(dic)

def get_top_keywords(service, profile_id, lan, type_name, slug):
    """Executes and returns data from the Core Reporting API.
    This queries the API for the top 25 organic search terms by visits.
    Args:
    service: The service object built by the Google API Python client library.
    profile_id: String The profile ID from which to retrieve analytics data.
    Returns:
    The response returned from the Core Reporting API.
    """
    return service.data().ga().get(
            ids='ga:' + profile_id,
            start_date=time[0],
            end_date=time[1],
            metrics='ga:pageviews',
            dimensions='ga:pagePath',
#            segment = "sessions::condition::ga:country=@{}".format(cname)
            filters = "ga:pagePath=@{};ga:pagePath=~/how-to/{};ga:pagePath=~{}".format(lan, type_name, slug)
            ).execute()

def print_results(results, lan):
    """Prints out the results.
    This prints out the profile name, the column headers, and all the rows of
    data.
    Args:
        results: The response returned from the Core Reporting API.
    """
    print('Profile Name: %s' % results.get('profileInfo').get('profileName'))
    print('language: %s' % lan)
    header = [h['name'][3:] for h in results.get('columnHeaders')] #this takes the column headers and gets rid of ga: prefix
    print(''.join('%30s' %h for h in header))
    if results.get('rows', []):
        for row in results.get('rows'):
            print(''.join('%30s' %r for r in row))
    return lan,row[1]

def connectDB(db, table):
    """
    db = "web_analytics"
    """
    try:
        db = MySQLdb.connect(host="10.8.2.125",user="marketing_query",passwd="WStFfFDSrzzdEQFW",db=db)
        sql = "SELECT slug FROM `qa` WHERE `cid` = 1 AND `lang_set` = 'zh-tw'"
        cursor = db.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except MySQLdb.Error as e:
        print ("Error %d: %s" % (e.args[0], e.args[1]))


def main(type_name, slug):
#    lan_list = ["/en/","/en-us/","/en-uk/","/en-au/","/en-in/","/de-de/","/es-es/","/es-mx/","/fr-fr/","/it-it/","/nl-nl/","/sv-se/","/zh-tw/","/zh-hk/","/pt-pt/","/pl-pl/","/ja-jp/","/ko-kr/","/cs-cz/"]
    lan_list2 = ["/zh-tw/","/zh-hk/"]
    res = []
    try:
        scopes = ['https://https://www.googleapis.com/auth/analytics']
        ServiceAccountCredentials.from_json_keyfile_name(
                'C:/Users/Lily/Documents/GA/R/key_secrets.json', scopes=scopes)
        service, flags = sample_tools.init("", 
        'analytics', 'v3', __doc__, __file__,
        scope='https://www.googleapis.com/auth/analytics.readonly')
        
        profile_id = '3035421'
        for lan in lan_list2:
            results = get_top_keywords(service, profile_id, lan, type_name, slug)
            print(results)
            res.append(print_results(results, lan))
        return res
    except TypeError as error:
        # Handle errors in constructing a query.
        print(('There was an error in constructing your query : %s' % error))
    
    except HttpError as error:
        # Handle API errors.
        print(('Arg, there was an API error : %s : %s' %
               (error.resp.status, error._get_reason())))
    except AccessTokenRefreshError:
        # Handle Auth errors.
        print ('The credentials have been revoked or expired, please re-run '
               'the application to re-authorize')
    
if __name__ == '__main__':
    re = main(type_name[1], slug)
    print(re[0][1])
