from inndapi.enum.innova_ldap_sync import InnovaLdapSyncEnum

from inndapi.ext.database import db
from sqlalchemy_serializer import SerializerMixin


class InnovaLdapSync(db.Model, SerializerMixin):
    __tablename__ = 'innova-ldap-sync'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid_innova_person = db.Column(db.String(45), db.ForeignKey('innova-person.uid'), nullable=False)
    status = db.Column(db.Enum(InnovaLdapSyncEnum), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    domain = db.Column(db.String(140), nullable=False)

    def __init__(self, **kwargs):

        self.id = kwargs.get('id')
        self.status = kwargs.get('status')
        self.date = kwargs.get('date')
        self.domain = kwargs.get('domain')
        self.uid_innova_person = kwargs.get('uid_innova_person')

    def pk(self):
        return self.id

    def __repr__(self):
        return str(self.__dict__)
