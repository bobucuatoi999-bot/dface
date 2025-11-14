# 🚨 Quick Fix: 502 Bad Gateway Error

## ⚠️ What 502 Error Means

**502 Bad Gateway** = Backend server is **DOWN** or **NOT STARTING**

The CORS error is a **side effect** - if the backend is down, it can't send CORS headers.

---

## 🔍 Step 1: Check Railway Backend Logs

**This is THE MOST IMPORTANT step!**

### How to Check Logs:

1. **Railway Dashboard** → Your Project
2. **Backend service** (`testrtcc-production`)
3. **"Deployments"** tab → **Latest deployment**
4. **"View Logs"** tab
5. **Scroll to the bottom** - look for the LAST error message

### What to Look For:

**✅ If backend started successfully:**
```
✓ DATABASE_URL is configured
✓ Database migrations completed successfully
✓ Application import successful
Starting uvicorn...
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**❌ If backend failed to start:**
```
❌ ERROR: ...
Traceback (most recent call last):
  ...
```

---

## 🐛 Common Causes & Fixes

### 1. Database Connection Failed

**Symptoms:**
- Logs show: `Database connection failed`
- Logs show: `could not connect to database`
- Logs show: `FATAL: database "..." does not exist`

**Fix:**
1. Railway Dashboard → Backend → Variables
2. Find `DATABASE_URL`
3. **Make sure there's NO trailing space!**
4. Should be: `postgresql://user:pass@host:port/database` (no space at end)
5. Save and wait for redeploy

### 2. Import Error

**Symptoms:**
- Logs show: `ImportError: ...`
- Logs show: `ModuleNotFoundError: ...`

**Fix:**
- Check if all dependencies are in `requirements.txt`
- Railway will rebuild automatically after you push to GitHub

### 3. Application Crash on Startup

**Symptoms:**
- Logs show: `Traceback (most recent call last)`
- Logs show: `Exception: ...`

**Fix:**
- Check the error message in logs
- That's what's causing the 502
- Share the error message and I'll help fix it

### 4. DATABASE_URL Not Set

**Symptoms:**
- Logs show: `ERROR: DATABASE_URL environment variable is not set!`

**Fix:**
1. Railway Dashboard → Backend → Variables
2. Add variable:
   - **Name:** `DATABASE_URL`
   - **Value:** `{{Postgres.DATABASE_URL}}` (replace `Postgres` with your PostgreSQL service name)
3. Save and wait for redeploy

---

## ✅ Quick Checklist

1. ✅ **Check Railway Backend Logs** - Look for the LAST error message
2. ✅ **Verify DATABASE_URL** - Make sure it's set and has NO trailing space
3. ✅ **Check if backend is running** - Look for "Uvicorn running" in logs
4. ✅ **Check for import errors** - Look for "ImportError" in logs
5. ✅ **Check for database errors** - Look for "database" errors in logs

---

## 📋 What to Share

After checking the logs, share:

1. **The LAST error message** in the logs (the one that's causing the 502)
2. **Any traceback/stack trace** shown
3. **Whether you see "Uvicorn running"** in logs (yes/no)
4. **What the DATABASE_URL looks like** (masked, like `postgresql://user:***@host:port/db`)

---

## 🎯 Most Likely Issue

Based on the 502 error, the backend is likely:

1. **Crashing on startup** - Check logs for the error
2. **Database connection failing** - Check DATABASE_URL (no trailing space!)
3. **Import error** - Check if dependencies are installed
4. **Port issue** - Backend should use `PORT` environment variable (Railway sets this automatically)

---

## 💡 Next Steps

1. **Check Railway Backend Logs** - This will show the exact error
2. **Share the error message** - I'll help fix it
3. **Wait for redeploy** - After fixing, Railway will automatically redeploy (2-3 minutes)

---

**Check the Railway logs first - that will tell you exactly what's wrong!**

