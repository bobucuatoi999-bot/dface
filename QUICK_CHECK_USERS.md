# 🔍 Quick Check: What Users Exist?

## ✅ Yes, `admin` / `admin123` Should Work!

But first, let's verify the admin user was actually created.

---

## 🌐 Method 1: Check Debug Endpoint (Easiest!)

After Railway redeploys (2-3 minutes), open this URL in your browser:

```
https://testrtcc-production.up.railway.app/debug/users
```

This will show you:
- All users in the database
- Their usernames
- Their roles
- Whether they're active

**Look for:**
- Username: `admin`
- Role: `admin`
- Active: `true`

---

## 📋 Method 2: Check Backend Logs

1. **Railway Dashboard** → **Backend service** → **Deployments** → **View Logs**
2. Look for these messages:

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
```

---

## 🎯 What to Look For

### Scenario 1: Admin User Exists
- **Username:** `admin`
- **Role:** `admin`
- **Active:** `true`

→ Try logging in with: `admin` / `admin123`

### Scenario 2: Different Username
- **Username:** `123admin` (or something else)
- **Role:** `admin`

→ Try logging in with that username and password `admin123` or `duyan2892006`

### Scenario 3: No Users
- **Total users:** 0

→ Admin will be auto-created on next deployment, or create manually

---

## 🔧 Quick Fix: Create Admin Now

If no admin exists, the auto-create script will run on next deployment.

**Or manually create via Railway CLI:**

```bash
railway login
cd backend
railway link
railway run python scripts/create_admin.py
```

Then enter:
- Username: `admin`
- Password: `admin123`

---

## ✅ After Checking

1. **Check the debug endpoint:** `https://testrtcc-production.up.railway.app/debug/users`
2. **See what users exist**
3. **Try logging in with the username shown**
4. **If password is wrong, check logs for the actual password**

---

## 💡 Most Likely Issue

The admin might have been created with:
- **Username:** `123admin` (from `create_admin_direct.py`)
- **Password:** `duyan2892006`

Try these credentials first:
- Username: `123admin`
- Password: `duyan2892006`

---

**Check the debug endpoint first - it will show exactly what users exist!**

