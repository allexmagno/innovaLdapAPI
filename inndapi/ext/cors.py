from flask_cors import CORS

cors = CORS(resources={r"/api/*": {"origins": "*"}})
def init_app(app):
    cors.init_app(app=app)