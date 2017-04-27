# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 09:59:23 2017

@author: Lily
This script works with Python 3.x
"""

import sys
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import unhelpful_percent

file_path = os.path.dirname(__file__)
COMMASPACE = ', '
unhelpful_percent.main()

def main():
    sender = 'lilyli@qnap.com'
    username = 'lilyli@qnap.com'
    password = 'qnaplily07'
    recipients = ['lilyli@qnap.com', 'lily60622@gmail.com']   
    outer = MIMEMultipart()
    outer['Subject'] = 'Top10 unhelpful Tutorial & FAQ'
    outer['To'] = COMMASPACE.join(recipients)
    outer['From'] = sender
    outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'    
    body = """
    Hi,
    
    Here are the top10s of FAQ and Tutorial pages.
    FYI.
    
    Best regards,
    QNAP Marketing.
    """    
    outer.attach(MIMEText(body, 'plain'))     
    
    # List of attachments
    attachments = ['/unhelpful_tutorial.csv', '/unhelpful_faq.csv']

    # Add the attachments to the message
    for file in attachments:
        try:
            with open('%s%s' % (file_path, file), 'rb') as fp:
                msg = MIMEBase('application', "octet-stream")
                msg.set_payload(fp.read())
            encoders.encode_base64(msg)
            msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
            outer.attach(msg)

        except:
            print("Unable to open one of the attachments. Error: ", sys.exc_info()[0])
            raise

    composed = outer.as_string()

    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com:587') as s:
            s.ehlo()
            s.starttls()
            s.login(username,password)
            s.sendmail(sender, recipients, composed)
            s.close()
        print("Email sent!")
    except:
        print("Unable to send the email. Error: ", sys.exc_info()[0])
        raise

if __name__ == '__main__':
    main()