from inndapi.ext.database import db
from inndapi.ext.serialization import ma
from sqlalchemy_serializer import SerializerMixin


class InnovaPerson(db.Model, SerializerMixin):
    __tablename__ = 'innova-person'
    uid = db.Column(db.String(45), primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    given_name = db.Column(db.String(140))
    surname = db.Column(db.String(140))
    email = db.Column(db.String(140), nullable=False, unique=True)
    cpf = db.Column(db.String(140))
    passport = db.Column(db.String(140))
    password = db.Column(db.String(140))
    domain = db.Column(db.String(140), nullable=False)
    to_update = db.Column(db.JSON)
    affiliations = db.relationship(
        'InnovaAffiliation',
        cascade='all, delete',
    )
    ldap_sync = db.relationship('InnovaLdapSync', uselist=False)

    def __init__(self, **kwargs):

        for mapper in self.map_entry():
            attr = kwargs.get(mapper)
            setattr(self, mapper, attr if attr else '')
        # self.uid = kwargs.get('uid')
        # self.name = kwargs.get('name')
        # self.email = kwargs.get('email')
        # self.password = kwargs.get('password')
        # self.domain = kwargs.get('domain')
        # self.given_name = kwargs.get('given_name')
        # self.surname = kwargs.get('surname')
        # self.cpf = kwargs.get('cpf')
        # self.passport = kwargs.get('passport')
        # self.to_update = kwargs.get('to_update')

    def pk(self):
        return self.uid

    def __repr__(self):
        return str(self.__dict__)

    @staticmethod
    def schema():
        return ['uid', 'name', 'email', 'password', 'domain', 'given_name', 'surname', 'cpf', 'passport']

    def map_entry(self):
        return {
            'objectclass': {
                'map': 'objectclass',
                'value': ['inetOrgPerson', 'person', 'brPerson'],
            },
            'uid': {
                'map': 'uid',
                'value': self.uid
            },
            'domain': {
                'map': '',
                'value': self.domain
            },
            'name': {
                'map': 'cn',
                'value': self.name
            },
            'cpf': {
                'map': 'brPersonCPF',
                'value': self.cpf if self.cpf else ''
            },
            'email': {
                'map': 'mail',
                'value': self.email
            },
            'surname': {
                'map': 'sn',
                'value': self.surname
            },
            'given_name': {
                'map': 'givenName',
                'value': self.given_name if self.given_name else ''
            },
            'passport': {
                'map': 'brPersonPassport',
                'value': self.passport if self.passport else ''
            },
            'password': {
                'map': 'userPassword',
                'value': self.password
            }
        }

    def get_rdn(self):
        return f'uid={self.uid}'

    def get_entry(self, to_save=True) -> list:
        no_map = ['uid', 'domain', 'objectclass']
        entry = []
        for attr, value in self.map_entry().items():
            v = value.get('value')
            if not v: continue
            if isinstance(v, list):
                v = list(map(lambda x: str(x).encode(), v))
            else:
                v = [str(v).encode()]
            if to_save:
                if attr == 'domain': continue
                entry.append(
                    (value.get('map'), v)
                )
            else:
                if attr in no_map: continue
                entry.append(
                    {value.get('map'): v}
                )

        return entry


# https://variable-scope.com/posts/storing-and-verifying-passwords-with-sqlalchemy

class InnovaPersonSchema(ma.Schema):
    class Meta:
        model = InnovaPerson

    @staticmethod
    def schema_list():
        return InnovaPerson.schema()
