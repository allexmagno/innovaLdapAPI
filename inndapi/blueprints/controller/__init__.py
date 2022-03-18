from flask import Blueprint
from flask_restful import Api
from .innova_person_controller import InnovaPersonController, InnovaPersonIdController, InnovaPersonUserController
from .innova_domain_controller import InnovaGatewayController, InnovaGatewayIdController
from .innova_ldap_server_controller import InnovaLdapServeController, InnovaLdapServerIdController
from .innova_ldap_sync_controller import InnovaLdapSyncController, InnovaLdapSyncIdController
from .mail_server_controller import MailServerController, MailServerIdController

bp = Blueprint("controller-api", __name__, url_prefix="/api/v1")


api = Api(bp, catch_all_404s=True)


def init_app(app):

    """Innova Person Route"""
    api.add_resource(InnovaPersonController, "/person")
    api.add_resource(InnovaPersonIdController, "/person/<uid>")
    api.add_resource(InnovaPersonUserController, "/person/user/<uid>")

    """Domain Route"""
    api.add_resource(InnovaGatewayController, "/domain")
    api.add_resource(InnovaGatewayIdController, "/domain/<id>")

    """Service Ldap Route"""
    api.add_resource(InnovaLdapServeController, "/service")
    api.add_resource(InnovaLdapServerIdController, "/service/<id>")

    """Sync Ldap Route"""
    api.add_resource(InnovaLdapSyncController, "/innova-ldap")
    api.add_resource(InnovaLdapSyncIdController, "/innova-ldap/<id>")

    """Mail Server Route"""
    api.add_resource(MailServerController, "/mail-server")
    api.add_resource(MailServerIdController, "/mail-server/<id>")

    app.register_blueprint(bp)
