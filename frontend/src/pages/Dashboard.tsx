import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore, apiRequest } from '../stores/authStore';

import { 
  Search,
  Bell,
  Scale,
  Footprints,
  Moon,
  Droplets,
  MoreHorizontal,
  Flame,
  UtensilsCrossed
} from 'lucide-react';
import MetricCard from '../components/ui/MetricCard';
import ProgressChart from '../components/ui/ProgressChart';
import MealCard from '../components/ui/MealCard';
import WorkoutCard from '../components/ui/WorkoutCard';
import Calendar from '../components/ui/Calendar';

interface HealthMetrics {
  weight_kg: number;
  target_weight_kg: number;
  steps_today: number;
  steps_goal: number;
  sleep_hours: number;
  sleep_goal: number;
  water_intake_l: number;
  water_goal_l: number;
  calories_eaten: number;
  calories_burned: number;
  calories_goal: number;
  macronutrients: {
    carbs_g: number;
    carbs_goal: number;
    protein_g: number;
    protein_goal: number;
    fat_g: number;
    fat_goal: number;
  };
}

interface UserProfile {
  full_name: string;
  age: number;
  gender: string;
  height_cm: number;
  weight_kg: number;
  current_weight_kg?: number;
  bmi?: number;
  primary_goals: string[];
  // Add other fields as needed
}

interface Meal {
  id: string;
  name: string;
  type: 'breakfast' | 'lunch' | 'snack' | 'dinner';
  calories: number;
  image?: string;
  carbs_g: number;
  protein_g: number;
  fat_g: number;
  completed: boolean;
}

