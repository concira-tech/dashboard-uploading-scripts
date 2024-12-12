import os
import jwt
from flask import request, jsonify
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")

def verify_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract the token from the Authorization header
        auth_header = request.headers.get("Authorization")
        token = auth_header.replace("Bearer ", "") if auth_header else None

        if not token:
            return jsonify({"message": "No Token! Access Denied"}), 401

        try:
            # Decode the token using the secret
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user = decoded_token  # Attach user info to the request
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid Token"}), 401

        return f(*args, **kwargs)

    return decorated_function
