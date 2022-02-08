from inndapi.ext.database import db
from .abstract_crud import AbstractCrud
from inndapi.model import LdapServer
from inndapi.model import InnovaPerson
from inndapi.service import LdapServerService
from inndapi.core import MailCore

from inndapi.model import InnovaDomain


class InnovaDomainService(AbstractCrud):

    def __init__(self):
        self._db = db
        self._innova_domain = InnovaDomain
        self._ldap_server_service = LdapServerService()

    def schema(self):
        pass

    def model(self):
        return self._innova_domain

    def model_pk(self):
        return InnovaDomain.id

    def mapper(self, **kwargs):
        domain = InnovaDomain(**kwargs)
        domain.ldap_servers = list(map(lambda x: LdapServer(**x), kwargs.get('ldap_servers')))
        return domain

    def child_service(self):
        return self._ldap_server_service

    def update_entity(self, entity):
        old_domain = self.find_by_pk(entity.id)
        old_domain.name = self.parser(entity.name, old_domain.name)
        old_domain.domain = self.parser(entity.domain, old_domain.domain)

        old_ldap_servers = old_domain.ldap_servers
        new_ldap_servers = entity.ldap_servers
        self.update_children(
            old_children=old_ldap_servers,
            new_children=new_ldap_servers
        )

        return old_domain

    def send_mail_create(self, person: InnovaPerson):
        domain: InnovaDomain = self.find_by_pk(person.domain)
        mail = MailCore(domain.mail_server)

        file = open('inndapi/static/mail.html')
        body = ''
        for line in file:
            a = line.replace('_INPNAME_', person.name + " " + person.surname)
            b = a.replace('_EMAIL_', person.email)
            c = b.replace("_PERSON_UID", person.uid)
            body += c
        file.close()

        with mail:
            mail.send(
                subject='[.INOVA RS] Registro de Contas Federadas',
                recipient=domain.mail_server.address,
                body=body,
                subtype='html'
            )
