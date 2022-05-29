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

    def update_entity(self, entity):
        old_mail: MailServer = self.find_by_pk(entity.id)

        old_mail.address = self.parser(entity.address, old_mail.address)
        old_mail.server = self.parser(entity.server, old_mail.server)
        old_mail.port = self.parser(entity.port, old_mail.port)
        old_mail.protocol = self.parser(entity.protocol, old_mail.protocol)
        old_mail.password = self.parser(entity.password, old_mail.password)
        old_mail.domain = self.parser(entity.domain, old_mail.domain)
   
        return old_mail