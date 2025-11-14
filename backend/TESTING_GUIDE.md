# Complete Testing Guide

## 🎯 How It Works Without a Frontend

The backend is a **headless API server** - it doesn't have a UI. Here's how it works:

### Architecture Overview

```
┌─────────────────────────────────────────┐
│   MOBILE APP (Frontend - Not Built Yet) │
│   - Camera capture                       │
│   - UI screens                          │
│   - User interactions                   │
└──────────────┬──────────────────────────┘
               │
               │ HTTP/REST API
               │ WebSocket
               │
               ↓
┌─────────────────────────────────────────┐
│   BACKEND SERVER (What We Built)        │
│   - Processes requests                  │
│   - Face recognition                   │
│   - Database operations                │
│   - Returns JSON responses             │
└─────────────────────────────────────────┘
```

### How Workflows Work

**The workflows you described work like this:**

1. **Mobile App** (frontend) handles:
   - Showing UI screens
   - Camera capture
   - User button taps
   - Displaying results

2. **Backend** (what we built) handles:
   - Receiving API requests
   - Processing images
   - Face recognition
   - Database operations
   - Returning results

3. **Communication** happens via:
   - REST API (HTTP) for user management
   - WebSocket for real-time recognition

---

## 🧪 Testing the Backend

### Prerequisites

1. **Start the backend server:**
   ```bash
   cd backend
   python -m app.main
   ```

2. **Install test dependencies:**
   ```bash
   pip install requests websockets
   ```

### Test Scripts

We've created comprehensive test scripts:

#### 1. **API Testing** (`tests/test_api.py`)

Tests all REST API endpoints:

```bash
python tests/test_api.py
```

**What it tests:**
- Health check
- User creation
- User retrieval
- User updates
- Recognition logs
- Statistics

#### 2. **WebSocket Testing** (`tests/test_websocket.py`)

Tests real-time recognition:

```bash
python tests/test_websocket.py
```

**What it tests:**
- WebSocket connection
- Frame processing
- Multiple frames (video simulation)
- Real image processing (if image provided)

**With real image:**
```bash
python tests/test_websocket.py path/to/face_image.jpg
```

#### 3. **Complete Workflow Testing** (`tests/test_complete_workflow.py`)

Simulates the exact workflows from your plan:

```bash
python tests/test_complete_workflow.py
```

**What it simulates:**
- Workflow 1: Admin registers user
- Workflow 2: Operator recognition mode
- Workflow 3: View logs

---

## 📱 How Frontend Would Integrate

### Example: Mobile App Code (Conceptual)

**Registration Screen:**
```javascript
// Mobile app (React Native / Flutter / etc.)
async function registerUser(name, email, imageBase64) {
  const response = await fetch('http://your-server.com/api/users/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      name: name,
      email: email,
      image_data: imageBase64  // From camera
    })
  });
  
  const user = await response.json();
  // Show success message in UI
  showSuccess(`User ${user.name} registered!`);
}
```

**Recognition Mode:**
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://your-server.com/ws/recognize');

// Send camera frames
camera.onFrame((imageBase64) => {
  ws.send(JSON.stringify({
    type: 'frame',
    data: imageBase64,
    timestamp: Date.now(),
    frame_id: frameCount++
  }));
});

// Receive recognition results
ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  if (result.type === 'recognition_result') {
    // Draw bounding boxes and labels on camera view
    result.faces.forEach(face => {
      drawBoundingBox(face.bbox, face.user_name, face.confidence);
    });
  }
};
```

---

## 🧪 Manual Testing with curl/Postman

### Test User Registration

```bash
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "image_data": "<base64_encoded_image>"
  }'
```

### Test Get Users

```bash
curl http://localhost:8000/api/users/
```

### Test Recognition Logs

```bash
curl http://localhost:8000/api/logs/stats
```

### Test WebSocket (using wscat)

```bash
# Install wscat: npm install -g wscat
wscat -c ws://localhost:8000/ws/recognize

# Then send:
{"type": "frame", "data": "<base64_image>", "timestamp": 1234567890, "frame_id": 1}
```

---

## 🌐 Using Swagger UI (Interactive Testing)

The backend automatically generates interactive API documentation:

1. **Start server:**
   ```bash
   python -m app.main
   ```

2. **Open browser:**
   ```
   http://localhost:8000/docs
   ```

3. **Test endpoints:**
   - Click "Try it out"
   - Enter parameters
   - Click "Execute"
   - See results

**This is the easiest way to test without writing code!**

---

## 📊 Testing Checklist

### Phase 1: Core Infrastructure ✅
- [x] Server starts
- [x] Database connects
- [x] Health check works
- [x] API docs accessible

### Phase 2: Face Processing ✅
- [ ] WebSocket connects
- [ ] Frames are received
- [ ] Faces are detected
- [ ] Recognition works (needs registered users)

### Phase 3: REST API ✅
- [ ] Create user
- [ ] Get users
- [ ] Update user
- [ ] Delete user
- [ ] Get logs
- [ ] Get statistics

### Phase 4: Enhancements ✅
- [ ] Multi-angle registration
- [ ] Similar face search
- [ ] Face comparison

---

## 🎬 Complete Test Scenario

### Step-by-Step Test

1. **Start Server:**
   ```bash
   cd backend
   python -m app.main
   ```

2. **Open Swagger UI:**
   ```
   http://localhost:8000/docs
   ```

3. **Register a User:**
   - Go to `POST /api/users/register`
   - Click "Try it out"
   - Enter name, email
   - For `image_data`, you need a base64-encoded face image
   - Click "Execute"
   - See user created!

4. **Start Recognition:**
   - Use `tests/test_websocket.py` script
   - Or use WebSocket client tool
   - Send frames with the registered user's face
   - See recognition results!

5. **View Logs:**
   - Go to `GET /api/logs/` in Swagger
   - See recognition events

---

## 💡 Key Points

1. **Backend is API-only** - No UI, just endpoints
2. **Frontend handles UI** - Mobile app shows screens, captures camera
3. **Communication via API** - HTTP for management, WebSocket for real-time
4. **Test scripts simulate** - They act like a frontend would
5. **Swagger UI helps** - Interactive testing without code

---

## 🚀 Next Steps

1. **Test the backend** using the scripts provided
2. **Build mobile frontend** that calls these APIs
3. **Frontend will:**
   - Show registration screen
   - Capture camera frames
   - Send to backend
   - Display recognition results

The backend is **ready and waiting** for the frontend to connect! 🎉

