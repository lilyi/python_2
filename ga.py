# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 14:08:01 2017

@author: Lily
"""

import os, MySQLdb, time, httplib2, webbrowser, sys, datetime
from googleapiclient.errors import HttpError
from oauth2client.client import AccessTokenRefreshError
from oauth2client import client
from apiclient import discovery

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import numpy as np

from sklearn.linear_model import LinearRegression
import sys
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tabulate import tabulate

#file_path = os.path.dirname(__file__)
#file_path = "C:\\Users\\Lily\\Documents\\GitHub\\python_2"
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

def get_ga_pageviews(credentials, stime,country):# , lan, type_name, slug):
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
        service = create_service_object(credentials) #The service object built by the Google API Python client library.
        return service.data().ga().get(
                ids='ga:3035421',
                start_date=stime,
                end_date="yesterday",
                metrics="ga:sessions,ga:pageViews,ga:bounceRate, ga:avgSessionDuration",
                dimensions='ga:date',
                segment="sessions::condition::ga:country=@{}".format(country)
#                filters='ga:pagePath=~/{}'.format(i),
#                filters = "ga:pagePath=@{};ga:pagePath=~/how-to/{};ga:pagePath=@{}".format(lan, type_name, slug)
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
        print ('The credentials have been revoked or expired, please re-run '
               'the application to re-authorize')

# 32 country alert
countries = ["Australia", "Austria", "Belgium", "Canada", "Czechia", "Denmark", "France", "Germany", "Greece", "Hong Kong", "Hungary", "India", "Iran", "Israel", "Italy", "Japan", "Mexico", "Netherlands", "Norway", "Poland", "Portugal", "Romania", "South Africa", "South Korea", "Spain", "Sweden", "Switzerland", "Taiwan", "Thailand", "Turkey", "United Kingdom", "United States"]
credentials = acquire_oauth2_credentials()
#country = "Taiwan"
    
def dataProcess(country): #
    print(country)
    results = get_ga_pageviews(credentials, "2017-01-01", country)
    rows = results.get('rows')
    date, sessions = [], []
    for row in rows:
        date.append(datetime.datetime.strptime(row[0],"%Y%m%d"))
        sessions.append(int(row[1]))
    lm = LinearRegression()
    x = range(len(sessions))
    y = sessions
    lm.fit(np.reshape(x, (len(x), 1)), np.reshape(y, (len(y), 1)))
    return(country, round(float(lm.coef_[0]), 2), round(float(lm.intercept_[0]),2))
lm_result = [] # lm.coef_, lm.intercept_
for country in countries:
    res = dataProcess(country)
    lm_result.append(res)
    print(res)
alert = [["Country", "Coef"]]
for each in lm_result:
    if each[1] > 0.1 or each[1] < (-0.1):
        alert.append([each[0], each[1]])

def sendEmail(alert):
#    COMMASPACE = ', '
    sender = 'Lily Li'
    recipients = 'lilyli@qnap.com'
    username = 'lilyli@qnap.com'
    password = 'Lilyshea07'
    text = """
    Hi,\n
    Here is your data:\n       
    {table}\n
    Regards,
    Lily"""    
    html = """
    <html><body><p>Hi</p>
    <p>Here is your data:</p>
    {table}
    <p>Regards,</p>
    <p>Lily Li</p>
    </body></html>
    """
    text = text.format(table=tabulate(alert, headers="firstrow", tablefmt="grid"))
    html = html.format(table=tabulate(alert, headers="firstrow", tablefmt="html"))
    outer = MIMEMultipart(
    "alternative", None, [MIMEText(text), MIMEText(html,'html')])
    outer['Subject'] = '32 Countries Monthly Info'
    outer['To'] = recipients#COMMASPACE.join(recipients)
    outer['From'] = sender
    outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'    
    composed = outer.as_string()
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(username,password)
        #server.sendmail(fromaddr, toaddrs, msg)
        server.sendmail(username, recipients, composed)
        server.quit()
        print("Email sent!")
    except:
        print("Unable to send the email. Error: ", sys.exc_info()[0])
        raise    
sendEmail(alert)   

#converted_dates = map(datetime.datetime.strptime, date, len(date)*['%Y%m%d'])
#x_axis = (converted_dates)
#formatter = mdates.DateFormatter('%Y%m%d')
sessions_df = pd.DataFrame(
    {"Date": date,
     "Sessions": sessions
    }
)
#fig, ax = plt.subplots()
#ax = sns.pointplot(data = sessions_df, x="Date", y="Sessions", ax=ax)
countries = ["Australia", "Austria", "Belgium", "Canada", "Czechia", "Denmark", "France", "Germany", "Greece", "Hong Kong", "Hungary", "India", "Iran", "Israel", "Italy", "Japan", "Mexico", "Netherlands", "Norway", "Poland", "Portugal", "Romania", "South Africa", "South Korea", "Spain", "Sweden", "Switzerland", "Taiwan", "Thailand", "Turkey", "United Kingdom", "United States"]
credentials = acquire_oauth2_credentials()
rowsSet = []
for country in countries:
    results = get_ga_pageviews(credentials, "2017-01-01", country)
    rowsSet.append(results)
for rowCountry in rowsSet:
    rowCountry = rowsSet[0]
    countryName = rowCountry.get('query').get('segment').split("@")[1]
    allRows = rowCountry.get('rows')
    date, sessions = [], []
    for row in allRows:
        date.append(datetime.datetime.strptime(row[0], "%Y%m%d").date())
        sessions.append(int(row[1]))
    df = pd.DataFrame({"Date":date, "Sessions" : sessions})
#    df["Date"] = date
#    df["Sessions"] = sessions
    f, ax = plt.subplots(1, 1)
    x_col='Date'
    y_col = 'Sessions'
    sns.tsplot(data=df)
    sns.tsplot(ax=ax,x=x_col,y=y_col,data=df,color='blue')
    ax.legend(handles=ax.lines[::len(df1)+1], labels=["A","B","C"])
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.set_xticklabels([t.get_text().split("T")[0] for t in ax.get_xticklabels()])
    ax.legend()
    
    plt.gcf().autofmt_xdate()
    plt.show()
    sns.pointplot(data=df, x="Date", y="Sessions")  
published_date = time.mktime(datetime.datetime.strptime(str(each_product[3]), "%Y-%m-%d").timetuple())

def plotLine(rowsSet):
    
    
    results = get_ga_pageviews(credentials, "2017-01-01", country)
    rows = results.get('rows') # ga:sessions,ga:pageViews,ga:bounceRate, ga:avgSessionDuration
    
    date = datetime.datetime.strptime(row[0],"%Y%m%d")
        res.append() 
    date, sessions, pageViews, bounceRate, avgSessionsDuration = [], [], [], [], [], []
    for row in rows:
        date.append(datetime.datetime.strptime(row[0],"%Y%m%d"))
        sessions.append(int(row[1]))
        pageViews.append(int(row[2]))
        bounceRate.append(float(int(row[3])))
        avgSessionsDuration.append(float(row[4]))
    return
    

