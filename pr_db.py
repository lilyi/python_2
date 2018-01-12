import os
from subprocess import check_output
os.chdir("C:\\Users\\Lily\\Documents\\GitHub\\python_2")
file_path = os.getcwd()
check_output("pip install -r requirements.txt", shell=True)

from xlrd import open_workbook
# from slugify import slugify
import re
import MySQLdb, httplib2, webbrowser, sys
import time
from datetime import datetime, date, time, timedelta
from googleapiclient.errors import HttpError
from oauth2client.client import AccessTokenRefreshError
from oauth2client import client
from apiclient import discovery

class Arm(object):
    def __init__(self, id, dsp_name, dsp_code, hub_code):
        self.id = id
        self.dsp_name = dsp_name
        self.dsp_code = dsp_code
        self.hub_code = hub_code


    def __str__(self):
        return("Arm object:\n"
               "  Arm_id = {0}\n"
               "  DSPName = {1}\n"
               "  DSPCode = {2}\n"
               "  HubCode = {3}\n"
               .format(self.id, self.dsp_name, self.dsp_code,
                       self.hub_code))

wb = open_workbook('C:\\Users\\Lily\\Documents\\GA\\list\\en.xlsx')
for sheet in wb.sheets():
    number_of_rows = sheet.nrows
    number_of_columns = sheet.ncols

    items = []

    rows = []
    for row in range(1, number_of_rows):
        values = []
        for col in range(number_of_columns):
            value  = (sheet.cell(row,col).value)
            try:
                value = str(int(value))
            except ValueError:
                pass
            finally:
                values.append(value)
        item = Arm(*values)
        items.append(item)

for item in items:
    print(item)
    print("Accessing one single value (eg. DSPName): {0}".format(item.dsp_name))

def slugify(s):
    """
    Simplifies ugly strings into something URL-friendly.
    >>> print slugify("[Some] _ Article's Title--")
    some-articles-title
    """

    # "[Some] _ Article's Title--"
    # "[some] _ article's title--"
    s = s.lower()

    # "[some] _ article's_title--"
    # "[some]___article's_title__"
    for c in [' ', '-', '.', '/']:
        s = s.replace(c, '_')

    # "[some]___article's_title__"
    # "some___articles_title__"
    s = re.sub('\W', '', s)

    # "some___articles_title__"
    # "some   articles title  "
    s = s.replace('_', ' ')

    # "some   articles title  "
    # "some articles title "
    s = re.sub('\s+', ' ', s)

    # "some articles title "
    # "some articles title"
    s = s.strip()

    # "some articles title"
    # "some-articles-title"
    s = s.replace(' ', '-')

    return s

