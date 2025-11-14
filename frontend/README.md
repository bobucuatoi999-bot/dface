# FaceStream Frontend

Web-based frontend for the FaceStream Recognition System.

## Features

- 🔐 Authentication & Login
- 👤 User Registration with Camera Capture
- 🎥 Real-time Recognition Mode
- 👥 User Management
- 📊 Logs & Analytics

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The frontend will be available at: http://localhost:3000

### 3. Configure Backend URL

Create `.env` file (optional, defaults to localhost:8000):
```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Usage

1. **Login** - Use admin credentials created via backend script
2. **Register User** - Capture face and register new users
3. **Recognition Mode** - Real-time face recognition from camera
4. **Users** - View and manage registered users
5. **Logs** - View recognition events and statistics

## Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

