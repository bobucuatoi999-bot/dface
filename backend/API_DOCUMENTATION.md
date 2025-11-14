# FaceStream Backend API Documentation

Complete REST API documentation for the FaceStream Recognition System.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. In production, add JWT or API key authentication.

---

## User Management API

### Create User

Create a new user without face embeddings.

**Endpoint:** `POST /api/users/`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "employee_id": "EMP-12345",
  "extra_data": "{\"department\": \"Engineering\"}"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "employee_id": "EMP-12345",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "face_count": 0
}
```

---

### Register User with Face

Register a new user and automatically capture face from image.

**Endpoint:** `POST /api/users/register`

**Request (Form Data):**
- `name` (required): User's full name
- `email` (optional): Email address
- `employee_id` (optional): Employee ID
- `image_data` (required): Base64 encoded image string

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "image_data": "<base64_encoded_image>"
  }'
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "employee_id": null,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "face_count": 1
}
```

**Errors:**
- `400 Bad Request`: No face detected, face too small, or duplicate face
- `500 Internal Server Error`: Server error

---

### Get All Users

Get a list of all users.

**Endpoint:** `GET /api/users/`

**Query Parameters:**
- `active_only` (optional, default: `true`): Only return active users

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "employee_id": "EMP-12345",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "face_count": 2
  },
  {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane@example.com",
    "employee_id": null,
    "is_active": true,
    "created_at": "2024-01-15T11:00:00Z",
    "updated_at": "2024-01-15T11:00:00Z",
    "face_count": 1
  }
]
```

---

### Get User by ID

Get a specific user.

**Endpoint:** `GET /api/users/{user_id}`

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "employee_id": "EMP-12345",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "face_count": 2
}
```

**Errors:**
- `404 Not Found`: User not found

---

### Update User

Update user information.

**Endpoint:** `PUT /api/users/{user_id}`

**Request Body:**
```json
{
  "name": "John Updated",
  "email": "john.new@example.com",
  "is_active": false
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "John Updated",
  "email": "john.new@example.com",
  "employee_id": "EMP-12345",
  "is_active": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T12:00:00Z",
  "face_count": 2
}
```

---

### Delete User

Delete a user and all associated data (face embeddings, logs).

**Endpoint:** `DELETE /api/users/{user_id}`

**Response:** `204 No Content`

**Errors:**
- `404 Not Found`: User not found

---

### Get User Face Embeddings

Get all face embeddings for a user.

**Endpoint:** `GET /api/users/{user_id}/faces`

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "embedding_length": 128,
    "capture_angle": "frontal",
    "quality_score": 0.95,
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "user_id": 1,
    "embedding_length": 128,
    "capture_angle": "left",
    "quality_score": 0.88,
    "created_at": "2024-01-15T10:35:00Z"
  }
]
```

---

### Add Face Embedding to User

Add a new face embedding for an existing user.

**Endpoint:** `POST /api/users/{user_id}/faces`

**Request (Form Data):**
- `image_data` (required): Base64 encoded image
- `capture_angle` (optional, default: "frontal"): Angle description

**Response:** `201 Created`
```json
{
  "id": 3,
  "user_id": 1,
  "embedding_length": 128,
  "capture_angle": "right",
  "quality_score": 0.92,
  "created_at": "2024-01-15T12:00:00Z"
}
```

---

## Recognition Logs API

### Get Recognition Logs

Get recognition event logs with optional filters.

**Endpoint:** `GET /api/logs/`

**Query Parameters:**
- `user_id` (optional): Filter by user ID
- `session_id` (optional): Filter by session ID
- `is_unknown` (optional): Filter by unknown status (`true`/`false`)
- `start_date` (optional): Start date filter (ISO format)
- `end_date` (optional): End date filter (ISO format)
- `min_confidence` (optional): Minimum confidence score (0.0-1.0)
- `limit` (optional, default: 100): Maximum results (1-1000)
- `offset` (optional, default: 0): Pagination offset

**Example:**
```bash
GET /api/logs/?user_id=1&min_confidence=0.85&limit=50
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "user_name": "John Doe",
    "track_id": "1",
    "confidence": 0.95,
    "is_unknown": false,
    "frame_position": "120,80,140,140",
    "session_id": "abc-123-def",
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "user_id": null,
    "user_name": null,
    "track_id": "2",
    "confidence": 0.0,
    "is_unknown": true,
    "frame_position": "450,100,120,120",
    "session_id": "abc-123-def",
    "created_at": "2024-01-15T10:30:05Z"
  }
]
```

---

### Get Recognition Statistics

Get aggregated statistics about recognition events.

**Endpoint:** `GET /api/logs/stats`

**Query Parameters:**
- `start_date` (optional): Start date filter
- `end_date` (optional): End date filter

**Response:** `200 OK`
```json
{
  "total_recognitions": 1250,
  "unique_users": 45,
  "unknown_count": 23,
  "average_confidence": 0.9123,
  "top_users": [
    {
      "user_id": 1,
      "name": "John Doe",
      "recognition_count": 156
    },
    {
      "user_id": 2,
      "name": "Jane Smith",
      "recognition_count": 134
    }
  ],
  "period": {
    "start_date": "2024-01-15T00:00:00Z",
    "end_date": "2024-01-15T23:59:59Z"
  }
}
```

---

### Get Recognition Sessions

Get list of recognition sessions.

**Endpoint:** `GET /api/logs/sessions`

**Query Parameters:**
- `limit` (optional, default: 50): Maximum results (1-200)

**Response:** `200 OK`
```json
[
  {
    "session_id": "abc-123-def",
    "start_time": "2024-01-15T10:30:00Z",
    "end_time": "2024-01-15T10:45:00Z",
    "duration_seconds": 900.0,
    "total_recognitions": 45,
    "unique_users": 8
  },
  {
    "session_id": "xyz-456-ghi",
    "start_time": "2024-01-15T11:00:00Z",
    "end_time": "2024-01-15T11:15:00Z",
    "duration_seconds": 900.0,
    "total_recognitions": 32,
    "unique_users": 5
  }
]
```

---

## WebSocket API

### Real-Time Recognition

**Endpoint:** `ws://localhost:8000/ws/recognize`

