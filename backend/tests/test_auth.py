"""
Authentication Route Tests

Tests for user registration, login, token verification, and admin role checks.
"""
import pytest
from fastapi import status
from unittest.mock import patch, MagicMock
import jwt
import time


class TestUserRegistration:
    """Test user registration endpoints"""
    
    def test_register_user_success(self, client, mock_firebase_auth, mock_firestore):
        """Test successful user registration"""
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "SecurePass123!"
        }
        
        response = client.post("/auth/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["success"] is True
        assert "message" in response.json()
        mock_firebase_auth.create_user.assert_called_once()
    
    def test_register_user_invalid_email(self, client):
        """Test registration with invalid email"""
        user_data = {
            "name": "John Doe",
            "email": "invalid-email",
            "password": "SecurePass123!"
        }
        
        response = client.post("/auth/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_user_weak_password(self, client):
        """Test registration with weak password"""
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "weak"
        }
        
        response = client.post("/auth/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_user_missing_name(self, client):
        """Test registration with missing name"""
        user_data = {
            "email": "john@example.com",
            "password": "SecurePass123!"
        }
        
        response = client.post("/auth/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_duplicate_email(self, client, mock_firebase_auth, mock_firestore):
        """Test registration with duplicate email"""
        mock_firebase_auth.create_user.side_effect = Exception("Email already exists")
        
        user_data = {
            "name": "John Doe",
            "email": "existing@example.com",
            "password": "SecurePass123!"
        }
        
        response = client.post("/auth/auth/register", json=user_data)
        
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR]


class TestUserLogin:
    """Test user login endpoints"""
    
    def test_login_success(self, client, mock_firebase_auth, mock_firestore):
        """Test successful login"""
        login_data = {
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        response = client.post("/auth/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.json()
        assert "token" in response.json()["data"]
    
    def test_login_invalid_credentials(self, client, mock_firebase_auth):
        """Test login with invalid credentials"""
        mock_firebase_auth.get_user_by_email.side_effect = Exception("User not found")
        
        login_data = {
            "email": "wrong@example.com",
            "password": "WrongPass123!"
        }
        
        response = client.post("/auth/auth/login", json=login_data)
        
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_login_missing_email(self, client):
        """Test login with missing email"""
        login_data = {
            "password": "SecurePass123!"
        }
        
        response = client.post("/auth/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_missing_password(self, client):
        """Test login with missing password"""
        login_data = {
            "email": "test@example.com"
        }
        
        response = client.post("/auth/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTokenVerification:
    """Test token verification"""
    
    def test_verify_valid_token(self, client, test_user_token):
        """Test verification with valid token"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        with patch('app.routes.auth.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com",
                "exp": int(time.time()) + 3600
            }
            
            response = client.get("/auth/auth/verify", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["success"] is True
    
    def test_verify_expired_token(self, client):
        """Test verification with expired token"""
        JWT_SECRET = "test-secret-key"
        JWT_ALGORITHM = "HS256"
        
        expired_payload = {
            "uid": "test_user_123",
            "email": "test@example.com",
            "exp": int(time.time()) - 3600,  # Expired 1 hour ago
            "iat": int(time.time()) - 7200
        }
        
        expired_token = jwt.encode(expired_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        with patch('app.routes.auth.jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.ExpiredSignatureError("Token expired")
            
            response = client.get("/auth/auth/verify", headers=headers)
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_verify_invalid_token(self, client):
        """Test verification with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        with patch('app.routes.auth.jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.InvalidTokenError("Invalid token")
            
            response = client.get("/auth/auth/verify", headers=headers)
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_verify_missing_token(self, client):
        """Test verification without token"""
        response = client.get("/auth/auth/verify")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAdminRole:
    """Test admin role checks"""
    
    def test_admin_access_with_admin_role(self, client, mock_firestore):
        """Test admin endpoint access with admin role"""
        # Mock admin user in Firestore
        mock_firestore.return_value.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {
            'id': 'admin_user_123',
            'email': 'admin@example.com',
            'role': 'admin'
        }
        
        JWT_SECRET = "test-secret-key"
        JWT_ALGORITHM = "HS256"
        
        admin_payload = {
            "uid": "admin_user_123",
            "email": "admin@example.com",
            "exp": int(time.time()) + 3600,
            "iat": int(time.time())
        }
        
        admin_token = jwt.encode(admin_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        with patch('app.routes.auth.jwt.decode') as mock_decode:
            mock_decode.return_value = admin_payload
            
            response = client.get("/admin/admin/users", headers=headers)
            
            # Should not return 403 Forbidden
            assert response.status_code != status.HTTP_403_FORBIDDEN
    
    def test_admin_access_without_admin_role(self, client, test_user_token, mock_firestore):
        """Test admin endpoint access without admin role"""
        # Mock regular user in Firestore
        mock_firestore.return_value.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {
            'id': 'test_user_123',
            'email': 'test@example.com',
            'role': 'user'
        }
        
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        with patch('app.routes.auth.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com",
                "exp": int(time.time()) + 3600
            }
            
            response = client.get("/admin/admin/users", headers=headers)
            
            # Should return 403 Forbidden or redirect
            assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]


class TestGetCurrentUser:
    """Test get current user endpoint"""
    
    def test_get_current_user_success(self, client, test_user_token, mock_firestore):
        """Test getting current user info"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        with patch('app.routes.auth.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com",
                "exp": int(time.time()) + 3600
            }
            
            response = client.get("/auth/auth/me", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            assert "email" in response.json()
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without token"""
        response = client.get("/auth/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
