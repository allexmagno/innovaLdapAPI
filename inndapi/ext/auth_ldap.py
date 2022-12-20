from flask_ldap3_login import LDAP3LoginManager

ldap_manager = LDAP3LoginManager()

def init_app(app):
    ldap_manager.init_app(app=app)