from flask import Flask
from app.routes import register_routes
from app.firebase import initialize_firebase
from app.routes import base_blueprint

def create_app():
    app = Flask(__name__)

    # Initialize Firebase
    initialize_firebase(app)

    # Register global routes
    app.register_blueprint(base_blueprint)
    register_routes(app)

    return app
