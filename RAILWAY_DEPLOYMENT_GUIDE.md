# 🚀 Railway Deployment Guide

Complete guide to deploy FaceStream Backend and Frontend to Railway.

## 📋 Prerequisites

- ✅ Railway account (you mentioned you already have one)
- ✅ GitHub account
- ✅ Domain names for backend and frontend (optional, Railway provides free domains)

## 🌐 Global Access

**Yes, it will work globally!** Once deployed on Railway:
- ✅ Backend will be accessible from anywhere via HTTPS
- ✅ Frontend will be accessible from anywhere via HTTPS
- ✅ Railway provides free SSL certificates
- ✅ You can use custom domains
- ✅ Works on mobile, desktop, and any device with internet

---

## 📦 Step 1: Prepare GitHub Repository

### 1.1 Initialize Git (if not already done)

```bash
cd C:\Users\Admin\Documents\wps\lfaceide
git init
```

### 1.2 Create Root .gitignore

The root `.gitignore` should exclude:
- Backend `.env` files
- Frontend `node_modules`
- Virtual environments
- Build artifacts

### 1.3 Commit and Push to GitHub

```bash
# Add all files
git add .

# Commit
git commit -m "Initial commit: FaceStream Recognition System"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/facestream.git
git branch -M main
git push -u origin main
```

---

## 🔧 Step 2: Deploy Backend to Railway

### 2.1 Create New Project on Railway

