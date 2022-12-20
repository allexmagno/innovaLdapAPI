from inndapi.enum.innova_affiliation import InnovaAffiliationTypeEnum
from inndapi.enum.innova_affiliation import InnovaAffiliationSubTypeEnum

from inndapi.ext.database import db
from inndapi.ext.serialization import ma
from sqlalchemy_serializer import SerializerMixin


class InnovaAffiliation(db.Model, SerializerMixin):
    __tablename__ = 'innova-affiliation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    affiliation = db.Column(db.Integer, nullable=False)
    organization = db.Column(db.String(140), nullable=False)
    type = db.Column(
        db.Enum(InnovaAffiliationTypeEnum),
        nullable=False)
    subtype = db.Column(
        db.Enum(InnovaAffiliationSubTypeEnum),
        nullable=False)
    role = db.Column(db.String(140))
    entrance = db.Column(db.Date, nullable=False)
    exit = db.Column(db.Date)
    uid_innova_person = db.Column(db.String(45), db.ForeignKey('innova-person.uid', ondelete='CASCADE'), nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.affiliation = kwargs.get('affiliation')
        self.organization = kwargs.get('organization')
        self.type = kwargs.get('type')
        self.subtype = kwargs.get('subtype')
        self.role = kwargs.get('role')
        self.entrance = kwargs.get('entrance')
        self.exit = kwargs.get('exit')
        self.uid_innova_person = kwargs.get('uid_innova_person')

    def pk(self):
        return self.id

    @staticmethod
    def schema():
        return ['id', 'affiliation', 'organization', 'type', 'subtype', 'role', 'entrance', 'exit']

    def map_entry(self):
        if not self.exit:
            exit_value = ''
        elif not isinstance(self.entrance, str):
            exit_value = self.exit.strftime("%Y%m%d") 
        else:
             exit_value = self.entrance.replace('-','')

        return {
            'objectclass': {
                'map': 'objectclass',
                'value': ['innovaPerson']
            },
            'affiliation': {
                'map': 'innovaAffiliation',
                'value': self.affiliation
            },
            'organization': {
                'map': 'innovaOrganization',
                'value': self.organization
            },
            'role': {
                'map': 'innovaAffiliationRole',
                'value': self.role if self.role else ''
            },
            'type': {
                'map': 'innovaAffiliationType',
                'value': self.type.name
            },
            'subtype': {
                'map': 'innovaAffiliationSubType',
                'value': self.subtype.name
            },
            'entrance': {
                'map': 'brentr',
                'value': self.entrance.strftime("%Y%m%d") if not isinstance(self.entrance, str) else self.entrance.replace('-','')
            },
            'exit': {
                'map': 'brexit',
                'value': exit_value
            }
        }

    def get_entry(self, to_save=True) -> list:
        no_map = ['objectclass']
        entry = []
        for attr, value in self.map_entry().items():
            v = value.get('value')
            if not v: continue
            if isinstance(v, list):
                v = list(map(lambda x: str(x).encode(), v))
            else:
                v = [str(v).encode()]
            if to_save:
                entry.append(
                    (value.get('map'), v)
                )
            else:
                if attr in no_map: continue
                entry.append(
                    {value.get('map'): v}
                )

        return entry

    def get_rdn(self):
        return f'innovaAffiliation={self.affiliation},uid='

    def __lt__(self, other):
        return (isinstance(other, self.__class__) and
                getattr(other, 'affiliation', None) < self.affiliation)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                getattr(other, 'affiliation', None) == self.affiliation)

    def __hash__(self):
        return hash(self.affiliation)

    def __repr__(self):
        return str(self.__dict__)


class InnovaAffiliationSchema(ma.Schema):
    class Meta:
        model = InnovaAffiliation

    @staticmethod
    def schema_list():
        return InnovaAffiliation.schema()
