# 🚨 Debug 502 Bad Gateway Error

## What 502 Error Means

**502 Bad Gateway** = Backend server is **DOWN** or **NOT STARTING**

This is different from:
- **500 Internal Server Error** = Server is running but has an error
- **502 Bad Gateway** = Server is NOT running at all

---

## 🔍 Step 1: Check Railway Backend Logs

**This is the MOST IMPORTANT step!**

1. **Railway Dashboard** → **Backend service** (`testrtcc-production`)
2. **"Deployments"** tab → **Latest deployment**
3. **"View Logs"** tab
4. **Look for errors** around startup

### What to Look For:

**If backend started successfully:**
```
✓ DATABASE_URL is configured
✓ Database migrations completed successfully
✓ Application import successful
Starting uvicorn...
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**If backend failed to start:**
```
❌ ERROR: ...
Traceback (most recent call last):
  ...
```

---

## 🐛 Common Causes of 502 Error

### 1. Database Connection Failed

**Symptoms:**
- Logs show: `Database connection failed`
- Logs show: `could not connect to database`

**Fix:**
- Verify `DATABASE_URL` is set correctly in Railway
- Make sure there's no trailing space
- Try using `DATABASE_PUBLIC_URL` if internal URL doesn't work

### 2. Import Error

**Symptoms:**
- Logs show: `ImportError: ...`
- Logs show: `ModuleNotFoundError: ...`

**Fix:**
- Check if all dependencies are installed
- Check `requirements.txt` includes all packages
- Rebuild the Docker image

### 3. Application Crash on Startup

**Symptoms:**
- Logs show: `Traceback (most recent call last)`
- Logs show: `Exception: ...`

**Fix:**
- Check the error message in logs
- Fix the underlying issue
- Redeploy

### 4. Port Conflict

**Symptoms:**
- Logs show: `Address already in use`
- Logs show: `Port 8000 is already in use`

**Fix:**
- Railway sets `PORT` environment variable automatically
- Make sure your app uses `PORT` environment variable, not hardcoded `8000`

### 5. Container Out of Memory

**Symptoms:**
- Logs show: `Killed` or `Out of memory`
- Container restarts continuously

**Fix:**
- Upgrade Railway plan
- Reduce memory usage
- Check for memory leaks

---

## ✅ Quick Checks

### Check 1: Is DATABASE_URL Set?

**Railway Dashboard** → **Backend service** → **Variables** → Look for `DATABASE_URL`

**Should be:**
```
postgresql://user:pass@host:port/database
```

**Should NOT be:**
```
postgresql://user:pass@host:port/database 
```
(no trailing space!)

### Check 2: Are Dependencies Installed?

Check if `requirements.txt` has all packages. Common ones:
- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `psycopg2-binary`
- `pydantic`
- `python-jose`
- `passlib`
- `bcrypt`

### Check 3: Is the App Starting?

Check logs for:
```
Starting uvicorn...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

If you don't see this, the app isn't starting.

---

## 🔧 Quick Fixes

### Fix 1: Check DATABASE_URL

1. Railway Dashboard → Backend → Variables
2. Find `DATABASE_URL`
3. Make sure it's correct (no trailing spaces!)
4. Save and wait for redeploy

### Fix 2: Check Backend Logs

1. Railway Dashboard → Backend → Deployments → View Logs
2. Look for the LAST error message
3. That's what's causing the 502

### Fix 3: Verify Environment Variables

Make sure these are set:
- `DATABASE_URL` (required)
- `SECRET_KEY` (recommended)
- `CORS_ORIGINS` (optional, but recommended)

---

## 📋 Action Items

1. ✅ **Check Railway Backend Logs** - This will show the exact error
2. ✅ **Verify DATABASE_URL** - Make sure it's set and correct
3. ✅ **Check if backend is running** - Look for "Uvicorn running" in logs
4. ✅ **Check for import errors** - Look for "ImportError" in logs
5. ✅ **Check for database errors** - Look for "database" errors in logs

---

## 💡 What to Share

After checking the logs, share:

1. **The LAST error message** in the logs
2. **Any traceback/stack trace** shown
3. **Whether you see "Uvicorn running"** in logs
4. **What the DATABASE_URL looks like** (masked, like `postgresql://user:***@host:port/db`)

---

## 🎯 Most Likely Issue

Based on the 502 error, the backend is likely:

1. **Crashing on startup** - Check logs for the error
2. **Database connection failing** - Check DATABASE_URL
3. **Import error** - Check if dependencies are installed
4. **Port issue** - Check if PORT environment variable is used

**Check the Railway logs first - that will tell you exactly what's wrong!**

