# Admin Panel API Documentation

## Overview
The admin panel provides privileged endpoints for user management, content moderation, and platform monitoring.

## Authentication

### Admin Role Setup
To grant admin privileges to a user, run the admin role script:

```bash
cd backend
python scripts/set_admin_role.py
```

Or use Firebase Admin SDK directly:
```python
from app.config.firebase_config import get_auth

auth = get_auth()
auth.set_custom_user_claims(user_id, {'admin': True})
```

### Admin Login
**POST** `/admin/login`

Headers:
```
Authorization: Bearer <firebase-id-token>
```

Response:
```json
{
  "message": "Admin authentication successful",
  "data": {
    "admin_id": "user_abc123",
    "email": "admin@example.com",
    "name": "Admin User",
    "is_admin": true
  }
}
```

**Error Response (403):**
```json
{
  "detail": "Access denied. Admin privileges required."
}
```

---

## User Management

### List All Users
**GET** `/admin/users?page=1&limit=20`

**Auth:** Admin only

**Query Parameters:**
- `page` (default: 1) - Page number
- `limit` (default: 20, max: 100) - Users per page

**Response:**
```json
{
  "message": "Retrieved 20 users",
  "data": {
    "users": [
      {
        "id": "user_123",
        "email": "user@example.com",
        "name": "John Doe",
        "created_at": "2025-12-28T10:00:00Z",
        "disabled": false,
        "email_verified": true,
        "stories_count": 5,
        "custom_claims": {}
      }
    ],
    "page": 1,
    "limit": 20,
    "has_next_page": true,
    "total_retrieved": 20
  }
}
```

---

### Block User
**POST** `/admin/users/{user_id}/block`

**Auth:** Admin only

**Request Body:**
```json
{
  "action_type": "ban_user",
  "target_user_id": "user_123",
  "reason": "Violation of terms of service"
}
```

**Response:**
```json
{
  "message": "User user@example.com has been blocked successfully",
  "data": {
    "user_id": "user_123",
    "email": "user@example.com",
    "disabled": true,
    "action": "ban_user",
    "reason": "Violation of terms of service"
  }
}
```

**Protection:**
- Cannot block yourself
- Cannot block other admins
- Action is logged in admin_logs

---

### Unblock User
**POST** `/admin/users/{user_id}/unblock`

**Auth:** Admin only

**Request Body:**
```json
{
  "action_type": "unban_user",
  "target_user_id": "user_123",
  "reason": "Appeal approved"
}
```

**Response:**
```json
{
  "message": "User user@example.com has been unblocked successfully",
  "data": {
    "user_id": "user_123",
    "email": "user@example.com",
    "disabled": false,
    "action": "unban_user",
    "reason": "Appeal approved"
  }
}
```

---

### Delete User
**DELETE** `/admin/users/{user_id}`

**Auth:** Admin only

**Request Body:**
```json
{
  "action_type": "delete_story",
  "target_user_id": "user_123",
  "reason": "Permanent ban for repeated violations"
}
```

**Response:**
```json
{
  "message": "User user@example.com has been permanently deleted",
  "data": {
    "user_id": "user_123",
    "email": "user@example.com",
    "stories_deleted": 10,
    "files_deleted": 45,
    "reviews_deleted": 3
  }
}
```

**What gets deleted:**
- User from Firebase Authentication
- All user's stories
- All associated media files (images, audio, video)
- User document from Firestore
- All user's reviews

**Protection:**
- Cannot delete yourself
- Cannot delete other admins
- Action is logged with complete details

---

## Admin Logs

### Get Admin Logs
**GET** `/admin/logs?page=1&limit=50&action_type=ban_user`

**Auth:** Admin only

**Query Parameters:**
- `page` (default: 1) - Page number
- `limit` (default: 50, max: 200) - Logs per page
- `action_type` (optional) - Filter by action type

