import datetime

from .abstract_crud import AbstractCrud
from inndapi.enum import InnovaLdapSyncEnum
from sqlalchemy import and_
from inndapi.model import InnovaLdapSync


class InnovaLdapSyncService(AbstractCrud):

    def __init__(self):
        pass

    def schema(self):
        pass

    def model(self):
        return InnovaLdapSync

    def model_pk(self):
        return InnovaLdapSync.id

    def mapper(self, **kwargs):
        return InnovaLdapSync(**kwargs)

    def required_fields(self, entity: InnovaLdapSync) -> list:
        required = []

        if not entity.status:
            required.append('status')

        if not entity.date:
            required.append('date')

        if not entity.uid_innova_person:
            required.append('uid_innova_person')

        return required

    def update_entity(self, entity: InnovaLdapSync):
        old_sync: InnovaLdapSync = self.find_by_pk(entity.id)

        old_sync.date = self.parser(entity.date, old_sync.date)
        old_sync.status = self.parser(entity.status, old_sync.status)

        return old_sync

    def find_all_by_status(self, status: InnovaLdapSyncEnum, domain):
        return self.model().query.filter(
            and_(
                InnovaLdapSync.status == status,
                InnovaLdapSync.domain == domain)
        ).all()

    def find_all_by_date(self, date):
        date = datetime.datetime.strptime(date, '%Y-%m-%d')

        start_of_day = datetime.datetime(date.year, date.month, date.day)
        end_of_day = datetime.datetime(date.year, date.month, date.day, 23, 59, 59)

        return self.model().query.filter(
            self.model().date >= start_of_day,
            self.model().date <= end_of_day
        ).all()
