"""
Pytest Configuration and Fixtures
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_firebase_auth():
    """Mock Firebase Authentication"""
    with patch('app.config.firebase_config.auth') as mock_auth:
        # Mock user creation
        mock_user = MagicMock()
        mock_user.uid = 'test_user_123'
        mock_user.email = 'test@example.com'
        mock_user.display_name = 'Test User'
        
        mock_auth.create_user.return_value = mock_user
        mock_auth.get_user.return_value = mock_user
        mock_auth.get_user_by_email.return_value = mock_user
        mock_auth.verify_id_token.return_value = {
            'uid': 'test_user_123',
            'email': 'test@example.com'
        }
        
        yield mock_auth


@pytest.fixture
def mock_firestore():
    """Mock Firestore database"""
    with patch('app.config.firebase_config.get_db') as mock_db:
        mock_collection = MagicMock()
        mock_document = MagicMock()
        
        # Setup mock chain
        mock_db.return_value.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        mock_collection.where.return_value = mock_collection
        mock_collection.get.return_value = []
        
        mock_document.get.return_value.exists = True
        mock_document.get.return_value.to_dict.return_value = {
            'id': 'test_id',
            'user_id': 'test_user_123',
            'name': 'Test User',
            'email': 'test@example.com',
            'role': 'user'
        }
        
        yield mock_db


@pytest.fixture
def test_user_token():
    """Generate test JWT token"""
    import jwt
    import time
    
    JWT_SECRET = "test-secret-key"
    JWT_ALGORITHM = "HS256"
    
    payload = {
        "uid": "test_user_123",
        "email": "test@example.com",
        "exp": int(time.time()) + 3600,
        "iat": int(time.time())
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


@pytest.fixture
def admin_user_token():
    """Generate admin JWT token"""
    import jwt
    import time
    
    JWT_SECRET = "test-secret-key"
    JWT_ALGORITHM = "HS256"
    
    payload = {
        "uid": "admin_user_123",
        "email": "admin@example.com",
        "role": "admin",
        "exp": int(time.time()) + 3600,
        "iat": int(time.time())
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


@pytest.fixture
def mock_together_api():
    """Mock Together.ai API"""
    with patch('app.services.image_service.Together') as mock_together:
        mock_client = MagicMock()
        mock_together.return_value = mock_client
        
        # Mock image generation response
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(url='https://example.com/image1.png'),
            MagicMock(url='https://example.com/image2.png')
        ]
        mock_client.images.generate.return_value = mock_response
        
        yield mock_client


@pytest.fixture
def mock_storage():
    """Mock Firebase Storage"""
    with patch('app.config.firebase_config.get_bucket') as mock_bucket:
        mock_blob = MagicMock()
        mock_blob.public_url = 'https://storage.example.com/test-file.png'
        
        mock_bucket.return_value.blob.return_value = mock_blob
        
        yield mock_bucket
