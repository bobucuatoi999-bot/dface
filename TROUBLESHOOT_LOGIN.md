# 🔍 Troubleshoot Login Issues

## Problem: `admin` / `admin123` Not Working

If you're getting "Incorrect username or password", let's debug step by step.

---

## 🔍 Step 1: Check if Admin User Exists

### Method 1: Use Debug Endpoint (Easiest)

After Railway redeploys, open this URL:

```
https://testrtcc-production.up.railway.app/debug/users
```

This will show:
- All users in database
- Their usernames
- Their roles
- Whether they're active

**Look for:**
- Username: `admin`
- Role: `admin`
- Active: `true`

### Method 2: Check Railway Database

1. Railway Dashboard → PostgreSQL → Database → `auth_users` table
2. Click on the `auth_users` table
3. Check if there's a user with:
   - `username`: `admin`
   - `role`: `admin`
   - `is_active`: `true`

---

## 🔍 Step 2: Check Backend Logs

### Check Admin Creation Logs

1. Railway Dashboard → Backend → Deployments → Latest → View Logs
2. Look for:

**If admin was created:**
```
✅ Auto-created admin user: admin
   Password: admin123
✅ Verified: User 'admin' exists in database
✅ Verified: Password verification works correctly
✅ Admin user is ready to use: username='admin', password='admin123'
```

**If admin already exists:**
```
ℹ️  Admin user already exists: admin (ID: 1)
   Email: admin@facestream.local
   Active: True
```

**If admin creation failed:**
```
❌ ERROR: Could not auto-create admin: ...
```

### Check Login Attempt Logs

1. Try logging in from frontend
2. Check backend logs immediately after
3. Look for:

**If user not found:**
```
Login attempt for username: 'admin'
User not found: 'admin'
Existing usernames in database: ['admin', 'user1']
```

**If password wrong:**
```
Login attempt for username: 'admin'
Verifying password for user: 'admin'
Password verification failed for user: 'admin'
```

**If login successful:**
```
Login attempt for username: 'admin'
Login successful for user: 'admin' (role: admin)
```

---

## 🔍 Step 3: Common Issues

### Issue 1: Admin User Doesn't Exist

**Symptoms:**
- `auth_users` table is empty
- Debug endpoint shows `total_users: 0`
- Logs show "No users found in database!"

**Fix:**
1. Check backend logs for admin creation errors
2. Manually create admin using Railway CLI:
   ```bash
   railway login
   railway link
   cd backend
   railway run python auto_create_admin.py
   ```

### Issue 2: Wrong Username

**Symptoms:**
- Logs show: `User not found: 'admin'`
- Logs show: `Existing usernames in database: ['123admin']`

**Fix:**
- Try the username shown in logs (might be `123admin` instead of `admin`)
- Or check the database for the actual username

### Issue 3: Password Verification Fails

**Symptoms:**
- Logs show: `Password verification failed for user: 'admin'`
- User exists but password doesn't work

**Possible Causes:**
1. Password hash is incorrect
2. Password was changed manually in database
3. Password hashing algorithm mismatch

**Fix:**
1. Delete the admin user from database
2. Let the auto_create_admin script recreate it
3. Or manually create admin using Railway CLI

### Issue 4: User Not Active

**Symptoms:**
- Logs show: `User 'admin' is not active`
- User exists but `is_active = false`

**Fix:**
1. Check database: `auth_users` table → `is_active` column
2. Should be `true` for admin user
3. If `false`, update it in database or recreate user

### Issue 5: Case-Sensitive Username

**Symptoms:**
- Logs show: `User not found: 'Admin'` (capital A)
- But user exists as `admin` (lowercase)

**Fix:**
- The login endpoint now uses case-insensitive lookup (`.ilike()`)
- But try both: `admin` and `Admin`

---

## 🔧 Quick Fixes

### Fix 1: Verify Admin User Exists

**Check debug endpoint:**
```
https://testrtcc-production.up.railway.app/debug/users
```

**Check database:**
- Railway Dashboard → PostgreSQL → Database → `auth_users`
- Look for user with `username = 'admin'`

### Fix 2: Check Backend Logs

**Check admin creation:**
- Railway Dashboard → Backend → Deployments → View Logs
- Look for "Auto-created admin user" or "Admin user already exists"

**Check login attempts:**
- Try logging in
- Check logs immediately after
- Look for "Login attempt" and "Password verification"

### Fix 3: Recreate Admin User

**Using Railway CLI:**
```bash
railway login
railway link
cd backend
railway run python auto_create_admin.py
```

**Or delete and let auto-create:**
1. Delete admin user from database
2. Redeploy backend (admin will be auto-created)

---

## 📋 What to Share

After checking, share:

1. **What the debug endpoint shows:**
   - `https://testrtcc-production.up.railway.app/debug/users`
   - How many users exist?
   - What are their usernames?

2. **What the backend logs show:**
   - Did admin creation succeed?
   - What does login attempt log show?
   - Any error messages?

3. **What the database shows:**
   - Does `auth_users` table have any users?
   - What's the username?
   - What's the `is_active` value?

---

## 💡 Most Likely Issues

Based on "wrong credentials" error:

1. **Admin user doesn't exist** - Check if auto_create_admin script ran
2. **Wrong username** - Check actual username in database
3. **Password hash issue** - Password verification failing
4. **User not active** - `is_active = false`

**Check the debug endpoint first - it will show exactly what users exist!**

---

## 🎯 Next Steps

1. ✅ **Check debug endpoint** - See what users exist
2. ✅ **Check backend logs** - See if admin was created
3. ✅ **Check login logs** - See what's happening during login
4. ✅ **Share the results** - I'll help fix the issue

---

**The debug endpoint will show exactly what's in the database!**

