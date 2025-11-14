# 🚀 Render Deployment Checklist

## Pre-Deployment Checklist

- [x] ✅ `requirements.txt` created in `backend/` folder
- [x] ✅ Frontend updated to use environment variable for API URL
- [x] ✅ Backend code is committed and pushed to GitHub

## Render Deployment Steps

### 1. Create Web Service
- [ ] Go to https://dashboard.render.com
- [ ] Click **"New +"** → **"Web Service"**
- [ ] Connect repository: `Sharvarii-Kulkarni/Apriori-based-Market-Basket-Analysis-Dashboard`

### 2. Configure Settings
- [ ] **Name**: `market-basket-backend` (or your preferred name)
- [ ] **Region**: Choose closest to your users
- [ ] **Branch**: `main`
- [ ] **Root Directory**: `apriori-based-market-basket-analysis/backend` ⚠️ **CRITICAL**
- [ ] **Runtime**: `Python 3`
- [ ] **Build Command**: `pip install -r requirements.txt`
- [ ] **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT` ⚠️ **CRITICAL**

### 3. Deploy
- [ ] Click **"Create Web Service"**
- [ ] Wait for build to complete (2-5 minutes)
- [ ] Copy your service URL (e.g., `https://market-basket-backend.onrender.com`)

### 4. Test Backend
- [ ] Visit your Render URL - should show: `{"status":"Market Basket Analysis API is running","version":"2.0.0"}`
- [ ] Visit `/docs` endpoint for API documentation

### 5. Connect Frontend
- [ ] Get your Render backend URL
- [ ] In Firebase project, add environment variable or update build:
  - Create `.env.production` in `frontend/` folder:
    ```
    VITE_API_URL=https://your-render-service-url.onrender.com
    ```
- [ ] Rebuild frontend: `cd frontend && npm run build`
- [ ] Redeploy to Firebase: `firebase deploy`

### 6. Test Full Application
- [ ] Visit your Firebase frontend URL
- [ ] Test file upload functionality
- [ ] Test sample dataset loading
- [ ] Verify all API calls work

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Build fails | Check Root Directory path is correct |
| Service won't start | Verify start command uses `$PORT` |
| CORS errors | Backend allows all origins, should work |
| Slow first request | Normal on free tier (service spins down) |

## Quick Reference

**Render Service URL Format**: `https://your-service-name.onrender.com`

**Frontend Environment Variable**: 
```env
VITE_API_URL=https://your-render-service-url.onrender.com
```

**Test Endpoints**:
- Health: `https://your-service.onrender.com/`
- Docs: `https://your-service.onrender.com/docs`

---

📖 **For detailed instructions, see `RENDER_DEPLOYMENT_GUIDE.md`**

