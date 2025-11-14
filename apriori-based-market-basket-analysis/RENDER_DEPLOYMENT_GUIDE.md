# Render Deployment Guide for Market Basket Analysis Backend

This guide will walk you through deploying your Python FastAPI backend on Render and connecting it with your Firebase-hosted frontend.

## Prerequisites

- ✅ Render account created
- ✅ GitHub account linked to Render
- ✅ Frontend deployed on Firebase
- ✅ Repository: `Sharvarii-Kulkarni/Apriori-based-Market-Basket-Analysis-Dashboard`

---

## Step-by-Step Deployment Instructions

### Step 1: Prepare Your Repository

Make sure your `backend/requirements.txt` file is committed and pushed to GitHub. The file should contain:
```
fastapi==0.120.4
uvicorn[standard]==0.38.0
pandas==2.3.3
numpy==2.3.4
mlxtend==0.23.4
python-multipart==0.0.20
scikit-learn==1.7.2
scipy==1.16.3
matplotlib==3.10.7
pillow==12.0.0
```

### Step 2: Create a New Web Service on Render

1. **Log in to Render Dashboard**
   - Go to https://dashboard.render.com
   - Sign in with your account

2. **Create New Web Service**
   - Click the **"New +"** button in the top right
   - Select **"Web Service"**

3. **Connect Your Repository**
   - Click **"Connect account"** if you haven't linked GitHub yet
   - Select **"Sharvarii-Kulkarni/Apriori-based-Market-Basket-Analysis-Dashboard"**
   - Click **"Connect"**

### Step 3: Configure the Web Service

Fill in the following settings:

#### Basic Settings:
- **Name**: `market-basket-backend` (or any name you prefer)
- **Region**: Choose the closest region to your users (e.g., `Oregon (US West)`)
- **Branch**: `main` (or your default branch)
- **Root Directory**: `apriori-based-market-basket-analysis/backend`
   - ⚠️ **IMPORTANT**: This tells Render to look in the `backend` folder, not the root

#### Build & Deploy Settings:
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - ⚠️ **IMPORTANT**: Render provides the PORT via environment variable, so use `$PORT`

#### Advanced Settings (Optional):
- **Environment**: `Python 3` (auto-detected)
- **Python Version**: `3.12` or `3.11` (check your local version)

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will start building and deploying your service
3. Wait for the build to complete (usually 2-5 minutes)
4. Once deployed, you'll see a URL like: `https://market-basket-backend.onrender.com`

### Step 5: Test Your Backend

1. Visit your Render service URL
2. You should see: `{"status":"Market Basket Analysis API is running","version":"2.0.0"}`
3. Test an endpoint: `https://your-service-url.onrender.com/docs` (FastAPI auto-generated docs)

---

## Connecting Frontend to Backend

### Step 6: Update Frontend Environment Variable

1. **Get Your Render Backend URL**
   - Copy your Render service URL (e.g., `https://market-basket-backend.onrender.com`)

2. **Update Firebase Frontend**
   - Go to your Firebase project
   - Navigate to **Hosting** → **Environment Variables** (if available)
   - OR create a `.env.production` file in your `frontend` folder:
     ```
     VITE_API_URL=https://your-render-service-url.onrender.com
     ```
   - Rebuild and redeploy your frontend:
     ```bash
     cd frontend
     npm run build
     firebase deploy
     ```

### Step 7: Update CORS in Backend (Optional but Recommended)

If you want to restrict CORS to only your Firebase domain:

1. **Get Your Firebase URL**
   - Your Firebase hosting URL (e.g., `https://your-project.web.app`)

2. **Update Backend CORS**
   - In Render dashboard, go to your service
   - Click **"Environment"** tab
   - Add environment variable:
     - **Key**: `FRONTEND_URL`
     - **Value**: `https://your-firebase-project.web.app`
   - Update `backend/main.py` to use this:
     ```python
     import os
     
     frontend_url = os.getenv("FRONTEND_URL", "*")
     app.add_middleware(
         CORSMiddleware,
         allow_origins=[frontend_url] if frontend_url != "*" else ["*"],
         allow_credentials=True,
         allow_methods=["*"],
         allow_headers=["*"],
     )
     ```
   - Commit and push changes
   - Render will auto-deploy

---

## Troubleshooting

### Build Fails
- **Check logs**: Click on your service → "Logs" tab
- **Common issues**:
  - Wrong root directory path
  - Missing dependencies in requirements.txt
  - Python version mismatch

### Backend Not Responding
- **Check service status**: Should be "Live"
- **Check logs**: Look for errors in the "Logs" tab
- **Test locally**: Make sure it works with `uvicorn main:app --host 0.0.0.0 --port 8000`

### CORS Errors in Frontend
- **Check CORS settings**: Make sure `allow_origins` includes your Firebase URL
- **Check backend URL**: Verify `VITE_API_URL` is correct in frontend
- **Check browser console**: Look for specific CORS error messages

### Slow First Request
- **Render free tier**: Services spin down after 15 minutes of inactivity
- **First request**: May take 30-60 seconds to wake up
- **Solution**: Upgrade to paid plan for always-on service, or use a keep-alive service

---

## Important Notes

1. **Free Tier Limitations**:
   - Services spin down after 15 minutes of inactivity
   - First request after spin-down takes longer
   - Limited build minutes per month

2. **Environment Variables**:
   - Use Render's "Environment" tab for sensitive data
   - Never commit API keys or secrets to GitHub

3. **File Uploads**:
   - The `uploads` folder is ephemeral on Render
   - Files are lost on restart
   - Consider using cloud storage (S3, Cloudinary) for production

4. **Auto-Deploy**:
   - Render auto-deploys on every push to your main branch
   - Check "Auto-Deploy" settings in your service

---

## Quick Reference

### Render Service Settings Summary:
```
Name: market-basket-backend
Root Directory: apriori-based-market-basket-analysis/backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Frontend Environment Variable:
```
VITE_API_URL=https://your-render-service-url.onrender.com
```

### Test Endpoints:
- Health check: `https://your-service.onrender.com/`
- API docs: `https://your-service.onrender.com/docs`
- Upload: `https://your-service.onrender.com/upload`

---

## Next Steps After Deployment

1. ✅ Test all API endpoints from your frontend
2. ✅ Monitor Render logs for any errors
3. ✅ Set up custom domain (optional, paid feature)
4. ✅ Configure environment variables for production
5. ✅ Set up monitoring/alerts (optional)

---

## Support

- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Render Support**: support@render.com

Good luck with your deployment! 🚀

