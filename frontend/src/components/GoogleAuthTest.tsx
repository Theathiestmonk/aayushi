import React, { useState } from 'react';
import { supabase } from '@/lib/supabase';

const GoogleAuthTest: React.FC = () => {
  const [status, setStatus] = useState<string>('Ready');
  const [error, setError] = useState<string | null>(null);

  const testSupabaseConnection = async () => {
    try {
      setStatus('Testing Supabase connection...');
      setError(null);

      // Test basic connection
      const { data, error } = await supabase.auth.getSession();
      
      if (error) {
        setError(`Connection error: ${error.message}`);
        setStatus('Connection failed');
        return;
      }

      setStatus('Supabase connected successfully!');
      console.log('Supabase session:', data);
    } catch (err) {
      setError(`Test failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
      setStatus('Test failed');
    }
  };

  const testGoogleOAuth = async () => {
    try {
      setStatus('Testing Google OAuth...');
      setError(null);

      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
      });

      if (error) {
        setError(`OAuth error: ${error.message}`);
        setStatus('OAuth failed');
        return;
      }

      setStatus('Google OAuth initiated successfully!');
      console.log('OAuth data:', data);
    } catch (err) {
      setError(`OAuth test failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
      setStatus('OAuth test failed');
    }
  };

  return (
    <div className="p-4 bg-gray-100 rounded-lg">
      <h3 className="text-lg font-semibold mb-4">Google Auth Test</h3>
      <div className="space-y-2">
        <p><strong>Status:</strong> {status}</p>
        {error && <p className="text-red-600"><strong>Error:</strong> {error}</p>}
      </div>
      <div className="mt-4 space-x-2">
        <button
          onClick={testSupabaseConnection}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Test Supabase Connection
        </button>
        <button
          onClick={testGoogleOAuth}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Test Google OAuth
        </button>
      </div>
    </div>
  );
};

export default GoogleAuthTest;
