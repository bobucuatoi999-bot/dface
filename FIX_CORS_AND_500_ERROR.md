# 🔧 Fix CORS and 500 Error - Step by Step

## Problem

You're seeing:
- **CORS Error**: `Access to XMLHttpRequest ... has been blocked by CORS policy`
- **500 Internal Server Error**: `POST ... net::ERR_FAILED 500`

## Root Causes

1. **CORS**: Backend `CORS_ORIGINS` environment variable doesn't include your frontend URL
2. **500 Error**: Likely a database connection issue or missing configuration

---

## ✅ Solution: Set Backend Environment Variables

### Step 1: Go to Railway Backend Service

1. Railway Dashboard → **Backend service** (testrtcc-production)
2. Click **"Variables"** tab

### Step 2: Add/Update CORS_ORIGINS

Add or update this variable:

```
Name:  CORS_ORIGINS
Value: https://testrtcc-production-2f74.up.railway.app
```

**Important:** Use your exact frontend URL (the one showing in the error).

### Step 3: Verify Other Required Variables

Make sure these are also set:

```
DATABASE_URL = (should be auto-set by Railway from PostgreSQL)
SECRET_KEY = (should be a strong random string)
DEBUG = False
LOG_LEVEL = INFO
```

### Step 4: Save and Redeploy

1. Click **"Save"** or **"Add"** for the variable
2. Railway will automatically redeploy
3. Wait 2-3 minutes for deployment

---

## 🔍 Check Backend Logs for 500 Error

After setting CORS_ORIGINS, check if the 500 error persists:

1. Railway Dashboard → Backend service → **"Deployments"** → **"View Logs"**
2. Look for error messages around the time you tried to login
3. Common causes of 500 errors:

### Common 500 Error Causes:

#### 1. Database Connection Issue
```
Error: could not connect to database
```
**Fix:** Verify `DATABASE_URL` is set correctly

#### 2. Missing SECRET_KEY
```
Error: SECRET_KEY not set
```
**Fix:** Set `SECRET_KEY` to a random string (generate one below)

#### 3. Auth Service Error
```
Error in authenticate_user
```
**Fix:** Check if admin user exists (see below)

---

## 🔑 Generate SECRET_KEY (if needed)

If `SECRET_KEY` is missing or weak, generate a new one:

**Option 1: Using Python**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Option 2: Using OpenSSL**
```bash
openssl rand -hex 32
```

Then set it in Railway Backend → Variables:
```
SECRET_KEY = <generated-key>
```

---

## 👤 Create Admin User (if login fails)

If you don't have an admin user yet, create one:

### Method 1: Using Railway CLI

```bash
railway run python scripts/create_admin.py
```

### Method 2: Using Railway Console

1. Railway Dashboard → Backend service → **"Deployments"** → **"View Logs"**
2. Click **"Shell"** or **"Console"** tab
3. Run:
```bash
python scripts/create_admin.py
```

### Method 3: Using API (if backend is running)

```bash
curl -X POST https://testrtcc-production.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your-secure-password",
    "email": "admin@example.com",
    "role": "admin"
  }'
```

**Note:** This requires an existing admin user. If you don't have one, use Method 1 or 2.

---

## ✅ Complete Checklist

- [ ] Set `CORS_ORIGINS` = `https://testrtcc-production-2f74.up.railway.app`
- [ ] Verify `DATABASE_URL` is set (from PostgreSQL service)
- [ ] Verify `SECRET_KEY` is set (strong random string)
- [ ] Set `DEBUG=False`
- [ ] Set `LOG_LEVEL=INFO`
- [ ] Wait for backend redeployment
- [ ] Check backend logs for errors
- [ ] Verify admin user exists
- [ ] Test login from frontend

---

## 🧪 Test After Fix

1. **Test Backend Health:**
   ```
   https://testrtcc-production.up.railway.app/health
   ```
   Should return: `{"status": "healthy", ...}`

2. **Test Login from Frontend:**
   - Open frontend: `https://testrtcc-production-2f74.up.railway.app`
   - Try logging in
   - Check browser console (F12) - should see no CORS errors
   - Check Network tab - login request should return 200 (not 500)

---

## 🐛 Still Getting 500 Error?

If CORS is fixed but you still get 500:

1. **Check Backend Logs:**
   - Railway Dashboard → Backend → View Logs
   - Look for Python traceback/error messages
   - Common issues:
     - Database connection failed
     - Missing environment variable
     - Import error (face recognition packages)

2. **Check Database Connection:**
   - Verify PostgreSQL service is running
   - Verify `DATABASE_URL` is correct
   - Try using `DATABASE_PUBLIC_URL` if internal URL doesn't work

3. **Check Admin User Exists:**
   - If no admin user, create one using methods above
   - Verify username/password are correct

---

## 📝 Quick Fix Summary

**In Railway Backend → Variables, set:**

```
CORS_ORIGINS = https://testrtcc-production-2f74.up.railway.app
```

**Then:**
1. Save
2. Wait for redeployment
3. Test login

---

## 💡 Pro Tip

If you have multiple frontend URLs (e.g., custom domain + Railway domain), separate them with commas:

```
CORS_ORIGINS = https://testrtcc-production-2f74.up.railway.app,https://your-custom-domain.com
```

---

**After setting CORS_ORIGINS, the CORS error should be fixed. If you still get a 500 error, check the backend logs to see what's causing it.**

