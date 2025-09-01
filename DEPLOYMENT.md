# AI Dietitian Agent System - Deployment Guide

This guide covers deploying all three components of the AI Dietitian Agent System:
1. **Frontend** → Vercel
2. **Backend** → Render
3. **Database** → Supabase

## 🚀 Quick Start

### Prerequisites
- GitHub account
- Vercel account
- Render account
- Supabase account
- OpenAI API key

## 📊 Database Setup (Supabase)

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - Name: `ai-dietitian-system`
   - Database Password: Generate a strong password
   - Region: Choose closest to your users
5. Click "Create new project"

### 2. Set Up Database Schema
1. Wait for project to be ready (green status)
2. Go to SQL Editor
3. Copy the contents of `database/schema.sql`
4. Paste and execute the SQL script
5. Verify all tables are created in the Table Editor

### 3. Get Connection Details
1. Go to Settings → API
2. Copy:
   - Project URL
   - Anon (public) key
3. Save these for backend configuration

## 🔧 Backend Setup (Render)

### 1. Prepare Backend Code
1. Ensure your backend code is in a GitHub repository
2. Verify `requirements.txt` and `Dockerfile` are present
3. Set up environment variables (see `backend/env.example`)

### 2. Deploy to Render
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `ai-dietitian-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Choose appropriate plan (Free tier available)

### 3. Set Environment Variables
In Render dashboard, go to Environment and add:
```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your-secret-key-here
```

### 4. Deploy
1. Click "Create Web Service"
2. Wait for build and deployment
3. Note the service URL (e.g., `https://ai-dietitian-backend.onrender.com`)

## 🎨 Frontend Setup (Vercel)

### 1. Prepare Frontend Code
1. Ensure your frontend code is in a GitHub repository
2. Verify `package.json`, `vite.config.ts`, and `vercel.json` are present
3. Update `vercel.json` with your backend URL

### 2. Deploy to Vercel
1. Go to [vercel.com](https://vercel.com) and sign up/login
2. Click "New Project"
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### 3. Set Environment Variables
In Vercel dashboard, go to Settings → Environment Variables:
```bash
VITE_API_URL=https://your-backend-url.onrender.com
```

### 4. Deploy
1. Click "Deploy"
2. Wait for build and deployment
3. Note your domain (e.g., `https://ai-dietitian-frontend.vercel.app`)

## 🔐 Security Configuration

### 1. Update CORS Settings
In your backend `app/core/config.py`, update:
```python
ALLOWED_HOSTS: List[str] = [
    "https://your-frontend-domain.vercel.app",
    "http://localhost:3000"  # For development
]
```

### 2. Environment Variables Security
- Never commit `.env` files to Git
- Use strong, unique secrets for production
- Rotate API keys regularly
- Enable 2FA on all accounts

## 📱 Testing the Deployment

### 1. Test Backend
```bash
# Health check
curl https://your-backend-url.onrender.com/health

# API docs
open https://your-backend-url.onrender.com/docs
```

### 2. Test Frontend
1. Open your Vercel domain
2. Test the onboarding form
3. Verify API calls work
4. Check console for errors

### 3. Test Database
1. Go to Supabase dashboard
2. Check Table Editor for data
3. Verify API endpoints work

## 🔄 Continuous Deployment

### 1. Automatic Deployments
- **Vercel**: Automatically deploys on push to main branch
- **Render**: Automatically deploys on push to main branch
- **Supabase**: Schema changes require manual execution

### 2. Environment Management
- Use different branches for staging/production
- Set up environment-specific variables
- Test changes in staging first

## 📊 Monitoring and Maintenance

### 1. Health Checks
- Backend: `/health` endpoint
- Frontend: Vercel analytics
- Database: Supabase dashboard

### 2. Logs and Debugging
- **Backend**: Render logs
- **Frontend**: Vercel function logs
- **Database**: Supabase logs

### 3. Performance Monitoring
- Set up uptime monitoring
- Monitor API response times
- Track user engagement metrics

## 🚨 Troubleshooting

### Common Issues

#### Backend Won't Start
- Check environment variables
- Verify requirements.txt
- Check Render logs

#### Frontend Build Fails
- Check Node.js version
- Verify dependencies
- Check build logs

#### Database Connection Issues
- Verify Supabase credentials
- Check network access
- Verify table permissions

#### CORS Errors
- Update ALLOWED_HOSTS
- Check frontend domain
- Verify backend CORS settings

### Getting Help
1. Check application logs
2. Verify environment variables
3. Test endpoints individually
4. Check service status pages

## 🔒 Production Checklist

- [ ] Environment variables set
- [ ] CORS configured correctly
- [ ] Database schema deployed
- [ ] API endpoints tested
- [ ] Frontend builds successfully
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Security measures in place
- [ ] Backup strategy defined
- [ ] Documentation updated

## 📈 Scaling Considerations

### Backend (Render)
- Upgrade to paid plan for better performance
- Consider multiple instances
- Implement caching strategies

### Database (Supabase)
- Monitor usage limits
- Implement connection pooling
- Set up read replicas if needed

### Frontend (Vercel)
- Use CDN for static assets
- Implement service workers
- Optimize bundle size

## 🔄 Updates and Maintenance

### Regular Tasks
- Update dependencies monthly
- Review security settings quarterly
- Monitor performance metrics
- Backup database regularly

### Emergency Procedures
- Keep backup deployment URLs
- Document rollback procedures
- Set up alerting for critical issues

---

## 📞 Support

For deployment issues:
1. Check service status pages
2. Review service documentation
3. Contact service support
4. Check community forums

**Happy Deploying! 🚀**





