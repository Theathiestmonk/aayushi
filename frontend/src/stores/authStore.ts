import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { signInWithGoogle, handleAuthCallback, supabase } from '../lib/supabase';

// Types
export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  created_at?: string;
  updated_at?: string;
  onboarding_completed?: boolean;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  onboardingCompleted: boolean;
}

export interface AuthActions {
  // Authentication actions
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string; data?: any }>;
  register: (email: string, password: string, userData: { full_name: string }) => Promise<{ success: boolean; error?: string; data?: any }>;
  logout: () => Promise<void>;
  
  // Google OAuth actions
  loginWithGoogle: () => Promise<{ success: boolean; error?: string }>;
  registerWithGoogle: () => Promise<{ success: boolean; error?: string }>;
  handleGoogleCallback: () => Promise<{ success: boolean; error?: string; user?: any }>;
  
  // State management
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  setOnboardingCompleted: (completed: boolean) => void;
  
  // Utility actions
  checkAuth: () => Promise<boolean>;
  refreshToken: () => Promise<boolean>;
  checkOnboardingStatus: () => Promise<boolean>;
  resetAuthState: () => void;
  clearInvalidToken: () => void;
}

export interface AuthStore extends AuthState, AuthActions {}

// API base URL - automatically detects environment
const getApiBaseUrl = () => {
  // If environment variable is set, use it
  if ((import.meta as any).env?.VITE_API_URL) {
    console.log('🔧 Using VITE_API_URL:', (import.meta as any).env.VITE_API_URL);
    return (import.meta as any).env.VITE_API_URL;
  }
  
  // Auto-detect environment based on hostname
  const hostname = window.location.hostname;
  console.log('🌐 Detected hostname:', hostname);
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    console.log('🏠 Using localhost API');
    return 'http://localhost:8000'; // Local development
  } else if (hostname.includes('vercel.app')) {
    console.log('☁️ Using production API for Vercel');
    return 'https://aayushi-4swl.onrender.com'; // Production
  } else {
    console.log('⚠️ Using fallback localhost API');
    return 'http://localhost:8000'; // Default fallback
  }
};

const API_BASE_URL = getApiBaseUrl();

