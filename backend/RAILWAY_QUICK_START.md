# 🚀 Railway CLI Quick Start

## ✅ Railway CLI is Installed

Railway CLI is ready to use. Now you need to authenticate and link your project.

---

## Step 1: Login to Railway (Run in Your Terminal)

**Open your terminal/PowerShell and run:**

```powershell
cd C:\Users\Admin\Documents\wps\lfaceide\backend
railway login
```

This will:
1. Open your default browser
2. Prompt you to login to Railway
3. Complete authentication
4. Save your credentials locally

**After logging in, return to your terminal.**

---

## Step 2: Link to Your Project

**In your terminal, run:**

```powershell
railway link
```

This will:
1. Show a list of your Railway projects
2. Select your project (use arrow keys)
3. Link the current directory to that project

---

## Step 3: Create Admin User (After Login & Link)

**After completing Step 1 and Step 2, I can run this for you:**

```powershell
railway run python create_admin_simple.py
```

Or you can run it yourself:
```powershell
railway run python create_admin_simple.py
```

Or use the PowerShell script:
```powershell
.\create_admin_now.ps1
```

---

## 📋 Complete Command Sequence

**Run these commands in your terminal:**

```powershell
# 1. Navigate to backend directory
cd C:\Users\Admin\Documents\wps\lfaceide\backend

# 2. Login to Railway (opens browser)
railway login

# 3. Link to your project (select from list)
railway link

# 4. Create admin user
railway run python create_admin_simple.py
```

---

## ✅ After Admin User is Created

1. **Verify admin exists:**
   ```
   https://testrtcc-production.up.railway.app/debug/users
   ```

2. **Try logging in:**
   - Username: `admin`
   - Password: `admin123`

---

## 🔍 Troubleshooting

**If `railway login` doesn't open browser:**
- Manually go to: https://railway.app/login
- Login there
- Then run `railway login` again

**If `railway link` doesn't show your project:**
- Make sure you're logged in: `railway whoami`
- Check you're in the backend directory
- Try `railway link` again

**If script fails:**
- Check backend logs in Railway Dashboard
- Make sure DATABASE_URL is set in Railway
- Verify database connection is working

---

## 💡 What Happens Next

After you complete `railway login` and `railway link`, tell me and I'll:
1. Run the admin creation script for you
2. Verify the admin user was created
3. Check the debug endpoint
4. Test the login

---

**Ready? Run `railway login` in your terminal now, then come back here!**

