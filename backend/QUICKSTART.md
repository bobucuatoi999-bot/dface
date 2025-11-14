# Quick Start Guide - FaceStream Backend

## 🚀 5-Minute Setup

### Step 1: Install Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Setup PostgreSQL

**Option A: Local PostgreSQL**
```bash
# Install PostgreSQL, then:
psql -U postgres
CREATE DATABASE facestream;
\q
```

**Option B: Railway PostgreSQL (Recommended)**
1. Go to [railway.app](https://railway.app)
2. Create new project
3. Add PostgreSQL service
4. Copy the connection URL

### Step 3: Configure Environment

```bash
# Copy example file
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env and set DATABASE_URL
# Example: DATABASE_URL=postgresql://user:pass@localhost:5432/facestream
```

### Step 4: Initialize Database

```bash
# Option 1: Using init script
python init_db.py

# Option 2: Using Alembic (recommended for production)
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Step 5: Test Connection

```bash
python test_connection.py
```

Expected output:
```
✅ Connected to PostgreSQL: PostgreSQL 15.x
✅ All tables exist: ['users', 'face_embeddings', 'recognition_logs']
✅ User model works. Current users: 0
✅ All tests passed! Backend is ready.
```

### Step 6: Start Server

```bash
python -m app.main
```

Or:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 7: Verify

Open browser:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

## 🧪 Test WebSocket Connection

You can test the WebSocket endpoint using a simple Python script:

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/recognize"
    async with websockets.connect(uri) as websocket:
        # Receive connection message
        message = await websocket.recv()
        print(f"Received: {json.loads(message)}")
        
        # Send ping
        await websocket.send(json.dumps({
            "type": "ping",
            "timestamp": 1234567890
        }))
        
        # Receive pong
        response = await websocket.recv()
        print(f"Response: {json.loads(response)}")

asyncio.run(test_websocket())
```

## 📝 Common Issues

### Issue: "Module not found"
**Solution**: Make sure virtual environment is activated and dependencies are installed.

### Issue: "Database connection failed"
**Solution**: 
- Check DATABASE_URL in .env file
- Verify PostgreSQL is running
- Check firewall/network settings

### Issue: "Table doesn't exist"
**Solution**: Run `python init_db.py` or `alembic upgrade head`

### Issue: "Port already in use"
**Solution**: Change PORT in .env or kill the process using port 8000

## ✅ Phase 1 Complete Checklist

- [x] FastAPI app running
- [x] Database connected
- [x] Tables created (users, face_embeddings, recognition_logs)
- [x] WebSocket endpoint responding
- [x] Health check working
- [x] API docs accessible

## 🎯 Next Steps

Phase 1 is complete! Ready for Phase 2:
- Face detection service
- Face embedding extraction
- Face recognition comparison
- Face tracking

