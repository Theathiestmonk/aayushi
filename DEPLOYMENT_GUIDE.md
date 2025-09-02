# Deployment Guide for AI Dietitian App

## Current Status
- ✅ Frontend deployed on Vercel: https://aayushi-seven.vercel.app/
- ⏳ Backend needs to be deployed

## Backend Deployment Options

### Option 1: Render.com (Recommended - Free Tier Available)

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Deploy Backend**
   - Connect your GitHub repository
   - Create a new "Web Service"
   - Configure:
     - **Build Command**: `pip install -r requirements-production.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Environment**: Python 3.11
     - **Root Directory**: `backend`

3. **Set Environment Variables in Render**
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   SECRET_KEY=your_secret_key
   OPENAI_API_KEY=your_openai_api_key
   ALLOWED_ORIGINS=https://aayushi-seven.vercel.app
   ```

4. **Get Backend URL**
   - After deployment, you'll get a URL like: `https://your-app-name.onrender.com`

### Option 2: Railway.app

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy Backend**
   - Connect your repository
   - Select the `backend` folder
   - Railway will auto-detect Python and use the requirements file

3. **Set Environment Variables**
   - Same as Render.com

### Option 3: Heroku

1. **Create Heroku Account**
   - Go to [heroku.com](https://heroku.com)
   - Install Heroku CLI

2. **Deploy Backend**
   ```bash
   cd backend
   heroku create your-app-name
   git subtree push --prefix backend heroku main
   ```

## Frontend Configuration Update

After deploying your backend:

1. **Update Vercel Environment Variables**
   - Go to your Vercel project dashboard
   - Navigate to Settings > Environment Variables
   - Add: `VITE_API_URL` = `https://your-backend-url.onrender.com`

2. **Redeploy Frontend**
   - Push changes to trigger automatic deployment
   - Or manually redeploy from Vercel dashboard

## Testing Your Deployment

1. **Test Backend**
   - Visit: `https://your-backend-url.onrender.com/`
   - Should see: `{"message": "AI Dietitian Agent System API", "version": "1.0.0", "status": "running"}`

2. **Test Frontend**
   - Visit: https://aayushi-seven.vercel.app/
   - Check browser console for API connection errors
   - Try logging in/registering

## Troubleshooting

### CORS Issues
- Ensure your backend's `ALLOWED_HOSTS` includes `https://aayushi-seven.vercel.app`
- Check that environment variable `ALLOWED_ORIGINS` is set correctly

### API Connection Issues
- Verify `VITE_API_URL` is set correctly in Vercel
- Check that backend is running and accessible
- Look for network errors in browser dev tools

### Environment Variables
- Make sure all required environment variables are set in your backend deployment
- Check that Supabase credentials are correct
- Verify OpenAI API key is valid

## Next Steps

1. Deploy backend to Render/Railway/Heroku
2. Update Vercel environment variables with backend URL
3. Test the complete application
4. Set up custom domain (optional)

## Support

If you encounter issues:
1. Check the deployment logs in your hosting platform
2. Verify all environment variables are set
3. Test API endpoints directly
4. Check browser console for frontend errors