// API helper functions
export const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${API_BASE_URL}/api/v1${endpoint}`;
  console.log('🚀 Making API request to:', url);
  console.log('🔧 API_BASE_URL:', API_BASE_URL);
  
  // Get auth token from localStorage
  let token = localStorage.getItem('auth_token');
  console.log('🔑 Auth token exists:', !!token);
  console.log('🔑 Auth token value:', token ? token.substring(0, 50) + '...' : 'null');
  console.log('🔑 Auth token full value:', token);
  
  // If no token in localStorage, try to get from Zustand state
  if (!token) {
    const { token: stateToken } = useAuthStore.getState();
    if (stateToken) {
      token = stateToken;
      console.log('🔑 Using token from Zustand state');
    }
  }
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };
  
  console.log('🔧 Request headers:', defaultOptions.headers);

  try {
    const response = await fetch(url, defaultOptions);
    console.log('📥 Response status:', response.status);
    console.log('📥 Response headers:', Object.fromEntries(response.headers.entries()));
    
    if (!response.ok) {
      // Handle 401 Unauthorized specifically
      if (response.status === 401) {
        console.log('🔐 401 Unauthorized - checking if token is valid...');
        
        // First, try to get the response body to see what the actual error is
        let errorMessage = 'Authentication failed';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || 'Authentication failed';
          console.log('🔐 401 Error details:', errorData);
        } catch (e) {
          console.log('🔐 401 Error - could not parse response body');
        }
        
        // Check if this is a token format error (not expired)
        if (errorMessage.includes('Not enough segments') || errorMessage.includes('Invalid token format')) {
          console.log('🔐 401 Error - Invalid token format, clearing auth state');
          const { resetAuthState } = useAuthStore.getState();
          resetAuthState();
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
          throw new Error('Invalid token format. Please log in again.');
        }
        
        // Check if this is an "Invalid user information" error (corrupted token)
        if (errorMessage.includes('Invalid user information')) {
          console.log('🔐 401 Error - Invalid user information, clearing corrupted token');
          const { clearInvalidToken } = useAuthStore.getState();
          clearInvalidToken();
          throw new Error('Invalid user information. Please log in again.');
        }
        
        // For other 401 errors, don't clear the token immediately
        console.log('🔐 401 Error - Other authentication issue:', errorMessage);
        throw new Error(`Authentication failed: ${errorMessage}`);
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('✅ API request successful:', data);
    return data;
  } catch (error) {
    console.error(`❌ API request failed for ${endpoint}:`, error);
    throw error;
  }
};

// Create the store
export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      onboardingCompleted: false,

      // Authentication actions
      login: async (email: string, password: string) => {
        try {
          set({ isLoading: true, error: null });

          const response = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
          });

          console.log('🔐 Login response received:', response);

          if (response.success && response.data) {
            const { user_id, email: userEmail, username, access_token, profile } = response.data;
            console.log('🔐 Extracted data:', { user_id, userEmail, username, access_token, profile });
            
            const user: User = {
              id: user_id,
              email: userEmail,
              username: username || profile?.username || userEmail.split('@')[0],
              full_name: profile?.full_name || '',
              created_at: profile?.created_at,
              updated_at: profile?.updated_at,
              onboarding_completed: profile?.onboarding_completed || false,
            };

            set({
              user,
              token: access_token,
              isAuthenticated: true,
              isLoading: false,
              error: null,
              onboardingCompleted: profile?.onboarding_completed || false,
            });

            console.log('🔐 User state set:', { user, isAuthenticated: true, onboardingCompleted: profile?.onboarding_completed || false });

            // Store token in localStorage for persistence
            localStorage.setItem('auth_token', access_token);
            
            console.log('🔐 Login successful, returning success');
            return { success: true };
          } else {
            set({ isLoading: false, error: response.error || 'Login failed' });
            return { success: false, error: response.error || 'Login failed' };
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Login failed';
          set({ isLoading: false, error: errorMessage });
          return { success: false, error: errorMessage };
        }
      },

      register: async (email: string, password: string, userData: { full_name: string }) => {
        try {
          set({ isLoading: true, error: null });

          const response = await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify({
              email,
              password,
              full_name: userData.full_name,
            }),
          });

          if (response.success) {
            set({ isLoading: false, error: null });
            return { success: true, data: response.data };
          } else {
            set({ isLoading: false, error: response.error || 'Registration failed' });
            return { success: false, error: response.error || 'Registration failed' };
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Registration failed';
          set({ isLoading: false, error: errorMessage });
          return { success: false, error: errorMessage };
        }
      },

      logout: async () => {
        try {
          console.log('🔄 AuthStore: Logging out...');
          
          // Sign out from Supabase
          const { error } = await supabase.auth.signOut();
          
          if (error) {
            console.error('❌ Supabase logout error:', error);
          } else {
            console.log('✅ Supabase logout successful');
          }
        } catch (error) {
          console.error('💥 Logout failed:', error);
        } finally {
          // Clear local state
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
            onboardingCompleted: false,
          });

          // Clear all storage
          localStorage.clear();
          sessionStorage.clear();
        }
      },

      // Google OAuth methods
      loginWithGoogle: async () => {
        try {
          console.log('🔄 AuthStore: Starting Google OAuth...');
          
          // Start the OAuth process immediately without any state changes
          const { error } = await signInWithGoogle();
          
          if (error) {
            const errorMessage = error instanceof Error ? error.message : 'Google sign-in failed';
            set({ error: errorMessage });
            return { success: false, error: errorMessage };
          }
          
          // Clear storage only after successful OAuth initiation
          localStorage.removeItem('auth-storage');
          sessionStorage.clear();
          
          // Return success - let the component handle the redirect with success message
          return { success: true };
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Google sign-in failed';
          set({ error: errorMessage });
          return { success: false, error: errorMessage };
        }
      },

      registerWithGoogle: async () => {
        // For OAuth providers, sign-up and sign-in are the same
        return get().loginWithGoogle();
      },

      handleGoogleCallback: async () => {
        try {
          console.log('🔄 AuthStore: Starting Google callback handling...');
          console.log('🔄 AuthStore: Current URL:', window.location.href);
          
          // Set loading state but don't clear existing data yet
          set({ 
            isLoading: true, 
            error: null 
          });
          
          console.log('🔄 AuthStore: Calling handleAuthCallback...');
          const { success, session, user, error } = await handleAuthCallback();
          
          console.log('🔄 AuthStore: Callback result:', { success, user: user?.email, hasSession: !!session });
          console.log('🔄 AuthStore: Session details:', session ? { access_token: !!session.access_token, user: session.user?.email } : 'No session');
          console.log('🔄 AuthStore: User details:', user ? { id: user.id, email: user.email } : 'No user');
          
          if (success && user) {
            // Send OAuth data to backend for proper account linking
            console.log('🔄 AuthStore: Sending OAuth data to backend for account linking...');
            console.log('🔄 AuthStore: User data from Supabase:', { id: user.id, email: user.email });
            
            try {
              const oauthData = {
                supabase_user_id: user.id,
                email: user.email || '',
                full_name: user.user_metadata?.full_name || user.user_metadata?.name || '',
                avatar_url: user.user_metadata?.avatar_url || null,
                provider: 'google'
              };

              console.log('🔄 AuthStore: OAuth data:', oauthData);
              console.log('🔄 AuthStore: Making request to:', `${API_BASE_URL}/api/v1/auth/google-oauth`);

              const response = await fetch(`${API_BASE_URL}/api/v1/auth/google-oauth`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify(oauthData),
              });

              console.log('🔄 AuthStore: Backend response status:', response.status);
              console.log('🔄 AuthStore: Backend response headers:', Object.fromEntries(response.headers.entries()));
              
              const result = await response.json();
              console.log('🔄 AuthStore: Backend response data:', result);

              if (result.success && result.data) {
                const userData: User = {
                  id: result.data.user_id,
                  email: result.data.email,
                  username: result.data.username,
                  full_name: result.data.full_name || '',
                  created_at: result.data.created_at,
                  updated_at: result.data.updated_at,
                  onboarding_completed: result.data.onboarding_completed,
                };

                console.log('✅ AuthStore: User data from backend (account linked):', userData);

                set({
                  user: userData,
                  token: result.data.access_token,
                  isAuthenticated: true,
                  isLoading: false,
                  error: null,
                  onboardingCompleted: result.data.onboarding_completed,
                });

                console.log('✅ AuthStore: Google OAuth - onboardingCompleted set to:', result.data.onboarding_completed);
                console.log('✅ AuthStore: Google OAuth - token set in state:', !!result.data.access_token);

                // Store token in localStorage for persistence
                localStorage.setItem('auth_token', result.data.access_token);
                console.log('✅ AuthStore: Google OAuth - token stored in localStorage');
                console.log('✅ AuthStore: Google OAuth - token value:', result.data.access_token.substring(0, 50) + '...');
                
                return { success: true, user: userData };
              } else {
                console.error('❌ AuthStore: Backend OAuth failed:', result.error);
                console.error('❌ AuthStore: Backend OAuth response:', result);
                throw new Error(result.error || 'Backend authentication failed');
              }
            } catch (backendError) {
              console.error('❌ AuthStore: Backend integration failed:', backendError);
              console.log('🔄 AuthStore: Using basic user data without profile...');
              
              // Use basic user data without trying to fetch from Supabase directly
              // This ensures compatibility with RLS policies on domain
              const userData: User = {
                id: user.id,
                email: user.email || '',
                username: user.user_metadata?.full_name?.split(' ')[0] || user.email?.split('@')[0] || '',
                full_name: user.user_metadata?.full_name || user.user_metadata?.name || '',
                created_at: user.created_at,
                updated_at: user.updated_at,
                onboarding_completed: false, // Default to false, will be updated by checkOnboardingStatus
              };

              console.log('✅ AuthStore: Using basic user data:', userData);

              set({
                user: userData,
                token: null, // Don't set Supabase token - it won't work with backend
                isAuthenticated: false, // Set to false since we don't have valid backend token
                isLoading: false,
                error: 'Backend authentication failed - diet plan generation will not work',
                onboardingCompleted: false,
              });

              // Don't store any token since we don't have a valid backend token
              console.log('⚠️ AuthStore: Fallback - No valid backend token available');
              console.log('⚠️ AuthStore: Fallback - User will be redirected to login');
              
              return { success: false, error: 'Backend authentication failed' };
            }
          } else {
            const errorMessage = typeof error === 'string' ? error : (error as unknown as Error)?.message || 'Authentication failed';
            console.error('❌ AuthStore: Callback failed:', errorMessage);
            set({ 
              user: null, 
              token: null, 
              isAuthenticated: false, 
              isLoading: false, 
              error: errorMessage 
            });
            return { success: false, error: errorMessage };
          }
        } catch (error) {
          const errorMessage = typeof error === 'string' ? error : (error as Error)?.message || 'Authentication callback failed';
          console.error('💥 AuthStore: Callback error:', errorMessage);
          set({ 
            user: null, 
            token: null, 
            isAuthenticated: false, 
            isLoading: false, 
            error: errorMessage 
          });
          return { success: false, error: errorMessage };
        }
      },

      // State management actions
      setUser: (user: User | null) => {
        set({ user, isAuthenticated: !!user });
      },

      setToken: (token: string | null) => {
        console.log('🔄 setToken: Setting token:', !!token);
        set({ token, isAuthenticated: !!token });
        if (token) {
          localStorage.setItem('auth_token', token);
          console.log('🔄 setToken: Token stored in localStorage');
        } else {
          localStorage.removeItem('auth_token');
          console.log('🔄 setToken: Token removed from localStorage');
        }
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      setError: (error: string | null) => {
        set({ error });
      },

      clearError: () => {
        set({ error: null });
      },

      setOnboardingCompleted: (completed: boolean) => {
        set({ onboardingCompleted: completed });
      },

      // Utility actions
      checkAuth: async () => {
        try {
          console.log('🔍 checkAuth: Starting authentication check...');
          
          const { token } = get();
          console.log('🔍 checkAuth: token exists:', !!token);
          
          if (!token) {
            console.log('🔍 checkAuth: No token in state, checking localStorage...');
            const storedToken = localStorage.getItem('auth_token');
            if (storedToken) {
              console.log('🔍 checkAuth: Found token in localStorage, restoring to state...');
              set({ token: storedToken, isAuthenticated: true });
            } else {
              console.log('🔍 checkAuth: No token found, setting isAuthenticated to false');
              set({ isAuthenticated: false });
              return false;
            }
          }

          // Check with backend API to get proper user data
          console.log('🔍 checkAuth: Checking with backend API...');
          const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (!response.ok) {
            console.error('❌ Backend auth check failed:', response.status);
            
            // If backend auth fails, check if there's a valid Supabase session
            console.log('🔍 checkAuth: Backend auth failed, checking Supabase session...');
            const { data: sessionData, error: sessionError } = await supabase.auth.getSession();
            
            if (sessionError) {
              console.error('❌ Supabase session error:', sessionError);
              set({ isAuthenticated: false, token: null });
              localStorage.removeItem('auth_token');
              return false;
            }
            
            if (sessionData.session) {
              console.log('✅ checkAuth: Valid Supabase session found, handling OAuth callback...');
              // Try to handle the OAuth callback to get a new token
              const { handleGoogleCallback } = get();
              const result = await handleGoogleCallback();
              
              if (result.success) {
                console.log('✅ checkAuth: OAuth callback successful, user authenticated');
                return true;
              }
            }
            
            set({ isAuthenticated: false, token: null });
            localStorage.removeItem('auth_token');
            return false;
          }

          const result = await response.json();
          
          if (result.success && result.data) {
            const user: User = {
              id: result.data.id,
              email: result.data.email,
              username: result.data.username,
              full_name: result.data.full_name,
              created_at: result.data.created_at,
              updated_at: result.data.updated_at,
              onboarding_completed: result.data.onboarding_completed,
            };

            console.log('✅ checkAuth: User found:', user.email);

            set({
              user,
              isAuthenticated: true,
              onboardingCompleted: result.data.onboarding_completed,
              error: null,
            });

            return true;
          } else {
            set({ isAuthenticated: false, token: null });
            localStorage.removeItem('auth_token');
            return false;
          }
        } catch (error) {
          console.error('💥 Auth check failed:', error);
          set({ isAuthenticated: false, token: null, error: null });
          localStorage.removeItem('auth_token');
          return false;
        }
      },

      refreshToken: async () => {
        try {
          const { token } = get();
          
          if (!token) {
            return false;
          }

          const response = await apiRequest('/auth/verify-session', {
            method: 'POST',
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });

          if (response.success && response.data?.valid) {
            return true;
          } else {
            // Token is invalid, clear auth state
            set({
              user: null,
              token: null,
              isAuthenticated: false,
            });
            localStorage.removeItem('auth_token');
            return false;
          }
        } catch (error) {
          console.error('Token refresh failed:', error);
          return false;
        }
      },

      checkOnboardingStatus: async () => {
        try {
          const { token } = get();
          if (!token) {
            console.log('🔍 checkOnboardingStatus: No token available');
            return false;
          }
          
          console.log('🔍 checkOnboardingStatus: Checking status with token...');
          const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/status`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          console.log('🔍 checkOnboardingStatus: Response status:', response.status);
          
          if (response.ok) {
            const result = await response.json();
            console.log('🔍 checkOnboardingStatus: Response data:', result);
            
            if (result.success && result.data?.onboarding_completed) {
              console.log('✅ checkOnboardingStatus: Onboarding completed');
              set({ onboardingCompleted: true });
              return true;
            } else {
              console.log('⚠️ checkOnboardingStatus: Onboarding not completed');
              set({ onboardingCompleted: false });
              return false;
            }
          } else {
            console.error('❌ checkOnboardingStatus: API call failed:', response.status);
            set({ onboardingCompleted: false });
            return false;
          }
        } catch (error) {
          console.error('❌ checkOnboardingStatus: Error:', error);
          set({ onboardingCompleted: false });
          return false;
        }
      },

      resetAuthState: () => {
        console.log('🔄 AuthStore: Resetting authentication state...');
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
          onboardingCompleted: false,
        });
        localStorage.clear();
        sessionStorage.clear();
      },

      clearInvalidToken: () => {
        console.log('🧹 Clearing invalid token and forcing fresh login...');
        const { resetAuthState } = get();
        resetAuthState();
        
        // Also clear any Supabase session
        supabase.auth.signOut();
        
        // Redirect to login page
        window.location.href = '/login';
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
        onboardingCompleted: state.onboardingCompleted,
      }),
      onRehydrateStorage: () => (state) => {
        // Always restore token from localStorage on app start, but validate it first
        if (state) {
          const storedToken = localStorage.getItem('auth_token');
          console.log('🔄 onRehydrateStorage: Stored token exists:', !!storedToken);
          console.log('🔄 onRehydrateStorage: Token value:', storedToken ? storedToken.substring(0, 50) + '...' : 'null');
          
          if (storedToken) {
            // Validate token before restoring it
            try {
              // Decode token without verification to check structure
              const payload = JSON.parse(atob(storedToken.split('.')[1]));
              console.log('🔄 onRehydrateStorage: Token payload:', payload);
              
              // Check if token has required fields and valid structure
              if (payload.sub && payload.email && payload.email !== '') {
                state.token = storedToken;
                state.isAuthenticated = true;
                console.log('🔄 onRehydrateStorage: Valid token restored from localStorage');
                console.log('🔄 onRehydrateStorage: State updated - isAuthenticated:', true);
              } else {
                console.log('⚠️ onRehydrateStorage: Invalid token structure, clearing...');
                console.log('⚠️ onRehydrateStorage: Token fields - sub:', payload.sub, 'email:', payload.email);
                localStorage.removeItem('auth_token');
                state.token = null;
                state.isAuthenticated = false;
                console.log('🔄 onRehydrateStorage: Invalid token cleared');
              }
            } catch (error) {
              console.log('⚠️ onRehydrateStorage: Token decode failed, clearing...', error);
              localStorage.removeItem('auth_token');
              state.token = null;
              state.isAuthenticated = false;
              console.log('🔄 onRehydrateStorage: Corrupted token cleared');
            }
          } else {
            console.log('🔄 onRehydrateStorage: No token found in localStorage');
            state.token = null;
            state.isAuthenticated = false;
          }
        }
      },
    }
  )
);

