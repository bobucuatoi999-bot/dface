# 🚀 Run Admin Creation via Railway CLI

## ✅ Railway CLI is Linked

Your project is linked to Railway. Now we can run the script directly in Railway's environment.

---

## 🎯 Most Reliable Method

**Run this command in your terminal:**

```bash
cd C:\Users\Admin\Documents\wps\lfaceide\backend
railway run python create_admin_sql.py
```

This will:
1. Connect to your Railway database
2. Create admin user using bcrypt directly
3. Show detailed output
4. Verify the user was created

---

## ⏳ Wait for Railway Redeploy First

Railway is currently redeploying with the bcrypt fixes. 

**Check deployment status:**
1. Railway Dashboard → Backend service
2. Deployments tab → Latest deployment
3. Wait for status: "Active" or "Deployed"

**Estimated time:** 3-5 minutes

---

## ✅ After Redeploy: Run the Script

Once redeploy is complete, run:

```bash
railway run python create_admin_sql.py
```

**Expected output:**
```
============================================================
  Creating Admin User (SQL Direct Method)
============================================================

Step 1: Ensuring database tables exist...
✓ Database tables exist

Step 2: Connecting to database...
✓ Connected to database

Step 3: Checking if admin user exists...
   Username: admin
✓ No admin user found - will create one

Step 4: Creating admin user...
   Username: admin
   Email: admin@facestream.local
   Role: admin
   Hashing password with bcrypt...
✓ Password hashed
✓ User added to session
✓ Transaction committed
✓ User refreshed (ID: 1)

Step 5: Verifying admin user...
✅ User exists in database (ID: 1)
   Username: admin
   Email: admin@facestream.local
   Role: admin
   Active: True
   Testing password verification...
✅ Password verification works correctly

============================================================
  ✅ SUCCESS: Admin user created successfully!
============================================================

Username: admin
Password: admin123
Email: admin@facestream.local

You can now login with these credentials!
```

---

## 🔍 Verify Admin User

After running the script, verify:

**Check debug endpoint:**
```powershell
Invoke-RestMethod -Uri "https://testrtcc-production.up.railway.app/debug/users" -Method GET | ConvertTo-Json
```

Should show:
```json
{
  "total_users": 1,
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@facestream.local",
      "role": "admin",
      "is_active": true
    }
  ],
  "admin_count": 1
}
```

---

## 🎯 Try Logging In

After admin is created:
- **Username:** `admin`
- **Password:** `admin123`

---

## 💡 Why This Script Works

The `create_admin_sql.py` script:
- ✅ Uses bcrypt directly (no passlib issues)
- ✅ Runs in Railway environment (has database access)
- ✅ Creates user directly in database
- ✅ Verifies password works correctly
- ✅ Shows detailed output

---

## 📋 Next Steps

1. ✅ **Wait 3-5 minutes** for Railway redeploy
2. ✅ **Run Railway CLI script:**
   ```bash
   railway run python create_admin_sql.py
   ```
3. ✅ **Verify admin exists** using `/debug/users`
4. ✅ **Try logging in** with `admin` / `admin123`

---

**This is the most reliable method - it runs directly in Railway with full database access!**

