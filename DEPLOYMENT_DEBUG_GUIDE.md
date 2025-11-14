# Deployment Debug Guide - Silent Crashes

## If Deployment Crashes with No Logs

### Step 1: Check Railway Build Logs

1. Go to Railway Dashboard → Your Backend Service
2. Click on **"Deployments"** tab
3. Click on the latest deployment
4. Check **"Build Logs"** (not just runtime logs)

**Common Build Issues:**
- Face recognition packages failing to compile (dlib takes 15-20 minutes)
- Out of memory during build
- Network timeout downloading packages

### Step 2: Check Runtime Logs

1. In the same deployment, check **"Logs"** tab
2. Look for:
   - `FaceStream Backend - Starting...`
   - `✓ DATABASE_URL is configured`
   - `Starting uvicorn server...`

**If you see nothing:**
- Container might be crashing before startup script runs
- Check if Dockerfile CMD is correct
- Verify start.sh is executable

### Step 3: Common Silent Crash Causes

#### 1. Build Timeout
**Symptom**: Build stops mid-way, no error
**Fix**: Face recognition packages take 15-20 minutes. Railway free tier might timeout.
**Solution**: 
- Upgrade Railway plan, OR
- Build locally and push image, OR
- Use Railway's build cache

#### 2. Out of Memory During Build
**Symptom**: Build fails when compiling dlib
**Fix**: dlib compilation requires ~2GB RAM
**Solution**: Railway might need more resources

#### 3. Missing Dependencies
**Symptom**: Import errors in logs
**Fix**: Check if all packages installed correctly
**Solution**: Review Dockerfile installation steps

#### 4. Database Connection Failure
**Symptom**: Container starts but crashes immediately
**Fix**: Check DATABASE_URL is set correctly
**Solution**: Use DATABASE_PUBLIC_URL instead of DATABASE_URL

### Step 4: Enable Verbose Logging

The startup script now includes:
- Pre-flight checks (DATABASE_URL)
- Migration status with error output
- Application import verification
- Detailed error messages

### Step 5: Manual Testing

If Railway logs don't show anything:

1. **Build locally:**
   ```bash
   docker build -t facestream-backend ./backend
   docker run -e DATABASE_URL=your_url -p 8000:8000 facestream-backend
   ```

2. **Check container logs:**
   ```bash
   docker logs <container_id>
   ```

### Step 6: Railway-Specific Issues

**Railway Build Cache:**
- Railway caches Docker layers
- If previous build failed, cache might be corrupted
- **Solution**: Clear Railway build cache or force rebuild

**Railway Logs Delay:**
- Railway logs can take 30-60 seconds to appear
- **Solution**: Wait 1-2 minutes after deployment starts

**Railway Resource Limits:**
- Free tier has limited build time/resources
- Face recognition build might exceed limits
- **Solution**: Consider Railway Pro plan or alternative deployment

## What to Look For in Logs

### Successful Startup Should Show:
```
==========================================
FaceStream Backend - Starting...
==========================================
✓ DATABASE_URL is configured

Running database migrations...
✓ Database migrations completed successfully

Starting uvicorn server on port 8080...
==========================================

Verifying application can be imported...
✓ Application import successful

Starting uvicorn...
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### Failed Startup Will Show:
- Error messages before "Starting uvicorn..."
- Import errors
- Database connection errors
- Missing dependency errors

## Next Steps

If deployment still crashes silently:
1. Check Railway build logs (not just runtime logs)
2. Verify DATABASE_URL is set correctly
3. Check Railway resource limits
4. Consider building locally and pushing image
5. Contact Railway support if build times out

