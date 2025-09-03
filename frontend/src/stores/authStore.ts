import { create } from 'zustand';
import { persist } from 'zustand/middleware';

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
}

export interface AuthStore extends AuthState, AuthActions {}

// API base URL - automatically detects environment
const getApiBaseUrl = () => {
  // If environment variable is set, use it
  if ((import.meta as any).env?.VITE_API_URL) {
    return (import.meta as any).env.VITE_API_URL;
  }
  
  // Auto-detect environment based on hostname
  const hostname = window.location.hostname;
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000'; // Local development
  } else if (hostname.includes('vercel.app')) {
    return 'https://aayushi-4swl.onrender.com'; // Production
  } else {
    return 'http://localhost:8000'; // Default fallback
  }
};

const API_BASE_URL = getApiBaseUrl();

// API helper functions
const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${API_BASE_URL}/api/v1${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || `HTTP error! status: ${response.status}`);
    }
    
    return data;
  } catch (error) {
    console.error('API request failed:', error);
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

          if (response.success && response.data) {
            const { user_id, email: userEmail, username, access_token, profile } = response.data;
            
            const user: User = {
              id: user_id,
              email: userEmail,
              username: username || profile?.username || userEmail.split('@')[0],
              full_name: profile?.full_name,
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

            // Store token in localStorage for persistence
            localStorage.setItem('auth_token', access_token);
            
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
          
          console.log('🔐 Auth store: Starting registration API call');
          console.log('📝 Auth store: User data:', { email, userData });

          const response = await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify({
              email,
              password,
              full_name: userData.full_name,
            }),
          });

          console.log('📡 Auth store: API response:', response);

          if (response.success) {
            set({ isLoading: false, error: null });
            console.log('✅ Auth store: Registration successful, returning result');
            return { success: true, data: response.data };
          } else {
            console.log('❌ Auth store: Registration failed:', response.error);
            set({ isLoading: false, error: response.error || 'Registration failed' });
            return { success: false, error: response.error || 'Registration failed' };
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Registration failed';
          console.error('💥 Auth store: Registration error:', error);
          set({ isLoading: false, error: errorMessage });
          return { success: false, error: errorMessage };
        }
      },

      logout: async () => {
        try {
          const { token } = get();
          
          if (token) {
            // Call logout endpoint
            await apiRequest('/auth/logout', {
              method: 'POST',
              headers: {
                Authorization: `Bearer ${token}`,
              },
            });
          }
        } catch (error) {
          console.error('Logout API call failed:', error);
          // Continue with logout even if API call fails
        } finally {
          // Clear local state
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });

          // Clear localStorage
          localStorage.removeItem('auth_token');
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
          const { token } = get();
          
          if (!token) {
            set({ isAuthenticated: false });
            return false;
          }

          const response = await apiRequest('/auth/me', {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });

          if (response.success && response.data) {
            const profile = response.data;
            const user: User = {
              id: profile.id,
              email: profile.email,
              username: profile.username || profile.email.split('@')[0],
              full_name: profile.full_name,
              created_at: profile.created_at,
              updated_at: profile.updated_at,
              onboarding_completed: profile.onboarding_completed || false,
            };

            set({
              user,
              isAuthenticated: true,
              onboardingCompleted: profile.onboarding_completed || false,
              error: null,
            });

            return true;
          } else {
            set({ isAuthenticated: false, token: null });
            localStorage.removeItem('auth_token');
            return false;
          }
        } catch (error) {
          console.error('Auth check failed:', error);
          
          // Check if it's a 404 error (user profile not found)
          if (error instanceof Error && error.message.includes('404')) {
            // User is authenticated but hasn't completed onboarding
            // Try to decode the token to get basic user info
            try {
              const { token } = get(); // Get token again in catch block
              if (token) {
                const payload = JSON.parse(atob(token.split('.')[1]));
                const user: User = {
                  id: payload.sub,
                  email: payload.email,
                  username: payload.email?.split('@')[0] || '',
                  onboarding_completed: false,
                };

                set({
                  user,
                  isAuthenticated: true,
                  onboardingCompleted: false,
                  error: null,
                });

                return true;
              }
            } catch (decodeError) {
              console.error('Failed to decode token:', decodeError);
            }
          }
          
          // For any other error, treat as authentication failure
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
            return false;
          }
                     const response = await apiRequest('/onboarding/status', {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
          if (response.success && response.data?.onboarding_completed) {
            set({ onboardingCompleted: true });
            return true;
          } else {
            set({ onboardingCompleted: false });
            return false;
          }
        } catch (error) {
          console.error('Onboarding status check failed:', error);
          return false;
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
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
  const { checkAuth } = useAuthStore.getState();
  await checkAuth();
};
