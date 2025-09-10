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
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    console.log('📥 Response status:', response.status);
    console.log('📥 Response headers:', Object.fromEntries(response.headers.entries()));
    
    if (!response.ok) {
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
          
          // Set loading state but don't clear existing data yet
          set({ 
            isLoading: true, 
            error: null 
          });
          
          const { success, session, user, error } = await handleAuthCallback();
          
          console.log('🔄 AuthStore: Callback result:', { success, user: user?.email, hasSession: !!session });
          
          if (success && user) {
            // Send OAuth data to backend for proper account linking
            console.log('🔄 AuthStore: Sending OAuth data to backend for account linking...');
            
            try {
              const oauthData = {
                supabase_user_id: user.id,
                email: user.email || '',
                full_name: user.user_metadata?.full_name || user.user_metadata?.name || '',
                avatar_url: user.user_metadata?.avatar_url || null,
                provider: 'google'
              };

              console.log('🔄 AuthStore: OAuth data:', oauthData);

              const response = await fetch(`${API_BASE_URL}/api/v1/auth/google-oauth`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify(oauthData),
              });

              console.log('🔄 AuthStore: Backend response status:', response.status);
              
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

                // Store token in localStorage for persistence
                localStorage.setItem('auth_token', result.data.access_token);
                
                return { success: true, user: userData };
              } else {
                console.error('❌ AuthStore: Backend OAuth failed:', result.error);
                throw new Error(result.error || 'Backend authentication failed');
              }
            } catch (backendError) {
              console.error('❌ AuthStore: Backend integration failed:', backendError);
              console.log('🔄 AuthStore: Falling back to Supabase data...');
              
              // Try to get user profile from user_profiles table
              try {
                const { data: profile, error: profileError } = await supabase
                  .from('user_profiles')
                  .select('*')
                  .eq('id', user.id)
                  .single();

                if (profile && !profileError) {
                  console.log('✅ AuthStore: Found user profile:', profile);
                  
                  const userData: User = {
                    id: user.id,
                    email: user.email || '',
                    username: profile.username || user.user_metadata?.full_name?.split(' ')[0] || user.email?.split('@')[0] || '',
                    full_name: profile.full_name || user.user_metadata?.full_name || user.user_metadata?.name || '',
                    created_at: user.created_at,
                    updated_at: user.updated_at,
                    onboarding_completed: profile.onboarding_completed || false,
                  };

                  console.log('✅ AuthStore: Using profile data:', userData);

                  set({
                    user: userData,
                    token: session?.access_token || null,
                    isAuthenticated: true,
                    isLoading: false,
                    error: null,
                    onboardingCompleted: profile.onboarding_completed || false,
                  });

                  // Store token in localStorage for persistence
                  if (session?.access_token) {
                    localStorage.setItem('auth_token', session.access_token);
                  }
                  
                  return { success: true, user: userData };
                } else {
                  console.log('⚠️ AuthStore: No profile found, using basic user data');
                  throw new Error('No profile found');
                }
              } catch (profileError) {
                console.log('⚠️ AuthStore: Profile fetch failed, using basic user data');
                
                // Fallback to basic user data if profile fetch fails
                const userData: User = {
                  id: user.id,
                  email: user.email || '',
                  username: user.user_metadata?.full_name?.split(' ')[0] || user.email?.split('@')[0] || '',
                  full_name: user.user_metadata?.full_name || user.user_metadata?.name || '',
                  created_at: user.created_at,
                  updated_at: user.updated_at,
                  onboarding_completed: false, // Default to false if no profile found
                };

                console.log('✅ AuthStore: Using basic user data:', userData);

                set({
                  user: userData,
                  token: session?.access_token || null,
                  isAuthenticated: true,
                  isLoading: false,
                  error: null,
                  onboardingCompleted: false,
                });

                // Store token in localStorage for persistence
                if (session?.access_token) {
                  localStorage.setItem('auth_token', session.access_token);
                }
                
                return { success: true, user: userData };
              }
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
        set({ token, isAuthenticated: !!token });
        if (token) {
          localStorage.setItem('auth_token', token);
        } else {
          localStorage.removeItem('auth_token');
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
            console.log('🔍 checkAuth: No token, setting isAuthenticated to false');
            set({ isAuthenticated: false });
            return false;
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
        // Restore token from localStorage if not in state
        if (state && !state.token) {
          const storedToken = localStorage.getItem('auth_token');
          if (storedToken) {
            state.token = storedToken;
            state.isAuthenticated = true;
          }
        }
      },
    }
  )
);

// Initialize auth state on app start
export const initializeAuth = async () => {
  try {
    console.log('🔄 initializeAuth: Starting auth initialization...');
  const { checkAuth } = useAuthStore.getState();
    const isAuthenticated = await checkAuth();
    console.log('🔄 initializeAuth: Auth check result:', isAuthenticated);
    return isAuthenticated;
  } catch (error) {
    console.error('💥 initializeAuth failed:', error);
    return false;
  }
};
