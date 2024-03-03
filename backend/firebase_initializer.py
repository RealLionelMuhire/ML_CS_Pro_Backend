from firebase_admin import credentials, initialize_app

from decouple import AutoConfig

config = AutoConfig()



def initialize_firebase():
    # Use environment variables for sensitive data
    project_id = config('FIREBASE_PROJECT_ID')
    private_key_id = config('FIREBASE_PRIVATE_KEY_ID')
    private_key = config('FIREBASE_PRIVATE_KEY').replace('\\n', '\n')
    client_email = config('FIREBASE_CLIENT_EMAIL')
    client_id = config('FIREBASE_CLIENT_ID')
    universe_domain = config('FIREBASE_UNIVERSE_DOMAIN')

    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": project_id,
        "private_key_id": private_key_id,
        "private_key": private_key,
        "client_email": client_email,
        "client_id": client_id,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email}",
        "universe_domain": universe_domain
    })

    # Initialize Firebase Admin SDK if not already initialized
    try:
        print("Initializing Firebase Admin SDK...")
        initialize_app(cred)
    except ValueError:
        print("Firebase Admin SDK already initialized.")

