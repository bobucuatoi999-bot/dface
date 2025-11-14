# FaceStream Recognition System - Backend

Real-time facial recognition backend built with FastAPI, PostgreSQL, and WebSockets.

## 🏗️ Architecture

- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Real-time**: WebSocket support for live video streaming
- **Migrations**: Alembic for database version control

## 📋 Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env and set your DATABASE_URL
# Example: DATABASE_URL=postgresql://user:password@localhost:5432/facestream
```

### 4. Create Database

```bash
# Connect to PostgreSQL and create database
psql -U postgres
CREATE DATABASE facestream;
\q
```

### 5. Run Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic  # Skip if already initialized

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 6. Start Server

```bash
python -m app.main

# Or using uvicorn directly:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws/recognize

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection & session
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── face_embedding.py
│   │   └── recognition_log.py
│   ├── api/                 # API endpoints (Phase 3)
│   ├── services/            # Business logic (Phase 2)
│   └── utils/               # Utility functions
├── alembic/                 # Database migrations
├── requirements.txt
├── .env.example
└── README.md
```

## 🗄️ Database Models

### User
Stores registered users:
- `id`: Primary key
- `name`: Full name
- `email`: Email address (optional)
- `employee_id`: Employee ID (optional)
- `is_active`: Active status
- `created_at`, `updated_at`: Timestamps

### FaceEmbedding
Stores face embeddings (128-dim vectors):
- `id`: Primary key
- `user_id`: Foreign key to User
- `embedding`: 128-dimensional float array
- `capture_angle`: Angle description
- `quality_score`: Quality score (0-1)
- `created_at`: Timestamp

### RecognitionLog
Stores recognition events:
- `id`: Primary key
- `user_id`: Foreign key to User (nullable for unknowns)
- `track_id`: Track ID from face tracking
- `confidence`: Confidence score (0-1)
- `is_unknown`: Unknown person flag
- `frame_position`: Face position in frame
- `session_id`: Session identifier
- `created_at`: Timestamp

## 🔌 WebSocket API

### Connection
```
ws://localhost:8000/ws/recognize
```

### Message Format (Client → Server)

```json
{
  "type": "frame",
  "data": "<base64_encoded_image>",
  "timestamp": 1234567890,
  "frame_id": 1
}
```

### Message Format (Server → Client)

```json
{
  "type": "recognition_result",
  "frame_id": 1,
  "faces": [
    {
      "track_id": "1",
      "user_id": 248,
      "user_name": "John Doe",
      "confidence": 0.95,
      "bbox": [120, 80, 140, 140],
      "is_unknown": false
    }
  ],
  "timestamp": 1234567890
}
```

## 🔧 Configuration

All configuration is managed through environment variables (see `.env.example`):

- `DATABASE_URL`: PostgreSQL connection string
- `DEBUG`: Enable debug mode
- `MAX_FRAME_RATE`: Maximum frames per second (default: 5)
- `FACE_MATCH_THRESHOLD`: Face matching threshold (default: 0.6)
- `FACE_CONFIDENCE_THRESHOLD`: Minimum confidence (default: 0.85)

## 📊 Development Status

### ✅ Phase 1: Core Infrastructure (COMPLETE)
- [x] FastAPI app setup
- [x] PostgreSQL database models
- [x] Database connection & session management
- [x] Configuration management
- [x] WebSocket endpoint structure
- [x] Alembic migrations setup

### 🚧 Phase 2: Face Processing (NEXT)
- [ ] Face detection service
- [ ] Face embedding extraction
- [ ] Embedding comparison
- [ ] Face tracking

### 🚧 Phase 3: API Endpoints (UPCOMING)
- [ ] User registration API
- [ ] User management API
- [ ] Recognition logs API

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest

# Check database connection
python -c "from app.database import engine; engine.connect(); print('Connected!')"
```

## 🚢 Deployment (Railway)

1. Create a new Railway project
2. Add PostgreSQL service
3. Set environment variables in Railway dashboard
4. Deploy from Git or upload files
5. Run migrations: `alembic upgrade head`

## 📝 License

[Your License Here]

## 🤝 Contributing

[Contributing Guidelines]

