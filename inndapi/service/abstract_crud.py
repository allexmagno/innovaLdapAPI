from abc import ABC, abstractmethod
from inndapi.ext.database import db
from inndapi.enum import InnovaLdapSyncEnum

from .error_handler import *


class AbstractCrud(ABC):
    """
    class abstrada de crud
    """

    @abstractmethod
    def schema(self):
        pass

    @abstractmethod
    def model(self):
        """
        método abstrado para capturar model a ser trabalhado
        :return model
        """
        raise NotImplementedError

    @abstractmethod
    def model_pk(self):
        """
        método abstrado para capturar a chave privada do model
        :return Model.pk
        """
        raise NotImplementedError

    def sync_s(self, sync: InnovaLdapSyncEnum):
        """método para configurar o modo de atualização de dados"""
        pass

    def fill_pk(self, entity):
        """Verifica se o objeto tem a PK"""
        return entity.pk() is not None

    @abstractmethod
    def mapper(self, **kwargs):
        """
        classe abstrada para transformar dict em instancia de objeto
        :return: entity
        """
        raise NotImplementedError

    @abstractmethod
    def update_entity(self, entity):
        raise NotImplementedError

    def required_fields(self, entity) -> list:
        """
        Obtém os campos obrigatórios de uma entidade
        :param entity:
        :return: list
        """
        return []

    def child_service(self):
        return None

    def child_model(self):
        return None

    def find_all(self):
        """
        Obtém todas entidades do banco
        :return:
        """
        return self.model().query.all()

    def find_by_pk(self, pk):
        """
        obtém uma entidade via chave primária
        :param pk:
        :return: entity
        """
        entity = self.model().query.get(pk)
        if not entity:
            raise ResourceDoesNotExist(self.model(), pk)
        return entity

    def save(self, **kwargs) -> dict:
        """
        insere uma entidade no banco de dados
        :param kwargs:
        :return: dict
        """
        self.sync_s(InnovaLdapSyncEnum.PENDING)
        entity = kwargs.get('entity')
        if not entity:
            entity = self.mapper(**kwargs)

        required = self.required_fields(entity)
        if required:
            raise MissedFields(self.model(), required)

        try:
            db.session.add(entity)
            db.session.commit()
            return entity
        except Exception as e:
            db.session.rollback()
            raise e

    def update(self, **kwargs):
        """
        Atualiza uma entidade
        :return: entity
        """
        entity = kwargs.get('entity')
        sync = kwargs.get('sync')
        if sync:
            self.sync_s(InnovaLdapSyncEnum.SYNC)
        else:
            self.sync_s(InnovaLdapSyncEnum.UPDATE)

        if not entity:
            entity = self.mapper(**kwargs)
        if not self.fill_pk(entity):
            raise MissedFields(self.model(), 'primary key')

        required = self.required_fields(entity)
        if required:
            raise MissedFields(self.model(), required)

        try:
            entity = self.update_entity(entity)
            db.session.commit()
            return entity
        except Exception as e:
            db.session.rollback()
            raise e
        
    def update_children(self, old_children: list, new_children: list):

        children = []
        to_update = new_children

        if len(old_children) > len(new_children):
            to_remove = set(old_children) - set(new_children)
            for child in to_remove:
                self.child_service().delete(child.pk())
            to_update = list(set(old_children) - set(to_remove))
            children = to_update

        elif len(old_children) < len(new_children):
            to_append = list(filter(lambda x: not self.fill_pk(x), new_children))
            for child in to_append:
                self.child_service().save(entity=child)
            to_update = list(filter(lambda x: self.fill_pk(x), new_children))

        updated_children = []
        for child in to_update:
            if self.fill_pk(child):
                updated_children.append(self.child_service().update(entity=child))
            else:
                raise MissedFields(self.child_model(), 'primary key')

        return children + updated_children

    def delete(self, pk):
        """
        Remove uma entidade do banco de dados
        :param pk:
        """
        try:
            self.model().query.filter(self.model_pk() == pk).delete()
            db.session.commit()
            db.session.commit()
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def parser(new_attr, old_attr):
        """
        Método auxiliar para atualizar um objeto e manter os dados antigos
        caso algum campo não obrigatório seja omitido
        :param new_attr: valor do novo atributo
        :param old_attr: valor do antigo atributo
        :return: attr
        """
        return new_attr if new_attr else old_attr
