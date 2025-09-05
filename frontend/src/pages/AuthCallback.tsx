import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { motion } from 'framer-motion';

const AuthCallback: React.FC = () => {
  const navigate = useNavigate();
  const { handleGoogleCallback } = useAuthStore();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        console.log('🔄 AuthCallback: Starting callback handling...');
        console.log('🔗 Current URL:', window.location.href);
        console.log('🔗 URL params:', new URLSearchParams(window.location.search).toString());
        
        // DON'T clear storage here - let Supabase handle the session
        const result = await handleGoogleCallback();
        
        console.log('🔄 AuthCallback: Result:', result);
        
        if (result.success) {
          setStatus('success');
          console.log('✅ AuthCallback: Authentication successful, redirecting...');
          
          // Redirect to dashboard after a short delay
          setTimeout(() => {
            navigate('/dashboard');
          }, 2000);
        } else {
          setStatus('error');
          setError(result.error || 'Authentication failed');
          console.error('❌ AuthCallback: Authentication failed:', result.error);
          
          // Redirect to login after error
          setTimeout(() => {
            navigate('/login');
          }, 3000);
        }
      } catch (error) {
        console.error('💥 AuthCallback: Unexpected error:', error);
        setStatus('error');
        setError('An unexpected error occurred');
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      }
    };

    handleCallback();
  }, [handleGoogleCallback, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full mx-4 text-center"
      >
        {status === 'loading' && (
          <>
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="w-16 h-16 bg-gradient-to-r from-blue-500 to-green-500 rounded-full mx-auto mb-6 flex items-center justify-center"
            >
              <span className="text-white text-2xl font-bold">🍎</span>
            </motion.div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Completing Sign In</h2>
            <p className="text-gray-600 mb-6">Please wait while we complete your Google authentication...</p>
            <LoadingSpinner />
          </>
        )}

        {status === 'success' && (
          <>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="w-16 h-16 bg-green-500 rounded-full mx-auto mb-6 flex items-center justify-center"
            >
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </motion.div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Welcome!</h2>
            <p className="text-gray-600 mb-6">You've successfully signed in with Google. Redirecting to your dashboard...</p>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <motion.div
                className="bg-green-500 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: "100%" }}
                transition={{ duration: 2 }}
              />
            </div>
          </>
        )}

        {status === 'error' && (
          <>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="w-16 h-16 bg-red-500 rounded-full mx-auto mb-6 flex items-center justify-center"
            >
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </motion.div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Authentication Failed</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <p className="text-sm text-gray-500">Redirecting to login page...</p>
          </>
        )}
      </motion.div>
    </div>
  );
};

export default AuthCallback;
