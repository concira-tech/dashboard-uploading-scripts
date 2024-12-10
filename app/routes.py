from flask import Blueprint, jsonify
from app.services.room_service import room_service_blueprint

def register_routes(app):
    """Register all service routes."""
    app.register_blueprint(room_service_blueprint, url_prefix='/room-service')

# Create a blueprint for the base routes
base_blueprint = Blueprint('base', __name__)

@base_blueprint.route("/", methods=["GET"])
def server_status():
    """Test API to check if the server is running."""
    return jsonify({"message": "The server is running!"})
