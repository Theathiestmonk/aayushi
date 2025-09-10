/**
 * API utility functions for making HTTP requests to the backend
 */

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
    return 'http://localhost:8000'; // Temporarily use local backend for testing
  } else {
    return 'http://localhost:8000'; // Default fallback
  }
};

export const API_BASE_URL = getApiBaseUrl();

/**
 * Make an API request to the backend
 * @param endpoint - API endpoint (e.g., '/auth/login')
 * @param options - Fetch options (method, body, headers, etc.)
 * @returns Promise with the API response data
 */
export const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${API_BASE_URL}/api/v1${endpoint}`;
  
  // Get auth token from localStorage
  const token = localStorage.getItem('auth_token');
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    const data = await response.json();
    
    if (!response.ok) {
      // Handle different error response formats
      const errorMessage = data.detail || data.error || data.message || `HTTP error! status: ${response.status}`;
      throw new Error(errorMessage);
    }
    
    return data;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

/**
 * Make a GET request
 * @param endpoint - API endpoint
 * @returns Promise with the API response data
 */
export const apiGet = (endpoint: string) => apiRequest(endpoint, { method: 'GET' });

/**
 * Make a POST request
 * @param endpoint - API endpoint
 * @param data - Request body data
 * @returns Promise with the API response data
 */
export const apiPost = (endpoint: string, data?: any) => apiRequest(endpoint, {
  method: 'POST',
  body: data ? JSON.stringify(data) : undefined,
});

/**
 * Make a PUT request
 * @param endpoint - API endpoint
 * @param data - Request body data
 * @returns Promise with the API response data
 */
export const apiPut = (endpoint: string, data?: any) => apiRequest(endpoint, {
  method: 'PUT',
  body: data ? JSON.stringify(data) : undefined,
});

/**
 * Make a DELETE request
 * @param endpoint - API endpoint
 * @returns Promise with the API response data
 */
export const apiDelete = (endpoint: string) => apiRequest(endpoint, { method: 'DELETE' });

/**
 * Check if the user is authenticated by verifying the token
 * @returns Promise<boolean> - true if authenticated, false otherwise
 */
export const checkAuthStatus = async (): Promise<boolean> => {
  try {
    const token = localStorage.getItem('auth_token');
    if (!token) return false;
    
    const response = await apiGet('/auth/me');
    return response.success || false;
  } catch (error) {
    console.error('Auth check failed:', error);
    return false;
  }
};

/**
 * Clear authentication data
 */
export const clearAuth = () => {
  localStorage.removeItem('auth_token');
};




