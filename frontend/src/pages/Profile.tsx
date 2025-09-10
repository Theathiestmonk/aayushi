import React, { useState, useEffect } from 'react';
import { useAuthStore, apiRequest } from '@/stores/authStore';
import { useNavigate } from 'react-router-dom';
import { 
  User, 
  Heart, 
  Activity, 
  Utensils, 
  Target, 
  Ruler, 
  Star,
  Edit,
  Calendar,

  Mail,
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  Droplets,
  Download
} from 'lucide-react';

interface UserProfile {
  // Basic Information
  full_name: string;
  age: number;
  gender: string;
  height_cm: number;
  weight_kg: number;
  contact_number?: string;
  email: string;
  emergency_contact_name?: string;
  emergency_contact_number?: string;
  occupation: string;
  occupation_other?: string;
  
  // Medical & Health History
  medical_conditions: string[];
  medications_supplements: string[];
  surgeries_hospitalizations?: string;
  food_allergies: string[];
  family_history: string[];
  
  // Lifestyle & Habits
  daily_routine: string;
  sleep_hours: string;
  alcohol_consumption: boolean;
  alcohol_frequency?: string;
  smoking: boolean;
  stress_level: string;
  physical_activity_type?: string;
  physical_activity_frequency?: string;
  physical_activity_duration?: string;
  
  // Eating Habits
  breakfast_habits?: string;
  lunch_habits?: string;
  dinner_habits?: string;
  snacks_habits?: string;
  beverages_habits?: string;
  meal_timings: string;
  food_preference: string;
  cultural_restrictions?: string;
  eating_out_frequency: string;
  daily_water_intake: string;
  common_cravings: string[];
  
  // Goals & Expectations
  primary_goals: string[];
  specific_health_concerns?: string;
  past_diets?: string;
  progress_pace: string;
  
  // Measurements & Tracking
  current_weight_kg?: number;
  waist_circumference_cm?: number;
  bmi?: number;
  weight_trend: string;
  blood_reports: string[];
  
  // Personalization & Motivation
  loved_foods?: string;
  disliked_foods?: string;
  cooking_facilities: string[];
  who_cooks: string;
  budget_flexibility: string;
  motivation_level: number;
  support_system: string;
  
  // System fields
  onboarding_completed: boolean;
  created_at: string;
  updated_at: string;
}

