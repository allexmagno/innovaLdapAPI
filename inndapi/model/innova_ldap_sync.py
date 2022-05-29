from inndapi.enum.innova_ldap_sync import InnovaLdapSyncEnum

from inndapi.ext.database import db
from sqlalchemy_serializer import SerializerMixin


class InnovaLdapSync(db.Model, SerializerMixin):
    __tablename__ = 'innova-ldap-sync'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid_innova_person = db.Column(db.String(45), db.ForeignKey('innova-person.uid'), nullable=False)
    status = db.Column(db.Enum(InnovaLdapSyncEnum), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    domain = db.Column(db.String(140))

    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value if value else '')

    def pk(self):
        return self.id

    def __repr__(self):
        return str(self.__dict__)