// Test function to check token status (for debugging)
export const checkTokenStatus = () => {
  const localStorageToken = localStorage.getItem('auth_token');
  const { token: stateToken, isAuthenticated } = useAuthStore.getState();
  
  console.log('🔍 Token Status Check:');
  console.log('  - localStorage token exists:', !!localStorageToken);
  console.log('  - localStorage token value:', localStorageToken ? localStorageToken.substring(0, 50) + '...' : 'null');
  console.log('  - Zustand state token exists:', !!stateToken);
  console.log('  - Zustand state token value:', stateToken ? stateToken.substring(0, 50) + '...' : 'null');
  console.log('  - isAuthenticated:', isAuthenticated);
  
  return {
    localStorageToken: !!localStorageToken,
    stateToken: !!stateToken,
    isAuthenticated,
    tokenValue: localStorageToken || stateToken
  };
};

// Function to manually clear corrupted token
export const clearCorruptedToken = () => {
  console.log('🧹 Manually clearing corrupted token...');
  localStorage.removeItem('auth_token');
  sessionStorage.clear();
  
  const { resetAuthState } = useAuthStore.getState();
  resetAuthState();
  
  // Also clear Supabase session
  supabase.auth.signOut();
  
  console.log('✅ Corrupted token cleared, redirecting to login...');
  window.location.href = '/login';
};

