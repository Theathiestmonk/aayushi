# 🔧 Supabase Auth Callback Setup Guide

## **Required Configuration Steps**

### **1. Supabase Dashboard Configuration**

Go to: https://supabase.com/dashboard/project/yemfctzdmuatwhareemm

#### **A. Authentication → URL Configuration**
1. Navigate to **Authentication** → **URL Configuration**
2. Add these **Site URLs**:
   ```
   http://localhost:3000
   https://your-production-domain.com
   ```
3. Add these **Redirect URLs**:
   ```
   http://localhost:3000/auth/callback
   https://your-production-domain.com/auth/callback
   ```

#### **B. Authentication → Providers → Google**
1. Make sure **"Enable sign in with Google"** is **ON**
2. Verify your **Client ID** and **Client Secret** are correct
3. The **Callback URL** should be:
   ```
   https://yemfctzdmuatwhareemm.supabase.co/auth/v1/callback
   ```

### **2. Google Cloud Console Configuration**

Go to: https://console.cloud.google.com/

#### **A. APIs & Services → Credentials**
1. Select your project
2. Go to **APIs & Services** → **Credentials**
3. Click on your **OAuth 2.0 Client ID**
4. Add these **Authorized redirect URIs**:
   ```
   https://yemfctzdmuatwhareemm.supabase.co/auth/v1/callback
   http://localhost:3000/auth/callback
   ```

### **3. Get Your Supabase Anon Key**

1. In Supabase Dashboard, go to **Settings** → **API**
2. Copy your **anon/public** key
3. Replace the placeholder in `frontend/src/lib/supabase.ts` line 5

### **4. Test the Configuration**

1. Start your development server: `npm run dev`
2. Go to the login page
3. Use the **"Test Supabase Connection"** button to verify setup
4. Use the **"Test Google OAuth"** button to test the flow

## **How the OAuth Flow Works**

1. **User clicks "Continue with Google"**
2. **Redirects to Google** for authentication
3. **Google redirects to Supabase** with auth code
4. **Supabase processes the code** and redirects to your app
5. **Your app receives the callback** at `/auth/callback`
6. **AuthCallback component** handles the response
7. **User is logged in** and redirected to dashboard

## **Common Issues & Solutions**

### **❌ "Invalid redirect URI"**
- **Solution**: Make sure all redirect URIs are added to both Supabase and Google Console

### **❌ "Client not found"**
- **Solution**: Verify your Google Client ID and Secret are correct in Supabase

### **❌ "Invalid anon key"**
- **Solution**: Update the anon key in `frontend/src/lib/supabase.ts`

### **❌ "CORS error"**
- **Solution**: Add your domain to Google OAuth settings

## **Debug Steps**

1. **Check browser console** for error messages
2. **Use the test component** on the login page
3. **Verify URLs** match exactly in all configurations
4. **Check Supabase logs** in the dashboard

## **Production Deployment**

When deploying to production:
1. Update **Site URLs** and **Redirect URLs** in Supabase
2. Add production domain to **Google OAuth settings**
3. Update environment variables with production URLs

Your OAuth callback is essential for the Google sign-in to work properly! 🚀
