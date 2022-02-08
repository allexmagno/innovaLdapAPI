from inndapi.ext.database import db
from sqlalchemy_serializer import SerializerMixin


class InnovaDomain(db.Model, SerializerMixin):
    __tablename__ = 'innova-domain'
    id = db.Column(db.String(140), primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    ldap_servers = db.relationship(
        'LdapServer'
    )
    mail_server = db.relationship('MailServer', uselist=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.domain = kwargs.get('domain')

    def __repr__(self):
        return str(self.__dict__)

    def pk(self):
        return self.id
