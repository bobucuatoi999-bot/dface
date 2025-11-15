# 🚀 Railway CLI Setup Guide

## ✅ Railway CLI Installed

Railway CLI is now installed (version 4.11.0).

---

## Step 1: Login to Railway

**You need to run this command in your terminal** (it will open a browser):

```bash
railway login
```

This will:
1. Open your default browser
2. Prompt you to login to Railway
3. Complete authentication
4. Save your credentials locally

---

## Step 2: Link to Your Project

After logging in, link to your Railway project:

```bash
railway link
```

This will:
1. Show a list of your Railway projects
2. Let you select your project
3. Link the current directory to that project

---

## Step 3: Create Admin User

Once linked, run the admin creation script:

```bash
railway run python create_admin_simple.py
```

This will:
1. Connect to your Railway database
2. Create the admin user (`admin` / `admin123`)
3. Show detailed output of each step
4. Verify the user was created successfully

---

## Step 4: Verify Admin User

After running the script, verify the admin user exists:

**Check the debug endpoint:**
```
https://testrtcc-production.up.railway.app/debug/users
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

**Try logging in:**
- Username: `admin`
- Password: `admin123`

---

## 📋 Quick Commands

```bash
# 1. Login (run in terminal - opens browser)
railway login

# 2. Link to project
railway link

# 3. Create admin user
railway run python create_admin_simple.py

# 4. Check Railway status
railway status

# 5. Check who you're logged in as
railway whoami
```

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

**Ready to proceed? Run `railway login` in your terminal now!**

