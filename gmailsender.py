#!/usr/bin/env python3

'''
Sends e-mail via gmail via smtp lib
'''

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from multiprocessing import Process

class Gmailsender():
    def __init__(self, gmail_email, gmail_password, from_name=None, from_email=None, debug=False):
        self._gmail_email = gmail_email
        self._gmail_password = gmail_password
        self._from_name = from_name if from_name else gmail_email
        self._from_email = from_email if from_email else gmail_email
        self._debug = debug

    def send_email(self, subject, text, recipients):
        '''
        sends an email via gmail, with provided subject, text, to the recipients
        '''
        if self._debug:
            print("mail:")
            print("subject: %s" % subject)
            print("content: %s" % text)
            print("to: %s" % recipients)
            return

        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = formataddr((str(Header(self._from_name, 'utf-8')), self._from_email))
        message['Reply-To'] = formataddr((str(Header(self._from_name, 'utf-8')), self._from_email))
        message['To'] = ", ".join(recipients)
        mimeText = MIMEText(text, 'plain')
        message.attach(mimeText)

        mailServer = smtplib.SMTP('smtp.gmail.com', 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(self._gmail_email, self._gmail_password) 

        mailServer.sendmail(self._from_email, recipients, message.as_string())
        mailServer.quit()


    def send_email_async(self, subject, text, recipients):
        '''
        Sends an e-mail via gmail, asynchronously, with provided subject, text, to the recipients
        '''
        p = Process(target=self.send_email, args=(subject, text, recipients,))
        p.start()
