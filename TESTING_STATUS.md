# 🧪 Testing Status

## Current Status

✅ **Frontend**: Starting on http://localhost:3000
✅ **Backend**: Should be on http://localhost:8000

## Quick Test Steps

### 1. Verify Backend is Running

Open: http://localhost:8000/health

Should see:
```json
{
  "status": "healthy",
  "database": "connected",
  "active_connections": 0
}
```

### 2. Access Frontend

Open: http://localhost:3000

### 3. Login

- Username: (your admin username from create_admin.py)
- Password: (your admin password)

### 4. Test Registration

1. Click "📝 Register User"
2. Enter name: "Test User"
3. Click "📹 Start Camera"
4. Allow camera permissions
5. Click "📸 Capture Photo"
6. Click "✅ Register User"

### 5. Test Recognition

1. Click "🎥 Recognition Mode"
2. Click "▶ Start Recognition"
3. Point camera at registered user
4. See name appear!

## Troubleshooting

### Frontend not loading?
- Check: `npm run dev` is running
- Check: Port 3000 is available
- Check: Browser console for errors

### Backend connection errors?
- Check: Backend is running (`python -m app.main`)
- Check: http://localhost:8000/health works
- Check: CORS settings in backend

### Login fails?
- Create admin: `python backend/scripts/create_admin.py`
- Check: Backend logs for errors

### Camera not working?
- Use Chrome/Edge browser
- Allow camera permissions
- Must be on localhost or HTTPS

## Next Steps

1. ✅ Frontend should be running
2. ✅ Backend should be running
3. ✅ Open http://localhost:3000
4. ✅ Login and test!

