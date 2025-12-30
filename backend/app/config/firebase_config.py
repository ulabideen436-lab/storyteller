"""
Firebase Configuration Module

Initializes Firebase Admin SDK with credentials from environment variables.
Provides access to Firebase Auth, Firestore, and Storage services.
"""

import os
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Global references for Firebase services
firebase_auth = None
firebase_db = None
firebase_bucket = None


def initialize_firebase():
    """
    Initialize Firebase Admin SDK with credentials from environment variables.
    
    Returns:
        tuple: (auth, db, bucket) - Firebase Auth, Firestore client, and Storage bucket
        
    Raises:
        ValueError: If required environment variables are missing
        Exception: If Firebase initialization fails
    """
    global firebase_auth, firebase_db, firebase_bucket
    
    # Check if already initialized
    if firebase_auth is not None:
        return firebase_auth, firebase_db, firebase_bucket
    
    try:
        # Retrieve required environment variables
        required_vars = [
            'FIREBASE_PROJECT_ID',
            'FIREBASE_PRIVATE_KEY_ID',
            'FIREBASE_PRIVATE_KEY',
            'FIREBASE_CLIENT_EMAIL',
            'FIREBASE_CLIENT_ID',
            'FIREBASE_AUTH_URI',
            'FIREBASE_TOKEN_URI',
            'FIREBASE_STORAGE_BUCKET'
        ]
        
        # Validate all required variables are present
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                "Please ensure all Firebase credentials are set in your .env file."
            )
        
        # Create credentials dictionary from environment variables
        cred_dict = {
            "type": "service_account",
            "project_id": os.getenv('FIREBASE_PROJECT_ID'),
            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
            "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),  # Handle escaped newlines
            "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
            "client_id": os.getenv('FIREBASE_CLIENT_ID'),
            "auth_uri": os.getenv('FIREBASE_AUTH_URI'),
            "token_uri": os.getenv('FIREBASE_TOKEN_URI'),
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('FIREBASE_CLIENT_EMAIL')}"
        }
        
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
        })
        
        # Initialize service references
        firebase_auth = auth
        firebase_db = firestore.client()
        firebase_bucket = storage.bucket()
        
        print("✓ Firebase initialized successfully")
        
        return firebase_auth, firebase_db, firebase_bucket
        
    except ValueError as ve:
        print(f"✗ Firebase initialization failed: {ve}")
        raise
    except Exception as e:
        print(f"✗ Firebase initialization failed: {str(e)}")
        raise Exception(f"Failed to initialize Firebase: {str(e)}")


def get_auth():
    """Get Firebase Auth instance."""
    if firebase_auth is None:
        initialize_firebase()
    return firebase_auth


def get_db():
    """Get Firestore client instance."""
    if firebase_db is None:
        initialize_firebase()
    return firebase_db


def get_bucket():
    """Get Firebase Storage bucket instance."""
    if firebase_bucket is None:
        initialize_firebase()
    return firebase_bucket
