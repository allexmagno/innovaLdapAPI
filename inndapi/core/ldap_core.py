import ast
from ldap import modlist, initialize, LDAPError, SCOPE_SUBTREE, SCOPE_ONELEVEL, OPT_REFERRALS
from .enum import *


class LdapCore:

    def __init__(self, host: str, port: int, base_dn: str, bind_dn: str, bind_credential: str):
        self.host = host
        self.port = port
        self.base_dn = base_dn
        self.bind_dn = bind_dn
        self.bind_credential = bind_credential
        self.__connection = None

    def connect(self):
        self.__connection = initialize(f'ldap://{self.host}:{self.port}')
        self.__connection.set_option(OPT_REFERRALS, 0)

    def bind(self):
        self.__connection.simple_bind_s(self.bind_dn, self.bind_credential)

    def save(self, rdn, entity):

        entry = entity.get_entry(to_save=True)

        try:
            self.__connection.add_s(self.entity_dn(rdn), entry)
            return LdapStatus.SUCCESS
        except LDAPError as e:
            raise e
        except Exception as e:
            raise e

    def search(self, search_filter=None, sub=True):
        if sub:
            scope = SCOPE_SUBTREE
        else:
            scope = SCOPE_ONELEVEL
        return self.__connection.search_s(self.base_dn, scope, search_filter)

    def modify(self, rdn, old_entity, new_entity):

        try:
            old_entry = old_entity.get_entry(to_save=False)
            new_entry = new_entity.get_entry(to_save=False)

            for i in range(len(old_entry)):
                ldif = modlist.modifyModlist(old_entry[i], new_entry[i])
                self.__connection.modify_s(self.entity_dn(rdn), ldif)
            return LdapStatus.SUCCESS
        except LDAPError as e:
            return ast.literal_eval(str(e))['desc']

    def delete(self, entity):
        '''TODO: criar medodo para deletar usuarios'''
        pass

    def entity_dn(self, rdn):
        return f'{rdn},' + self.base_dn

    def __enter__(self):
        return self.bind()

    def __exit__(self, *args, **kwargs):
        self.__connection.unbind_s()