// Make it available globally for debugging
if (typeof window !== 'undefined') {
  (window as any).checkTokenStatus = checkTokenStatus;
  (window as any).clearCorruptedToken = clearCorruptedToken;
}

// Initialize auth state on app start
export const initializeAuth = async () => {
  try {
    console.log('🔄 initializeAuth: Starting auth initialization...');
    
    // First check if we have a token in localStorage
    const storedToken = localStorage.getItem('auth_token');
    console.log('🔄 initializeAuth: Stored token exists:', !!storedToken);
    
    // If we have a token, check if it's valid
    if (storedToken) {
      console.log('🔄 initializeAuth: Checking stored token with backend...');
      const { checkAuth } = useAuthStore.getState();
      const isAuthenticated = await checkAuth();
      console.log('🔄 initializeAuth: Auth check result:', isAuthenticated);
      return isAuthenticated;
    }
    
    // If no token, check if there's a valid Supabase session
    console.log('🔄 initializeAuth: No token found, checking Supabase session...');
    const { data: sessionData, error: sessionError } = await supabase.auth.getSession();
    
    console.log('🔍 initializeAuth: Supabase session data:', sessionData);
    console.log('🔍 initializeAuth: Supabase session error:', sessionError);
    
    if (sessionError) {
      console.error('❌ initializeAuth: Supabase session error:', sessionError);
      return false;
    }
    
    if (sessionData.session) {
      console.log('✅ initializeAuth: Valid Supabase session found:', sessionData.session.user?.email);
      console.log('🔍 initializeAuth: Session access token exists:', !!sessionData.session.access_token);
      
      // Handle the Google OAuth callback to get our backend token
      const { handleGoogleCallback } = useAuthStore.getState();
      const result = await handleGoogleCallback();
      
      console.log('🔍 initializeAuth: OAuth callback result:', result);
      
      if (result.success) {
        console.log('✅ initializeAuth: Google OAuth callback successful');
        // Verify the token was stored
        const newToken = localStorage.getItem('auth_token');
        console.log('🔍 initializeAuth: New token stored:', !!newToken);
        return true;
      } else {
        console.error('❌ initializeAuth: Google OAuth callback failed:', result.error);
        return false;
      }
    }
    
    console.log('🔄 initializeAuth: No valid session found, user not authenticated');
    return false;
  } catch (error) {
    console.error('💥 initializeAuth failed:', error);
    return false;
  }
};
