from flask import Blueprint
from flask_restful import Api
from .innova_person_controller import InnovaPersonController, InnovaPersonIdController
from .innova_gateway_controller import InnovaGatewayController, InnovaGatewayIdController
from .innova_ldap_server_controller import InnovaLdapServeController, InnovaLdapServerIdController
from .innova_ldap_sync_controller import InnovaLdapSyncController, InnovaLdapSyncIdController

bp = Blueprint("controller-api", __name__, url_prefix="/api/v1")


api = Api(bp, catch_all_404s=True)


def init_app(app):
    api.add_resource(InnovaPersonController, "/person")
    api.add_resource(InnovaPersonIdController, "/person/<uid>")

    api.add_resource(InnovaGatewayController, "/gateway")
    api.add_resource(InnovaGatewayIdController, "/gateway/<id>")

    api.add_resource(InnovaLdapServeController, "/service")
    api.add_resource(InnovaLdapServerIdController, "/service/<id>")

    api.add_resource(InnovaLdapSyncController, "/innova-ldap")
    api.add_resource(InnovaLdapSyncIdController, "/innova-ldap/<id>")

    app.register_blueprint(bp)
