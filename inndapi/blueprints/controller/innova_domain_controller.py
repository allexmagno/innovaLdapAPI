from flask import jsonify, request, abort
from flask_restful import Resource
from inndapi.service.error_handler import *

from inndapi.service import InnovaDomainService


class InnovaGatewayController(Resource):

    def __init__(self):
        self.service = InnovaDomainService()

    def get(self):
        try:
            gateways = self.service.find_all()
            return jsonify(
                {"innova_gateway": [gateway.to_dict() for gateway in gateways]}
            )
        except Exception:
            abort(500, "Erro Inesperado")

    def post(self):
        gateway = request.get_json(force=True)
        try:
            res = self.service.save(**gateway)
            return res.to_dict(), 201
        except MissedFields as mf:
            abort(mf.code, str(mf))
        except ResourceDoesNotExist as rdne:
            abort(rdne.code, str(rdne))
        except Exception:
            abort(500, "Erro inesperado")


class InnovaGatewayIdController(Resource):

    def __init__(self):
        self.service = InnovaDomainService()

    def get(self, id):
        try:
            gateway = self.service.find_by_pk(id)
            return jsonify(gateway.to_dict())
        except ResourceDoesNotExist as rdne:
            abort(rdne.code, str(rdne))
        except Exception:
            abort(500, "Erro inesperado")

    def put(self, id):
        gateway = request.get_json(force=True)
        try:
            res = self.service.update(**gateway)
            return res.to_dict(), 200
        except MissedFields as mf:
            abort(mf.code, str(mf))
        except ResourceDoesNotExist as rdne:
            abort(rdne.code, str(rdne))
        except Exception:
            abort(500, "Erro inesperado")

    def delete(self, id):
        try:
            self.service.delete(id)
            return jsonify(dict({'status': 'ok'}))
        except ResourceDoesNotExist as rdne:
            abort(rdne.code, str(rdne))
        except Exception:
            abort(500, "Erro inesperado")