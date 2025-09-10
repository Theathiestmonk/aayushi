# 🚀 AI Dietitian Agent System - Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ **Completed Features:**
- [x] Google OAuth authentication
- [x] User name display in navigation
- [x] Onboarding status persistence
- [x] Account linking for existing users
- [x] Dashboard routing for completed onboarding
- [x] Success messages for authentication

## 🌐 Domain Deployment Steps

### **1. Frontend Deployment (Vercel/Netlify)**

#### **Environment Variables to Set:**
```bash
# API Configuration
VITE_API_URL=https://your-backend-domain.com

# Supabase Configuration
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Application Settings
VITE_APP_NAME=AI Dietitian Agent System
VITE_APP_VERSION=1.0.0
VITE_NODE_ENV=production

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_DEBUG_LOGS=false
VITE_ENABLE_TERMS_AGREEMENT=false

# External Services
VITE_MAP_API_KEY=your_map_api_key_here
VITE_ANALYTICS_ID=your_analytics_id_here

# Development Settings
VITE_HOT_RELOAD=false
VITE_SOURCE_MAPS=false
```

#### **Build Commands:**
```bash
# Install dependencies
npm install

# Build for production
npm run build

# Preview production build
npm run preview
```

### **2. Backend Deployment (Railway/Render/Heroku)**

#### **Environment Variables to Set:**
```bash
# Application Settings
APP_NAME=AI Dietitian Agent System
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production

# Server Settings
HOST=0.0.0.0
PORT=8000
SKIP_API_ROUTER=false

# Database Settings (Supabase)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# Security Settings
SECRET_KEY=your-super-secret-jwt-key-change-in-production-make-it-very-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRRESH_TOKEN_EXPIRE_DAYS=7

# CORS Settings
ALLOWED_ORIGINS=https://your-frontend-domain.com,https://your-frontend-domain.vercel.app

# AI/OpenAI Settings
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7

# External API Keys
NUTRITION_API_KEY=your_nutrition_api_key_here
RECIPE_API_KEY=your_recipe_api_key_here
GROCERY_API_KEY=your_grocery_api_key_here
ZEPTO_API_KEY=your_zepto_api_key_here
BLINKIT_API_KEY=your_blinkit_api_key_here

# Redis Settings
REDIS_URL=redis://localhost:6379

# File Upload Settings
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=.jpg,.jpeg,.png,.gif,.pdf

# Email Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Agent Settings
AGENT_TIMEOUT_SECONDS=300
MAX_CONCURRENT_AGENTS=10
AGENT_RETRY_ATTEMPTS=3

# Monitoring and Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
ENABLE_METRICS=true
METRICS_PORT=9090
```

#### **Start Command:**
```bash
python main.py
```

### **3. Supabase Configuration**

#### **Authentication Settings:**
1. Go to **Supabase Dashboard → Authentication → URL Configuration**
2. Set **Site URL** to: `https://your-frontend-domain.com`
3. Add **Redirect URLs**:
   - `https://your-project-id.supabase.co/auth/v1/callback`
   - `https://your-frontend-domain.com`

#### **Google OAuth Setup:**
1. Go to **Authentication → Providers**
2. Enable **Google** provider
3. Add your **Google Client ID** and **Client Secret**
4. Set **Redirect URL** to: `https://your-project-id.supabase.co/auth/v1/callback`

### **4. Google Cloud Console Configuration**

#### **OAuth 2.0 Client IDs:**
1. Go to **Google Cloud Console → APIs & Services → Credentials**
2. Edit your OAuth 2.0 Client ID
3. Add **Authorized JavaScript origins**:
   - `https://your-frontend-domain.com`
   - `https://your-project-id.supabase.co`
4. Add **Authorized redirect URIs**:
   - `https://your-project-id.supabase.co/auth/v1/callback`

## 🔧 **Git Repository Push Commands**

### **Initialize and Push Repository:**
```bash
# Navigate to project root
cd C:\Users\Lenovo\Desktop\aayushi

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: AI Dietitian Agent System with Google OAuth and onboarding fixes"

# Add remote repository (replace with your actual repository URL)
git remote add origin https://github.com/yourusername/your-repo-name.git

# Push to main branch
git branch -M main
git push -u origin main
```

### **Update Repository:**
```bash
# Add changes
git add .

# Commit changes
git commit -m "Update: Fix Google OAuth onboarding flow and user name display"

# Push changes
git push origin main
```

## 🧪 **Testing After Deployment**

### **Test Checklist:**
- [ ] Frontend loads on your domain
- [ ] Backend API responds on your domain
- [ ] Google OAuth works (redirects to Google and back)
- [ ] User name displays correctly in navigation
- [ ] Onboarding form works for new users
- [ ] Dashboard loads for users with completed onboarding
- [ ] Database operations work (profile creation, updates)
- [ ] Authentication persists across page refreshes

### **Common Issues and Solutions:**

#### **CORS Errors:**
- Ensure `ALLOWED_ORIGINS` includes your frontend domain
- Check that both HTTP and HTTPS are configured if needed

#### **Google OAuth Not Working:**
- Verify redirect URLs in Google Cloud Console
- Check Supabase OAuth configuration
- Ensure site URL is set correctly in Supabase

#### **Database Connection Issues:**
- Verify Supabase URL and keys are correct
- Check that service role key has proper permissions
- Ensure database tables exist and are accessible

## 📞 **Support**

If you encounter any issues during deployment:
1. Check the browser console for frontend errors
2. Check the backend logs for API errors
3. Verify all environment variables are set correctly
4. Test the API endpoints directly using tools like Postman

## 🎉 **Success!**

Once deployed, your AI Dietitian Agent System will be live on your domain with:
- ✅ Google OAuth authentication
- ✅ User name display
- ✅ Proper onboarding flow
- ✅ Dashboard routing
- ✅ Database integration
- ✅ Production-ready configuration

**Your application is ready for production! 🚀**