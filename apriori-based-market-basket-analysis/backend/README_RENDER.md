# Backend Deployment on Render - Quick Start

## Render Configuration

When creating a new Web Service on Render, use these settings:

### Required Settings:
- **Root Directory**: `apriori-based-market-basket-analysis/backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Python Version**: `3.12` or `3.11`

### Important Notes:
1. The **Root Directory** must point to the `backend` folder, not the repository root
2. Use `$PORT` in the start command (Render provides this automatically)
3. The service will be available at `https://your-service-name.onrender.com`

## Testing After Deployment

1. Visit your Render service URL - you should see:
   ```json
   {"status":"Market Basket Analysis API is running","version":"2.0.0"}
   ```

2. Visit `/docs` endpoint for interactive API documentation:
   ```
   https://your-service-name.onrender.com/docs
   ```

## Connecting Frontend

Update your frontend's environment variable:
```env
VITE_API_URL=https://your-render-service-url.onrender.com
```

Then rebuild and redeploy your frontend on Firebase.

## Troubleshooting

- **Build fails**: Check that `requirements.txt` exists in the backend folder
- **Service won't start**: Verify the start command uses `$PORT`
- **CORS errors**: The backend currently allows all origins (`*`), which should work for Firebase

