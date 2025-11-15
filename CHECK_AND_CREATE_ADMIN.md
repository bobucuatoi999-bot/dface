# 🔐 Check Credentials & Create Admin User

## ✅ Database Connection is Working!

The "Incorrect username or password" error means the database is connected, but there's no admin user yet (or the credentials are wrong).

---

## 🔍 Step 1: Check What Users Exist in Database

### Option A: Using Railway Console (Easiest)

1. **Railway Dashboard** → **Backend service** → **"Deployments"** → **"View Logs"**
2. Click **"Shell"** or **"Console"** tab
3. Run this Python command:

```python
python -c "
from app.database import SessionLocal
from app.models.auth import AuthUser
db = SessionLocal()
users = db.query(AuthUser).all()
print('\\n=== Existing Users ===')
for u in users:
    print(f'ID: {u.id}, Username: {u.username}, Role: {u.role.value}, Email: {u.email}')
if not users:
    print('No users found in database!')
db.close()
"
```

This will show all existing users.

### Option B: Using Railway CLI

```bash
railway run python -c "
from app.database import SessionLocal
from app.models.auth import AuthUser
db = SessionLocal()
users = db.query(AuthUser).all()
for u in users:
    print(f'{u.username} ({u.role.value})')
db.close()
"
```

---

## 🆕 Step 2: Create Admin User

### Method 1: Using Railway Console (Recommended)

1. **Railway Dashboard** → **Backend service** → **"Deployments"** → **"View Logs"**
2. Click **"Shell"** or **"Console"** tab
3. Run:

```bash
python scripts/create_admin.py
```

4. Follow the prompts:
   - Enter username (e.g., `admin`)
   - Enter password (at least 6 characters)
   - Enter email (optional)

### Method 2: Using Railway CLI

```bash
railway run python scripts/create_admin.py
```

### Method 3: Direct Script (Non-Interactive)

If you want to create with specific credentials, edit `backend/create_admin_direct.py`:

```python
username = "admin"  # Change this
password = "your_password_here"  # Change this
email = "admin@example.com"  # Change this
```

Then run:
```bash
railway run python create_admin_direct.py
```

### Method 4: Using Python Directly in Railway Console

1. Railway Console → Run:

```python
from app.database import SessionLocal, init_db
from app.models.auth import AuthUser, UserRole
from app.services.auth_service import AuthService

# Initialize database
init_db()

db = SessionLocal()
auth_service = AuthService()

# Create admin
username = "admin"
password = "your_secure_password"
email = "admin@example.com"

admin = auth_service.create_user(
    db=db,
    username=username,
    password=password,
    email=email,
    role=UserRole.ADMIN
)

db.commit()
print(f"✅ Admin created: {username}")
print(f"Password: {password}")
db.close()
```

---

## 📋 Database Structure

Your database has a table called `auth_users` with these fields:

- `id` - User ID
- `username` - Login username (unique)
- `email` - Email address (optional, unique)
- `hashed_password` - Encrypted password (bcrypt)
- `role` - User role: `admin`, `operator`, or `viewer`
- `is_active` - Whether user is active
- `created_at` - When user was created
- `last_login` - Last login timestamp

---

## 🔑 Default Credentials (If Created Earlier)

If you ran `create_admin_direct.py` before, it might have created:

- **Username:** `123admin`
- **Password:** `duyan2892006`
- **Email:** `admin@facestream.local`

Try logging in with these credentials first!

---

## ✅ Verify Login Works

After creating admin user, test login:

### Using Frontend:
1. Go to your frontend URL
2. Enter username and password
3. Click Login

### Using API (Test):
```bash
curl -X POST https://testrtcc-production.up.railway.app/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your_password"
```

Should return:
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

---

## 🐛 Troubleshooting

### "No users found"
- Create an admin user using Method 1 or 2 above

### "Username already exists"
- User exists, but password might be wrong
- Reset password using Method 4 (update existing user)

### "Password incorrect"
- Check if you're using the right username
- Create a new admin user with different username
- Or reset password for existing user

---

## 💡 Quick Commands Reference

**Check users:**
```python
python -c "from app.database import SessionLocal; from app.models.auth import AuthUser; db = SessionLocal(); [print(f'{u.username} ({u.role.value})') for u in db.query(AuthUser).all()]; db.close()"
```

**Create admin (interactive):**
```bash
python scripts/create_admin.py
```

**Create admin (direct):**
```bash
python create_admin_direct.py
```

---

## 🎯 Recommended: Create Admin Now

**Quickest way:**

1. Railway Dashboard → Backend → Console
2. Run:
```bash
python scripts/create_admin.py
```
3. Enter:
   - Username: `admin`
   - Password: `your_secure_password` (at least 6 chars)
   - Email: `admin@example.com` (optional)
4. Try logging in!

---

**After creating admin, you should be able to login!** 🎉