**Response:**
```json
{
  "message": "Retrieved 50 admin logs",
  "data": {
    "logs": [
      {
        "id": "log_abc123",
        "admin_id": "admin_456",
        "admin_name": "Admin User",
        "action": "ban_user",
        "target_user_id": "user_789",
        "target_user_name": "John Doe",
        "reason": "Violation of ToS",
        "details": {
          "email": "john@example.com"
        },
        "timestamp": "2025-12-28T10:30:00Z"
      }
    ],
    "page": 1,
    "limit": 50,
    "total": 150,
    "has_next_page": true
  }
}
```

**Logged Actions:**
- admin_login
- ban_user
- unban_user
- suspend_user
- delete_user
- warn_user

---

## Platform Statistics

### Get Admin Dashboard Stats
**GET** `/admin/stats`

**Auth:** Admin only

**Response:**
```json
{
  "message": "Platform statistics retrieved successfully",
  "data": {
    "users": {
      "total": 1250,
      "active": 1200,
      "disabled": 50
    },
    "stories": {
      "total": 5432,
      "completed": 5200,
      "processing": 32,
      "failed": 200
    },
    "reviews": {
      "total": 3210
    },
    "admin_actions": {
      "last_30_days": 45
    }
  }
}
```

---

## Firestore Structure

### admin_logs collection
```javascript
admin_logs/{log_id}
  - id: string
  - admin_id: string
  - action: string
  - target_user_id: string | null
  - reason: string | null
  - details: object
  - timestamp: timestamp
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication: Token expired"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied. Admin privileges required."
}
```

### 404 Not Found
```json
{
  "detail": "User not found"
}
```

### 400 Bad Request
```json
{
  "detail": "Cannot block your own admin account"
}
```

---

## Usage Examples

### Python Client

```python
import requests

# 1. Login as admin (first get token from regular login)
headers = {"Authorization": f"Bearer {admin_token}"}

# Verify admin access
response = requests.post(
    "http://localhost:8000/admin/login",
    headers=headers
)
print(response.json())

# 2. List users
response = requests.get(
    "http://localhost:8000/admin/users?page=1&limit=20",
    headers=headers
)
users = response.json()["data"]["users"]

# 3. Block a user
response = requests.post(
    f"http://localhost:8000/admin/users/{user_id}/block",
    headers=headers,
    json={
        "action_type": "ban_user",
        "target_user_id": user_id,
        "reason": "Spam content"
    }
)

# 4. Get admin logs
response = requests.get(
    "http://localhost:8000/admin/logs?page=1&limit=50",
    headers=headers
)
logs = response.json()["data"]["logs"]

# 5. Get platform stats
response = requests.get(
    "http://localhost:8000/admin/stats",
    headers=headers
)
stats = response.json()["data"]
```

### cURL Examples

```bash
# Verify admin access
curl -X POST http://localhost:8000/admin/login \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# List users
curl -X GET "http://localhost:8000/admin/users?page=1&limit=20" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Block user
curl -X POST http://localhost:8000/admin/users/USER_ID/block \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "ban_user",
    "target_user_id": "USER_ID",
    "reason": "Inappropriate content"
  }'

# Get logs
curl -X GET "http://localhost:8000/admin/logs?page=1&limit=50" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Security Considerations

1. **Admin Claims**: Set via Firebase custom claims, cannot be modified by users
2. **Self-Protection**: Admins cannot block/delete themselves
3. **Admin Protection**: Regular admins cannot affect other admin accounts
4. **Audit Trail**: All admin actions are logged with timestamps and details
5. **Authorization**: Every endpoint checks admin role via `check_admin_role` dependency
6. **Token Verification**: Uses Firebase Admin SDK for secure token validation

---

## Testing Admin Functionality

### Setup Test Admin
```bash
cd backend
python scripts/set_admin_role.py
# Select option 1 and enter admin email
```

### Verify Admin Role
```bash
python scripts/set_admin_role.py
# Select option 4 and enter admin email
```

### Test Non-Admin Access
Should receive 403 Forbidden:
```python
# Login as regular user
regular_token = get_regular_user_token()

# Try to access admin endpoint
response = requests.get(
    "http://localhost:8000/admin/users",
    headers={"Authorization": f"Bearer {regular_token}"}
)
# Expected: 403 Forbidden
```
