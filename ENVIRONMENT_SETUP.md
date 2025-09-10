# 🔧 Environment Setup Guide

This guide will help you set up all the necessary environment variables for the AI Dietitian Agent System to work properly.

## 📋 Quick Setup Checklist

- [ ] Backend `.env` file configured
- [ ] Frontend `.env` file configured  
- [ ] Supabase project set up
- [ ] Google OAuth configured
- [ ] OpenAI API key added
- [ ] External API keys added (optional)

## 🚀 Backend Environment Setup

### 1. Copy the example file
```bash
cd backend
cp env.example .env
```

### 2. Essential Variables (Required)

#### Database (Supabase)
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
```

#### Security
```env
SECRET_KEY=your-super-secret-jwt-key-change-in-production-make-it-very-long-and-random
```

#### CORS (for frontend communication)
```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-frontend-domain.vercel.app
```

### 3. Optional Variables

#### AI/OpenAI
```env
OPENAI_API_KEY=your_openai_api_key_here
```

#### External APIs (for enhanced features)
```env
NUTRITION_API_KEY=your_nutrition_api_key_here
RECIPE_API_KEY=your_recipe_api_key_here
ZEPTO_API_KEY=your_zepto_api_key_here
BLINKIT_API_KEY=your_blinkit_api_key_here
```

## 🎨 Frontend Environment Setup

### 1. Copy the example file
```bash
cd frontend
cp env.example .env
```

### 2. Essential Variables (Required)

#### API Configuration
```env
VITE_API_URL=http://localhost:8000
```

#### Supabase
```env
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

### 3. Optional Variables

#### Google OAuth
```env
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
```

## 🔑 How to Get API Keys

### Supabase Setup
1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Settings → API
4. Copy the Project URL and anon key
5. For service role key, copy the service_role key (keep this secret!)

### Google OAuth Setup (via Supabase)
Since you're using Supabase as the authentication provider, Google OAuth is configured in Supabase, not directly in your app:

1. **Google Cloud Console Setup**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing
   - Enable Google+ API
   - Go to Credentials → Create Credentials → OAuth 2.0 Client ID
   - Set authorized redirect URIs to: `https://your-project-id.supabase.co/auth/v1/callback`

2. **Supabase Dashboard Setup**:
   - Go to your Supabase project dashboard
   - Navigate to Authentication → Providers
   - Enable Google provider
   - Add your Google Client ID and Secret from step 1
   - Save the configuration

**Note**: No Google credentials needed in your frontend/backend code - Supabase handles everything!

### OpenAI Setup
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create an account and add billing
3. Go to API Keys section
4. Create a new secret key

## 🛠️ Development vs Production

### Development
- Use `http://localhost:8000` for backend
- Use `http://localhost:5173` for frontend
- Set `ENVIRONMENT=development`
- Enable debug logs

### Production
- Use your production domain URLs
- Set `ENVIRONMENT=production`
- Use strong, unique secret keys
- Disable debug logs
- Use HTTPS only

## 🔒 Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use strong, unique secret keys** (at least 32 characters)
3. **Rotate keys regularly** in production
4. **Use different keys** for development and production
5. **Keep service role keys secret** (Supabase service role key)

## 🚨 Common Issues

### Backend won't start
- Check if all required environment variables are set
- Verify Supabase credentials are correct
- Ensure port 8000 is available

### Frontend can't connect to backend
- Check `VITE_API_URL` is correct
- Verify CORS settings in backend
- Ensure backend is running

### Google OAuth not working
- Verify Google OAuth credentials
- Check redirect URIs match exactly
- Ensure Supabase auth is configured

### Database connection issues
- Verify Supabase URL and keys
- Check if service role key has proper permissions
- Ensure database tables are created

## 📞 Need Help?

If you encounter issues:
1. Check the logs for error messages
2. Verify all environment variables are set correctly
3. Ensure all services (Supabase, Google, etc.) are properly configured
4. Check the troubleshooting guide in the project README

## 🔄 Environment Variable Reference

### Backend Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | ✅ | Supabase project URL |
| `SUPABASE_ANON_KEY` | ✅ | Supabase anonymous key |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | Supabase service role key |
| `SECRET_KEY` | ✅ | JWT secret key |
| `ALLOWED_ORIGINS` | ✅ | CORS allowed origins |
| `OPENAI_API_KEY` | ❌ | OpenAI API key for AI features |
| `NUTRITION_API_KEY` | ❌ | Nutrition API key |
| `ZEPTO_API_KEY` | ❌ | Zepto delivery API key |
| `BLINKIT_API_KEY` | ❌ | Blinkit delivery API key |

### Frontend Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | ❌ | Backend API URL (auto-detected) |
| `VITE_SUPABASE_URL` | ✅ | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | ✅ | Supabase anonymous key |
| `VITE_GOOGLE_CLIENT_ID` | ❌ | Not needed - Google OAuth handled by Supabase |