const Profile: React.FC = () => {
  const { token } = useAuthStore();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showEditDialog, setShowEditDialog] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      
      // Use the exported apiRequest function
      const data = await apiRequest('/onboarding/profile', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (data.success) {
        if (data.data.profile) {
          setProfile(data.data.profile);
        } else {
          // User hasn't completed onboarding yet
          setError('Please complete your onboarding to view your profile');
        }
      } else {
        throw new Error(data.message || 'Profile data not found');
      }
    } catch (err) {
      console.error('Profile fetch error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch profile');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const capitalizeWords = (text: string) => {
    if (!text) return text;
    return text.split(' ').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    ).join(' ');
  };

  const handleEditProfile = () => {
    setShowEditDialog(true);
  };

  const confirmEditProfile = () => {
    setShowEditDialog(false);
    navigate('/onboarding');
  };

  const cancelEditProfile = () => {
    setShowEditDialog(false);
  };

  // Close modal when clicking outside or pressing escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && showEditDialog) {
        setShowEditDialog(false);
      }
    };

    const handleClickOutside = (e: MouseEvent) => {
      if (showEditDialog && e.target === e.currentTarget) {
        setShowEditDialog(false);
      }
    };

    if (showEditDialog) {
      document.addEventListener('keydown', handleEscape);
      document.addEventListener('click', handleClickOutside);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('click', handleClickOutside);
      document.body.style.overflow = 'unset';
    };
  }, [showEditDialog]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-red-800 mb-2">Error Loading Profile</h2>
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={fetchProfile}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-yellow-800 mb-2">Profile Not Found</h2>
          <p className="text-yellow-600">Please complete your onboarding to view your profile.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Your Profile</h1>
        <p className="text-gray-600 text-lg">Complete overview of your health and nutrition information</p>
        <div className="flex items-center justify-center mt-4 space-x-4 text-sm text-gray-500">
          <div className="flex items-center">
            <Calendar className="w-4 h-4 mr-2" />
            Created: {formatDate(profile.created_at)}
          </div>
          <div className="flex items-center">
            <Clock className="w-4 h-4 mr-2" />
            Updated: {formatDate(profile.updated_at)}
          </div>
        </div>
      </div>

      {/* Profile Cards Grid - 4 Columns */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">

      {/* Basic Information Card */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200">
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 rounded-t-xl">
          <h2 className="text-xl font-bold text-blue-900 flex items-center">
            <User className="w-6 h-6 mr-3" />
            Basic Information
          </h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-500">Full Name</label>
              <p className="text-lg font-semibold">{profile.full_name}</p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-500">Age & Gender</label>
              <p className="text-lg font-semibold">
                {profile.age} years • {capitalizeWords(profile.gender)}
              </p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-500">Height & Weight</label>
              <p className="text-lg font-semibold">
                {profile.height_cm} cm • {profile.weight_kg} kg
              </p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-500">Contact</label>
              <div className="flex items-center space-x-2">
                <Mail className="w-4 h-4 text-gray-400" />
                <span>{profile.email}</span>
              </div>
              {profile.contact_number && (
                <div className="flex items-center space-x-2">
                  <p className="text-sm text-gray-600">{profile.contact_number}</p>
                </div>
              )}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-500">Occupation</label>
              <p className="text-lg font-semibold">
                {capitalizeWords(profile.occupation)}
                {profile.occupation_other && profile.occupation === 'other' && (
                  <span className="text-gray-600 ml-2">({capitalizeWords(profile.occupation_other)})</span>
                )}
              </p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-500">Emergency Contact</label>
              {profile.emergency_contact_name ? (
                <div>
                  <p className="font-semibold">{profile.emergency_contact_name}</p>
                  {profile.emergency_contact_number && (
                    <p className="text-sm text-gray-600">{profile.emergency_contact_number}</p>
                  )}
                </div>
              ) : (
                <p className="text-gray-400">Not specified</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Medical History Card */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200">
        <div className="bg-gradient-to-r from-red-50 to-pink-50 px-6 py-4 rounded-t-xl">
          <h2 className="text-xl font-bold text-red-900 flex items-center">
            <Heart className="w-6 h-6 mr-3" />
            Medical & Health History
          </h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Medical Conditions</label>
              {profile.medical_conditions.length > 0 ? (
                <div className="flex flex-wrap gap-2 mt-2">
                  {profile.medical_conditions.map((condition, index) => (
                    <span key={index} className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm">
                      {condition}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400 mt-2">No medical conditions</p>
              )}
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Food Allergies</label>
              {profile.food_allergies.length > 0 ? (
                <div className="flex flex-wrap gap-2 mt-2">
                  {profile.food_allergies.map((allergy, index) => (
                    <span key={index} className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm">
                      {allergy}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400 mt-2">No food allergies</p>
              )}
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Medications & Supplements</label>
              {profile.medications_supplements.length > 0 ? (
                <div className="flex flex-wrap gap-2 mt-2">
                  {profile.medications_supplements.map((med, index) => (
                    <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                      {med}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400 mt-2">None</p>
              )}
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Family History</label>
              {profile.family_history.length > 0 ? (
                <div className="flex flex-wrap gap-2 mt-2">
                  {profile.family_history.map((condition, index) => (
                    <span key={index} className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                      {condition}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400 mt-2">None</p>
              )}
            </div>
          </div>
          {profile.surgeries_hospitalizations && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <label className="text-sm font-medium text-red-800">Recent Surgeries/Hospitalizations</label>
              <p className="text-red-700 mt-1">{profile.surgeries_hospitalizations}</p>
            </div>
          )}
        </div>
      </div>

      {/* Lifestyle & Habits Card */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200">
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 px-6 py-4 rounded-t-xl">
          <h2 className="text-xl font-bold text-green-900 flex items-center">
            <Activity className="w-6 h-6 mr-3" />
            Lifestyle & Daily Habits
          </h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-500">Daily Routine</label>
              <p className="text-lg font-semibold">{capitalizeWords(profile.daily_routine.replace('_', ' '))}</p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-500">Sleep Pattern</label>
              <p className="text-lg font-semibold">{profile.sleep_hours} hours</p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-500">Stress Level</label>
              <p className="text-lg font-semibold">{capitalizeWords(profile.stress_level)}</p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-500">Alcohol Consumption</label>
              <div className="flex items-center space-x-2">
                {profile.alcohol_consumption ? (
                  <>
                    <CheckCircle className="w-5 h-5 text-red-500" />
                    <span className="text-red-600 font-medium">Yes</span>
                    {profile.alcohol_frequency && (
                      <span className="text-sm text-gray-600">({profile.alcohol_frequency})</span>
                    )}
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span className="text-green-600 font-medium">No</span>
                  </>
                )}
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-500">Smoking</label>
              <div className="flex items-center space-x-2">
                {profile.smoking ? (
                  <>
                    <AlertTriangle className="w-5 h-5 text-red-500" />
                    <span className="text-red-600 font-medium">Yes</span>
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span className="text-green-600 font-medium">No</span>
                  </>
                )}
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-500">Physical Activity</label>
              {profile.physical_activity_type ? (
                <div>
                  <p className="font-semibold">{profile.physical_activity_type}</p>
                  <p className="text-sm text-gray-600">
                    {profile.physical_activity_frequency} • {profile.physical_activity_duration}
                  </p>
                </div>
              ) : (
                <p className="text-gray-400">Not specified</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Eating Habits Card */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200">
        <div className="bg-gradient-to-r from-orange-50 to-amber-50 px-6 py-4 rounded-t-xl">
          <h2 className="text-xl font-bold text-orange-900 flex items-center">
            <Utensils className="w-6 h-6 mr-3" />
            Eating Habits & Preferences
          </h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Food Preference</label>
              <span className="inline-block px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-lg border border-orange-300">
                {capitalizeWords(profile.food_preference.replace('_', ' '))}
              </span>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Meal Timings</label>
              <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-lg border border-blue-300">
                {capitalizeWords(profile.meal_timings)}
              </span>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Water Intake</label>
              <div className="flex items-center space-x-2 mt-2">
                <Droplets className="w-5 h-5 text-blue-500" />
                <span className="font-semibold">{profile.daily_water_intake}</span>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Eating Out Frequency</label>
              <span className="inline-block px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-lg border border-purple-300">
                {capitalizeWords(profile.eating_out_frequency.replace(/_/g, ' '))}
              </span>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Common Cravings</label>
              {profile.common_cravings.length > 0 ? (
                <div className="flex flex-wrap gap-2 mt-2">
                  {profile.common_cravings.map((craving, index) => (
                    <span key={index} className="px-3 py-1 bg-pink-100 text-pink-800 rounded-full text-sm border border-pink-300">
                      {craving}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400 mt-2">None specified</p>
              )}
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Cultural Restrictions</label>
              {profile.cultural_restrictions ? (
                <p className="text-gray-700 mt-2">{profile.cultural_restrictions}</p>
              ) : (
                <p className="text-gray-400 mt-2">None</p>
              )}
            </div>
          </div>
          
          {/* Meal Details */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {profile.breakfast_habits && (
              <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                <label className="text-sm font-medium text-orange-800">Breakfast</label>
                <p className="text-orange-700 mt-1">{profile.breakfast_habits}</p>
              </div>
            )}
            {profile.lunch_habits && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <label className="text-sm font-medium text-yellow-800">Lunch</label>
                <p className="text-yellow-700 mt-1">{profile.lunch_habits}</p>
              </div>
            )}
            {profile.dinner_habits && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <label className="text-sm font-medium text-red-800">Dinner</label>
                <p className="text-red-700 mt-1">{profile.dinner_habits}</p>
              </div>
            )}
            {profile.snacks_habits && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <label className="text-sm font-medium text-green-800">Snacks</label>
                <p className="text-green-700 mt-1">{profile.snacks_habits}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Goals & Expectations Card */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200">
        <div className="bg-gradient-to-r from-purple-50 to-violet-50 px-6 py-4 rounded-t-xl">
          <h2 className="text-xl font-bold text-purple-900 flex items-center">
            <Target className="w-6 h-6 mr-3" />
            Goals & Expectations
          </h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Primary Goals</label>
              {profile.primary_goals.length > 0 ? (
                <div className="flex flex-wrap gap-2 mt-2">
                  {profile.primary_goals.map((goal, index) => (
                    <span key={index} className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm border border-purple-300">
                      {goal}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400 mt-2">No specific goals</p>
              )}
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Progress Pace</label>
              <span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-lg border border-green-300">
                {capitalizeWords(profile.progress_pace)}
              </span>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Specific Health Concerns</label>
              {profile.specific_health_concerns ? (
                <p className="text-gray-700 mt-2">{profile.specific_health_concerns}</p>
              ) : (
                <p className="text-gray-400 mt-2">None specified</p>
              )}
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Past Diets</label>
              {profile.past_diets ? (
                <p className="text-gray-700 mt-2">{profile.past_diets}</p>
              ) : (
                <p className="text-gray-400 mt-2">None tried</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Measurements & Tracking Card */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200">
        <div className="bg-gradient-to-r from-indigo-50 to-blue-50 px-6 py-4 rounded-t-xl">
          <h2 className="text-xl font-bold text-indigo-900 flex items-center">
            <Ruler className="w-6 h-6 mr-3" />
            Measurements & Tracking
          </h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-500">Current Weight</label>
              <p className="text-2xl font-bold text-indigo-600">
                {profile.current_weight_kg || profile.weight_kg} kg
              </p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-500">Waist Circumference</label>
              <p className="text-2xl font-bold text-indigo-600">
                {profile.waist_circumference_cm || 'N/A'} cm
              </p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-500">BMI</label>
              <p className="text-2xl font-bold text-indigo-600">
                {profile.bmi || 'N/A'}
              </p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-500">Weight Trend</label>
              <span className="inline-block px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-lg border border-indigo-300">
                {capitalizeWords(profile.weight_trend)}
              </span>
            </div>
          </div>
          
          <div className="mt-6">
            <label className="text-sm font-medium text-gray-500">Blood Reports Available</label>
            {profile.blood_reports.length > 0 ? (
              <div className="flex flex-wrap gap-2 mt-2">
                {profile.blood_reports.map((report, index) => (
                  <span key={index} className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm border border-indigo-300">
                    {report}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-gray-400 mt-2">No blood reports available</p>
            )}
          </div>
        </div>
      </div>

      {/* Personalization & Motivation Card */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200">
        <div className="bg-gradient-to-r from-pink-50 to-rose-50 px-6 py-4 rounded-t-xl">
          <h2 className="text-xl font-bold text-pink-900 flex items-center">
            <Star className="w-6 h-6 mr-3" />
            Personalization & Motivation
          </h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Loved Foods</label>
              {profile.loved_foods ? (
                <p className="text-gray-700 mt-2">{profile.loved_foods}</p>
              ) : (
                <p className="text-gray-400 mt-2">Not specified</p>
              )}
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Disliked Foods</label>
              {profile.disliked_foods ? (
                <p className="text-gray-700 mt-2">{profile.disliked_foods}</p>
              ) : (
                <p className="text-gray-400 mt-2">Not specified</p>
              )}
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Cooking Facilities</label>
              {profile.cooking_facilities.length > 0 ? (
                <div className="flex flex-wrap gap-2 mt-2">
                  {profile.cooking_facilities.map((facility, index) => (
                    <span key={index} className="px-3 py-1 bg-pink-100 text-pink-800 rounded-full text-sm border border-pink-300">
                      {facility}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400 mt-2">None specified</p>
              )}
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Who Cooks</label>
              <span className="inline-block px-3 py-1 bg-pink-100 text-pink-800 rounded-full text-lg border border-pink-300">
                {capitalizeWords(profile.who_cooks.replace('_', ' '))}
              </span>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Budget Flexibility</label>
              <span className="inline-block px-3 py-1 bg-pink-100 text-pink-800 rounded-full text-lg border border-pink-300">
                {capitalizeWords(profile.budget_flexibility)}
              </span>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Motivation Level</label>
              <div className="flex items-center space-x-2 mt-2">
                <span className="text-2xl font-bold text-pink-600">
                  {profile.motivation_level}/10
                </span>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Support System</label>
              <span className="inline-block px-3 py-1 bg-pink-100 text-pink-800 rounded-full text-lg border border-pink-300">
                {capitalizeWords(profile.support_system)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Data Protection Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <div className="flex items-start space-x-3">
          <Shield className="w-6 h-6 text-blue-600 mt-1 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-blue-900 mb-2">Data Protection & Privacy</h3>
            <p className="text-blue-800 text-sm">
              Your profile information is protected with enterprise-grade security measures including 
              Row Level Security (RLS), data encryption, and comprehensive audit logging. 
              All access to your sensitive health data is logged and monitored for your privacy and security.
            </p>
          </div>
        </div>
      </div>
      </div> {/* Close the grid div */}

      {/* Action Buttons */}
      <div className="text-center">
        <p className="text-sm text-gray-600 mb-4">
          Need to update your information? Use the Edit Profile button to modify your details.
        </p>
        <div className="flex justify-center space-x-4">
          <button 
            onClick={handleEditProfile}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center transition-colors duration-200"
            title="Update your profile information through the onboarding form"
          >
            <Edit className="w-5 h-5 mr-2" />
            Edit Profile
          </button>
          <button className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center transition-colors duration-200">
            <Download className="w-5 h-5 mr-2" />
            Export Data
          </button>
        </div>
      </div>

      {/* Beautiful Edit Profile Confirmation Dialog */}
      {showEditDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-fadeIn">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full transform transition-all duration-300 scale-100 animate-slideIn">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-4 rounded-t-2xl">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                  <Edit className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Edit Profile</h3>
                  <p className="text-blue-100 text-sm">Update your information</p>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="px-6 py-6">
              <div className="flex items-start space-x-4 mb-6">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <User className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">
                    Ready to update your profile?
                  </h4>
                  <p className="text-gray-600 leading-relaxed">
                    This will take you to the onboarding form where you can modify your personal information, 
                    health details, preferences, and goals. All your current data will be preserved and updated.
                  </p>
                </div>
              </div>

              {/* Features List */}
              <div className="bg-gray-50 rounded-xl p-4 mb-6">
                <h5 className="text-sm font-medium text-gray-700 mb-3">What you can update:</h5>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-sm text-gray-600">Personal information & measurements</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm text-gray-600">Health history & preferences</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span className="text-sm text-gray-600">Goals & lifestyle habits</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="px-6 py-4 bg-gray-50 rounded-b-2xl flex space-x-3">
              <button
                onClick={cancelEditProfile}
                className="flex-1 px-4 py-3 text-gray-700 bg-white border border-gray-300 rounded-xl font-medium hover:bg-gray-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-300 focus:ring-offset-2"
              >
                Cancel
              </button>
              <button
                onClick={confirmEditProfile}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-medium hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transform hover:scale-105"
              >
                Continue to Edit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
