# Restart Loop Fix - DATABASE_URL Missing

## Problem

The application was stuck in a restart loop because:
1. `DATABASE_URL` environment variable was not set in Railway
2. When `alembic upgrade head` ran, it imported `app.database`, which immediately checked for `DATABASE_URL` and exited with code 1
3. Railway's restart policy (`ON_FAILURE`) kept restarting the container
4. This created an infinite restart loop with error messages repeating

## Root Cause

The issue occurred because:
- `alembic/env.py` imports `app.database` before checking if `DATABASE_URL` exists
- `app.database` immediately exits if `DATABASE_URL` is missing
- The startup command runs `alembic upgrade head` before starting uvicorn
- Railway restarts on failure, creating a loop

## Solution Applied

### 1. Created Startup Script (`backend/start.sh`)
   - Checks for `DATABASE_URL` **before** running any Python code
   - Provides clear, actionable error messages
   - Exits gracefully with clear instructions if `DATABASE_URL` is missing
   - Runs migrations and starts the server only if `DATABASE_URL` is present

### 2. Updated Alembic (`backend/alembic/env.py`)
   - Checks for `DATABASE_URL` before importing `app.database`
   - Exits gracefully (code 0) if `DATABASE_URL` is missing
   - Prevents crash during migration step

### 3. Updated Dockerfile and Railway Config
   - Dockerfile now uses the startup script
   - Railway.json updated to use the startup script
   - Ensures consistent startup behavior

## What Happens Now

### If DATABASE_URL is Missing:
1. Startup script detects missing `DATABASE_URL` immediately
2. Prints clear error message with instructions
3. Waits 30 seconds (so you can see the error in logs)
4. Exits with code 1 (Railway will show as error, but message is clear)
5. Railway will restart, but the error message is visible and actionable

### If DATABASE_URL is Set:
1. Startup script verifies `DATABASE_URL` is present
2. Runs database migrations
3. Starts uvicorn server
4. Application runs normally

## Next Steps for You

**You MUST add a PostgreSQL database to your Railway project:**

1. Go to Railway Dashboard
2. Select your project
3. Click **"New"** → **"Database"** → **"Add PostgreSQL"**
4. Railway will automatically:
   - Create a PostgreSQL database
   - Inject `DATABASE_URL` into your backend service
   - Redeploy your application

**OR manually set the variable:**
- Go to Railway Dashboard → Your Backend Service → Variables
- Add: `DATABASE_URL=${{Postgres.DATABASE_URL}}`

## Files Changed

- `backend/start.sh` - New startup script with DATABASE_URL check
- `backend/Dockerfile` - Updated to use startup script
- `backend/railway.json` - Updated startCommand to use startup script
- `backend/alembic/env.py` - Added DATABASE_URL check before importing database

## Benefits

✅ No more restart loops - clear error message instead  
✅ Early detection - fails fast with helpful message  
✅ Better user experience - actionable instructions  
✅ Prevents wasted resources - doesn't keep restarting unnecessarily  

