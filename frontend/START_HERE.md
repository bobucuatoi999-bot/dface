# 🚀 Quick Start Guide - Frontend

## Prerequisites

1. **Node.js** installed (v16 or higher)
2. **Backend server running** on http://localhost:8000
3. **Admin user created** (run `python backend/scripts/create_admin.py`)

## Setup & Run

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

### Step 2: Start Frontend

```bash
npm run dev
```

Frontend will start at: **http://localhost:3000**

### Step 3: Login

1. Open http://localhost:3000
2. Login with admin credentials
3. Start using the app!

## Features

### 🔐 Login Page
- Enter username and password
- Gets JWT token
- Stores token for API calls

### 📝 Register User Page
- Enter user details (name, email, employee ID)
- Start camera
- Capture photo
- Register user with face

### 🎥 Recognition Mode
- Start camera
- Real-time face recognition
- See bounding boxes and names
- Track multiple faces

### 👥 Users Page
- View all registered users
- See face count per user
- Delete users

### 📊 Logs Page
- View statistics
- See recognition events
- Track unknown persons

## Troubleshooting

### "Cannot connect to backend"
- Make sure backend is running: `python -m app.main` in backend folder
- Check backend URL in browser console

### "Camera not working"
- Allow camera permissions in browser
- Use HTTPS or localhost (required for camera access)

### "Login failed"
- Create admin user: `python backend/scripts/create_admin.py`
- Check backend is running

### "CORS errors"
- Backend CORS is configured to allow all origins
- Check backend logs for errors

## Testing Workflows

### Workflow 1: Register a User
1. Go to "Register User"
2. Enter name and email
3. Click "Start Camera"
4. Click "Capture Photo"
5. Click "Register User"
6. ✅ User registered!

### Workflow 2: Recognition Mode
1. Go to "Recognition Mode"
2. Click "Start Recognition"
3. Allow camera access
4. Point camera at registered users
5. See names appear in real-time!

### Workflow 3: View Logs
1. Go to "Logs & Analytics"
2. See statistics
3. View recent recognition events

## Development

- **Hot Reload**: Changes auto-refresh
- **API Proxy**: Configured in `vite.config.js`
- **WebSocket**: Connects to backend automatically

## Build for Production

```bash
npm run build
```

Output in `dist/` folder - deploy to any static host!

