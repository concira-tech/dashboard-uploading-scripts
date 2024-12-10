import os
from firebase_admin import credentials, firestore, initialize_app, storage
from dotenv import load_dotenv

def initialize_firebase(app):
    """Initialize Firebase Admin SDK and attach clients to the app."""
    load_dotenv()
    FIREBASE_AUTH_TOKEN = {
        "type": os.getenv("FIREBASE_TYPE"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    }

    cred = credentials.Certificate(FIREBASE_AUTH_TOKEN)
    initialize_app(cred, {
        "databaseURL": os.getenv("FIREBASE_REALTIMEDB_URL"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    })

    # Attach Firestore and Storage clients to app config
    app.config['FIRESTORE_CLIENT'] = firestore.client()
    app.config['STORAGE_BUCKET'] = storage.bucket()
