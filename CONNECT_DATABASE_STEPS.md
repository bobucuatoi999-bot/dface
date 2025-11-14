# Connect PostgreSQL to Backend - Quick Guide

## ✅ You've Created the Database!

Now you need to connect it to your backend service.

## Step-by-Step Instructions

### Step 1: Go to Your Backend Service

1. In Railway Dashboard, look at your services list
2. Find your **backend service** (the one that's failing/stopping)
3. Click on it to open it

### Step 2: Open Variables Tab

1. In your backend service, click on the **"Variables"** tab
2. This shows all environment variables for your backend

### Step 3: Check if DATABASE_URL Already Exists

Look for a variable named `DATABASE_URL`:
- ✅ **If it exists**: Railway already connected it! Just wait for redeploy.
- ❌ **If it doesn't exist**: Continue to Step 4

### Step 4: Add DATABASE_URL Variable

1. Click **"New Variable"** or **"+"** button
2. Fill in:
   - **Variable Name**: `DATABASE_URL`
   - **Variable Value**: `${{Postgres.DATABASE_URL}}`
     - ⚠️ **Important**: Replace `Postgres` with your actual PostgreSQL service name
     - To find the exact name: Look at your services list - it might be "Postgres", "PostgreSQL", or something else
3. Click **"Add"** or **"Save"**

### Step 5: Verify

1. After adding, Railway will automatically redeploy (wait 1-2 minutes)
2. Go to **"Deployments"** → **"View Logs"**
3. You should see:
   ```
   ✓ DATABASE_URL is configured
   Running database migrations...
   ✓ Database migrations completed successfully
   Starting uvicorn server...
   ```

## Alternative: Copy Connection String Directly

If the `${{...}}` syntax doesn't work:

1. Go to **Postgres service** → **"Variables"** tab
2. Find `DATABASE_URL` or `POSTGRES_URL` 
3. Copy the entire value (looks like: `postgresql://user:pass@host:port/db`)
4. Go to **Backend service** → **"Variables"** tab
5. Add new variable:
   - **Name**: `DATABASE_URL`
   - **Value**: Paste the connection string you copied
6. Save

## Troubleshooting

### Can't find "Variables" tab
- Make sure you're in the **backend service**, not the Postgres service
- Look for tabs: Deployments, Variables, Metrics, Settings

### Variable shows as `${{Postgres.DATABASE_URL}}` literally
- Check that your PostgreSQL service name matches exactly
- Railway service names are case-sensitive
- Try copying the connection string directly instead

### Still seeing "DATABASE_URL not set" error
- Wait 2-3 minutes for Railway to redeploy
- Check that the variable is actually saved (refresh the Variables page)
- Make sure you're looking at the correct service

## Success Indicators

✅ **Success looks like:**
```
✓ DATABASE_URL is configured
Running database migrations...
✓ Database migrations completed successfully
Starting uvicorn server on port 8080...
INFO: Uvicorn running on http://0.0.0.0:8080
```

❌ **Still failing:**
```
ERROR: DATABASE_URL environment variable is not set!
```
→ Go back and check the variable is saved correctly

