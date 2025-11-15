# 🖥️ How to Access Railway Console

Railway Console is a **web-based terminal** that lets you run commands directly in your deployed service.

---

## 📍 Step-by-Step: Access Railway Console

### Step 1: Go to Railway Dashboard

1. Open your browser
2. Go to: **https://railway.app**
3. Log in to your Railway account

### Step 2: Select Your Backend Service

1. In Railway Dashboard, you'll see your projects
2. Click on your **project** (the one with your backend)
3. You'll see your services listed:
   - Backend service (e.g., `testrtcc-production`)
   - PostgreSQL service
   - Frontend service (if deployed)

4. **Click on your Backend service** (`testrtcc-production`)

### Step 3: Open Console/Shell

You have **two ways** to access the console:

#### Method 1: Via Deployments Tab (Recommended)

1. Click on **"Deployments"** tab (at the top)
2. Click on the **latest deployment** (most recent one)
3. Look for **"View Logs"** button
4. In the logs view, look for tabs:
   - **"Logs"** (default)
   - **"Shell"** or **"Console"** ← Click this!

#### Method 2: Via Service Overview

1. In your Backend service page
2. Look for a button/tab called:
   - **"Shell"**
   - **"Console"**
   - **"Terminal"**
   - Or an icon that looks like `>_` (terminal icon)

3. Click it!

---

## 🖼️ Visual Guide

```
Railway Dashboard
  └─ Your Project
      └─ Backend Service (testrtcc-production)
          ├─ Overview
          ├─ Deployments ← Click here
          │   └─ Latest Deployment
          │       └─ View Logs
          │           ├─ Logs tab
          │           └─ Shell/Console tab ← Click here!
          ├─ Variables
          └─ Settings
```

---

## ✅ What You'll See

Once you open the Console, you'll see:

```
$ 
```

This is a command prompt where you can type commands.

---

## 🧪 Test It Works

Try typing:
```bash
ls
```

You should see files and folders listed.

---

## 📝 Common Commands You'll Need

### Check Python Version
```bash
python --version
```

### Check Current Directory
```bash
pwd
```

### List Files
```bash
ls -la
```

### Check Users in Database
```python
python -c "from app.database import SessionLocal; from app.models.auth import AuthUser; db = SessionLocal(); users = db.query(AuthUser).all(); print('Users:', [(u.username, u.role.value) for u in users] if users else 'No users'); db.close()"
```

### Create Admin User
```bash
python scripts/create_admin.py
```

---

## 🎯 Quick Access Path

**Fastest way:**

1. **Railway Dashboard** → Your Project
2. **Backend Service** → **"Deployments"** tab
3. **Latest Deployment** → **"View Logs"**
4. **"Shell"** or **"Console"** tab (next to "Logs" tab)

---

## 💡 Alternative: Railway CLI

If you prefer command line, you can also use Railway CLI:

### Install Railway CLI
```bash
npm install -g @railway/cli
```

### Login
```bash
railway login
```

### Link to Project
```bash
railway link
```

### Run Commands
```bash
railway run python scripts/create_admin.py
```

But the **web console is easier** for quick tasks!

---

## 🐛 Can't Find Console?

If you don't see "Shell" or "Console" tab:

1. **Make sure you're in the Backend service** (not PostgreSQL or Frontend)
2. **Check if deployment is active** - Console only works if service is running
3. **Try refreshing the page**
4. **Look for "Terminal" icon** in the top menu

---

## 📸 What It Looks Like

The Railway Console looks like a terminal/command prompt:
- Black or dark background
- White/green text
- Command prompt: `$` or `#`
- You can type commands and press Enter

---

## ✅ Summary

**Railway Console = Web-based Terminal**

**Access:**
1. Railway Dashboard → Your Project
2. Backend Service → Deployments
3. Latest Deployment → View Logs
4. **Shell/Console tab** ← This is it!

**It's a web console** - no need to install anything, just use your browser!

---

**Once you're in the console, you can run Python commands to check users and create admin accounts!** 🎉

