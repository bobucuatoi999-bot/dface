# Railway PostgreSQL Setup - Step by Step Guide

## ⚠️ Current Status

Your application is **correctly detecting** that `DATABASE_URL` is missing. The container exits intentionally - this is **NOT a crash**, it's the expected behavior until you add a database.

## ✅ What You Need to Do

### Option 1: Add PostgreSQL Database (Recommended - Easiest)

1. **Open Railway Dashboard**
   - Go to https://railway.app
   - Log in to your account
   - Select your project

2. **Add PostgreSQL Service**
   - In your project, click the **"New"** button (usually top right or in the services list)
   - Select **"Database"** from the dropdown
   - Click **"Add PostgreSQL"**
   - Railway will automatically:
     - Create a PostgreSQL database
     - Generate connection credentials
     - **Automatically inject `DATABASE_URL` into your backend service**
     - Trigger a redeploy

3. **Wait for Redeploy**
   - Railway will automatically redeploy your backend
   - Check the logs - you should see:
     ```
     ✓ DATABASE_URL is configured
     ✓ Database migrations completed successfully
     Starting uvicorn server...
     ```

### Option 2: Manual Variable Setup (If PostgreSQL Already Exists)

If you already have a PostgreSQL service but `DATABASE_URL` isn't being injected:

1. **Find Your PostgreSQL Service**
   - In Railway Dashboard, look for a service named "Postgres" or "PostgreSQL"
   - Note the exact service name

2. **Go to Backend Service Variables**
   - Click on your **backend service** (the one that's failing)
   - Go to the **"Variables"** tab

3. **Add DATABASE_URL Variable**
   - Click **"New Variable"**
   - **Variable Name**: `DATABASE_URL`
   - **Variable Value**: `${{Postgres.DATABASE_URL}}`
     - Replace `Postgres` with your actual PostgreSQL service name if different
     - The `${{...}}` syntax tells Railway to reference another service's variable

4. **Save and Redeploy**
   - Click **"Add"** or **"Save"**
   - Railway will automatically redeploy

### Option 3: Get Connection String Directly

If the above doesn't work:

1. **Get PostgreSQL Connection String**
   - Go to your PostgreSQL service in Railway
   - Click on **"Variables"** tab
   - Find `DATABASE_URL` or `POSTGRES_URL` or similar
   - Copy the full connection string (looks like: `postgresql://user:pass@host:port/db`)

2. **Set in Backend Service**
   - Go to your backend service → Variables
   - Add new variable:
     - **Name**: `DATABASE_URL`
     - **Value**: Paste the connection string you copied

## 🔍 How to Verify

After setting `DATABASE_URL`:

1. **Check Railway Logs**
   - Go to your backend service → **"Deployments"** → **"View Logs"**
   - You should see:
     ```
     ✓ DATABASE_URL is configured
     Running database migrations...
     ✓ Database migrations completed successfully
     Starting uvicorn server on port 8080...
     ```

2. **Check Variables**
   - Backend service → Variables tab
   - You should see `DATABASE_URL` listed with a value starting with `postgresql://`

## 🚨 Troubleshooting

### Railway doesn't auto-inject DATABASE_URL

**Solution**: Manually add it using Option 2 or 3 above.

### Can't find PostgreSQL service

**Solution**: Use Option 1 to create a new PostgreSQL database.

### Variable shows as `${{Postgres.DATABASE_URL}}` literally

**Solution**: Make sure:
- The PostgreSQL service exists and is named correctly
- The variable name matches exactly (case-sensitive)
- You're using the correct syntax: `${{ServiceName.VARIABLE_NAME}}`

### Still seeing "DATABASE_URL not set" error

**Solution**:
1. Double-check the variable is saved in Railway
2. Wait for Railway to redeploy (can take 1-2 minutes)
3. Check logs to see if the variable is actually being read

## 📝 Quick Checklist

- [ ] PostgreSQL service exists in Railway project
- [ ] `DATABASE_URL` variable is set in backend service
- [ ] Variable value is correct (starts with `postgresql://`)
- [ ] Railway has redeployed after adding variable
- [ ] Logs show "✓ DATABASE_URL is configured"

## 🎯 Expected Result

Once `DATABASE_URL` is set correctly, your logs should show:

```
==========================================
FaceStream Backend - Starting...
==========================================

✓ DATABASE_URL is configured

Running database migrations...
✓ Database migrations completed successfully

Starting uvicorn server on port 8080...
==========================================
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

If you see this, your application is running successfully! 🎉

