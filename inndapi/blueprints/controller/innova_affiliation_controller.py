from flask import jsonify, request, abort
from flask_restful import Resource
from sqlalchemy import exc

from inndapi.service.error_handler import *
from inndapi.service import InnovaAffiliationService


class InnovaAffiliationController(Resource):
       
    def __init__(self):
        self.service = InnovaAffiliationService()

    def delete(self, id):
        try:
            self.service.delete(id)
            return jsonify(dict({'status': 'ok'}))
        except ResourceDoesNotExist as rdne:
            abort(rdne.code, str(rdne))
        except Exception:
            abort(500, "Erro inesperado")
