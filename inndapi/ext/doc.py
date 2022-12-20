from flasgger import Swagger

swagger = Swagger()
def init_app(app):
    swagger.init_app(app=app)