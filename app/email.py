"""
This file contains functions to send emails to users from the openaqi support email.
"""

from flask import current_app
import smtplib
from threading import Thread
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_async_email(app, to, msg):
    """
    Connects to mail server and sends message to given email
    """
    with app.app_context():
        server = smtplib.SMTP_SSL(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT'])
        server.ehlo()
        server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
        fromaddr = current_app.config['MAIL_USERNAME']
        server.sendmail(fromaddr, to, msg.as_string())
        server.quit()



def send_email(to, subject, token):
    """
    Creates message and thread to send an email
    """
    app = current_app._get_current_object()
    msg = MIMEMultipart()

    msg['From'] = current_app.config['MAIL_SENDER']
    msg['To'] = to
    msg['Subject'] = current_app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject
    body =  """ Below is your token for access to OpenAQI's API:
                \n{token}
                \nFor instructions on how to use your API token, visit openaqi.io/api
                \n\nKind Regards,\n\nOpenAQI Support\nsupport@openaqi.io
            """.format(token=token)
    msg.attach(MIMEText(body, 'plain'))
    thr = Thread(target=send_async_email, args=[app, to, msg])
    thr.start()
    return thr

