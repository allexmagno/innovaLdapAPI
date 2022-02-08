import datetime
import bcrypt
from .abstract_crud import AbstractCrud

from inndapi.enum import InnovaLdapSyncEnum
from .innova_affiliation_service import InnovaAffiliationService
from inndapi.model import InnovaPerson, InnovaPersonSchema
from inndapi.model import InnovaAffiliation
from inndapi.model import InnovaLdapSync


class InnovaPersonService(AbstractCrud):

    def __init__(self):
        self._affiliation_service = InnovaAffiliationService()
        self._schema = InnovaPersonSchema()
        self._sync = InnovaLdapSyncEnum.UPDATE

    @property
    def schema(self):
        return self._schema

    def sync_s(self, sync):
        self._sync = sync

    def model(self):
        return InnovaPerson

    def mapper(self, **kwargs):
        person = InnovaPerson(**kwargs)
        person.affiliations = list(map(lambda x: InnovaAffiliation(**x), kwargs.get('affiliations')))

        return person

    def model_pk(self):
        return InnovaPerson.uid

    def child_service(self):
        return self._affiliation_service

    def child_model(self):
        return InnovaAffiliation

    def required_fields(self, entity) -> dict:
        required = []
        if not entity.uid:
            required.append('uid')

        if not entity.domain:
            required.append('domain')

        if not entity.email:
            required.append('email')

        if not entity.password:
            required.append('password')

        return required

    def update_entity(self, entity):
        old_person: InnovaPerson = self.find_by_pk(entity.uid)
        old_person.ldap_sync.status = self._sync

        if not old_person.to_update and self._sync is InnovaLdapSyncEnum.UPDATE:
            old_person.to_update = old_person.to_dict()
            old_person.to_update['to_update'] = {}

        old_person.name = self.parser(entity.name, old_person.name)
        old_person.given_name = self.parser(entity.given_name, old_person.given_name)
        old_person.surname = self.parser(entity.surname, old_person.surname)
        old_person.email = self.parser(entity.address, old_person.email)
        old_person.domain = self.parser(entity.domain, old_person.domain)
        old_person.cpf = self.parser(entity.cpf, old_person.cpf)
        old_person.passport = self.parser(entity.passport, old_person.passport)

        old_affiliations = old_person.affiliations
        new_affiliations = entity.affiliations
        old_person.affiliations = self.update_children(
                                    old_children=old_affiliations,
                                    new_children=new_affiliations
                                )

        return old_person

    def save(self, **kwargs) -> dict:
        entity = kwargs.get('entity')
        if not entity:
            entity = self.mapper(**kwargs)

        if not kwargs.get('from_ldap'):
            salt = bcrypt.gensalt()
            entity.password = "{CRYPT}" + bcrypt.hashpw(entity.password.encode(), salt).decode()

            c1 = ''.join(list(filter(lambda x: x.isalnum(), entity.name)))
            h1 = str(hash(entity.email.encode()))

            x, y = h1[-2:]
            x = int(x)
            y = int(y)

            if x > y:
                x1 = y
                y = x
                x = x1
            entity.uid = c1 + h1[x:y]

            sync = InnovaLdapSync(
                status=InnovaLdapSyncEnum.PENDING,
                date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                domain=kwargs.get('domain')
            )
            entity.ldap_sync = sync
        return super().save(entity=entity)
