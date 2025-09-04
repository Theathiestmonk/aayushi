import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore, initializeAuth } from '@/stores/authStore';
import Layout from '@/components/Layout';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import OnboardingCheck from '@/components/OnboardingCheck';

// Pages
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import EmailConfirmation from '@/pages/EmailConfirmation';
import Dashboard from '@/pages/Dashboard';
import Onboarding from '@/pages/Onboarding';
import DietPlans from '@/pages/DietPlans';
import DietPlanner from '@/pages/DietPlanner';
import Tracking from '@/pages/Tracking';
import Profile from '@/pages/Profile';

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuthStore();
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

// Public Route Component (redirects authenticated users to dashboard)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuthStore();
  
  console.log('🔍 PublicRoute: isAuthenticated:', isAuthenticated, 'isLoading:', isLoading);
  
  if (isLoading) {
    console.log('⏳ PublicRoute: Still loading, showing spinner');
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }
  
  if (isAuthenticated) {
    console.log('🚫 PublicRoute: User authenticated, redirecting to dashboard');
    return <Navigate to="/dashboard" replace />;
  }
  
  console.log('✅ PublicRoute: User not authenticated, showing public content');
  return <>{children}</>;
};

const App: React.FC = () => {
  const [isInitializing, setIsInitializing] = useState(true);
  const { isAuthenticated, onboardingCompleted, checkOnboardingStatus } = useAuthStore();

  console.log('🔍 App: isAuthenticated:', isAuthenticated, 'onboardingCompleted:', onboardingCompleted, 'isInitializing:', isInitializing);

  useEffect(() => {
    const initApp = async () => {
      try {
        console.log('🔍 App: Initializing auth...');
        await initializeAuth();
        console.log('🔍 App: Auth initialized, isAuthenticated:', isAuthenticated);
        // If authenticated, check onboarding status
        if (isAuthenticated) {
          console.log('🔍 App: Checking onboarding status...');
          await checkOnboardingStatus();
        }
      } catch (error) {
        console.error('Failed to initialize authentication:', error);
      } finally {
        console.log('🔍 App: Initialization complete');
        setIsInitializing(false);
      }
    };

    initApp();
  }, [isAuthenticated, checkOnboardingStatus]);

  if (isInitializing) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex items-center justify-center">
        <div className="text-center">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="w-24 h-24 bg-gradient-to-r from-blue-500 to-green-500 rounded-full mx-auto mb-6 flex items-center justify-center"
          >
            <span className="text-white text-3xl font-bold">🍎</span>
          </motion.div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">AI Dietitian</h1>
          <p className="text-gray-600 mb-6">Initializing your personalized experience...</p>
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <AnimatePresence mode="wait">
        <Routes>
          {/* Public Routes */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <Login />
                </motion.div>
              </PublicRoute>
            }
          />
          
          <Route
            path="/register"
            element={
              <PublicRoute>
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <Register />
                </motion.div>
              </PublicRoute>
            }
          />

          <Route
            path="/email-confirmation"
            element={
              <PublicRoute>
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <EmailConfirmation />
                </motion.div>
              </PublicRoute>
            }
          />

          {/* Root route - redirect based on auth status and onboarding */}
          <Route
            path="/"
            element={
              isAuthenticated ? (
                onboardingCompleted ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <Navigate to="/onboarding" replace />
                )
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <OnboardingCheck
                  fallback={<Navigate to="/onboarding" replace />}
                >
                  <Layout>
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Dashboard />
                    </motion.div>
                  </Layout>
                </OnboardingCheck>
              </ProtectedRoute>
            }
          />

          <Route
            path="/onboarding"
            element={
              <ProtectedRoute>
                <Layout>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Onboarding />
                  </motion.div>
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/diet-plans"
            element={
              <ProtectedRoute>
                <Layout>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <DietPlans />
                  </motion.div>
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/diet-planner"
            element={
              <ProtectedRoute>
                <Layout>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <DietPlanner />
                  </motion.div>
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/tracking"
            element={
              <ProtectedRoute>
                <Layout>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Tracking />
                  </motion.div>
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Layout>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Profile />
                  </motion.div>
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Catch all route - redirect to dashboard if authenticated, login if not */}
          <Route
            path="*"
            element={
              isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
        </Routes>
      </AnimatePresence>
    </div>
  );
};

export default App;

