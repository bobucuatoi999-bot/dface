# ✅ Railway Deployment Checklist

Use this checklist to ensure everything is ready for deployment.

## 📋 Pre-Deployment

### GitHub Setup
- [ ] Repository created on GitHub
- [ ] All code committed and pushed
- [ ] `.gitignore` files are correct (no secrets committed)
- [ ] Repository is public or Railway has access

### Backend Preparation
- [ ] `backend/Dockerfile` is updated (handles optional dependencies)
- [ ] `backend/railway.json` is configured
- [ ] `backend/.env` is NOT committed (in .gitignore)
- [ ] `backend/env.example` has all required variables
- [ ] CORS configuration supports environment variables
- [ ] Database migrations are ready (alembic)

### Frontend Preparation
- [ ] `frontend/railway.json` is created
- [ ] `frontend/package.json` has build and preview scripts
- [ ] `frontend/vite.config.js` has preview configuration
- [ ] Frontend uses `VITE_API_URL` environment variable
- [ ] Frontend uses `VITE_WS_URL` for WebSocket (wss:// in production)

## 🚀 Railway Backend Deployment

### Project Setup
- [ ] New Railway project created
- [ ] Connected to GitHub repository
- [ ] Root directory set to `backend/`
- [ ] Build method: Dockerfile

### Database
- [ ] PostgreSQL database added to project
- [ ] Database is running
- [ ] Connection string is available

### Environment Variables
- [ ] `DATABASE_URL` set (Railway auto-injects from PostgreSQL)
- [ ] `SECRET_KEY` set (strong random value)
- [ ] `DEBUG=False`
- [ ] `LOG_LEVEL=INFO`
- [ ] `CORS_ORIGINS` set with frontend URL(s)
- [ ] `PORT` (Railway sets automatically, but can override)
- [ ] All other required variables from `env.example`

### Deployment
- [ ] Backend builds successfully
- [ ] Backend starts without errors
- [ ] Health check endpoint works: `/health`
- [ ] API docs accessible: `/docs`
- [ ] Database migrations ran successfully
- [ ] Admin user created (via script or API)

### Testing
- [ ] Backend URL is accessible: `https://your-backend.railway.app`
- [ ] API endpoints respond correctly
- [ ] CORS headers are correct
- [ ] Authentication works

## 🎨 Railway Frontend Deployment

### Project Setup
- [ ] New Railway project created (separate from backend)
- [ ] Connected to GitHub repository
- [ ] Root directory set to `frontend/`
- [ ] Build method: Nixpacks (auto-detected)

### Environment Variables
- [ ] `VITE_API_URL` set to backend Railway URL
- [ ] `VITE_WS_URL` set to backend Railway URL (wss://)
- [ ] `PORT` (Railway sets automatically)

### Deployment
- [ ] Frontend builds successfully (`npm run build`)
- [ ] Frontend starts successfully (`npm run preview`)
- [ ] No build errors

### Testing
- [ ] Frontend URL is accessible: `https://your-frontend.railway.app`
- [ ] Frontend loads correctly
- [ ] Can login with admin credentials
- [ ] API calls work (check browser console)
- [ ] WebSocket connections work (if using recognition features)

## 🔗 Integration Testing

### Connection
- [ ] Frontend can connect to backend API
- [ ] No CORS errors in browser console
- [ ] Authentication flow works end-to-end
- [ ] WebSocket connections work (if applicable)

### Functionality
- [ ] Login works
- [ ] User registration works (if implemented)
- [ ] All API endpoints accessible from frontend
- [ ] Error handling works correctly

## 🌍 Global Access Testing

### Accessibility
- [ ] Accessible from different networks
- [ ] Accessible from mobile devices
- [ ] HTTPS/SSL works (Railway provides automatically)
- [ ] No mixed content warnings

### Performance
- [ ] Page loads reasonably fast
- [ ] API responses are timely
- [ ] No timeout errors

## 🔒 Security

### Backend Security
- [ ] `SECRET_KEY` is strong and unique
- [ ] `DEBUG=False` in production
- [ ] CORS origins are specific (not `*`)
- [ ] Database credentials are secure
- [ ] Admin password is strong

### Frontend Security
- [ ] No secrets in frontend code
- [ ] API URLs use HTTPS
- [ ] WebSocket URLs use WSS (secure)

## 📊 Monitoring

### Railway Dashboard
- [ ] Can view backend logs
- [ ] Can view frontend logs
- [ ] Can see deployment history
- [ ] Can monitor resource usage

### Application Monitoring
- [ ] Health checks are working
- [ ] Error logging is configured
- [ ] Can track API usage

## 🌐 Custom Domains (Optional)

### Backend Domain
- [ ] Custom domain added to Railway
- [ ] DNS records configured
- [ ] SSL certificate issued (automatic)
- [ ] Backend accessible via custom domain
- [ ] CORS updated with custom domain

### Frontend Domain
- [ ] Custom domain added to Railway
- [ ] DNS records configured
- [ ] SSL certificate issued (automatic)
- [ ] Frontend accessible via custom domain
- [ ] Frontend environment variables updated

## 📝 Documentation

### For Users
- [ ] Deployment guide is complete
- [ ] Environment variables documented
- [ ] Troubleshooting guide available

### For Developers
- [ ] Code is well-documented
- [ ] API documentation accessible (`/docs`)
- [ ] README files are updated

## ✅ Final Verification

- [ ] Everything works from a fresh browser (incognito)
- [ ] Tested from different device/network
- [ ] No console errors
- [ ] No network errors
- [ ] All features functional
- [ ] Ready for production use!

---

## 🎉 Deployment Complete!

Once all items are checked, your application is:
- ✅ Globally accessible
- ✅ Secure with HTTPS
- ✅ Auto-deploying on git push
- ✅ Monitored and logged
- ✅ Production-ready

**Next Steps:**
1. Share your app URLs with users
2. Monitor Railway dashboard for issues
3. Set up custom domains (if desired)
4. Consider upgrading Railway plan for better performance

