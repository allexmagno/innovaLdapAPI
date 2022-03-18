import datetime
import logging
from sqlalchemy import exc

from .abstract_crud import AbstractCrud
from .innova_ldap_sync_service import InnovaLdapSyncService
from .error_handler import *
from inndapi.core import LdapCore, LdapStatus
from inndapi.model import InnovaPerson
from inndapi.model import InnovaAffiliation
from inndapi.model import InnovaLdapSync
from inndapi.enum import InnovaLdapSyncEnum

from .innova_person_service import InnovaPersonService
from inndapi.model import LdapServer


class LdapServerService(AbstractCrud):

    def __init__(self):
        self.sync_service = InnovaLdapSyncService()
        self.entry_service = InnovaPersonService()

    def schema(self):
        pass

    def model(self):
        return LdapServer

    def model_pk(self):
        return LdapServer.id

    def mapper(self, **kwargs):
        return LdapServer(**kwargs)

    def required_fields(self, entity) -> list:
        required = []
        if not entity.domain:
            required.append('domain')

        if not entity.ip:
            required.append('id')

        if not entity.port:
            required.append('port')

        if not entity.base_dn:
            required.append('base_dn')

        if not entity.bind_dn:
            required.append('bind_dn')

        if not entity.bind_credential:
            required.append('bind_credential')

        if not entity.bind_credential:
            required.append('ldap_server_id')

        return required

    def update_entity(self, entity: LdapServer):
        old_ldap_server: LdapServer = self.find_by_pk(entity.id)

        old_ldap_server.domain = self.parser(entity.domain, old_ldap_server.domain)
        old_ldap_server.ip = self.parser(entity.ip, old_ldap_server.ip)
        old_ldap_server.port = self.parser(entity.port, old_ldap_server.port)
        old_ldap_server.base_dn = self.parser(entity.base_dn, old_ldap_server.base_dn)
        old_ldap_server.bind_dn = self.parser(entity.bind_dn, old_ldap_server.bind_dn)
        old_ldap_server.bind_credential = self.parser(entity.bind_credential, old_ldap_server.bind_credential)

        return old_ldap_server

    def sync_entries(self):
        logging.log(logging.INFO, 'Tasks: Start sync entries')

        def run(t_list):
            for t in t_list:
                self.save_entry(entity.id, t.uid)

        servers = self.find_all()
        for entity in servers:
            to_save = self.sync_service.find_all_by_status(InnovaLdapSyncEnum.VALID, entity.domain)
            to_update = self.sync_service.find_all_by_status(InnovaLdapSyncEnum.UPDATE, entity.domain)

            run(to_save)
            run(to_update)

    def save_entry(self, pk: LdapServer.id, uid, is_update=False):

        entity: LdapServer = self.find_by_pk(pk)
        entry = self.entry_service.find_by_pk(uid)

        if not is_update:
            if not entry.ldap_sync.status == InnovaLdapSyncEnum.VALID:
                raise ResourceDoesNotExist(InnovaPerson, entry.uid)

        ldap = LdapCore(
            host=entity.ip,
            port=entity.port,
            base_dn=entity.base_dn,
            bind_dn=entity.bind_dn,
            bind_credential=entity.bind_credential
        )

        ldap.connect()

        with ldap:
            if not is_update:
                res = ldap.save(rdn=entry.get_rdn(), entity=entry)
                for affiliation in entry.affiliations:
                    res = ldap.save(
                        rdn=affiliation.get_rdn()+entry.uid, entity=affiliation)
            else:
                new_entry = InnovaPerson(**entry.to_update)
                res = ldap.modify(entry.get_rdn(), new_entry, entry)

                for affiliation in entry.to_update['affiliations']:
                    new_entry: InnovaAffiliation = InnovaAffiliation(**affiliation)
                    aff_entry = list(filter(lambda x: x.affiliation == new_entry.affiliation, entry.affiliations)).pop()
                    res = ldap.modify(new_entry.get_rdn()+entry.uid, new_entry, aff_entry)

        if res == LdapStatus.SUCCESS:
            sync: InnovaLdapSync = entry.ldap_sync
            sync.status = InnovaLdapSyncEnum.SYNC
            sync.date = datetime.datetime.now()
            self.sync_service.update(entity=sync)

        entry.to_update = None

        return self.entry_service.update(entity=entry, sync=True)

    def sync(self, pk: LdapServer.id):
        entity: LdapServer = self.find_by_pk(pk)
        ldap = LdapCore(
            host=entity.ip,
            port=entity.port,
            base_dn=entity.base_dn,
            bind_dn=entity.bind_dn,
            bind_credential=entity.bind_credential
        )

        ldap.connect()
        with ldap:
            res = dict(ldap.search(sub=False))
            ldap_format = {}
            for key, value in res.items():
                ldap_format.update(
                    {key: [v.decode("utf-8") if not isinstance(type(v), str.__class__) else v for v in value]}
                )

            keys = ldap_format.keys()

        people = []
        sync_errors = []
        for base in keys:
            new_entity = False
            uid = base.split(',').pop(0).split('=').pop(1)
            try:
                person = self.entry_service.find_by_pk(pk=uid)
            except ResourceDoesNotExist:
                logging.log(logging.INFO, f'A new person has been found: {uid}')
                person = None
            if not person:
                person = InnovaPerson(uid=uid, domain=entity.domain)
                new_entity = True

            new_person = self.process_data(ldap=ldap, person=person, search_dn="(uid:dn:=" + uid + ")")

            if new_entity:
                sync = InnovaLdapSync(
                    status=InnovaLdapSyncEnum.SYNC,
                    date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    domain=entity.domain
                )
                new_person.ldap_sync = sync
                try:
                    sync_person = self.entry_service.save(entity=new_person, from_ldap=True)
                    people.append(sync_person.to_dict())
                except exc.SQLAlchemyError as e:
                    error = str(e.orig)
                    error = error.split(',') \
                        .pop(1) \
                        .replace(" \"", "") \
                        .replace("\"", "") \
                        .replace(")", "")
                    logging.log(logging.ERROR, str(e.orig))
                    sync_errors.append(
                        {
                            'base_dn': base,
                            'detail': error
                        }
                    )
                    logging.log(logging.WARN, f'Can\'t sync {base}')
            else:
                sync: InnovaLdapSync = person.ldap_sync
                sync.status = InnovaLdapSyncEnum.SYNC
                sync.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                try:
                    self.sync_service.update(entity=sync)
                    sync_person = self.entry_service.update(entity=new_person, from_ldap=True)
                    people.append(sync_person.to_dict())
                except Exception:
                    sync_errors.append({'base_dn': base})
                    logging.log(logging.WARN, f'Can\'t update sync {base}')
        people.append(dict({'errors': sync_errors}))
        return {"innova-person": people}

    def sync_entity(self, pk: LdapServer.id, uid: InnovaPerson.uid):

        entity: LdapServer = self.find_by_pk(pk)
        person: InnovaPerson = self.entry_service.find_by_pk(uid)

        if not person.ldap_sync.status == InnovaLdapSyncEnum.SYNC \
                and not person.ldap_sync.status == InnovaLdapSyncEnum.UPDATE:
            raise ResourceDoesNotExist(InnovaPerson, person.uid)

        ldap = LdapCore(
            host=entity.ip,
            port=entity.port,
            base_dn=entity.base_dn,
            bind_dn=entity.bind_dn,
            bind_credential=entity.bind_credential
        )

        new_person = self.process_data(ldap=ldap, person=person)
        new_person.to_update = None

        sync: InnovaLdapSync = person.ldap_sync
        sync.status = InnovaLdapSyncEnum.SYNC
        sync.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sync_service.update(entity=sync)

        return self.entry_service.update(entity=new_person, from_ldap=True)

    @staticmethod
    def process_data(ldap: LdapCore, person: InnovaPerson, search_dn: str = None):

        def parse_attr(attr_list, obj_list):
            attrs = {}
            for attr in attr_list:
                attrs.update(
                    {attr: ','.join(v.decode("utf-8") for v in obj_list.get(attr))}
                )
            return attrs

        if not search_dn:
            search_dn = "(uid:dn:=" + person.uid + ")"

        ldap.connect()
        with ldap:
            res = dict(ldap.search(search_dn))
            ldap_format = {}
            for key, value in res.items():
                ldap_format.update(
                    {key: [v.decode("utf-8") if not isinstance(type(v), str.__class__) else v for v in value]}
                )

            keys = ldap_format.keys()
            new_person = InnovaPerson(domain=person.domain, uid=person.uid)
            for key in keys:
                innova_class, innova_value = key.split(',')[0].split('=')
                if 'uid' in innova_class:
                    new_person.uid = innova_value

                    attrs = parse_attr(ldap_format.get(key), res.get(key))
                    new_person.name = attrs.get('cn')
                    new_person.surname = attrs.get('sn')
                    new_person.given_name = attrs.get('givenName')
                    new_person.email = attrs.get('mail')
                    new_person.password = attrs.get('userPassword')
                    new_person.cpf = attrs.get('brCpf')
                    new_person.passport = attrs.get('brPassport')

                elif 'innovaAffiliation' in innova_class:
                    affiliation = InnovaAffiliation(uid_innova_person=person.uid)
                    affiliation.affiliation = int(innova_value)
                    pk_value = list(filter(lambda x: x.affiliation == affiliation.affiliation, person.affiliations))
                    if pk_value:
                        affiliation.id = pk_value.pop().id
                    attrs = parse_attr(ldap_format.get(key), res.get(key))
                    affiliation.organization = attrs.get('innovaOrganization')
                    affiliation.type = attrs.get('innovaAffiliationType')
                    affiliation.subtype = attrs.get('innovaAffiliationSubType')
                    affiliation.role = attrs.get('innovaAffiliationRole')
                    affiliation.entrance = attrs.get('brEntranceDate')
                    affiliation.exit = attrs.get('brExitDate')

                    new_person.affiliations.append(affiliation)

        return new_person
