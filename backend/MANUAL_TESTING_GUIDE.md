# Manual Testing Guide for Account Linking Fix

## 🎯 **Testing the Google OAuth Account Linking Fix**

This guide will help you manually test the account linking functionality to ensure that users can link their Google OAuth account to an existing email/password account.

## 📋 **Prerequisites**

1. Backend server running (`python main.py`)
2. Frontend application running (`npm run dev`)
3. Supabase project configured with Google OAuth

## 🧪 **Test Steps**

### **Step 1: Create Account with Email/Password**

1. Open the frontend application in your browser
2. Go to the registration page
3. Register a new account with:
   - **Email**: `test@example.com` (or any test email)
   - **Password**: `password123`
   - **Full Name**: `Test User`
4. Complete the registration process
5. **Important**: Note down any data you create (diet plans, profile info, etc.)

### **Step 2: Create Some Test Data**

1. After successful registration, create some test data:
   - Complete the onboarding process
   - Create a diet plan
   - Add some progress tracking data
   - Update your profile information
2. **Important**: This data should be accessible after account linking

### **Step 3: Logout and Test Google OAuth**

1. Logout from the application
2. Go to the login page
3. Click "Sign in with Google"
4. Use the **same email address** (`test@example.com`) for Google OAuth
5. Complete the Google OAuth flow

### **Step 4: Verify Account Linking**

1. After successful Google OAuth authentication, you should be logged in
2. **Check that you can access all your existing data**:
   - Your profile information should be the same
   - Your diet plans should still be there
   - Your progress tracking should be preserved
   - Your onboarding status should be maintained

## ✅ **Expected Results**

### **Before the Fix (What Was Happening)**
- ❌ New account created with Google OAuth
- ❌ All existing data was lost
- ❌ User had to start over

### **After the Fix (What Should Happen)**
- ✅ Existing account is found by email
- ✅ Google OAuth is linked to existing account
- ✅ All existing data is preserved
- ✅ User can access everything they had before
- ✅ User can now use either email/password or Google OAuth to login

## 🔍 **What to Look For**

### **In the Backend Logs**
Look for these log messages:
```
✅ User exists, linking OAuth account: test@example.com
✅ Account linked successfully for existing user: test@example.com
📋 User data preserved: ID=123, Original Supabase ID=abc-def-ghi
```

### **In the Frontend**
- No error messages during Google OAuth
- Smooth transition to dashboard
- All existing data visible
- Profile shows updated provider info (Google avatar, etc.)

## 🐛 **Troubleshooting**

### **If Account Linking Fails**
1. Check backend logs for error messages
2. Verify Supabase configuration
3. Check that the email addresses match exactly
4. Ensure the backend server is running

### **If Data is Lost**
1. Check that the `supabase_user_id` is preserved in the database
2. Verify that the user record was updated, not replaced
3. Check the database directly to see if data exists

## 📊 **Database Verification**

You can also verify the fix by checking the database directly:

1. **Before Google OAuth**: Note the user's `id` and `supabase_user_id`
2. **After Google OAuth**: Check that:
   - The same `id` is used
   - The same `supabase_user_id` is preserved
   - Only `provider` and `avatar_url` are updated
   - All related data (diet plans, etc.) still references the same user ID

## 🎉 **Success Criteria**

The test is successful if:
- ✅ User can authenticate with Google OAuth using the same email
- ✅ All existing data is accessible after Google OAuth
- ✅ User can switch between authentication methods
- ✅ No duplicate accounts are created
- ✅ Data integrity is maintained

## 📝 **Test Report Template**

```
Test Date: ___________
Tester: ___________
Email Used: ___________

Results:
□ Account linking successful
□ Existing data preserved
□ No duplicate accounts created
□ User can access all previous data
□ Google OAuth works smoothly

Notes:
_________________________________
_________________________________
```

---

## 🔧 **Technical Details**

The fix ensures that:
1. When a user tries Google OAuth with an existing email, the system finds the existing user
2. Instead of creating a new account, it links the OAuth provider to the existing account
3. The original `supabase_user_id` is preserved to maintain data relationships
4. Only OAuth-specific metadata (provider, avatar_url) is updated
5. All existing user data remains accessible

This provides a seamless user experience where users can use either authentication method without losing their data.
