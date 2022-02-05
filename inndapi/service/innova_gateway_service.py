from inndapi.ext.database import db
from .abstract_crud import AbstractCrud
from inndapi.model import LdapServer
from inndapi.service import LdapServerService

from inndapi.model import InnovaGateway


class InnovaGatewayService(AbstractCrud):

    def __init__(self):
        self._db = db
        self._innova_gateway = InnovaGateway
        self._ldap_server_service = LdapServerService()

    def schema(self):
        pass

    def model(self):
        return self._innova_gateway

    def model_pk(self):
        return InnovaGateway.id

    def db(self):
        return self._db

    def mapper(self, **kwargs):
        innova_gateway = InnovaGateway(**kwargs)
        innova_gateway.ldap_servers = list(map(lambda x: LdapServer(**x), kwargs.get('ldap_servers')))
        return innova_gateway

    def child_service(self):
        return self._ldap_server_service

    def update_entity(self, entity):
        old_gateway = self.find_by_pk(entity.id)
        old_gateway.name = self.parser(entity.name, old_gateway.name)
        old_gateway.domain = self.parser(entity.domain, old_gateway.domain)

        old_ldap_servers = old_gateway.ldap_servers
        new_ldap_servers = entity.ldap_servers
        self.update_children(
            old_children=old_ldap_servers,
            new_children=new_ldap_servers
        )

        return old_gateway

