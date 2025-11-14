# Authentication & Authorization Guide

## Overview

The backend now includes JWT-based authentication and role-based access control (RBAC).

## Features

✅ **JWT Authentication** - Secure token-based authentication
✅ **Role-Based Access Control** - Admin, Operator, Viewer roles
✅ **Protected Endpoints** - User management requires admin role
✅ **Password Hashing** - Bcrypt password hashing
✅ **Token Expiration** - Configurable token expiration

## User Roles

### Admin
- Full access to all endpoints
- Can create/update/delete users
- Can register new users with faces
- Can view all logs and statistics

### Operator
- Can use recognition mode (WebSocket)
- Can view logs and statistics
- Cannot modify users

### Viewer
- Read-only access
- Can view logs and statistics
- Cannot use recognition or modify data

## Setup

### 1. Create Admin User

```bash
python scripts/create_admin.py
```

Or manually via API (if you have an existing admin):
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "secure_password",
    "email": "admin@example.com",
    "role": "admin"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=secure_password"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Use Token

Include token in Authorization header:
```bash
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer <access_token>"
```

## API Endpoints

### Authentication

- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/register` - Register new user (admin only)

### Protected Endpoints

**Require Admin:**
- `POST /api/users/` - Create user
- `POST /api/users/register` - Register user with face
- `DELETE /api/users/{id}` - Delete user

**Require Authentication (any role):**
- `GET /api/users/` - List users
- `GET /api/logs/` - Get logs
- `GET /api/logs/stats` - Get statistics

**Public:**
- `GET /health` - Health check
- `GET /docs` - API documentation
- `WS /ws/recognize` - WebSocket (can be protected if needed)

## Example Usage

### Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    data={"username": "admin", "password": "password"}
)
token = response.json()["access_token"]

# Use token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/api/users/", headers=headers)
users = response.json()
```

### JavaScript/Frontend

```javascript
// Login
const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: 'username=admin&password=password'
});

const {access_token} = await response.json();

// Use token
const usersResponse = await fetch('http://localhost:8000/api/users/', {
  headers: {'Authorization': `Bearer ${access_token}`}
});
```

## Configuration

In `.env`:
```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Security Notes

- **Change SECRET_KEY** in production!
- Use strong passwords
- Tokens expire after 30 minutes (configurable)
- Passwords are hashed with bcrypt
- HTTPS recommended in production

