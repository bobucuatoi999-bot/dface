# Database Connection Issue - Fix Guide

## Problem

You're seeing this error:
```
could not translate host name "postgres.railway.internal" to address: Name or service not known
```

## Root Cause

Railway provides two database URLs:
1. **`DATABASE_URL`** - Uses internal hostname (`postgres.railway.internal`) - only works if services are properly connected
2. **`DATABASE_PUBLIC_URL`** - Uses public hostname - works from anywhere

If the internal DNS isn't resolving, you need to use the public URL instead.

## Solution

### Step 1: Get the Public Database URL

1. Go to Railway Dashboard → **Postgres service** → **Variables** tab
2. Find **`DATABASE_PUBLIC_URL`** (or `POSTGRES_PUBLIC_URL`)
3. Copy the entire value (looks like: `postgresql://user:pass@host.railway.app:port/db`)

### Step 2: Update Backend Service Variable

1. Go to Railway Dashboard → **Backend service** → **Variables** tab
2. Find **`DATABASE_URL`** variable
3. Click to edit it
4. Replace the value with the **`DATABASE_PUBLIC_URL`** you copied
5. Save

### Step 3: Wait for Redeploy

Railway will automatically redeploy. Check logs - you should see:
```
✓ DATABASE_URL is configured
Running database migrations...
✓ Database migrations completed successfully
Starting uvicorn server...
```

## Alternative: Use Railway's Variable Reference

If Railway's variable reference works:

1. Backend service → Variables
2. Edit `DATABASE_URL`
3. Set value to: `${{Postgres.DATABASE_PUBLIC_URL}}`
   - Replace `Postgres` with your actual PostgreSQL service name

## Why This Happens

- Railway's internal DNS (`*.railway.internal`) only works when services are properly connected
- Sometimes the connection isn't established immediately
- Using the public URL (`*.railway.app`) always works, but goes through Railway's public network

## Verification

After updating, check your logs. You should see:
- ✅ `✓ DATABASE_URL is configured`
- ✅ `✓ Database migrations completed successfully`
- ✅ `INFO: Uvicorn running on http://0.0.0.0:8080`

If you still see connection errors, the database might not be ready yet. Wait 1-2 minutes and check again.

