from inndapi.ext.database import db
from sqlalchemy_serializer import SerializerMixin


class InnovaGateway(db.Model, SerializerMixin):
    __tablename__ = 'innova-gateway'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(140), nullable=False)
    domain = db.Column(db.String(140), nullable=False)
    ldap_servers = db.relationship(
        'LdapServer'
    )

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.domain = kwargs.get('domain')

    def __repr__(self):
        return str(self.__dict__)

    def pk(self):
        return self.id