1. Go to [Railway Dashboard](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Select the `backend` folder as the root directory

### 2.2 Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically create a PostgreSQL database
4. Note the connection details (you'll need them)

### 2.3 Configure Environment Variables

In Railway project settings, add these environment variables:

```env
# Database (Railway will auto-inject this, but you can override)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=$PORT

# Security (IMPORTANT: Generate a strong secret key!)
SECRET_KEY=your-super-secret-key-here-generate-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS - Add your frontend domain(s)
CORS_ORIGINS=https://your-frontend-domain.railway.app,https://your-custom-domain.com

# Face Recognition (optional - can leave defaults)
FACE_RECOGNITION_MODEL=hog
FACE_MATCH_THRESHOLD=0.6
FACE_CONFIDENCE_THRESHOLD=0.85
MAX_FRAME_RATE=5
MIN_FACE_SIZE=100

# Redis (optional - disable if not using)
REDIS_ENABLED=False
```

**🔑 Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.4 Deploy Backend

1. Railway will automatically detect the `Dockerfile` in the backend folder
2. It will build and deploy automatically
3. Wait for deployment to complete (check logs)

### 2.5 Get Backend URL

1. After deployment, Railway will provide a URL like:
   - `https://your-backend-name.up.railway.app`
2. Note this URL - you'll need it for the frontend

### 2.6 Create Admin User

After backend is deployed, you can create admin via Railway's console:

1. Go to your backend service in Railway
2. Click **"Deployments"** → **"View Logs"**
3. Or use Railway's CLI to run:
   ```bash
   railway run python create_admin_direct.py
   ```

Or use the API:
```bash
curl -X POST https://your-backend.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "123admin",
    "password": "duyan2892006",
    "email": "admin@facestream.local",
    "role": "admin"
  }'
```

---

## 🎨 Step 3: Deploy Frontend to Railway

### 3.1 Create Frontend Railway Configuration

Create `frontend/railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "npm run preview",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 3.2 Create Frontend Build Script

Update `frontend/package.json` to add build script if missing:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview --host 0.0.0.0 --port $PORT"
  }
}
```

### 3.3 Create New Railway Project for Frontend

1. In Railway Dashboard, create a **new project**
2. Select **"Deploy from GitHub repo"**
3. Choose the same repository
4. Select the `frontend` folder as root directory

### 3.4 Configure Frontend Environment Variables

In Railway frontend project, add:

```env
# Backend API URL (use your backend Railway URL)
VITE_API_URL=https://your-backend-name.up.railway.app
VITE_WS_URL=wss://your-backend-name.up.railway.app

# Port (Railway sets this automatically)
PORT=$PORT
```

### 3.5 Deploy Frontend

1. Railway will detect it's a Node.js project
2. It will run `npm install` and `npm run build`
3. Then start with `npm run preview`
4. Wait for deployment

### 3.6 Get Frontend URL

Railway will provide a URL like:
- `https://your-frontend-name.up.railway.app`

---

## 🔗 Step 4: Connect Frontend to Backend

### 4.1 Update Backend CORS

In Railway backend environment variables, update:

```env
CORS_ORIGINS=https://your-frontend-name.up.railway.app
```

If you have a custom domain:
```env
CORS_ORIGINS=https://your-frontend-name.up.railway.app,https://your-custom-domain.com
```

### 4.2 Update Frontend API URL

In Railway frontend environment variables, ensure:

```env
VITE_API_URL=https://your-backend-name.up.railway.app
VITE_WS_URL=wss://your-backend-name.up.railway.app
```

**Note:** Use `wss://` (secure WebSocket) for production, not `ws://`

### 4.3 Redeploy Both Services

After updating environment variables, both services will automatically redeploy.

---

## 🌍 Step 5: Custom Domains (Optional)

### 5.1 Add Custom Domain to Backend

1. In Railway backend project → **Settings** → **Domains**
2. Click **"Custom Domain"**
3. Add your domain (e.g., `api.yourdomain.com`)
4. Follow Railway's DNS instructions

### 5.2 Add Custom Domain to Frontend

1. In Railway frontend project → **Settings** → **Domains**
2. Click **"Custom Domain"**
3. Add your domain (e.g., `app.yourdomain.com`)
4. Follow Railway's DNS instructions

### 5.3 Update Environment Variables

After adding custom domains, update:

**Backend:**
```env
CORS_ORIGINS=https://app.yourdomain.com,https://your-frontend-name.up.railway.app
```

**Frontend:**
```env
VITE_API_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com
```

---

## ✅ Step 6: Verify Deployment

### 6.1 Test Backend

```bash
# Health check
curl https://your-backend.railway.app/health

# API docs
open https://your-backend.railway.app/docs
```

### 6.2 Test Frontend

1. Open `https://your-frontend.railway.app`
2. Try logging in with admin credentials
3. Verify all features work

### 6.3 Test from Different Locations

- ✅ Test from your phone (mobile data)
- ✅ Test from a different network
- ✅ Test from a different country (if possible)

---

## 🔒 Security Checklist

- [ ] Changed `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False` in production
- [ ] Configured `CORS_ORIGINS` with specific domains (not `*`)
- [ ] Using HTTPS (Railway provides this automatically)
- [ ] Database credentials are secure (Railway manages this)
- [ ] Admin password is strong

---

## 🐛 Troubleshooting

### Backend won't start

1. Check Railway logs for errors
2. Verify all environment variables are set
3. Check if database is connected
4. Verify `DATABASE_URL` is correct

### Frontend can't connect to backend

1. Check `VITE_API_URL` is correct
2. Verify backend CORS allows frontend origin
3. Check browser console for CORS errors
4. Ensure backend is deployed and running

### Database connection errors

1. Verify `DATABASE_URL` in Railway environment variables
2. Check if PostgreSQL service is running
3. Run migrations: `railway run alembic upgrade head`

### WebSocket not working

1. Use `wss://` (secure) not `ws://` in production
2. Check Railway WebSocket support (should work automatically)
3. Verify backend WebSocket endpoint is accessible

---

## 📊 Monitoring

Railway provides:
- ✅ Real-time logs
- ✅ Deployment history
- ✅ Resource usage
- ✅ Error tracking

Access via Railway Dashboard → Your Project → Logs

---

## 🚀 Next Steps

1. **Set up monitoring** - Use Railway's built-in monitoring
2. **Configure backups** - Railway PostgreSQL has automatic backups
3. **Set up CI/CD** - Railway auto-deploys on git push
4. **Scale resources** - Upgrade Railway plan if needed
5. **Add custom domains** - Use your own domain names

---

## 📝 Important Notes

1. **Railway Free Tier:**
   - Limited resources
   - Services may sleep after inactivity
   - Consider upgrading for production

2. **Database:**
   - Railway PostgreSQL is managed
   - Automatic backups included
   - Connection string is auto-injected

3. **Environment Variables:**
   - Never commit `.env` files
   - Use Railway's environment variable UI
   - Secrets are encrypted

4. **Build Times:**
   - First build may take 5-10 minutes
   - Subsequent builds are faster (cached)

5. **Global Access:**
   - ✅ Works from anywhere in the world
   - ✅ HTTPS/SSL included
   - ✅ CDN for static assets (frontend)

---

## 🎉 Success!

Once deployed, your application will be:
- ✅ Accessible globally via HTTPS
- ✅ Auto-scaling (based on Railway plan)
- ✅ Secure with SSL certificates
- ✅ Monitored with Railway's dashboard
- ✅ Auto-deploying on git push

**Your app URLs:**
- Backend: `https://your-backend.railway.app`
- Frontend: `https://your-frontend.railway.app`
- API Docs: `https://your-backend.railway.app/docs`

Happy deploying! 🚀

