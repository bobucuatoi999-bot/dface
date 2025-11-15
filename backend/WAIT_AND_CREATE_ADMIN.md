# ⏳ Wait for Redeploy, Then Create Admin

## ✅ Fix Applied

I've fixed the bcrypt initialization issue in the `/debug/create-admin` endpoint. The fix:
- Uses `AuthService.get_password_hash()` instead of creating a new `CryptContext`
- This avoids the bcrypt initialization bug
- Changes are pushed to GitHub and Railway will redeploy automatically

---

## ⏳ Wait for Redeploy

Railway is now redeploying your backend with the fix. This usually takes **2-3 minutes**.

**Check deployment status:**
1. Railway Dashboard → Backend service (`testrtcc`)
2. Deployments tab → Latest deployment
3. Wait until status shows "Active" or "Deployed"

---

## 🚀 After Redeploy: Create Admin User

Once redeploy is complete, run this command:

```powershell
$response = Invoke-RestMethod -Uri "https://testrtcc-production.up.railway.app/debug/create-admin" -Method POST -ContentType "application/json"; $response | ConvertTo-Json -Depth 10
```

**Or check if admin was created:**
```powershell
Invoke-RestMethod -Uri "https://testrtcc-production.up.railway.app/debug/users" -Method GET | ConvertTo-Json
```

---

## ✅ Expected Response

**If successful:**
```json
{
  "status": "created",
  "message": "Admin user created successfully",
  "username": "admin",
  "password": "admin123",
  "id": 1,
  "email": "admin@facestream.local",
  "role": "admin",
  "is_active": true,
  "verified": true
}
```

**If admin already exists:**
```json
{
  "status": "exists",
  "message": "Admin user already exists: admin",
  "username": "admin",
  "id": 1
}
```

---

## 🔍 Verify Admin User

After creating admin, verify it exists:

```powershell
# Check users
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

After admin is created, try logging in:
- **Username:** `admin`
- **Password:** `admin123`

---

## ⏰ Next Steps

1. **Wait 2-3 minutes** for Railway redeploy
2. **Check deployment status** in Railway Dashboard
3. **Call the endpoint** to create admin user
4. **Verify admin exists** using `/debug/users`
5. **Try logging in** with `admin` / `admin123`

---

**After redeploy completes, I'll call the endpoint again to create the admin user!**

