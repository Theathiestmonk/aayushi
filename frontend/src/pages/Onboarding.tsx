import React, { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion } from 'framer-motion';
import { 
  ChevronLeft, 
  ChevronRight, 
  User, 
  Heart, 
  Activity, 
  Utensils, 
  Target, 
  Ruler, 
  Star,
  Shield,
  Lock
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

// Step-based validation schemas
const stepSchemas = {
  0: z.object({
    // Basic Information - Required fields
    full_name: z.string().min(2, 'Full name must be at least 2 characters'),
    age: z.number().min(1, 'Age must be at least 1').max(150, 'Age must be less than 150'),
    gender: z.enum(['male', 'female', 'other'], { required_error: 'Please select your gender' }),
    height_cm: z.number().min(50, 'Height must be at least 50cm').max(300, 'Height must be less than 300cm'),
    weight_kg: z.number().min(20, 'Weight must be at least 20kg').max(500, 'Weight must be less than 500kg'),
    contact_number: z.string().optional(),
    emergency_contact_name: z.string().optional(),
    emergency_contact_number: z.string().optional(),
    occupation: z.enum(['student', 'professional', 'homemaker', 'retired', 'other'], { required_error: 'Please select your occupation' }),
    occupation_other: z.string().optional(),
  }),
  
  1: z.object({
    // Medical History - All optional but with validation
    medical_conditions: z.array(z.string()).default([]),
    medications_supplements: z.array(z.string()).default([]),
    surgeries_hospitalizations: z.string().optional(),
    food_allergies: z.array(z.string()).default([]),
    family_history: z.array(z.string()).default([]),
  }),
  
  2: z.object({
    // Lifestyle Habits - Required fields
    daily_routine: z.enum(['sedentary', 'moderately_active', 'highly_active'], { required_error: 'Please select your activity level' }),
    sleep_hours: z.enum(['<5', '5-6', '7-8', '>8'], { required_error: 'Please select your sleep duration' }),
    alcohol_consumption: z.boolean().default(false),
    alcohol_frequency: z.string().optional(),
    smoking: z.boolean().default(false),
    stress_level: z.enum(['low', 'moderate', 'high'], { required_error: 'Please select your stress level' }),
    physical_activity_type: z.string().optional(),
    physical_activity_frequency: z.string().optional(),
    physical_activity_duration: z.string().optional(),
  }),
  
  3: z.object({
    // Eating Habits - Required fields
    meal_timings: z.enum(['regular', 'irregular'], { required_error: 'Please select your meal timing pattern' }),
    food_preference: z.enum(['vegetarian', 'vegan', 'non_vegetarian', 'eggetarian'], { required_error: 'Please select your food preference' }),
    eating_out_frequency: z.enum(['rare', 'weekly', '2-3_times_week', 'daily'], { required_error: 'Please select how often you eat out' }),
    daily_water_intake: z.enum(['<1L', '1-2L', '2-3L', '>3L'], { required_error: 'Please select your daily water intake' }),
    breakfast_habits: z.string().optional(),
    lunch_habits: z.string().optional(),
    dinner_habits: z.string().optional(),
    snacks_habits: z.string().optional(),
    beverages_habits: z.string().optional(),
    cultural_restrictions: z.string().optional(),
    common_cravings: z.array(z.string()).default([]),
  }),
  
  4: z.object({
    // Goals & Expectations - Required fields
    progress_pace: z.enum(['gradual', 'moderate', 'aggressive'], { required_error: 'Please select your preferred progress pace' }),
    primary_goals: z.array(z.string()).default([]),
    specific_health_concerns: z.string().optional(),
    past_diets: z.string().optional(),
  }),
  
  5: z.object({
    // Measurements & Tracking - Required fields
    weight_trend: z.enum(['increased', 'decreased', 'stable'], { required_error: 'Please select your weight trend' }),
    current_weight_kg: z.number().min(20, 'Weight must be at least 20kg').max(500, 'Weight must be less than 500kg').optional(),
    waist_circumference_cm: z.number().min(30, 'Waist must be at least 30cm').max(200, 'Waist must be less than 200cm').optional(),
    bmi: z.number().min(10, 'BMI must be at least 10').max(100, 'BMI must be less than 100').optional(),
    blood_reports: z.array(z.string()).default([]),
  }),
  
  6: z.object({
    // Personalization & Motivation - Required fields
    who_cooks: z.enum(['self', 'family_member', 'cook_helper'], { required_error: 'Please select who cooks at home' }),
    budget_flexibility: z.enum(['limited', 'flexible', 'high'], { required_error: 'Please select your budget flexibility' }),
    motivation_level: z.number().min(1, 'Motivation level must be at least 1').max(10, 'Motivation level must be at most 10'),
    support_system: z.enum(['strong', 'moderate', 'weak'], { required_error: 'Please select your support system level' }),
    loved_foods: z.string().optional(),
    disliked_foods: z.string().optional(),
    cooking_facilities: z.array(z.string()).default([]),
  }),
};

// Complete schema for final validation
const onboardingSchema = z.object({
  // Basic Information
  full_name: z.string().min(2, 'Full name must be at least 2 characters'),
  age: z.number().min(1).max(150),
  gender: z.enum(['male', 'female', 'other']),
  height_cm: z.number().min(50).max(300),
  weight_kg: z.number().min(20).max(500),
  contact_number: z.string().optional(),
  emergency_contact_name: z.string().optional(),
  emergency_contact_number: z.string().optional(),
  occupation: z.enum(['student', 'professional', 'homemaker', 'retired', 'other']),
  occupation_other: z.string().optional(),
  
  // Medical History
  medical_conditions: z.array(z.string()).default([]),
  medications_supplements: z.array(z.string()).default([]),
  surgeries_hospitalizations: z.string().optional(),
  food_allergies: z.array(z.string()).default([]),
  family_history: z.array(z.string()).default([]),
  
  // Lifestyle Habits
  daily_routine: z.enum(['sedentary', 'moderately_active', 'highly_active']),
  sleep_hours: z.enum(['<5', '5-6', '7-8', '>8']),
  alcohol_consumption: z.boolean().default(false),
  alcohol_frequency: z.string().optional(),
  smoking: z.boolean().default(false),
  stress_level: z.enum(['low', 'moderate', 'high']),
  physical_activity_type: z.string().optional(),
  physical_activity_frequency: z.string().optional(),
  physical_activity_duration: z.string().optional(),
  
  // Eating Habits
  breakfast_habits: z.string().optional(),
  lunch_habits: z.string().optional(),
  dinner_habits: z.string().optional(),
  snacks_habits: z.string().optional(),
  beverages_habits: z.string().optional(),
  meal_timings: z.enum(['regular', 'irregular']),
  food_preference: z.enum(['vegetarian', 'vegan', 'non_vegetarian', 'eggetarian']),
  cultural_restrictions: z.string().optional(),
  eating_out_frequency: z.enum(['rare', 'weekly', '2-3_times_week', 'daily']),
  daily_water_intake: z.enum(['<1L', '1-2L', '2-3L', '>3L']),
  common_cravings: z.array(z.string()).default([]),
  
  // Goals & Expectations
  primary_goals: z.array(z.string()).min(1).default([]),
  specific_health_concerns: z.string().optional(),
  past_diets: z.string().optional(),
  progress_pace: z.enum(['gradual', 'moderate', 'aggressive']),
  
  // Measurements & Tracking
  current_weight_kg: z.number().min(20).max(500).optional(),
  waist_circumference_cm: z.number().min(30).max(200).optional(),
  bmi: z.number().min(10).max(100).optional(),
  weight_trend: z.enum(['increased', 'decreased', 'stable']),
  blood_reports: z.array(z.string()).default([]),
  
  // Personalization & Motivation
  loved_foods: z.string().optional(),
  disliked_foods: z.string().optional(),
  cooking_facilities: z.array(z.string()).default([]),
  who_cooks: z.enum(['self', 'family_member', 'cook_helper']),
  budget_flexibility: z.enum(['limited', 'flexible', 'high']),
  motivation_level: z.number().min(1).max(10),
  support_system: z.enum(['strong', 'moderate', 'weak']),
});

type OnboardingFormData = z.infer<typeof onboardingSchema>;

const Onboarding: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const { user, token, setToken, refreshToken } = useAuthStore();
  const { setOnboardingCompleted } = useAuthStore();

  // Ensure token is loaded from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken && !token) {
      console.log('🔑 Restoring token from localStorage');
      setToken(storedToken);
    }
  }, [token, setToken]);

  // Check if user is authenticated
  useEffect(() => {
    if (!token && !user) {
      console.log('⚠️ No token or user found, redirecting to login');
      navigate('/login');
    }
  }, [token, user, navigate]);

  // Auto-refresh token if expired
  useEffect(() => {
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const expirationTime = payload.exp * 1000;
        const currentTime = Date.now();
        const timeUntilExpiry = expirationTime - currentTime;
        
        // If token expires in less than 5 minutes, refresh it
        if (timeUntilExpiry > 0 && timeUntilExpiry < 300000) {
          console.log('🔄 Token expires soon, refreshing...');
          // You can implement token refresh logic here
          // For now, we'll redirect to login to get a fresh token
          setTimeout(() => {
            if (timeUntilExpiry <= 0) {
              console.log('⏰ Token expired, redirecting to login');
              navigate('/login');
            }
          }, timeUntilExpiry);
        }
      } catch (error) {
        console.error('❌ Failed to decode token for refresh check:', error);
      }
    }
  }, [token, navigate]);

  const {
    control,
    handleSubmit,
    formState: { errors, isValid },
    watch,
    setValue,
    trigger,
  } = useForm<OnboardingFormData>({
    resolver: zodResolver(onboardingSchema),
    mode: 'onChange',
  });

  // Debug form state
  console.log('🔍 Form Debug:', {
    currentStep,
    isValid,
    errors: Object.keys(errors),
    formData: watch()
  });

  // Debug token
  console.log('🔑 Token Debug:', {
    token: token ? `${token.substring(0, 20)}...` : 'No token',
    tokenLength: token?.length || 0,
    user: user?.email || 'No user'
  });

  // Check token expiration
  useEffect(() => {
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const expirationTime = payload.exp * 1000; // Convert to milliseconds
        const currentTime = Date.now();
        const timeUntilExpiry = expirationTime - currentTime;
        
        console.log('⏰ Token Expiration Debug:', {
          issuedAt: new Date(payload.iat * 1000).toLocaleString(),
          expiresAt: new Date(expirationTime).toLocaleString(),
          currentTime: new Date(currentTime).toLocaleString(),
          timeUntilExpiry: Math.round(timeUntilExpiry / 1000) + ' seconds',
          isExpired: timeUntilExpiry <= 0
        });
        
        if (timeUntilExpiry <= 0) {
          console.log('⚠️ Token has expired!');
        } else if (timeUntilExpiry < 60000) { // Less than 1 minute
          console.log('⚠️ Token expires soon!');
        }
      } catch (error) {
        console.error('❌ Failed to decode token:', error);
      }
    }
  }, [token]);

  // Set default values for form fields
  useEffect(() => {
    setValue('full_name', user?.full_name || '');
    // Set default values for required fields
    setValue('age', 25);
    setValue('gender', 'male');
    setValue('height_cm', 170);
    setValue('weight_kg', 70);
    setValue('daily_routine', 'moderately_active');
    setValue('sleep_hours', '7-8');
    setValue('stress_level', 'moderate');
    setValue('meal_timings', 'regular');
    setValue('food_preference', 'vegetarian');
    setValue('eating_out_frequency', 'weekly');
    setValue('daily_water_intake', '2-3L');
    setValue('progress_pace', 'moderate');
    setValue('weight_trend', 'stable');
    setValue('who_cooks', 'self');
    setValue('budget_flexibility', 'flexible');
    setValue('motivation_level', 7);
    setValue('support_system', 'moderate');
  }, [setValue, user]);

  // Step validation functions
  const validateCurrentStep = (): boolean => {
    try {
      const currentData = watch();
      const currentSchema = stepSchemas[currentStep as keyof typeof stepSchemas];
      
      if (!currentSchema) return false;
      
      // Extract only the fields for the current step
      const stepFields = Object.keys(currentSchema.shape);
      const stepData: Record<string, any> = {};
      
      stepFields.forEach(field => {
        if (currentData[field as keyof typeof currentData] !== undefined) {
          stepData[field] = currentData[field as keyof typeof currentData];
        }
      });
      
      // Debug logging for step 5
      if (currentStep === 4) {
        console.log('🔍 Step 5 Debug:', {
          stepFields,
          stepData,
          currentData: {
            primary_goals: currentData.primary_goals,
            progress_pace: currentData.progress_pace,
            specific_health_concerns: currentData.specific_health_concerns,
            past_diets: currentData.past_diets
          }
        });
      }
      
      currentSchema.parse(stepData);
      return true;
    } catch (error) {
      console.log(`❌ Step ${currentStep} validation failed:`, error);
      return false;
    }
  };

  const isCurrentStepValid = validateCurrentStep();

  const steps = [
    { title: 'Basic Information', icon: User, color: 'bg-blue-500' },
    { title: 'Medical History', icon: Heart, color: 'bg-red-500' },
    { title: 'Lifestyle Habits', icon: Activity, color: 'bg-green-500' },
    { title: 'Eating Habits', icon: Utensils, color: 'bg-yellow-500' },
    { title: 'Goals & Expectations', icon: Target, color: 'bg-purple-500' },
    { title: 'Measurements', icon: Ruler, color: 'bg-indigo-500' },
    { title: 'Personalization', icon: Star, color: 'bg-pink-500' },
  ];

  const nextStep = async () => {
    if (currentStep < steps.length - 1) {
      // Trigger validation for current step fields
      const currentSchema = stepSchemas[currentStep as keyof typeof stepSchemas];
      if (currentSchema) {
        const stepFields = Object.keys(currentSchema.shape);
        const isValid = await trigger(stepFields as any);
        
        if (isValid) {
          setCurrentStep(currentStep + 1);
        } else {
          console.log(`⚠️ Please complete step ${currentStep + 1} before proceeding`);
        }
      }
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const onSubmit = async (data: OnboardingFormData) => {
    setIsSubmitting(true);
    
    // Validate token before submission
    if (!token) {
      alert('Authentication token not found. Please log in again.');
      setIsSubmitting(false);
      return;
    }

    // Validate token format (should have 3 parts separated by dots)
    if (!token.includes('.') || token.split('.').length !== 3) {
      alert('Invalid authentication token. Please log in again.');
      setIsSubmitting(false);
      return;
    }

    // Check if token is expired and try to refresh it
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expirationTime = payload.exp * 1000;
      const currentTime = Date.now();
      
      if (expirationTime <= currentTime) {
        console.log('🔄 Token expired, attempting to refresh...');
        const refreshSuccess = await refreshToken();
        if (!refreshSuccess) {
          alert('Your session has expired. Please log in again.');
          navigate('/login');
          setIsSubmitting(false);
          return;
        }
        console.log('✅ Token refreshed successfully');
      }
    } catch (error) {
      console.error('❌ Failed to check token expiration:', error);
    }

    try {
      // Transform data for backend
      const onboardingData = {
        basic_info: {
          full_name: data.full_name,
          age: data.age,
          gender: data.gender,
          height_cm: data.height_cm,
          weight_kg: data.weight_kg,
          contact_number: data.contact_number,
          emergency_contact_name: data.emergency_contact_name,
          emergency_contact_number: data.emergency_contact_number,
          occupation: data.occupation,
          occupation_other: data.occupation_other,
        },
        medical_history: {
          medical_conditions: data.medical_conditions,
          medications_supplements: data.medications_supplements,
          surgeries_hospitalizations: data.surgeries_hospitalizations,
          food_allergies: data.food_allergies,
          family_history: data.family_history,
        },
        lifestyle_habits: {
          daily_routine: data.daily_routine,
          sleep_hours: data.sleep_hours,
          alcohol_consumption: data.alcohol_consumption,
          alcohol_frequency: data.alcohol_frequency,
          smoking: data.smoking,
          stress_level: data.stress_level,
          physical_activity_type: data.physical_activity_type,
          physical_activity_frequency: data.physical_activity_frequency,
          physical_activity_duration: data.physical_activity_duration,
        },
        eating_habits: {
          breakfast_habits: data.breakfast_habits,
          lunch_habits: data.lunch_habits,
          dinner_habits: data.dinner_habits,
          snacks_habits: data.snacks_habits,
          beverages_habits: data.beverages_habits,
          meal_timings: data.meal_timings,
          food_preference: data.food_preference,
          cultural_restrictions: data.cultural_restrictions,
          eating_out_frequency: data.eating_out_frequency,
          daily_water_intake: data.daily_water_intake,
          common_cravings: data.common_cravings,
        },
        goals_expectations: {
          primary_goals: data.primary_goals,
          specific_health_concerns: data.specific_health_concerns,
          past_diets: data.past_diets,
          progress_pace: data.progress_pace,
        },
        measurements_tracking: {
          current_weight_kg: data.current_weight_kg,
          waist_circumference_cm: data.waist_circumference_cm,
          bmi: data.bmi,
          weight_trend: data.weight_trend,
          blood_reports: data.blood_reports,
        },
        personalization_motivation: {
          loved_foods: data.loved_foods,
          disliked_foods: data.disliked_foods,
          cooking_facilities: data.cooking_facilities,
          who_cooks: data.who_cooks,
          budget_flexibility: data.budget_flexibility,
          motivation_level: data.motivation_level,
          support_system: data.support_system,
        },
      };

      const response = await fetch('/api/v1/onboarding/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(onboardingData),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Onboarding successful:', result);
        // Redirect to dashboard after successful onboarding
        navigate('/dashboard');
        setOnboardingCompleted(true); // Update onboarding status in auth store
              } else {
          const errorData = await response.json().catch(() => ({}));
          console.error('❌ Onboarding failed:', response.status, errorData);
          
          // Check if it's a token expiration error
          if (errorData.detail && errorData.detail.includes('Signature has expired')) {
            console.log('⏰ Token expired, redirecting to login');
            navigate('/login');
            throw new Error('Your session has expired. Please log in again to continue.');
          } else {
            throw new Error(`Failed to submit onboarding data: ${response.status} - ${errorData.detail || 'Unknown error'}`);
          }
        }
    } catch (error) {
      console.error('Onboarding submission failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to submit onboarding data. Please try again.';
      alert(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return <BasicInformationStep control={control} errors={errors} />;
      case 1:
        return <MedicalHistoryStep control={control} errors={errors} />;
      case 2:
        return <LifestyleHabitsStep control={control} errors={errors} />;
      case 3:
        return <EatingHabitsStep control={control} errors={errors} />;
      case 4:
        return <GoalsExpectationsStep control={control} errors={errors} />;
      case 5:
        return <MeasurementsTrackingStep control={control} errors={errors} />;
      case 6:
        return <PersonalizationMotivationStep control={control} errors={errors} />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Shield className="w-8 h-8 text-blue-600 mr-3" />
            <Lock className="w-6 h-6 text-green-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Complete Your Profile
          </h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Your information is encrypted and protected. This data helps us create personalized 
            diet plans and recommendations just for you.
          </p>
          <div className="mt-2 text-sm text-gray-500">
            Step {currentStep + 1} of {steps.length} • {Math.round(((currentStep + 1) / steps.length) * 100)}% Complete
          </div>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-between mb-8">
          {steps.map((step, index) => {
            const Icon = step.icon;
            const isActive = index === currentStep;
            const isCompleted = index < currentStep;
            const isStepValid = index <= currentStep ? 
              (index === currentStep ? isCurrentStepValid : true) : false;
            
            return (
              <div key={index} className="flex items-center">
                <div className={`flex items-center justify-center w-12 h-12 rounded-full ${
                  isActive ? (isStepValid ? step.color : 'bg-red-500') : 
                  isCompleted ? 'bg-green-500' : 'bg-gray-300'
                } text-white font-semibold transition-all duration-300 relative`}>
                  {isCompleted ? (
                    <span className="text-lg">✓</span>
                  ) : (
                    <Icon className="w-6 h-6" />
                  )}
                  {/* Validation indicator */}
                  {isActive && !isStepValid && (
                    <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center">
                      <span className="text-xs">!</span>
                    </div>
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-16 h-1 mx-2 ${
                    isCompleted ? 'bg-green-500' : 'bg-gray-300'
                  } transition-all duration-300`} />
                )}
              </div>
            );
          })}
        </div>

        {/* Form */}
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
          className="bg-white rounded-2xl shadow-xl p-8"
        >
          <form onSubmit={handleSubmit(onSubmit)}>
            {renderStepContent()}
            
            {/* Validation Status */}
            {!isCurrentStepValid && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center">
                  <div className="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center mr-3">
                    <span className="text-white text-xs">!</span>
                  </div>
                  <div>
                    <h4 className="text-red-800 font-medium">Step {currentStep + 1} Incomplete</h4>
                    <p className="text-red-600 text-sm">
                      Please complete all required fields in this step before proceeding to the next step.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
              {/* Debug Info */}
              <div className="text-xs text-gray-500 mb-2">
                Step {currentStep + 1}: {steps[currentStep]?.title} | 
                Step Valid: {isCurrentStepValid ? '✅' : '❌'} | 
                Form Valid: {isValid ? '✅' : '❌'}
              </div>
              <button
                type="button"
                onClick={prevStep}
                disabled={currentStep === 0}
                className={`flex items-center px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
                  currentStep === 0
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                <ChevronLeft className="w-5 h-5 mr-2" />
                Previous
              </button>
              
              {currentStep < steps.length - 1 ? (
                <button
                  type="button"
                  onClick={nextStep}
                  disabled={!isCurrentStepValid}
                  className={`flex items-center px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
                    !isCurrentStepValid
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  Next
                  <ChevronRight className="w-5 h-5 ml-2" />
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={!isValid || isSubmitting}
                  className={`flex items-center px-8 py-3 rounded-lg font-medium transition-all duration-200 ${
                    !isValid || isSubmitting
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-green-600 text-white hover:bg-green-700'
                  }`}
                >
                  {isSubmitting ? 'Submitting...' : 'Complete Profile'}
                </button>
              )}
            </div>
          </form>
        </motion.div>
      </div>
    </div>
  );
};

// Step Components
const BasicInformationStep: React.FC<{
  control: any;
  errors: any;
}> = ({ control, errors }) => (
  <div>
    <h2 className="text-2xl font-bold text-gray-900 mb-6">Basic Information</h2>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Full Name *
        </label>
        <Controller
          name="full_name"
          control={control}
          render={({ field }) => (
            <input
              {...field}
              type="text"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your full name"
            />
          )}
        />
        {errors.full_name && (
          <p className="text-red-500 text-sm mt-1">{errors.full_name.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Age *
        </label>
        <Controller
          name="age"
          control={control}
          render={({ field }) => (
            <input
              {...field}
              type="number"
              onChange={(e) => field.onChange(parseInt(e.target.value))}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="25"
              min="1"
              max="150"
            />
          )}
        />
        {errors.age && (
          <p className="text-red-500 text-sm mt-1">{errors.age.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Gender *
        </label>
        <Controller
          name="gender"
          control={control}
          render={({ field }) => (
            <select
              {...field}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          )}
        />
        {errors.gender && (
          <p className="text-red-500 text-sm mt-1">{errors.gender.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Height (cm) *
        </label>
        <Controller
          name="height_cm"
          control={control}
          render={({ field }) => (
            <input
              {...field}
              type="number"
              onChange={(e) => field.onChange(parseFloat(e.target.value))}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="170"
              min="50"
              max="300"
              step="0.1"
            />
          )}
        />
        {errors.height_cm && (
          <p className="text-red-500 text-sm mt-1">{errors.height_cm.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Weight (kg) *
        </label>
        <Controller
          name="weight_kg"
          control={control}
          render={({ field }) => (
            <input
              {...field}
              type="number"
              onChange={(e) => field.onChange(parseFloat(e.target.value))}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="70"
              min="20"
              max="500"
              step="0.1"
            />
          )}
        />
        {errors.weight_kg && (
          <p className="text-red-500 text-sm mt-1">{errors.weight_kg.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Contact Number
        </label>
        <Controller
          name="contact_number"
          control={control}
          render={({ field }) => (
            <input
              {...field}
              type="tel"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="+1234567890"
            />
          )}
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Occupation *
        </label>
        <Controller
          name="occupation"
          control={control}
          render={({ field }) => (
            <select
              {...field}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select occupation</option>
              <option value="student">Student</option>
              <option value="professional">Professional</option>
              <option value="homemaker">Homemaker</option>
              <option value="retired">Retired</option>
              <option value="other">Other</option>
            </select>
          )}
        />
        {errors.occupation && (
          <p className="text-red-500 text-sm mt-1">{errors.occupation.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Occupation (if Other)
        </label>
        <Controller
          name="occupation_other"
          control={control}
          render={({ field }) => (
            <input
              {...field}
              type="text"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Please specify your occupation"
            />
          )}
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Emergency Contact Name
        </label>
        <Controller
          name="emergency_contact_name"
          control={control}
          render={({ field }) => (
            <input
              {...field}
              type="text"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Emergency contact person's name"
            />
          )}
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Emergency Contact Number
        </label>
        <Controller
          name="emergency_contact_number"
          control={control}
          render={({ field }) => (
            <input
              {...field}
              type="tel"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Emergency contact phone number"
            />
          )}
        />
      </div>
    </div>
  </div>
);

// Add other step components here (MedicalHistoryStep, LifestyleHabitsStep, etc.)
// For brevity, I'll show one more step component:

const MedicalHistoryStep: React.FC<{
  control: any;
  errors: any;
}> = ({ control, errors }) => (
  <div>
    <h2 className="text-2xl font-bold text-gray-900 mb-6">Medical & Health History</h2>
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Do you have any diagnosed medical conditions?
        </label>
        <p className="text-sm text-gray-500 mb-3">
          Select all that apply, or choose "No medical conditions" if none apply to you.
        </p>
        <Controller
          name="medical_conditions"
          control={control}
          render={({ field }) => (
            <div className="space-y-3">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {['Diabetes', 'Hypertension', 'Thyroid', 'PCOS', 'Fatty Liver', 'Other'].map((condition) => (
                  <label key={condition} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={field.value?.includes(condition) || false}
                                           onChange={(e) => {
                       if (e.target.checked) {
                         // Add condition to array, but remove 'None' if it exists
                         const currentValue = field.value || [];
                         const withoutNone = currentValue.filter((c: string) => c !== 'None');
                         const newValue = [...withoutNone, condition];
                         field.onChange(newValue);
                       } else {
                         // Remove condition from array
                         const newValue = field.value?.filter((c: string) => c !== condition) || [];
                         field.onChange(newValue);
                       }
                     }}
                      className="mr-2"
                    />
                    {condition}
                  </label>
                ))}
              </div>
              {/* No medical conditions option */}
              <div className="mt-3 p-3 bg-gray-50 border border-gray-200 rounded-lg">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={field.value?.length === 0 || field.value?.includes('None') || false}
                    onChange={(e) => {
                      if (e.target.checked) {
                        // Clear all other selections and set to empty array
                        field.onChange([]);
                      } else {
                        // If unchecking "No", allow other selections
                        field.onChange([]);
                      }
                    }}
                    className="mr-2"
                  />
                  <span className="text-gray-700 font-medium">✓ No medical conditions</span>
                </label>
              </div>
              {/* Other medical condition input */}
              {field.value?.includes('Other') && (
                <div className="mt-3">
                  <input
                    type="text"
                    placeholder="Please specify other medical condition..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onChange={(e) => {
                      // Handle other medical condition input
                      const otherValue = e.target.value;
                      const currentValue = field.value || [];
                      const withoutOther = currentValue.filter((c: string) => c !== 'Other');
                      if (otherValue.trim()) {
                        field.onChange([...withoutOther, 'Other', otherValue]);
                      } else {
                        field.onChange(withoutOther);
                      }
                    }}
                  />
                </div>
              )}
            </div>
          )}
        />
        {errors.medical_conditions && (
          <p className="text-red-500 text-sm mt-1">{errors.medical_conditions.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Are you currently taking any medications or supplements?
        </label>
        <Controller
          name="medications_supplements"
          control={control}
          render={({ field }) => (
            <div className="space-y-3">
              <div className="flex items-center mb-3">
                <input
                  type="checkbox"
                  checked={field.value?.length > 0 && !field.value?.includes('None')}
                  onChange={(e) => {
                    if (!e.target.checked) {
                      field.onChange(['None']);
                    } else {
                      field.onChange([]);
                    }
                  }}
                  className="mr-2"
                />
                <span className="text-gray-600">Yes, I take medications/supplements</span>
              </div>
              {field.value?.length > 0 && !field.value?.includes('None') && (
                <textarea
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="List any medications or supplements you're currently taking..."
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value.trim()) {
                      field.onChange([value]);
                    } else {
                      field.onChange([]);
                    }
                  }}
                />
              )}
            </div>
          )}
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Any recent surgeries, hospitalizations, or chronic illnesses?
        </label>
        <Controller
          name="surgeries_hospitalizations"
          control={control}
          render={({ field }) => (
            <textarea
              {...field}
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Please provide details if any..."
            />
          )}
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Do you have any food allergies or intolerances?
        </label>
        <Controller
          name="food_allergies"
          control={control}
          render={({ field }) => (
            <div className="space-y-3">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {['Lactose', 'Gluten', 'Nuts', 'Seafood', 'Other'].map((allergy) => (
                  <label key={allergy} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={field.value?.includes(allergy) || false}
                      onChange={(e) => {
                        if (e.target.checked) {
                          const newValue = [...(field.value || []), allergy];
                          field.onChange(newValue);
                        } else {
                          const newValue = field.value?.filter((a: string) => a !== allergy) || [];
                          field.onChange(newValue);
                        }
                      }}
                      className="mr-2"
                    />
                    {allergy}
                  </label>
                ))}
              </div>
              {/* No allergies option */}
              <div className="mt-3 p-3 bg-gray-50 border border-gray-200 rounded-lg">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={field.value?.length === 0 || field.value?.includes('None') || false}
                    onChange={(e) => {
                      if (e.target.checked) {
                        field.onChange([]);
                      }
                    }}
                    className="mr-2"
                  />
                  <span className="text-gray-700 font-medium">✓ No food allergies or intolerances</span>
                </label>
              </div>
              {/* Other allergy input */}
              {field.value?.includes('Other') && (
                <div className="mt-3">
                  <input
                    type="text"
                    placeholder="Please specify other allergy/intolerance..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onChange={(e) => {
                      const otherValue = e.target.value;
                      const currentValue = field.value || [];
                      const withoutOther = currentValue.filter((a: string) => a !== 'Other');
                      if (otherValue.trim()) {
                        field.onChange([...withoutOther, 'Other', otherValue]);
                      } else {
                        field.onChange(withoutOther);
                      }
                    }}
                  />
                </div>
              )}
            </div>
          )}
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Family history of lifestyle diseases?
        </label>
        <Controller
          name="family_history"
          control={control}
          render={({ field }) => (
            <div className="space-y-3">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {['Diabetes', 'Heart Disease', 'Obesity', 'Hypertension', 'Other'].map((disease) => (
                  <label key={disease} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={field.value?.includes(disease) || false}
                      onChange={(e) => {
                        if (e.target.checked) {
                          const newValue = [...(field.value || []), disease];
                          field.onChange(newValue);
                        } else {
                          const newValue = field.value?.filter((d: string) => d !== disease) || [];
                          field.onChange(newValue);
                        }
                      }}
                      className="mr-2"
                    />
                    {disease}
                  </label>
                ))}
              </div>
              {/* No family history option */}
              <div className="mt-3 p-3 bg-gray-50 border border-gray-200 rounded-lg">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={field.value?.length === 0 || field.value?.includes('None') || false}
                    onChange={(e) => {
                      if (e.target.checked) {
                        field.onChange([]);
                      }
                    }}
                    className="mr-2"
                  />
                  <span className="text-gray-700 font-medium">✓ No family history of lifestyle diseases</span>
                </label>
              </div>
              {/* Other disease input */}
              {field.value?.includes('Other') && (
                <div className="mt-3">
                  <input
                    type="text"
                    placeholder="Please specify other disease..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onChange={(e) => {
                      const otherValue = e.target.value;
                      const currentValue = field.value || [];
                      const withoutOther = currentValue.filter((d: string) => d !== 'Other');
                      if (otherValue.trim()) {
                        field.onChange([...withoutOther, 'Other', otherValue]);
                      } else {
                        field.onChange(withoutOther);
                      }
                    }}
                  />
                </div>
              )}
            </div>
          )}
        />
      </div>
    </div>
  </div>
);

// Add the remaining step components following the same pattern...

const LifestyleHabitsStep: React.FC<{
  control: any;
  errors: any;
}> = ({ control, errors }) => (
  <div>
    <h2 className="text-2xl font-bold text-gray-900 mb-6">Lifestyle & Daily Habits</h2>
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          How would you describe your daily routine? *
        </label>
        <Controller
          name="daily_routine"
          control={control}
          render={({ field }) => (
            <select
              {...field}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select your activity level</option>
              <option value="sedentary">Sedentary (mostly sitting)</option>
              <option value="moderately_active">Moderately Active (some movement)</option>
              <option value="highly_active">Highly Active (very active lifestyle)</option>
            </select>
          )}
        />
        {errors.daily_routine && (
          <p className="text-red-500 text-sm mt-1">{errors.daily_routine.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Average hours of sleep per night *
        </label>
        <Controller
          name="sleep_hours"
          control={control}
          render={({ field }) => (
            <select
              {...field}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select sleep duration</option>
              <option value="<5">Less than 5 hours</option>
              <option value="5-6">5-6 hours</option>
              <option value="7-8">7-8 hours</option>
              <option value=">8">More than 8 hours</option>
            </select>
          )}
        />
        {errors.sleep_hours && (
          <p className="text-red-500 text-sm mt-1">{errors.sleep_hours.message}</p>
        )}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="flex items-center mb-3">
            <Controller
              name="alcohol_consumption"
              control={control}
              render={({ field }) => (
                <input
                  type="checkbox"
                  checked={field.value}
                  onChange={field.onChange}
                  className="mr-2"
                />
              )}
            />
            <span className="text-sm font-medium text-gray-700">Do you consume alcohol?</span>
          </label>
          <Controller
            name="alcohol_frequency"
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="text"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="How often? (e.g., weekly, monthly)"
              />
            )}
          />
        </div>
        
        <div>
          <label className="flex items-center mb-3">
            <Controller
              name="smoking"
              control={control}
              render={({ field }) => (
                <input
                  type="checkbox"
                  checked={field.value}
                  onChange={field.onChange}
                  className="mr-2"
                />
              )}
            />
            <span className="text-sm font-medium text-gray-700">Do you smoke?</span>
          </label>
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Stress levels *
        </label>
        <Controller
          name="stress_level"
          control={control}
          render={({ field }) => (
            <select
              {...field}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select stress level</option>
              <option value="low">Low</option>
              <option value="moderate">Moderate</option>
              <option value="high">High</option>
            </select>
          )}
        />
        {errors.stress_level && (
          <p className="text-red-500 text-sm mt-1">{errors.stress_level.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Physical Activity Type
        </label>
        <Controller
          name="physical_activity_type"
          control={control}
          render={({ field }) => (
            <input
              {...field}
              type="text"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., walking, gym, yoga, sports, etc."
            />
          )}
        />
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Physical Activity Frequency
          </label>
          <Controller
            name="physical_activity_frequency"
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="text"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., daily, 3 times/week, etc."
              />
            )}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Physical Activity Duration
          </label>
          <Controller
            name="physical_activity_duration"
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="text"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., 30 minutes, 1 hour, etc."
              />
            )}
          />
        </div>
      </div>
    </div>
  </div>
);

const EatingHabitsStep: React.FC<{
  control: any;
  errors: any;
}> = ({ control, errors }) => (
  <div>
    <h2 className="text-2xl font-bold text-gray-900 mb-6">Eating Habits & Preferences</h2>
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Food preference *
        </label>
        <Controller
          name="food_preference"
          control={control}
          render={({ field }) => (
            <select
              {...field}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select food preference</option>
              <option value="vegetarian">Vegetarian</option>
              <option value="vegan">Vegan</option>
              <option value="non_vegetarian">Non-Vegetarian</option>
              <option value="eggetarian">Eggetarian</option>
            </select>
          )}
        />
        {errors.food_preference && (
          <p className="text-red-500 text-sm mt-1">{errors.food_preference.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Meal timings *
        </label>
        <Controller
          name="meal_timings"
          control={control}
          render={({ field }) => (
            <select
              {...field}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select meal timing pattern</option>
              <option value="regular">Regular (consistent meal times)</option>
              <option value="irregular">Irregular (varying meal times)</option>
            </select>
          )}
        />
        {errors.meal_timings && (
          <p className="text-red-500 text-sm mt-1">{errors.meal_timings.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Daily water intake *
        </label>
        <Controller
          name="daily_water_intake"
          control={control}
          render={({ field }) => (
            <select
              {...field}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select water intake</option>
              <option value="<1L">Less than 1L</option>
              <option value="1-2L">1-2L</option>
              <option value="2-3L">2-3L</option>
              <option value=">3L">More than 3L</option>
            </select>
          )}
        />
        {errors.daily_water_intake && (
          <p className="text-red-500 text-sm mt-1">{errors.daily_water_intake.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Common Cravings
        </label>
        <Controller
          name="common_cravings"
          control={control}
          render={({ field }) => (
            <div className="space-y-3">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {['Sweet', 'Salty', 'Fried', 'Spicy', 'Crunchy', 'Other'].map((craving) => (
                  <label key={craving} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={field.value?.includes(craving) || false}
                      onChange={(e) => {
                        if (e.target.checked) {
                          const newValue = [...(field.value || []), craving];
                          field.onChange(newValue);
                        } else {
                          const newValue = field.value?.filter((c: string) => c !== craving) || [];
                          field.onChange(newValue);
                        }
                      }}
                      className="mr-2"
                    />
                    {craving}
                  </label>
                ))}
              </div>
              {/* Other craving input */}
              {field.value?.includes('Other') && (
                <div className="mt-3">
                  <input
                    type="text"
                    placeholder="Please specify other craving..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onChange={(e) => {
                      const otherValue = e.target.value;
                      const currentValue = field.value || [];
                      const withoutOther = currentValue.filter((c: string) => c !== 'Other');
                      if (otherValue.trim()) {
                        field.onChange([...withoutOther, 'Other', otherValue]);
                      } else {
                        field.onChange(withoutOther);
                      }
                    }}
                  />
                </div>
              )}
            </div>
          )}
        />
      </div>
    </div>
  </div>
);

const GoalsExpectationsStep: React.FC<{
  control: any;
  errors: any;
}> = ({ control, errors }) => (
  <div>
    <h2 className="text-2xl font-bold text-gray-900 mb-6">Goals & Expectations</h2>
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          What are your primary goals?
        </label>
        <p className="text-sm text-gray-500 mb-3">
          Select all that apply, or choose "No specific goals at this time" if you don't have specific goals yet.
        </p>
        <Controller
          name="primary_goals"
          control={control}
          render={({ field }) => (
            <div className="space-y-3">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {['Weight Loss', 'Weight Gain', 'Muscle Gain', 'Manage Diabetes', 'Improve Energy', 'Improve Digestion', 'Other'].map((goal) => (
                  <label key={goal} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={field.value?.includes(goal) || false}
                      onChange={(e) => {
                        if (e.target.checked) {
                          // Add goal to array
                          const newValue = [...(field.value || []), goal];
                          field.onChange(newValue);
                        } else {
                          // Remove goal from array
                          const newValue = field.value?.filter((g: string) => g !== goal) || [];
                          field.onChange(newValue);
                        }
                      }}
                      className="mr-2"
                    />
                    {goal}
                  </label>
                ))}
              </div>
              {/* Other goal input */}
              {field.value?.includes('Other') && (
                <div className="mt-3">
                  <input
                    type="text"
                    placeholder="Please specify other goal..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onChange={(e) => {
                      const otherValue = e.target.value;
                      const currentValue = field.value || [];
                      const withoutOther = currentValue.filter((g: string) => g !== 'Other');
                      if (otherValue.trim()) {
                        field.onChange([...withoutOther, 'Other', otherValue]);
                      } else {
                        field.onChange(withoutOther);
                      }
                    }}
                  />
                </div>
              )}
              {/* No goals option */}
              <div className="mt-3 p-3 bg-gray-50 border border-gray-200 rounded-lg">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={field.value?.length === 0 || field.value?.includes('None') || false}
                    onChange={(e) => {
                      if (e.target.checked) {
                        // Set to empty array to indicate no goals
                        field.onChange([]);
                      }
                    }}
                    className="mr-2"
                  />
                  <span className="text-gray-700 font-medium">✓ No specific goals at this time</span>
                </label>
              </div>
            </div>
          )}
        />
        {errors.primary_goals && (
          <p className="text-red-500 text-sm mt-1">{errors.primary_goals.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Any specific health concerns? *
        </label>
        <Controller
          name="specific_health_concerns"
          control={control}
          render={({ field }) => (
            <textarea
              {...field}
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., bloating, acidity, fatigue, poor sleep, etc."
            />
          )}
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Have you tried any diets in the past?
        </label>
        <Controller
          name="past_diets"
          control={control}
          render={({ field }) => (
            <textarea
              {...field}
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Please specify any diets you've tried before..."
            />
          )}
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Progress pace <span className="text-red-500">*</span>
        </label>
        <p className="text-sm text-gray-500 mb-3">
          This helps us tailor your plan to your preferred timeline.
        </p>
        <Controller
          name="progress_pace"
          control={control}
          render={({ field }) => (
            <select
              {...field}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select progress pace</option>
              <option value="gradual">Gradual (slow and steady)</option>
              <option value="moderate">Moderate (balanced approach)</option>
              <option value="aggressive">Aggressive (fast results)</option>
            </select>
          )}
        />
        {errors.progress_pace && (
          <p className="text-red-500 text-sm mt-1">{errors.progress_pace.message}</p>
        )}
      </div>
    </div>
  </div>
);

const MeasurementsTrackingStep: React.FC<{
  control: any;
  errors: any;
}> = ({ control, errors }) => (
  <div>
    <h2 className="text-2xl font-bold text-gray-900 mb-6">Measurements & Tracking</h2>
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Current Weight (kg)
          </label>
          <Controller
            name="current_weight_kg"
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="number"
                onChange={(e) => field.onChange(parseFloat(e.target.value))}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="70"
                min="20"
                max="500"
                step="0.1"
              />
            )}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Waist Circumference (cm)
          </label>
          <Controller
            name="waist_circumference_cm"
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="number"
                onChange={(e) => field.onChange(parseFloat(e.target.value))}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="80"
                min="30"
                max="200"
                step="0.1"
              />
            )}
          />
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Weight trend over the past 6 months *
        </label>
        <Controller
          name="weight_trend"
          control={control}
          render={({ field }) => (
            <select
              {...field}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select weight trend</option>
              <option value="increased">Increased</option>
              <option value="decreased">Decreased</option>
              <option value="stable">Stable</option>
            </select>
          )}
        />
        {errors.weight_trend && (
          <p className="text-red-500 text-sm mt-1">{errors.weight_trend.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Blood Reports Available
        </label>
        <Controller
          name="blood_reports"
          control={control}
          render={({ field }) => (
            <div className="space-y-3">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {['Lipid Profile', 'Fasting Sugar', 'HbA1c', 'Thyroid', 'Liver Function', 'Kidney Function', 'Vitamin D', 'Vitamin B12'].map((report) => (
                  <label key={report} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={field.value?.includes(report) || false}
                      onChange={(e) => {
                        if (e.target.checked) {
                          const newValue = [...(field.value || []), report];
                          field.onChange(newValue);
                        } else {
                          const newValue = field.value?.filter((r: string) => r !== report) || [];
                          field.onChange(newValue);
                        }
                      }}
                      className="mr-2"
                    />
                    {report}
                  </label>
                ))}
              </div>
              {/* No reports option */}
              <div className="mt-3 p-3 bg-gray-50 border border-gray-200 rounded-lg">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={field.value?.length === 0 || field.value?.includes('None') || false}
                    onChange={(e) => {
                      if (e.target.checked) {
                        field.onChange([]);
                      }
                    }}
                    className="mr-2"
                  />
                  <span className="text-gray-700 font-medium">✓ No blood reports available</span>
                </label>
              </div>
            </div>
          )}
        />
      </div>
    </div>
  </div>
);

const PersonalizationMotivationStep: React.FC<{
  control: any;
  errors: any;
}> = ({ control, errors }) => (
  <div>
    <h2 className="text-2xl font-bold text-gray-900 mb-6">Personalization & Motivation</h2>
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Who cooks at home? *
        </label>
        <Controller
          name="who_cooks"
          control={control}
          render={({ field }) => (
            <select
              {...field}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select who cooks</option>
              <option value="self">Self</option>
              <option value="family_member">Family Member</option>
              <option value="cook_helper">Cook/Helper</option>
            </select>
          )}
        />
        {errors.who_cooks && (
          <p className="text-red-500 text-sm mt-1">{errors.who_cooks.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Budget flexibility for special foods/supplements *
        </label>
        <Controller
          name="budget_flexibility"
          control={control}
          render={({ field }) => (
            <select
              {...field}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select budget flexibility</option>
              <option value="limited">Limited</option>
              <option value="flexible">Flexible</option>
              <option value="high">High</option>
            </select>
          )}
        />
        {errors.budget_flexibility && (
          <p className="text-red-500 text-sm mt-1">{errors.budget_flexibility.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Motivation level to make changes (1-10) *
        </label>
        <Controller
          name="motivation_level"
          control={control}
          render={({ field }) => (
            <input
              {...field}
              type="number"
              onChange={(e) => field.onChange(parseInt(e.target.value))}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="7"
              min="1"
              max="10"
            />
          )}
        />
        {errors.motivation_level && (
          <p className="text-red-500 text-sm mt-1">{errors.motivation_level.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Support system *
        </label>
        <Controller
          name="support_system"
          control={control}
          render={({ field }) => (
            <select
              {...field}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select support level</option>
              <option value="strong">Strong (family/friends support)</option>
              <option value="moderate">Moderate</option>
              <option value="weak">Weak</option>
            </select>
          )}
        />
        {errors.support_system && (
          <p className="text-red-500 text-sm mt-1">{errors.support_system.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Cooking Facilities Available
        </label>
        <Controller
          name="cooking_facilities"
          control={control}
          render={({ field }) => (
            <div className="space-y-3">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {['Gas Stove', 'Electric Stove', 'Microwave', 'Oven', 'Air Fryer', 'Blender', 'Food Processor', 'Other'].map((facility) => (
                  <label key={facility} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={field.value?.includes(facility) || false}
                      onChange={(e) => {
                        if (e.target.checked) {
                          const newValue = [...(field.value || []), facility];
                          field.onChange(newValue);
                        } else {
                          const newValue = field.value?.filter((f: string) => f !== facility) || [];
                          field.onChange(newValue);
                        }
                      }}
                      className="mr-2"
                    />
                    {facility}
                  </label>
                ))}
              </div>
              {/* Other facility input */}
              {field.value?.includes('Other') && (
                <div className="mt-3">
                  <input
                    type="text"
                    placeholder="Please specify other cooking facility..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onChange={(e) => {
                      const otherValue = e.target.value;
                      const currentValue = field.value || [];
                      const withoutOther = currentValue.filter((f: string) => f !== 'Other');
                      if (otherValue.trim()) {
                        field.onChange([...withoutOther, 'Other', otherValue]);
                      } else {
                        field.onChange(withoutOther);
                      }
                    }}
                  />
                </div>
              )}
            </div>
          )}
        />
      </div>
    </div>
  </div>
);

export default Onboarding;

