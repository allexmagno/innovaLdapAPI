import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from inndapi.enum import MailProtocolEnum

from inndapi.model import MailServer


class MailCore:

    def __init__(self, mail: MailServer):
        self._message = MIMEMultipart()
        self._mail = mail
        self._conn = None

    def __enter__(self):
        try:
            if self._mail.protocol == MailProtocolEnum.TLS:
                self._conn = smtplib.SMTP(self._mail.server, self._mail.port)
                self._conn.ehlo()
                self._conn.starttls()
            else:
                self._conn = smtplib.SMTP_SSL(self._mail.server, self._mail.port)
            return self._conn.login(self._mail.address, self._mail.password)
        except Exception as e:
            raise e

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()

    def send(self, subject, recipient, body, subtype='plain'):
        self._message['From'] = self._mail.address
        self._message['Subject'] = subject

        self._message.attach(MIMEText(body, subtype))
        try:
            self._conn.sendmail(self._mail.address, recipient, self._message.as_string())
        except Exception as e:
            raise e
