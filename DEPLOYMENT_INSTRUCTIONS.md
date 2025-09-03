# Deployment Instructions for AI Dietitian App

## 🚀 Smart Auto-Configuration

**The app now automatically detects the environment and configures itself!**

### Frontend (Vercel)
- **No environment variables needed!** The app automatically detects if it's running on Vercel and uses the correct API URL
- **Local development**: Uses `http://localhost:8000`
- **Production (Vercel)**: Uses `https://aayushi-4swl.onrender.com`

### Backend (Render)
- **No environment variables needed!** The app automatically detects if it's running on Render and configures CORS correctly
- **Local development**: Allows localhost origins
- **Production (Render)**: Allows Vercel domain origins

## 📋 Deployment Steps

### Frontend Deployment (Vercel)
1. **Connect your GitHub repository to Vercel**
2. **Deploy** - No environment variables needed!
3. **The app will automatically use the correct API URL**

### Backend Deployment (Render)
1. **Connect your GitHub repository to Render**
2. **Set only these essential environment variables:**
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   SECRET_KEY=your_jwt_secret_key
   OPENAI_API_KEY=your_openai_api_key
   ```
3. **Build Command:** `pip install -r requirements-python313.txt`
4. **Start Command:** `python main.py`
5. **The app will automatically detect it's in production and configure CORS correctly**

## Testing Production

### 1. Test Backend
```bash
curl https://aayushi-4swl.onrender.com/health
```

### 2. Test Frontend
Visit: https://aayushi-seven.vercel.app

### 3. Test Login
- Go to https://aayushi-seven.vercel.app/login
- Try logging in with your credentials
- Check browser network tab for API calls to https://aayushi-4swl.onrender.com

## Troubleshooting

### CORS Issues
- Make sure `ALLOWED_ORIGINS` includes your frontend domain
- Check that CORS middleware is properly configured

### Environment Variables
- Verify all environment variables are set correctly
- Check that API URLs match between frontend and backend

### Database Connection
- Ensure Supabase credentials are correct
- Check that database tables exist and are accessible
