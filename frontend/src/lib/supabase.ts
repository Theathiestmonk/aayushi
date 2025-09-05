import { createClient } from '@supabase/supabase-js'

// Get Supabase URL and anon key from environment variables
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://yemfctzdmuatwhareemm.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InllbWZjdHpkbXVhdHdoYXJlZW1tIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQ5NzQ4NzQsImV4cCI6MjA1MDU1MDg3NH0.REPLACE_WITH_YOUR_ACTUAL_ANON_KEY'

// Log configuration for debugging
console.log('🔧 Supabase URL:', supabaseUrl)
console.log('🔑 Supabase Anon Key:', supabaseAnonKey ? 'Set' : 'Missing')

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    // Configure auth options
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
    // Additional auth options
    flowType: 'pkce'
  }
})

// Listen for auth state changes
supabase.auth.onAuthStateChange((event, session) => {
  console.log('🔄 Supabase auth state changed:', event, session?.user?.email);
  
  if (event === 'SIGNED_IN' && session) {
    console.log('✅ User signed in:', session.user.email);
  } else if (event === 'SIGNED_OUT') {
    console.log('👋 User signed out');
    // Clear all storage when user signs out
    localStorage.clear();
    sessionStorage.clear();
  }
})

// Google OAuth sign-in function
export const signInWithGoogle = async () => {
  try {
    console.log('🚀 Starting Google OAuth sign-in...')
    console.log('🔗 Redirect URL:', `${window.location.origin}/auth/callback`)
    
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
        queryParams: {
          access_type: 'offline',
          prompt: 'consent',
        }
      }
    })
    
    if (error) {
      console.error('❌ Google sign-in error:', error)
      throw new Error(error.message || 'Google sign-in failed')
    }
    
    console.log('✅ Google OAuth initiated successfully')
    return { data, error: null }
  } catch (error) {
    console.error('💥 Google sign-in failed:', error)
    return { data: null, error: error instanceof Error ? error : new Error('Unknown error occurred') }
  }
}

// Google OAuth sign-up function (same as sign-in for OAuth providers)
export const signUpWithGoogle = async () => {
  return signInWithGoogle()
}

// Handle OAuth callback
export const handleAuthCallback = async () => {
  try {
    console.log('🔄 Handling OAuth callback...')
    console.log('🔗 Current URL:', window.location.href)
    
    // Add a small delay to allow Supabase to process the OAuth callback
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // First, try to get the session (this handles the OAuth callback)
    const { data: sessionData, error: sessionError } = await supabase.auth.getSession()
    
    if (sessionError) {
      console.error('❌ Session error:', sessionError)
      return { success: false, error: sessionError.message || 'Authentication failed' }
    }
    
    if (sessionData.session) {
      console.log('✅ Session found:', sessionData.session.user?.email)
      return { 
        success: true, 
        session: sessionData.session,
        user: sessionData.session.user 
      }
    }
    
    // If no session, try to get user directly (for cases where session isn't immediately available)
    const { data: userData, error: userError } = await supabase.auth.getUser()
    
    if (userError) {
      console.error('❌ User error:', userError)
      return { success: false, error: userError.message || 'Authentication failed' }
    }
    
    if (userData.user) {
      console.log('✅ User found:', userData.user.email)
      return { 
        success: true, 
        user: userData.user,
        session: null // Session might not be available immediately
      }
    }
    
    // If still no user, try to handle the OAuth callback from URL
    const urlParams = new URLSearchParams(window.location.search)
    const code = urlParams.get('code')
    const error = urlParams.get('error')
    
    if (error) {
      console.error('❌ OAuth error in URL:', error)
      return { success: false, error: `OAuth error: ${error}` }
    }
    
    if (code) {
      console.log('🔄 OAuth code found in URL, attempting to exchange...')
      // The code should be automatically handled by Supabase, but let's try to get the session again
      const { data: retryData, error: retryError } = await supabase.auth.getSession()
      
      if (retryError) {
        console.error('❌ Retry session error:', retryError)
        return { success: false, error: retryError.message || 'Authentication failed' }
      }
      
      if (retryData.session) {
        console.log('✅ Session found on retry:', retryData.session.user?.email)
        return { 
          success: true, 
          session: retryData.session,
          user: retryData.session.user 
        }
      }
    }
    
    console.log('⚠️ No session or user found in callback')
    return { success: false, error: 'No session found' }
  } catch (error) {
    console.error('💥 Auth callback failed:', error)
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error occurred' 
    }
  }
}

// Sign out function
export const signOut = async () => {
  try {
    const { error } = await supabase.auth.signOut()
    
    if (error) {
      console.error('Sign out error:', error)
      throw error
    }
    
    return { success: true, error: null }
  } catch (error) {
    console.error('Sign out failed:', error)
    return { success: false, error }
  }
}