def acquire_oauth2_credentials():
    """
    Flows through OAuth 2.0 authorization process for credentials.
    Create credentials file as cre.json
    """
    if os.path.isfile("%s/cre.json" % file_path):
        f = open("%s/cre.json" % file_path, "r")
        credentials = client.OAuth2Credentials.from_json(f.read())
        f.close()
    else:
        flow = client.flow_from_clientsecrets(
            "%s/client_secrets.json" % file_path,
            scope='https://www.googleapis.com/auth/analytics.readonly',
            redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        auth_uri = flow.step1_get_authorize_url()
        webbrowser.open(auth_uri)
        auth_code = input('Enter the authentication code: ')
        credentials = flow.step2_exchange(auth_code)
        write_credentials("%s/cre.json" % file_path, credentials)
    return credentials


def write_credentials(fname, credentials):
    """Writes credentials as JSON to file."""
    f = open(fname, "w")
    f.write(credentials.to_json())
    f.close()


def create_service_object(credentials):
    """Creates Service object for credentials."""
    http_auth = httplib2.Http()
    http_auth = credentials.authorize(http_auth)
    service = discovery.build('analytics', 'v3', http=http_auth)
    return service


def get_ga_pageviews(credentials, stime, locale, slug):  # , lan, type_name, slug):
    """Executes and returns data from the Core Reporting API.
    This queries the API for the top 25 organic search terms by visits.
    Args:
    credentials: from acquire_oauth2_credentials()
    stime: start_time
    etime: end_time
    lan: website page language
    type_name: 'tutorial', 'faq'
    slug: article title
    Returns:
    The response returned from the Core Reporting API.
    """
    try:
        end_date = datetime.strptime(stime, '%Y-%m-%d') + timedelta(days=30)
        etime = end_date.strftime('%Y-%m-%d')
        if end_date > datetime.today():
            etime = "yesterday"
        service = create_service_object(
            credentials)  # The service object built by the Google API Python client library.
        return service.data().ga().get(
            ids='ga:117842049',
            start_date=stime,
            end_date=etime,
            metrics="ga:sessions,ga:pageViews,ga:bounceRate, ga:avgSessionDuration",
            dimensions='ga:date',
            # segment="sessions::condition::ga:country=@{}".format(country)
            #                filters='ga:pagePath=~/{}'.format(i),
            filters = "ga:pagePath=@/{}/;ga:pagePath=@{}".format(locale, slug)
        ).execute()
    except TypeError as error:
        # Handle errors in constructing a query.
        print(('There was an error in constructing your query : %s' % error))

    except HttpError as error:
        # Handle API errors.
        print(('Arg, there was an API error : %s : %s' %
               (error.resp.status, error._get_reason())))
    except AccessTokenRefreshError:
        # Handle Auth errors.
        print('The credentials have been revoked or expired, please re-run '
              'the application to re-authorize')

credentials = acquire_oauth2_credentials()

try:
    db_web_analytics = MySQLdb.connect(host="localhost", user="root", passwd="root", db="web_analytics", charset='utf8')
    cursor_web_analytics = db_web_analytics.cursor()
    sql_newTable = '''CREATE TABLE IF NOT EXISTS `pr_list` (
    `id` int(10) NOT NULL,
      `title` varchar(100) NOT NULL,
      `status` varchar(100) NOT NULL,
      `locale` varchar(100) NOT NULL,
      `pageview` int(10) NOT NULL DEFAULT '0',
      `pub_date` int(10) NOT NULL DEFAULT '0',
      `created_at` int(10) NOT NULL DEFAULT '0',
      `updated_at` int(10) NOT NULL DEFAULT '0',
      PRIMARY KEY (`id`, `locale`)
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8;'''

    cursor_web_analytics.execute(sql_newTable)
    db_web_analytics.commit()

except MySQLdb.Error as e:
    print("Error %d: %s" % (e.args[0], e.args[1]))
    db_web_analytics.rollback()
db_web_analytics.close()

try:
    db_web_analytics = MySQLdb.connect(host="localhost", user="root", passwd="root", db="web_analytics", charset='utf8')
    cursor_web_analytics = db_web_analytics.cursor()
    wb = open_workbook('C:\\Users\\Lily\\Documents\\GA\\list\\en.xlsx')
    for sheet in wb.sheets():
        number_of_rows = sheet.nrows
        number_of_columns = sheet.ncols
        items = []
        rows = []
        for row in range(0, number_of_rows):
            values = []
            for col in range(number_of_columns):
                value  = (sheet.cell(row,col).value)
                try:
                    value = str(int(value))
                except ValueError:
                    pass
                finally:
                    values.append(value)
            items.append(values)
            stime = '2017-07-01'
            pageview = 0
            gaData = get_ga_pageviews(credentials=credentials, stime=stime, locale=values[3], slug=slugify(values[1]))
            rows = gaData.get('rows')
            if rows:
                # print(rows)
                for r in rows:
                    pageview += int(r[2])
                    sql_check = "SELECT * FROM `pr_list` WHERE `id` = '{}' AND `locale` = '{}'".format(str(values[0]), str(values[3]))
                    check = cursor_web_analytics.execute(sql_check)
                    if check == 1:
                        sql_update = "UPDATE `pr_list` SET `pageview` = '{a}', `status` = '{b}', updated_at = '{c}' WHERE `id` = '{d}' AND `locale` = '{e}'" \
                            .format(a=pageview, b=values[2], c=datetime.now().strftime('%Y-%m-%d'), d=values[0], e=values[3])
                        cursor_web_analytics.execute(sql_update)
                        db_web_analytics.commit()
                    else:
                        sql_insert = "INSERT INTO pr_list(id, title, status, locale, created_at, updated_at)" \
                                     "VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(
                            str(values[0]), str(values[1]), str(values[2]), str(values[3]), int(pageview), datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d'))
                        cursor_web_analytics.execute(sql_insert)
                        db_web_analytics.commit()
except MySQLdb.Error as e:
    print("Error %d: %s" % (e.args[0], e.args[1]))
    db_web_analytics.rollback()
db_web_analytics.close()