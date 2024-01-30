from firebase_admin import credentials, initialize_app, get_app
import os

def initialize_firebase():
    service_account_key_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "serviceAccountKey.json"))

    # Initialize Firebase Admin SDK if not already initialized
    try:
        print("Initializing Firebase Admin SDK...")
        cred = credentials.Certificate(service_account_key_path)
        initialize_app(cred)
    except ValueError:
        print("Firebase Admin SDK already initialized.")
