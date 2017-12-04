from subprocess import check_output
check_output("pip install -r requirements.txt", shell=True)
import os, MySQLdb, httplib2, webbrowser, sys
from datetime import datetime, date, time, timedelta
from googleapiclient.errors import HttpError
from oauth2client.client import AccessTokenRefreshError
from oauth2client import client
from apiclient import discovery

file_path = os.getcwd()

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
    sql = "SELECT `id`, `pub_date`, `locale`, `slug` FROM `mydata_pr_list`"
    cursor_web_analytics.execute(sql)
    pr_table = cursor_web_analytics.fetchall()
    for pr in pr_table:
        pg = 0
        print("id = " + str(pr[0]))
        if pr[1] != "2017-12-31" and pr[1] != "2017-12-04":
            gaData = get_ga_pageviews(credentials=credentials, stime=pr[1], locale=pr[2], slug=pr[3])
            # print("Here!")
            rows = gaData.get('rows')
            if rows:
                # print(rows)
                for r in rows:
                    pg += int(r[2])
        print(pg)

except MySQLdb.Error as e:
    print("Error %d: %s" % (e.args[0], e.args[1]))
    db_web_analytics.rollback()
db_web_analytics.close()