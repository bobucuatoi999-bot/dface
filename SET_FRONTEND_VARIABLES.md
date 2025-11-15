# 🎨 How to Set Frontend Environment Variables on Railway

Since your backend deployed successfully, follow these steps to configure your frontend.

## 📋 Step-by-Step Instructions

### Step 1: Get Your Backend URL

1. Go to [Railway Dashboard](https://railway.app)
2. Click on your **Backend service** (the one that's already deployed)
3. Click on the **"Settings"** tab
4. Scroll down to **"Networking"** section
5. Find **"Public Domain"** or **"Generate Domain"**
6. Copy the URL - it will look like:
   ```
   https://your-backend-name.up.railway.app
   ```
   or
   ```
   https://your-backend-name.railway.app
   ```

**Example:** If your backend URL is `https://facestream-backend.up.railway.app`, write it down!

---

### Step 2: Go to Frontend Service

1. In Railway Dashboard, click on your **Frontend service**
   - (If you haven't created it yet, see Step 3 below)
2. Click on the **"Variables"** tab

---

### Step 3: Add Environment Variables

In the **Variables** tab, click **"+ New Variable"** and add these two variables:

#### Variable 1: VITE_API_URL

- **Name:** `VITE_API_URL`
- **Value:** `https://your-backend-name.up.railway.app`
  - Replace `your-backend-name.up.railway.app` with your actual backend URL from Step 1
- **Example:** `https://facestream-backend.up.railway.app`

#### Variable 2: VITE_WS_URL

- **Name:** `VITE_WS_URL`
- **Value:** `wss://your-backend-name.up.railway.app/ws/recognize`
  - **Important:** Use `wss://` (secure WebSocket), NOT `ws://`
  - **Must include the path:** `/ws/recognize` at the end
  - Replace `your-backend-name.up.railway.app` with your actual backend URL
- **Example:** `wss://facestream-backend.up.railway.app/ws/recognize`

**Note:** VITE_WS_URL includes the full WebSocket path, while VITE_API_URL is just the base URL.

---

### Step 4: Save and Deploy

1. Click **"Save"** or **"Add"** for each variable
2. Railway will **automatically redeploy** your frontend
3. Wait for deployment to complete (check the **"Deployments"** tab)

---

## ✅ Verify It Works

After deployment:

1. Go to your frontend URL (Railway will show it in the frontend service)
2. Open browser **Developer Tools** (F12)
3. Go to **Console** tab
4. Check for any errors
5. Try logging in - if you see API calls in the **Network** tab, it's working!

---

## 🔍 How to Find Your Backend URL (Visual Guide)

### Method 1: From Backend Service Settings

```
Railway Dashboard
  └─ Your Project
      └─ Backend Service
          └─ Settings Tab
              └─ Networking Section
                  └─ Public Domain: https://your-backend.up.railway.app
```

### Method 2: From Backend Service Overview

1. Click on your **Backend service**
2. Look at the top of the page - Railway shows the URL there
3. Or click **"View Logs"** - the URL is often shown in the logs

### Method 3: Test the Backend Directly

Try opening this URL in your browser:
```
https://your-backend-name.up.railway.app/health
```

If it shows `{"status": "healthy", ...}`, that's your backend URL!

---

## 📝 Complete Example

If your backend URL is: `https://facestream-backend.up.railway.app`

Then set these variables in your **Frontend service**:

```
VITE_API_URL = https://facestream-backend.up.railway.app
VITE_WS_URL  = wss://facestream-backend.up.railway.app/ws/recognize
```

**Key Differences:**
- ✅ **VITE_API_URL**: Base URL only (`https://backend-url`) - no path
- ✅ **VITE_WS_URL**: Full WebSocket URL (`wss://backend-url/ws/recognize`) - includes path
- ✅ Use `https://` for API URL
- ✅ Use `wss://` for WebSocket URL (NOT `ws://`)
- ✅ VITE_WS_URL must include `/ws/recognize` path at the end

---

## 🐛 Troubleshooting

### Frontend still can't connect to backend?

1. **Check the backend URL is correct:**
   - Open `https://your-backend-url/health` in browser
   - Should return JSON with `"status": "healthy"`

2. **Check CORS settings:**
   - Go to Backend service → Variables
   - Set `CORS_ORIGINS` to your frontend URL:
     ```
     CORS_ORIGINS=https://your-frontend-name.up.railway.app
     ```

3. **Check browser console:**
   - Open frontend in browser
   - Press F12 → Console tab
   - Look for errors mentioning "CORS" or "API"

4. **Verify variables are set:**
   - Frontend service → Variables tab
   - Make sure both `VITE_API_URL` and `VITE_WS_URL` are there
   - Make sure they're spelled correctly (case-sensitive!)

---

## 🎯 Quick Checklist

- [ ] Got backend URL from Railway dashboard
- [ ] Opened Frontend service → Variables tab
- [ ] Added `VITE_API_URL` = `https://your-backend-url`
- [ ] Added `VITE_WS_URL` = `wss://your-backend-url` (note: wss://)
- [ ] Saved variables
- [ ] Waited for redeployment
- [ ] Tested frontend - can login and use features

---

## 🚀 After Setting Variables

Once variables are set and frontend redeploys:

1. **Frontend will automatically use the backend URL**
2. **All API calls will go to your Railway backend**
3. **WebSocket connections will use secure WSS protocol**
4. **Everything should work!**

---

## 💡 Pro Tip

If you're not sure what your backend URL is:

1. Go to Backend service → **Settings** → **Networking**
2. If no domain is shown, click **"Generate Domain"**
3. Railway will create a URL like `https://random-name.up.railway.app`
4. Copy that URL and use it in your frontend variables

---

**Need help?** Check Railway logs in the frontend service to see if there are any errors during build or deployment.

