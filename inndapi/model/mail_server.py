from inndapi.ext.database import db
from sqlalchemy_serializer import SerializerMixin

from inndapi.enum import MailProtocolEnum


class MailServer(db.Model, SerializerMixin):
    __tablename__ = 'mail-server'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address = db.Column(db.String(140), nullable=False)
    server = db.Column(db.String(45), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    protocol = db.Column(
        db.Enum(MailProtocolEnum),
        nullable=False)
    password = db.Column(db.String(140), nullable=False)
    domain = db.Column(db.String(140), db.ForeignKey('innova-domain.id'), nullable=False)

    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def __repr__(self):
        return str(self.__dict__)

    def pk(self):
        return self.id
