from firebase_admin import credentials, initialize_app

from decouple import AutoConfig

config = AutoConfig()



def initialize_firebase():

    cred = credentials.Certificate({
    "type": config("FIREBASE_TYPE"),
    "project_id": config("FIREBASE_PROJECT_ID"),
    "private_key_id": config("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": config("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": config("FIREBASE_CLIENT_EMAIL"),
    "client_id": config("FIREBASE_CLIENT_ID"),
    "auth_uri": config("FIREBASE_AUTH_URI"),
    "token_uri": config("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": config("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": config("FIREBASE_CLIENT_X509_CERT_URL"),
    })

    # Initialize Firebase Admin SDK if not already initialized
    try:
        # print("Initializing Firebase Admin SDK...")
        initialize_app(cred)
    except ValueError:
        pass
        # print("Firebase Admin SDK already initialized.")

