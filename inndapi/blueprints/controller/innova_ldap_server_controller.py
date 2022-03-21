from flask import jsonify, request, abort
from flask_restful import Resource, reqparse
from sqlalchemy import exc

from inndapi.service.error_handler import *
from inndapi.service import LdapServerService


class InnovaLdapServeController(Resource):

    def __init__(self):
        self.service = LdapServerService()

    def get(self):
        try:
            entities = self.service.find_all()
            return jsonify(
                [entity.to_dict() for entity in entities]
            )
        except Exception:
            abort(500, "Erro Inesperado")

    def post(self):
        entity = request.get_json(force=True)
        try:
            res = self.service.save(**entity)
            return res.to_dict(), 201
        except MissedFields as mf:
            abort(mf.code, str(mf))
        except exc.SQLAlchemyError as e:
            abort(400, "duplicado")
        except Exception:
            abort(500, "Erro inesperado")


class InnovaLdapServerIdController(Resource):

    def __init__(self):
        self.service = LdapServerService()

    def get(self, id):
        try:
            entity = self.service.find_by_pk(id)
            return jsonify(entity.to_dict())
        except ResourceDoesNotExist as rdne:
            abort(rdne.code, str(rdne))
        except Exception:
            abort(500, "Erro inesperado")

    def put(self, id):
        if not id:
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
        else:
            parser = reqparse.RequestParser()
            parser.add_argument('service', location='args')
            parser.add_argument('uid', location='args')
            args = parser.parse_args()

            service = args.get('service')

            if service == 'sync-entity':
                uid = args.get('uid')
                try:
                    entity = self.service.sync_entity(pk=id, uid=uid)
                except ResourceDoesNotExist as rdne:
                    abort(rdne.code, str(rdne) + " on LDAP Server")
                except ResourceDoesNotExist as rdne:
                    abort(rdne.code, str(rdne))
                except Exception:
                    abort(500, 'Erro Inesperado')

            elif service == 'sync':
                try:
                    entity = self.service.sync(pk=id)
                    return entity, 200
                except Exception as e:
                    abort(500, str(e))

            elif service == 'save':
                uid = args.get('uid')
                try:
                    entity = self.service.save_entry(pk=id, uid=uid, is_update=False)
                except ResourceDoesNotExist as rdne:
                    abort(rdne.code, str(rdne))
                except Exception:
                    abort(500, 'Erro Inesperado')

            elif service == 'update':
                uid = args.get('uid')
                try:
                    entity = self.service.save_entry(pk=id, uid=uid, is_update=True)
                except ResourceDoesNotExist as rdne:
                    abort(rdne.code, str(rdne))
                except Exception:
                    abort(500, 'Erro Inesperado')
            return jsonify(entity.to_dict())


    def delete(self, id):
        try:
            self.service.delete(id)
            return jsonify(dict({'status': 'ok'}))
        except ResourceDoesNotExist as rdne:
            abort(rdne.code, str(rdne))
        except Exception:
            abort(500, "Erro inesperado")

class InnovaLdapServerUserController(Resource):

    def __init__(self):
        self.service = LdapServerService()

    def put(self, id):
        person = request.get_json(force=True)
        try:
            res = self.service.change_password(pk=id, **person)
            return jsonify(res.to_dict())
        except InvalidPassword as ip:
            abort(ip.code, str(ip))
        except Exception:
            abort(500, "Erro inesperado")

