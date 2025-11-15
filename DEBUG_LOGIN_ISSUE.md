# 🔍 Debug Login Issue - Step by Step

You're getting "Incorrect username or password" even with `admin` / `admin123`. Let's investigate!

---

## 🔍 Step 1: Check Backend Logs

1. **Railway Dashboard** → **Backend service** → **"Deployments"** → **"View Logs"**
2. Look for these messages around startup:

### What to Look For:

**If admin was created:**
```
✅ Auto-created admin user: admin
   Password: admin123
✅ Verified: User 'admin' exists in database
✅ Verified: Password verification works correctly
```

**If admin already exists:**
```
ℹ️  Admin user already exists: <username> (ID: <id>)
   Email: <email>
   Active: True/False
```

**If there was an error:**
```
❌ ERROR: Could not auto-create admin: <error message>
```

---

## 🔍 Step 2: Check What Users Exist

After Railway redeploys (with the new logging), check the logs. You should see one of the messages above.

**Or manually check using Railway CLI:**

```bash
railway run python check_users.py
```

This will show all users in the database.

---

## 🐛 Common Issues

### Issue 1: Admin User Doesn't Exist

**Symptoms:**
- Logs show: `No users found` or no admin creation message
- Login fails with "Incorrect username or password"

**Fix:**
The auto-create script should run on next deployment. Or manually create:

```bash
railway run python scripts/create_admin.py
```

### Issue 2: Admin Exists But Wrong Password

**Symptoms:**
- Logs show admin exists
- But login fails

**Fix:**
Reset password or create new admin with known password.

### Issue 3: Username Case Sensitivity

**Symptoms:**
- Trying `Admin` instead of `admin` fails

**Fix:**
Username is case-sensitive. Use exactly: `admin` (lowercase)

### Issue 4: User is Inactive

**Symptoms:**
- User exists but `is_active = False`

**Fix:**
Activate the user in database or create a new one.

---

## ✅ Quick Fix: Create Admin Manually

If auto-create isn't working, create admin manually:

### Using Railway CLI:

1. **Login to Railway CLI:**
   ```bash
   railway login
   ```
   (Opens browser - complete authentication)

2. **Link to project:**
   ```bash
   cd backend
   railway link
   ```
   (Select your project and backend service)

3. **Create admin:**
   ```bash
   railway run python scripts/create_admin.py
   ```
   (Enter username: `admin`, password: `admin123`)

4. **Try login again!**

---

## 🔍 Step 3: Check Backend Logs for Login Attempts

When you try to login, check backend logs for:

```
Login error: ...
```

This will show what's happening during authentication.

---

## 🎯 Most Likely Issue

Based on the error, here are the most likely causes:

1. **Admin user wasn't created yet** - Check logs for creation message
2. **Different username/password** - Check what admin exists in logs
3. **Password verification issue** - Check logs for verification errors

---

## 📋 Action Items

1. ✅ **Check Railway Backend Logs** - Look for admin creation messages
2. ✅ **Wait for redeployment** - New logging will show what's happening
3. ✅ **Try Railway CLI** - `railway run python check_users.py` to see users
4. ✅ **Create admin manually** - If auto-create didn't work

---

## 💡 After Checking Logs

Once you check the logs, you'll see:
- ✅ If admin was created → Use those credentials
- ❌ If admin wasn't created → Create manually
- ℹ️ If admin exists → Use that username (might be different)

**Share what you see in the logs and I'll help you fix it!**

