from flask import jsonify, request, abort
from flask_restful import Resource
from sqlalchemy import exc

from inndapi.service.error_handler import *
from inndapi.service import InnovaPersonService
from inndapi.service import InnovaDomainService


class InnovaPersonController(Resource):

    def __init__(self):
        self.service = InnovaPersonService()
        self.domain_service = InnovaDomainService()

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
            self.domain_service.send_mail_create(res)
            return res.to_dict(), 201
        except MissedFields as mf:
            abort(mf.code, str(mf))
        except exc.SQLAlchemyError as e:
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


