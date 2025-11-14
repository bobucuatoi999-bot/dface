# 🔐 Create Admin Account Instructions

## Admin Credentials
- **Username**: `123admin`
- **Password**: `duyan2892006`

## Prerequisites

**You need PostgreSQL database running!**

### Option 1: Start PostgreSQL Locally

1. **Start PostgreSQL service:**
   ```bash
   # Windows (if installed as service)
   net start postgresql-x64-XX
   
   # Or start from Services app
   # Search "Services" → Find PostgreSQL → Start
   ```

2. **Verify database connection:**
   - Check `.env` file has correct `DATABASE_URL`
   - Example: `DATABASE_URL=postgresql://user:password@localhost:5432/facestream`

3. **Create admin:**
   ```bash
   cd backend
   .\venv\Scripts\Activate.ps1
   python create_admin_direct.py
   ```

### Option 2: Use Cloud Database

If using a cloud database (Railway, Supabase, etc.):

1. **Get connection string** from your provider
2. **Update `.env`** with the connection string
3. **Run create script:**
   ```bash
   cd backend
   .\venv\Scripts\Activate.ps1
   python create_admin_direct.py
   ```

### Option 3: Quick Test (If Backend Already Running)

If your backend is already running and connected to database:

1. **Check backend health:**
   ```
   http://localhost:8000/health
   ```

2. **If healthy, the script should work:**
   ```bash
   cd backend
   .\venv\Scripts\Activate.ps1
   python create_admin_direct.py
   ```

## After Creating Admin

Once admin is created, you can:

1. **Login at:** http://localhost:3000
2. **Use credentials:**
   - Username: `123admin`
   - Password: `duyan2892006`

## Troubleshooting

### "Connection refused"
- PostgreSQL not running
- Check PostgreSQL service status
- Verify port 5432 is open

### "Database does not exist"
- Create database first:
  ```sql
  CREATE DATABASE facestream;
  ```

### "Authentication failed"
- Check username/password in DATABASE_URL
- Verify database user has permissions

## Next Steps

After creating admin:
1. ✅ Start backend: `python -m app.main`
2. ✅ Start frontend: `npm run dev` (in frontend folder)
3. ✅ Login at http://localhost:3000
4. ✅ Start testing!

