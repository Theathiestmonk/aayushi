# Google OAuth Setup Instructions

## ✅ What's Been Implemented

I've successfully added Google sign-in and sign-up functionality to your AI Dietitian app using Supabase's OAuth providers. Here's what's been added:

### 1. **Supabase Client Configuration** (`frontend/src/lib/supabase.ts`)
- Created Supabase client with Google OAuth configuration
- Added Google sign-in/sign-up functions
- Added OAuth callback handler

### 2. **Updated Auth Store** (`frontend/src/stores/authStore.ts`)
- Added `loginWithGoogle()` and `registerWithGoogle()` methods
- Added `handleGoogleCallback()` for processing OAuth redirects
- Integrated with existing authentication flow

### 3. **Updated UI Components**
- **Login Page** (`frontend/src/pages/Login.tsx`): Added "Continue with Google" button
- **Register Page** (`frontend/src/pages/Register.tsx`): Added "Continue with Google" button
- **Auth Callback Page** (`frontend/src/pages/AuthCallback.tsx`): Handles OAuth redirects

### 4. **Updated Routing** (`frontend/src/App.tsx`)
- Added `/auth/callback` route for OAuth redirects

## 🔧 Required Setup Steps

### Step 1: Get Your Supabase Anon Key
1. Go to your Supabase dashboard: https://supabase.com/dashboard/project/yemfctzdmuatwhareemm
2. Navigate to **Settings** → **API**
3. Copy your **anon/public** key
4. Replace the placeholder in `frontend/src/lib/supabase.ts` line 5

### Step 2: Configure Google OAuth in Supabase
1. In your Supabase dashboard, go to **Authentication** → **Providers**
2. Make sure **Google** is enabled (it appears to be already configured)
3. Verify your **Client ID** and **Client Secret** are correct
4. Ensure the **Callback URL** is set to: `https://yemfctzdmuatwhareemm.supabase.co/auth/v1/callback`

### Step 3: Configure Google Console (if needed)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Go to **APIs & Services** → **Credentials**
4. Edit your OAuth 2.0 Client ID
5. Add these **Authorized redirect URIs**:
   - `https://yemfctzdmuatwhareemm.supabase.co/auth/v1/callback`
   - `http://localhost:3000/auth/callback` (for local development)

### Step 4: Environment Variables (Optional)
Create a `.env` file in the `frontend` directory:
```env
VITE_SUPABASE_URL=https://yemfctzdmuatwhareemm.supabase.co
VITE_SUPABASE_ANON_KEY=your-actual-anon-key-here
```

## 🚀 How It Works

1. **User clicks "Continue with Google"** on Login or Register page
2. **Redirects to Google OAuth** for authentication
3. **Google redirects back** to `/auth/callback` with authorization code
4. **AuthCallback component** processes the OAuth response
5. **User is authenticated** and redirected to dashboard

## 🧪 Testing

1. Start your development server: `npm run dev`
2. Go to the login or register page
3. Click "Continue with Google"
4. Complete Google authentication
5. You should be redirected back to your app and logged in

## 🔍 Troubleshooting

- **"Invalid client" error**: Check your Google OAuth client configuration
- **"Redirect URI mismatch"**: Ensure callback URLs are correctly configured
- **"Invalid anon key"**: Update the Supabase anon key in the code
- **CORS errors**: Make sure your domain is added to Google OAuth settings

## 📝 Notes

- The Google OAuth flow works for both sign-in and sign-up (same process)
- User data is automatically extracted from Google profile
- The system integrates with your existing authentication system
- All existing email/password authentication continues to work

Your Google OAuth integration is now ready to use! 🎉
