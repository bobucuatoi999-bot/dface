# FaceStream Recognition System

Complete real-time facial recognition system with web frontend and backend API.

## 🎯 What This Is

A production-ready facial recognition system that:
- Registers users by capturing their faces
- Recognizes people in real-time from video
- Tracks faces across frames
- Provides analytics and logging

## 🏗️ Architecture

```
Frontend (React) → Backend (FastAPI) → Database (PostgreSQL)
     ↓                    ↓
  WebSocket ←───────────┘
```

## 🚀 Quick Start

### 1. Setup Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
copy env.example .env
# Edit .env with your DATABASE_URL
python scripts/create_admin.py  # Create admin user
python -m app.main
```

### 2. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📱 Features

✅ User Registration with Camera
✅ Real-time Face Recognition
✅ User Management
✅ Recognition Logs & Analytics
✅ JWT Authentication
✅ Role-Based Access Control
✅ Redis Caching (optional)

## 📚 Documentation

- `QUICK_START.md` - Quick setup guide
- `COMPLETE_SETUP_GUIDE.md` - Detailed setup
- `backend/README.md` - Backend documentation
- `frontend/README.md` - Frontend documentation
- `backend/API_DOCUMENTATION.md` - API reference
- `backend/AUTHENTICATION_GUIDE.md` - Auth setup
- `backend/CACHING_GUIDE.md` - Redis setup

## 🧪 Testing

See `QUICK_START.md` for complete testing instructions.

## 📦 Project Structure

```
.
├── backend/          # Python FastAPI backend
│   ├── app/
│   │   ├── api/      # REST API endpoints
│   │   ├── models/   # Database models
│   │   ├── services/ # Business logic
│   │   └── utils/    # Utilities
│   └── scripts/      # Utility scripts
│
└── frontend/         # React frontend
    ├── src/
    │   ├── components/  # React components
    │   ├── services/     # API services
    │   └── utils/        # Utilities
    └── public/
```

## 🎉 Ready to Use!

Follow `QUICK_START.md` to get started in 5 minutes!

