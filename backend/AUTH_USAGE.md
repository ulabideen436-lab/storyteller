# Authentication System Usage Guide

## Overview
The authentication system uses Firebase Authentication with custom token generation and JWT verification.

## Endpoints

### 1. Register User
**POST** `/auth/register`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "data": {
    "id": "user_abc123",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "created_at": "2025-12-28T10:30:00Z"
  }
}
```

**Validations:**
- Name: 2-100 characters, no numbers
- Email: Valid email format
- Password: Min 8 chars, must contain uppercase, lowercase, and number

---

### 2. Login User
**POST** `/auth/login`

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "user_abc123",
      "name": "John Doe",
      "email": "john.doe@example.com",
      "created_at": "2025-12-28T10:30:00Z"
    }
  }
}
```

**Note:** The token is a custom Firebase token. In production, use Firebase Client SDK to exchange this for an ID token.

---

### 3. Verify Token
**GET** `/auth/verify`

**Headers:**
```
Authorization: Bearer <your-firebase-id-token>
```

**Response:**
```json
{
  "message": "Token verified successfully",
  "data": {
    "uid": "user_abc123",
    "email": "john.doe@example.com",
    "name": "John Doe",
    "token_valid": true,
    "exp": 1735478400,
    "iat": 1735392000
  }
}
```

---

### 4. Get Current User Profile
**GET** `/auth/me`

**Headers:**
```
Authorization: Bearer <your-firebase-id-token>
```

**Response:**
```json
{
  "id": "user_abc123",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "created_at": "2025-12-28T10:30:00Z"
}
```

---

## Using the `verify_token` Dependency

To protect any route with authentication, use the `verify_token` dependency:

```python
from app.routes.auth import verify_token
from typing import Dict, Any

@router.get("/protected-route")
async def protected_route(token_data: Dict[str, Any] = Depends(verify_token)):
    user_id = token_data['uid']
    user_email = token_data['email']
    
    # Your protected logic here
    return {"message": f"Hello {user_email}!"}
```

---

## Error Responses

### Invalid Token (401)
```json
{
  "detail": "Invalid authentication: Token expired"
}
```

### User Not Found (404)
```json
{
  "detail": "User not found"
}
```

### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Password must contain at least one uppercase letter",
      "type": "value_error"
    }
  ]
}
```

### Email Already Exists (400)
```json
{
  "detail": "Email already registered"
}
```

---

## Example: Python Client Usage

```python
import requests

# 1. Register
response = requests.post(
    "http://localhost:8000/auth/register",
    json={
        "name": "John Doe",
        "email": "john@example.com",
        "password": "SecurePass123!"
    }
)
print(response.json())

# 2. Login
response = requests.post(
    "http://localhost:8000/auth/login",
    json={
        "email": "john@example.com",
        "password": "SecurePass123!"
    }
)
token = response.json()["data"]["token"]

# 3. Use token in protected routes
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/auth/verify",
    headers=headers
)
print(response.json())
```

---

## Security Notes

1. **Password Storage**: Passwords are handled by Firebase Authentication (hashed with bcrypt)
2. **Token Expiration**: ID tokens expire after 1 hour by default
3. **HTTPS**: Always use HTTPS in production to prevent token interception
4. **Token Storage**: Store tokens securely (HttpOnly cookies or secure storage)
5. **Password Requirements**: Enforced both at Pydantic validation and Firebase level

---

## Firestore Data Structure

### users collection
```javascript
{
  "id": "user_abc123",
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": Timestamp,
  "updated_at": Timestamp
}
```
