from enum import Enum


class MailProtocolEnum(Enum):
    SSL = 'ssl'
    TLS = 'tls'


class MailStatusEnum(Enum):

    SUCCESS = 'success'
    FAILED = 'failed'