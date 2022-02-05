from flask import jsonify, request, abort
from flask_restful import Resource
from sqlalchemy import exc

from inndapi.service.error_handler import *
from inndapi.service import InnovaPersonService
from inndapi.service import MailService


class InnovaPersonController(Resource):

    def __init__(self):
        self.service = InnovaPersonService()
        self._mail_service = MailService(sender='ct.allex@gmail.com')

    def get(self):
        try:
            entities = self.service.find_all()
            return jsonify(
                {"innova-person": [entity.to_dict() for entity in entities]}
            )
        except Exception:
            abort(500, "Erro Inesperado")

    def post(self):
        entity = request.get_json(force=True)
        try:
            res = self.service.save(**entity)
            body = f'Conta de {res.email} criada<br>' \
                   f'<a href="http://localhost:5000/api/v1/person/{res.uid}">clique aqui para aprovar</a><br>'
            self._mail_service.send(
                subject='[.INOVA RS] Registro de Contas Federadas',
                recipient='ct.allex@gmail.com',
                body=body,
                subtype='html'
            )
            return res.to_dict(), 201
        except MissedFields as mf:
            abort(mf.code, str(mf))
        except exc.SQLAlchemyError as e:
            print()
            abort(400, str(e.orig))
        except Exception:
            abort(500, "Erro inesperado")


class InnovaPersonIdController(Resource):

    def __init__(self):
        self.service = InnovaPersonService()

    def get(self, uid):
        try:
            entity = self.service.find_by_pk(uid)
            return entity.to_dict()
        except ResourceDoesNotExist as rdne:
            abort(rdne.code, str(rdne))
        except Exception:
            abort(500, "Erro inesperado")

    def put(self, uid):
        entity = request.get_json(force=True)
        try:
            res = self.service.update(**entity)
            return res.to_dict(), 200
        except MissedFields as mf:
            abort(mf.code, str(mf))
        except ResourceDoesNotExist as rdne:
            abort(rdne.code, str(rdne))
        except Exception:
            abort(500, "Erro inesperado")

    def delete(self, uid):
        try:
            self.service.delete(uid)
            return jsonify(dict({'status': 'ok'}))
        except ResourceDoesNotExist as rdne:
            abort(rdne.code, str(rdne))
        except Exception:
            abort(500, "Erro inesperado")
