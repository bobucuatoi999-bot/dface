# 🖥️ Railway CLI Setup - Alternative to Web Console

Since Railway's web console isn't showing, we'll use **Railway CLI** instead. It's a command-line tool that lets you run commands in your Railway services.

---

## 📥 Step 1: Install Railway CLI

### Option A: Using npm (Node.js)

If you have Node.js installed:

```bash
npm install -g @railway/cli
```

### Option B: Using PowerShell (Windows)

```powershell
# Download and install Railway CLI
iwr https://railway.app/install.ps1 | iex
```

### Option C: Using Scoop (Windows)

```bash
scoop install railway
```

### Option D: Using Chocolatey (Windows)

```bash
choco install railway
```

---

## 🔐 Step 2: Login to Railway

Open PowerShell or Command Prompt and run:

```bash
railway login
```

This will open your browser to authenticate. After logging in, you're connected!

---

## 🔗 Step 3: Link to Your Project

Navigate to your project directory (or any directory):

```bash
cd C:\Users\Admin\Documents\wps\lfaceide\backend
```

Then link to your Railway project:

```bash
railway link
```

You'll be prompted to:
1. Select your Railway account
2. Select your project
3. Select your service (backend)

---

## ✅ Step 4: Run Commands

Now you can run commands in your Railway service!

### Check Users in Database

```bash
railway run python -c "from app.database import SessionLocal; from app.models.auth import AuthUser; db = SessionLocal(); users = db.query(AuthUser).all(); print('Users:', [(u.username, u.role.value) for u in users] if users else 'No users'); db.close()"
```

### Create Admin User (Interactive)

```bash
railway run python scripts/create_admin.py
```

### Create Admin User (Direct Script)

```bash
railway run python create_admin_direct.py
```

---

## 🎯 Quick Setup Commands

**Copy and paste these one by one:**

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Navigate to backend folder
cd C:\Users\Admin\Documents\wps\lfaceide\backend

# 4. Link to project
railway link

# 5. Create admin user
railway run python scripts/create_admin.py
```

---

## 🔍 Alternative: Check Users via API

If CLI is too complicated, you can also check if users exist by trying to query the database through a simple Python script.

---

## 💡 Even Simpler: Create Admin via Direct Script

If you want to avoid interactive prompts, edit `backend/create_admin_direct.py`:

1. Open `backend/create_admin_direct.py`
2. Change these lines:
   ```python
   username = "admin"  # Your desired username
   password = "your_password_here"  # Your desired password
   email = "admin@example.com"  # Your email
   ```
3. Save the file
4. Push to GitHub (Railway will auto-deploy)
5. Then run via Railway CLI:
   ```bash
   railway run python create_admin_direct.py
   ```

---

## 🐛 Troubleshooting

### "railway: command not found"
- Make sure Railway CLI is installed
- Try: `npm install -g @railway/cli` again
- Restart your terminal/PowerShell

### "Not logged in"
- Run: `railway login`
- Make sure you complete the browser authentication

### "No project linked"
- Run: `railway link`
- Select your project and service

---

## 📝 What Railway CLI Does

Railway CLI runs commands **inside your Railway service container**, just like the web console would. It's the same thing, just from your local terminal!

---

## ✅ Summary

**Since web console isn't available:**
1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Link project: `cd backend && railway link`
4. Run commands: `railway run python scripts/create_admin.py`

**This is equivalent to using the web console!** 🎉