**Connection:**
Client connects via WebSocket. Server sends connection confirmation.

**Message Format (Client → Server):**
```json
{
  "type": "frame",
  "data": "<base64_encoded_image>",
  "timestamp": 1234567890,
  "frame_id": 1
}
```

**Message Format (Server → Client):**
```json
{
  "type": "recognition_result",
  "frame_id": 1,
  "faces": [
    {
      "track_id": "1",
      "user_id": 1,
      "user_name": "John Doe",
      "confidence": 0.95,
      "bbox": [top, right, bottom, left],
      "is_unknown": false
    }
  ],
  "timestamp": 1234567890,
  "session_id": "uuid-string"
}
```

**Other Message Types:**
- `ping`: Heartbeat message
- `reset`: Reset face tracking

---

## Error Responses

All endpoints may return these error responses:

### 400 Bad Request
```json
{
  "detail": "Error message describing what went wrong"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

---

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive testing interfaces for all endpoints.

---

## Example Usage

### Register a User

```python
import requests
import base64

# Read image file
with open("photo.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Register user
response = requests.post(
    "http://localhost:8000/api/users/register",
    json={
        "name": "John Doe",
        "email": "john@example.com",
        "image_data": image_data
    }
)

print(response.json())
```

### Get Recognition Logs

```python
import requests

# Get logs for specific user
response = requests.get(
    "http://localhost:8000/api/logs/",
    params={
        "user_id": 1,
        "min_confidence": 0.85,
        "limit": 50
    }
)

logs = response.json()
for log in logs:
    print(f"{log['user_name']}: {log['confidence']:.2%}")
```

### WebSocket Recognition

```python
import asyncio
import websockets
import json
import base64

async def recognize():
    uri = "ws://localhost:8000/ws/recognize"
    async with websockets.connect(uri) as websocket:
        # Receive connection message
        msg = await websocket.recv()
        print(json.loads(msg))
        
        # Send frame
        with open("frame.jpg", "rb") as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        await websocket.send(json.dumps({
            "type": "frame",
            "data": image_data,
            "timestamp": 1234567890,
            "frame_id": 1
        }))
        
        # Receive result
        result = await websocket.recv()
        print(json.loads(result))

asyncio.run(recognize())
```

---

## Status Codes

- `200 OK`: Successful GET/PUT request
- `201 Created`: Successful POST request (resource created)
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider adding rate limiting to prevent abuse.

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Base64 images should include data URL prefix if present
- Face images should be at least 100x100 pixels
- Maximum frame rate for WebSocket is 5 FPS (configurable)

