# 🔧 Railway Dockerfile Troubleshooting

## Issue: Dockerfile Not Found

If Railway says "Dockerfile does not exist" even though it's in your repo:

### Solution 1: Remove dockerfilePath from railway.json (Recommended)

When Root Directory is set to `/backend`, Railway should auto-detect the Dockerfile.

**Updated `backend/railway.json`:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "sh -c 'alembic upgrade head || true && uvicorn app.main:app --host 0.0.0.0 --port $PORT'",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Note:** Removed `dockerfilePath` - Railway will auto-detect it when root is `/backend`.

---

### Solution 2: Configure in Railway UI

If railway.json doesn't work, configure directly in Railway:

1. Go to your service → **Settings**
2. Scroll to **"Build"** section
3. Set:
   - **Builder**: `Dockerfile`
   - **Dockerfile Path**: Leave empty OR set to `Dockerfile`
4. Save and redeploy

---

### Solution 3: Use Repository Root

If backend root doesn't work:

1. In Railway Settings, change **Root Directory** to: `.` (repository root)
2. Update `railway.json` in root to:
   ```json
   {
     "build": {
       "builder": "DOCKERFILE",
       "dockerfilePath": "backend/Dockerfile"
     }
   }
   ```

---

### Solution 4: Manual Build Configuration

In Railway UI:

1. Go to **Settings** → **Build**
2. **Build Command**: Leave empty (Railway auto-detects)
3. **Dockerfile Path**: `Dockerfile` (relative to root directory)
4. Make sure **Root Directory** is set to `/backend`

---

## Verification Checklist

- [ ] Dockerfile exists at `backend/Dockerfile` in GitHub
- [ ] Root Directory in Railway is set to `/backend`
- [ ] railway.json is in `backend/` folder
- [ ] Dockerfile is committed to git (check: `git ls-files backend/Dockerfile`)
- [ ] Latest code is pushed to GitHub

---

## Quick Test

Verify Dockerfile is in repo:
```bash
git ls-files backend/Dockerfile
```

Should output: `backend/Dockerfile`

If it doesn't, the file isn't tracked by git. Add it:
```bash
git add backend/Dockerfile
git commit -m "Add Dockerfile"
git push
```

---

## Still Not Working?

1. **Check Railway Logs**: Look for the exact error message
2. **Verify Root Directory**: Make sure it's exactly `/backend` (with leading slash)
3. **Try Different Path**: Set Dockerfile Path to just `Dockerfile` (no `./`)
4. **Remove railway.json**: Let Railway auto-detect everything
5. **Check File Permissions**: Make sure Dockerfile is readable

---

## Current Configuration

- ✅ Root Directory: `/backend`
- ✅ Dockerfile Location: `backend/Dockerfile` in repo
- ✅ railway.json: Removed explicit `dockerfilePath` (auto-detect)
- ✅ Latest code pushed to GitHub

**Next Step**: Redeploy in Railway after the latest commit.

