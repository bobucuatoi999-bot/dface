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

### ⚠️ IMPORTANT: Try Internal URL First (FREE)

**Before using DATABASE_PUBLIC_URL (which may cost money), try the internal URL:**

### Step 1: Try Internal DATABASE_URL First (FREE - Recommended)

1. Go to Railway Dashboard → **Backend service** → **Variables** tab
2. Find or create **`DATABASE_URL`** variable
3. Set value to: `${{Postgres.DATABASE_URL}}`
   - Replace `Postgres` with your actual PostgreSQL service name
4. Save and wait 2-3 minutes for Railway's DNS to propagate
5. Check logs - if connection works, you're done! ✅

**Why this is better:**
- ✅ **FREE** - No egress fees
- ✅ **Faster** - Internal network connection
- ✅ **More secure** - Not exposed publicly

### Step 2: If Internal URL Doesn't Work, Use Public URL (Fallback)

**Only use this if Step 1 doesn't work after waiting 2-3 minutes:**

1. Go to Railway Dashboard → **Postgres service** → **Variables** tab
2. Find **`DATABASE_PUBLIC_URL`** (or `POSTGRES_PUBLIC_URL`)
3. Copy the entire value (looks like: `postgresql://user:pass@host.railway.app:port/db`)

4. Go to Railway Dashboard → **Backend service** → **Variables** tab
5. Find **`DATABASE_URL`** variable
6. Click to edit it
7. Replace the value with the **`DATABASE_PUBLIC_URL`** you copied
8. Save

**⚠️ Note:** Using `DATABASE_PUBLIC_URL` may incur egress fees. See `DATABASE_URL_VS_PUBLIC_URL.md` for details.

### Step 3: Wait for Redeploy

Railway will automatically redeploy. Check logs - you should see:
```
✓ DATABASE_URL is configured
Running database migrations...
✓ Database migrations completed successfully
Starting uvicorn server...
```

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

