from inndapi.model import InnovaAffiliation
from .abstract_crud import AbstractCrud


class InnovaAffiliationService(AbstractCrud):

    def __init__(self):
        pass

    def schema(self):
        pass

    def model(self):
        return InnovaAffiliation

    def mapper(self, **kwargs):
        return InnovaAffiliation(**kwargs)

    def model_pk(self):
        return InnovaAffiliation.id

    def required_fields(self, entity) -> list:
        required = []
        if not entity.affiliation:
            required.append('affiliation')

        if not entity.organization:
            required.append('organization')

        if not entity.entrance:
            required.append('entrance')

        return required

    def update_entity(self, entity):
        old_affiliation = self.find_by_pk(entity.id)
        old_affiliation.affiliation = self.parser(entity.affiliation, old_affiliation.affiliation)
        old_affiliation.organization = self.parser(entity.organization, old_affiliation.organization)
        old_affiliation.type = self.parser(entity.type, old_affiliation.type)
        old_affiliation.subtype = self.parser(entity.subtype, old_affiliation.subtype)
        old_affiliation.role = self.parser(entity.role, old_affiliation.role)
        old_affiliation.entrance = self.parser(entity.entrance, old_affiliation.entrance)
        old_affiliation.exit = self.parser(entity.exit, old_affiliation.exit)

        return old_affiliation
