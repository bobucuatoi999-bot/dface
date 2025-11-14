# 🚀 Quick Start - Complete System

## Prerequisites

- Python 3.10+
- Node.js 16+
- PostgreSQL (or use Railway)
- Camera (for testing)

---

## Step-by-Step Setup

### 1️⃣ Setup Backend (5 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy env.example .env
# Edit .env and set DATABASE_URL

# Create admin user (IMPORTANT!)
python scripts/create_admin.py
# Enter: username, password, email
```

### 2️⃣ Setup Frontend (2 minutes)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install
```

### 3️⃣ Start Backend

```bash
cd backend
python -m app.main
```

**Wait for:** "Application startup complete"

### 4️⃣ Start Frontend

**New terminal:**
```bash
cd frontend
npm run dev
```

**Wait for:** "Local: http://localhost:3000"

---

## 🎯 Test the System

### 1. Open Frontend
Go to: **http://localhost:3000**

### 2. Login
- Username: (what you entered in create_admin.py)
- Password: (what you entered)
- Click "Login"

### 3. Register a User
- Click "📝 Register User"
- Enter name: "Test User"
- Click "📹 Start Camera"
- **Allow camera permissions**
- Click "📸 Capture Photo"
- Click "✅ Register User"
- ✅ Success!

### 4. Test Recognition
- Click "🎥 Recognition Mode"
- Click "▶ Start Recognition"
- Point camera at yourself (the registered user)
- See your name appear! 🎉

---

## 🎬 Complete Workflow Test

1. **Register 2-3 users** with different faces
2. **Start Recognition Mode**
3. **Point camera** at registered users
4. **See names appear** in real-time
5. **Point at unknown person** → Shows "Unknown"
6. **Check Logs** → See all recognition events

---

## 🐛 Troubleshooting

### "Cannot connect to backend"
- ✅ Backend running? Check http://localhost:8000/health
- ✅ Check backend terminal for errors

### "Login failed"
- ✅ Created admin user? Run `python backend/scripts/create_admin.py`
- ✅ Check username/password

### "Camera not working"
- ✅ Allow camera permissions in browser
- ✅ Use Chrome/Edge (best camera support)
- ✅ Must be on localhost or HTTPS

### "No face detected"
- ✅ Good lighting?
- ✅ Face clearly visible?
- ✅ Camera focused?

---

## 📱 What You Can Do

✅ **Register Users** - Capture faces and add to system
✅ **Real-time Recognition** - See names appear live
✅ **View Users** - See all registered users
✅ **View Logs** - See recognition statistics
✅ **Multi-face** - Recognize multiple people at once

---

## 🎉 You're Ready!

The complete system is now running:
- ✅ Backend processing faces
- ✅ Frontend providing UI
- ✅ Real-time recognition working
- ✅ All workflows functional

**Enjoy testing!** 🚀

