import React, { useEffect, useState } from 'react';
import { useAuthStore } from '@/stores/authStore';
import LoadingSpinner from './ui/LoadingSpinner';

interface OnboardingCheckProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

const OnboardingCheck: React.FC<OnboardingCheckProps> = ({ 
  children, 
  fallback = <div>Checking onboarding status...</div> 
}) => {
  const { onboardingCompleted, checkOnboardingStatus, isLoading } = useAuthStore();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const checkStatus = async () => {
      if (onboardingCompleted === undefined) {
        await checkOnboardingStatus();
      }
      setIsChecking(false);
    };

    checkStatus();
  }, [onboardingCompleted, checkOnboardingStatus]);

  if (isLoading || isChecking) {
    return <LoadingSpinner />;
  }

  if (onboardingCompleted) {
    return <>{children}</>;
  }

  return <>{fallback}</>;
};

export default OnboardingCheck;




