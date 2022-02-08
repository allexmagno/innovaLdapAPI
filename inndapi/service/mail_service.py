from .abstract_crud import AbstractCrud
from inndapi.model import MailServer


class MailService(AbstractCrud):

    def __init__(self):
        pass

    def schema(self):
        pass

    def model(self):
        return MailServer

    def model_pk(self):
        return MailServer.id

    def mapper(self, **kwargs):
        return MailServer(**kwargs)

    def update_entity(self, entity):
        pass