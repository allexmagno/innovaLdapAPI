import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from inndapi.enum import MailStatusEnum

# from flask_mail import Message
# from inndapi.ext import mail
class MailService:

    def __init__(self, sender):
        self._message = MIMEMultipart()
        self._sender = sender

    def send(self, subject, recipient, body, subtype='plain'):
        self._message['From'] = self._sender
        self._message['Subject'] = subject

        self._message.attach(MIMEText(body, subtype))
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.ehlo()
                server.starttls()
                server.login(self._sender, 'stibsnriqzrysknm')
                server.sendmail(self._sender, recipient, self._message.as_string())
        except Exception as e:
            logging.log(logging.ERROR, e)
            return MailStatusEnum.FAILED