interface Workout {
  id: string;
  name: string;
  progress: number;
  goal: number;
  category: 'cardio' | 'strength' | 'flexibility';
  icon: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, token } = useAuthStore();
  const [healthMetrics, setHealthMetrics] = useState<HealthMetrics | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [todayMeals, setTodayMeals] = useState<Meal[]>([]);
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [loading, setLoading] = useState(true);

  const formatNumber = (value?: number | null, options?: Intl.NumberFormatOptions) => {
    if (value === null || value === undefined) return '--';
    try {
      return value.toLocaleString(undefined, options);
    } catch {
      return String(value);
    }
  };

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    fetchDashboardData();
  }, [isAuthenticated, token, navigate]);

  // Refetch on window focus to get latest within 24h window
  useEffect(() => {
    const onFocus = () => {
      if (isAuthenticated) {
        fetchDashboardData();
      }
    };
    window.addEventListener('focus', onFocus);
    return () => window.removeEventListener('focus', onFocus);
  }, [isAuthenticated, token]);



  const calculateTargetWeight = (profile: UserProfile | null): number => {
    if (!profile) return 70; // Default fallback
    
    const currentWeight = profile.current_weight_kg || profile.weight_kg;
    const goals = profile.primary_goals || [];
    
    // Calculate target weight based on goals
    if (goals.includes('weight_loss')) {
      // Target 10-15% weight loss for healthy weight loss
      return Math.round(currentWeight * 0.85);
    } else if (goals.includes('muscle_gain')) {
      // Target 5-10% weight gain for muscle building
      return Math.round(currentWeight * 1.08);
    } else {
      // Maintenance - keep current weight
      return currentWeight;
    }
  };

  const fetchUserProfile = async () => {
    try {
      if (!token) return;
      
      // Use the exported apiRequest function
      const data = await apiRequest('/onboarding/profile', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (data.success && data.data.profile) {
        setUserProfile(data.data.profile);
      }
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
    }
  };

  const updateHealthMetrics = async (updates: Partial<HealthMetrics>) => {
    try {
      if (!token) return;
      
      const response = await apiRequest('/tracking/health-metrics', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });

      if (response.success && response.data) {
        // Update local state with new data
        setHealthMetrics(prev => {
          if (!prev) return prev;
          return {
            ...prev,
            ...updates
          };
        });
        console.log('Health metrics updated successfully');
      }
    } catch (error) {
      console.error('Failed to update health metrics:', error);
    }
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch user profile first
      await fetchUserProfile();
      
      // Calculate target weight based on user profile and goals
      const currentWeight = userProfile?.current_weight_kg || userProfile?.weight_kg || 70;
      const targetWeight = calculateTargetWeight(userProfile);
      
      // Fetch real health metrics from API (no demo or zero fallbacks)
      let healthMetricsData: HealthMetrics | null = null;
      
      try {
        const response = await apiRequest('/tracking/health-metrics', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        
        if (response.success && response.data) {
          const data = response.data;
          healthMetricsData = {
            weight_kg: data.weight_kg ?? currentWeight,
            target_weight_kg: data.target_weight_kg ?? targetWeight,
            steps_today: data.steps_today,
            steps_goal: data.steps_goal,
            sleep_hours: data.sleep_hours,
            sleep_goal: data.sleep_goal,
            water_intake_l: data.water_intake_l,
            water_goal_l: data.water_goal_l,
            calories_eaten: data.calories_eaten,
            calories_burned: data.calories_burned,
            calories_goal: data.calories_goal,
            macronutrients: {
              carbs_g: data.carbs_g,
              carbs_goal: data.carbs_goal,
              protein_g: data.protein_g,
              protein_goal: data.protein_goal,
              fat_g: data.fat_g,
              fat_goal: data.fat_goal
            }
          };
        }
      } catch (error) {
        console.error('Failed to fetch health metrics:', error);
        healthMetricsData = null;
      }

      const mockMeals: Meal[] = [
        {
          id: '1',
          name: 'Scrambled Eggs with Spinach & Whole Grain Toast',
          type: 'breakfast',
          calories: 300,
          carbs_g: 25,
          protein_g: 20,
          fat_g: 12,
          completed: true
        },
        {
          id: '2',
          name: 'Grilled Chicken Salad with Avocado and Quinoa',
          type: 'lunch',
          calories: 450,
          carbs_g: 40,
          protein_g: 35,
          fat_g: 20,
          completed: false
        },
        {
          id: '3',
          name: 'Greek Yogurt with Mixed Berries and Almonds',
          type: 'snack',
          calories: 200,
          carbs_g: 18,
          protein_g: 12,
          fat_g: 10,
          completed: false
        },
        {
          id: '4',
          name: 'Grilled Chicken with Sweet Potato and Green Beans',
          type: 'dinner',
          calories: 500,
          carbs_g: 45,
          protein_g: 35,
          fat_g: 20,
          completed: false
        }
      ];

      const mockWorkouts: Workout[] = [
        {
          id: '1',
          name: 'Running 10 km',
          progress: 7,
          goal: 10,
          category: 'cardio',
          icon: '🏃'
        },
        {
          id: '2',
          name: 'Squatting 50kg',
          progress: 5,
          goal: 8,
          category: 'strength',
          icon: '🏋️'
        },
        {
          id: '3',
          name: 'Stretching to touch toes',
          progress: 3,
          goal: 6,
          category: 'flexibility',
          icon: '🧘'
        }
      ];

      setHealthMetrics(healthMetricsData);
      setTodayMeals(mockMeals);
      setWorkouts(mockWorkouts);
      
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };



  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your health dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      
      {/* Top Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Hello, {userProfile?.full_name || user?.full_name || 'User'}! 👋
                </h1>
                <p className="text-gray-600">Let's begin our journey to better health today</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
            {/* Search Bar */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search anything"
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64"
              />
            </div>
            
            {/* Notifications */}
            <button className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
              <Bell className="w-6 h-6" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
            
            {/* User Profile */}
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                {userProfile?.full_name?.charAt(0) || user?.full_name?.charAt(0) || 'U'}
              </div>
              <div className="text-right">
                <p className="font-medium text-gray-900">{userProfile?.full_name || user?.full_name || 'User'}</p>
                <p className="text-sm text-gray-500">Member</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Main Content */}
        <div className="flex-1 p-6 space-y-6">
          {/* Key Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Weight"
              value={`${userProfile?.current_weight_kg || userProfile?.weight_kg || '--'} kg`}
              icon={Scale}
              iconColor="text-orange-600"
              iconBgColor="bg-orange-100"
              progress={{
                current: userProfile?.current_weight_kg || userProfile?.weight_kg || 0,
                goal: calculateTargetWeight(userProfile),
                unit: 'kg'
              }}
            />
            
            <div className="relative">
              <MetricCard
                title="Steps"
                value={`${formatNumber(healthMetrics?.steps_today)} steps`}
                icon={Footprints}
                iconColor="text-green-600"
                iconBgColor="bg-green-100"
                progress={{
                  current: healthMetrics?.steps_today || 0,
                  goal: healthMetrics?.steps_goal || 0,
                  unit: 'steps'
                }}
              />
              <button
                onClick={() => updateHealthMetrics({ 
                  steps_today: (healthMetrics?.steps_today || 0) + 1000 
                })}
                className="absolute top-2 right-2 bg-green-500 hover:bg-green-600 text-white text-xs px-2 py-1 rounded-full transition-colors"
                title="Add 1000 steps"
              >
                +1K
              </button>
            </div>
            
            <div className="relative">
              <MetricCard
                title="Sleep"
                value={`${formatNumber(healthMetrics?.sleep_hours)} hours`}
                icon={Moon}
                iconColor="text-purple-600"
                iconBgColor="bg-purple-100"
                progress={{
                  current: healthMetrics?.sleep_hours || 0,
                  goal: healthMetrics?.sleep_goal || 0,
                  unit: 'hours'
                }}
              />
              <button
                onClick={() => updateHealthMetrics({ 
                  sleep_hours: (healthMetrics?.sleep_hours || 0) + 0.5 
                })}
                className="absolute top-2 right-2 bg-purple-500 hover:bg-purple-600 text-white text-xs px-2 py-1 rounded-full transition-colors"
                title="Add 0.5 hours"
              >
                +0.5h
              </button>
            </div>
            
            <div className="relative">
              <MetricCard
                title="Water Intake"
                value={`${formatNumber(healthMetrics?.water_intake_l)}/${formatNumber(healthMetrics?.water_goal_l)} L`}
                icon={Droplets}
                iconColor="text-blue-600"
                iconBgColor="bg-blue-100"
                progress={{
                  current: healthMetrics?.water_intake_l || 0,
                  goal: healthMetrics?.water_goal_l || 0,
                  unit: 'L'
                }}
              />
              <button
                onClick={() => updateHealthMetrics({ 
                  water_intake_l: (healthMetrics?.water_intake_l || 0) + 0.25 
                })}
                className="absolute top-2 right-2 bg-blue-500 hover:bg-blue-600 text-white text-xs px-2 py-1 rounded-full transition-colors"
                title="Add 250ml water"
              >
                +250ml
              </button>
            </div>
          </div>

          {/* Weight Data and Calories Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Weight Data Card */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Weight Data</h3>
                <button className="p-1 hover:bg-gray-100 rounded-lg transition-colors">
                  <MoreHorizontal className="w-5 h-5 text-gray-400" />
                </button>
              </div>
              
              <div className="text-center">
                <ProgressChart
                  type="semi-circle"
                  value={userProfile?.current_weight_kg || userProfile?.weight_kg || 0}
                  maxValue={calculateTargetWeight(userProfile)}
                  size={128}
                  gradient={{ from: '#f97316', to: '#eab308' }}
                  label={`${userProfile?.current_weight_kg || userProfile?.weight_kg || '--'} kg`}
                  subtitle="Current Weight"
                  className="mb-4"
                />
                
                <p className="text-lg font-semibold text-gray-900 mb-2">
                  {Math.abs((userProfile?.current_weight_kg || userProfile?.weight_kg || 0) - calculateTargetWeight(userProfile))} kg left
                </p>
                <p className="text-gray-600 text-sm leading-relaxed">
                  Progress is progress, no matter how slow. Keep going, you're getting closer to your goal every day! 🚀
                </p>
              </div>
            </div>

            {/* Calories Intake Card */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Calories Intake</h3>
                <button className="p-1 hover:bg-gray-100 rounded-lg transition-colors">
                  <MoreHorizontal className="w-5 h-5 text-gray-400" />
                </button>
              </div>
              
              <div className="flex items-center space-x-6">
                {/* Left: Circular Progress */}
                <ProgressChart
                  type="circle"
                  value={healthMetrics?.calories_eaten ?? 0}
                  maxValue={healthMetrics?.calories_goal ?? 0}
                  size={96}
                  color="#3b82f6"
                  label={`${Math.max(0, (healthMetrics?.calories_goal ?? 0) - (healthMetrics?.calories_eaten ?? 0))}`}
                  subtitle="kcal left"
                />
                
                {/* Right: Details */}
                <div className="flex-1 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <UtensilsCrossed className="w-4 h-4 text-gray-500" />
                      <span className="text-sm text-gray-600">Eaten</span>
                    </div>
                    <span className="font-semibold text-gray-900">{healthMetrics?.calories_eaten} kcal</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Flame className="w-4 h-4 text-gray-500" />
                      <span className="text-sm text-gray-600">Burned</span>
                    </div>
                    <span className="font-semibold text-gray-900">{healthMetrics?.calories_burned} kcal</span>
                  </div>
                  
                  {/* Macronutrients */}
                  <div className="space-y-2">
                    <div>
                      <div className="flex justify-between text-sm text-gray-600 mb-1">
                        <span>Carbohydrates</span>
                        <span>{formatNumber(healthMetrics?.macronutrients.carbs_g)} / {formatNumber(healthMetrics?.macronutrients.carbs_goal)}g</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${Math.min(100, ((healthMetrics?.macronutrients.carbs_g ?? 0) / (healthMetrics?.macronutrients.carbs_goal || 1)) * 100)}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    <div>
                      <div className="flex justify-between text-sm text-gray-600 mb-1">
                        <span>Proteins</span>
                        <span>{formatNumber(healthMetrics?.macronutrients.protein_g)} / {formatNumber(healthMetrics?.macronutrients.protein_goal)}g</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${Math.min(100, ((healthMetrics?.macronutrients.protein_g ?? 0) / (healthMetrics?.macronutrients.protein_goal || 1)) * 100)}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    <div>
                      <div className="flex justify-between text-sm text-gray-600 mb-1">
                        <span>Fats</span>
                        <span>{formatNumber(healthMetrics?.macronutrients.fat_g)} / {formatNumber(healthMetrics?.macronutrients.fat_goal)}g</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-yellow-500 h-2 rounded-full"
                          style={{ width: `${Math.min(100, ((healthMetrics?.macronutrients.fat_g ?? 0) / (healthMetrics?.macronutrients.fat_goal || 1)) * 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Workout Progress Card */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Workout Progress</h3>
              <select className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                <option>This Week</option>
                <option>Last Week</option>
                <option>This Month</option>
              </select>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {workouts.map((workout) => (
                <WorkoutCard key={workout.id} workout={workout} />
              ))}
            </div>
          </div>

          {/* Recommended Menu Card */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Recommended Menu</h3>
              <button className="p-1 hover:bg-gray-100 rounded-lg transition-colors">
                <MoreHorizontal className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {todayMeals.slice(0, 2).map((meal) => (
                <div key={meal.id} className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg flex items-center justify-center">
                    <span className="text-2xl">🍽️</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-1">{meal.name}</h4>
                    <p className="text-sm text-gray-600">{meal.calories} kcal</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="w-80 bg-white border-l border-gray-200 p-6">
          {/* Calendar */}
          <Calendar
            selectedDate={selectedDate}
            onDateSelect={setSelectedDate}
            className="mb-8"
          />

          {/* Daily Meal Log */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Meal Log</h3>
            <div className="space-y-3">
              {todayMeals.map((meal) => (
                <MealCard
                  key={meal.id}
                  meal={meal}
                  onToggleComplete={(id) => {
                    setTodayMeals(prev => 
                      prev.map(m => m.id === id ? { ...m, completed: !m.completed } : m)
                    )
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
