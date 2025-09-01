import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { apiRequest } from '../utils/api';
import { 
  Calendar,
  Clock,
  Utensils,
  Apple,
  Target,
  Scale,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Loader2,
  ChevronDown,
  ChevronRight,
  Plus,
  Edit,
  Trash2
} from 'lucide-react';

interface DietPlan {
  plan_id: string;
  user_id: string;
  start_date: string;
  end_date: string;
  calorie_target: number;
  protein_target: number;
  carb_target: number;
  fat_target: number;
  plan_name: string;
  status: string;
  created_at: string;
  updated_at: string;
}

interface DailyPlan {
  daily_plan_id: string;
  plan_id: string;
  date: string;
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  water_intake_target: number;
  notes: string;
  meals?: Meal[];
}

interface Meal {
  meal_id: string;
  daily_plan_id: string;
  meal_type: string;
  meal_time: string;
  meal_name: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
  instructions: string;
  food_items?: FoodItem[];
}

interface FoodItem {
  food_id: string;
  meal_id: string;
  food_name: string;
  quantity: number;
  unit: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
}

interface ProgressTracking {
  progress_id: string;
  user_id: string;
  date: string;
  weight_kg: number;
  waist_cm: number;
  energy_level: number;
  compliance_percentage: number;
  notes: string;
}

const DietPlans: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  const [dietPlans, setDietPlans] = useState<DietPlan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [planDetails, setPlanDetails] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedDays, setExpandedDays] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    fetchDietPlans();
  }, [isAuthenticated, navigate]);

  const fetchDietPlans = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiRequest('/diet-plans/my-plans');
      
      if (response.success) {
        setDietPlans(response.plans || []);
      } else {
        setError('Failed to fetch diet plans');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch diet plans');
    } finally {
      setLoading(false);
    }
  };

  const fetchPlanDetails = async (planId: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiRequest(`/diet-plans/${planId}/details`);
      
      if (response.success) {
        setPlanDetails(response.data);
        setSelectedPlan(planId);
      } else {
        setError('Failed to fetch plan details');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch plan details');
    } finally {
      setLoading(false);
    }
  };

  const toggleDayExpansion = (dayId: string) => {
    const newExpanded = new Set(expandedDays);
    if (newExpanded.has(dayId)) {
      newExpanded.delete(dayId);
    } else {
      newExpanded.add(dayId);
    }
    setExpandedDays(newExpanded);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (timeString: string) => {
    return timeString;
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getMealTypeColor = (mealType: string) => {
    switch (mealType.toLowerCase()) {
      case 'breakfast':
        return 'bg-orange-100 text-orange-800';
      case 'lunch':
        return 'bg-blue-100 text-blue-800';
      case 'dinner':
        return 'bg-purple-100 text-purple-800';
      case 'snack':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading && dietPlans.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading your diet plans...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
            <Calendar className="w-8 h-8 mr-3 text-blue-600" />
            Your Diet Plans
          </h1>
          <p className="text-gray-600">View and manage your personalized nutrition plans</p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
              <span className="text-red-700">{error}</span>
            </div>
          </div>
        )}

        {/* Diet Plans Grid */}
        {dietPlans.length === 0 ? (
          <div className="text-center py-12">
            <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No diet plans yet</h3>
            <p className="text-gray-500 mb-6">Create your first personalized diet plan to get started</p>
            <button
              onClick={() => navigate('/diet-planner')}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Diet Plan
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {dietPlans.map((plan) => (
              <div key={plan.plan_id} className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
                {/* Plan Header */}
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">{plan.plan_name}</h3>
                      <div className="flex items-center text-sm text-gray-500 mb-2">
                        <Calendar className="w-4 h-4 mr-1" />
                        {formatDate(plan.start_date)} - {formatDate(plan.end_date)}
                      </div>
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(plan.status)}`}>
                        {plan.status}
                      </span>
                    </div>
                    <button
                      onClick={() => fetchPlanDetails(plan.plan_id)}
                      className="ml-2 p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Plan Targets */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-3 bg-blue-50 rounded-lg">
                      <Target className="w-5 h-5 text-blue-600 mx-auto mb-1" />
                      <p className="text-sm font-medium text-blue-900">{plan.calorie_target}</p>
                      <p className="text-xs text-blue-600">Calories</p>
                    </div>
                    <div className="text-center p-3 bg-green-50 rounded-lg">
                      <Scale className="w-5 h-5 text-green-600 mx-auto mb-1" />
                      <p className="text-sm font-medium text-green-900">{plan.protein_target}g</p>
                      <p className="text-xs text-green-600">Protein</p>
                    </div>
                  </div>
                </div>

                {/* Plan Actions */}
                <div className="p-4 bg-gray-50">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => fetchPlanDetails(plan.plan_id)}
                      className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-3 rounded-lg transition-colors"
                    >
                      View Details
                    </button>
                    <button className="flex-1 bg-green-600 hover:bg-green-700 text-white text-sm font-medium py-2 px-3 rounded-lg transition-colors">
                      Track Progress
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Plan Details Modal */}
        {selectedPlan && planDetails && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
              {/* Modal Header */}
              <div className="sticky top-0 bg-white border-b border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{planDetails.plan_name}</h2>
                    <p className="text-gray-600 mt-1">
                      {formatDate(planDetails.start_date)} - {formatDate(planDetails.end_date)}
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectedPlan(null)}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <span className="sr-only">Close</span>
                    ×
                  </button>
                </div>
              </div>

              {/* Plan Overview */}
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Plan Overview</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <Target className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                    <p className="text-lg font-semibold text-blue-900">{planDetails.calorie_target}</p>
                    <p className="text-sm text-blue-600">Daily Calories</p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <Scale className="w-6 h-6 text-green-600 mx-auto mb-2" />
                    <p className="text-lg font-semibold text-green-900">{planDetails.protein_target}g</p>
                    <p className="text-sm text-green-600">Protein</p>
                  </div>
                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-yellow-600 mx-auto mb-2" />
                    <p className="text-lg font-semibold text-yellow-900">{planDetails.carb_target}g</p>
                    <p className="text-sm text-yellow-600">Carbs</p>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <Apple className="w-6 h-6 text-purple-600 mx-auto mb-2" />
                    <p className="text-lg font-semibold text-purple-900">{planDetails.fat_target}g</p>
                    <p className="text-sm text-purple-600">Fat</p>
                  </div>
                </div>
              </div>

              {/* Daily Plans */}
              {planDetails.daily_plans && (
                <div className="p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Meal Plans</h3>
                  <div className="space-y-4">
                    {planDetails.daily_plans.map((day: DailyPlan) => (
                      <div key={day.daily_plan_id} className="border border-gray-200 rounded-lg overflow-hidden">
                        {/* Day Header */}
                        <div 
                          className="bg-gray-50 p-4 cursor-pointer hover:bg-gray-100 transition-colors"
                          onClick={() => toggleDayExpansion(day.daily_plan_id)}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center">
                              <Calendar className="w-5 h-5 text-gray-600 mr-3" />
                              <div>
                                <h4 className="font-medium text-gray-900">{formatDate(day.date)}</h4>
                                <p className="text-sm text-gray-600">
                                  {day.total_calories} cal • {day.total_protein}g protein • {day.total_carbs}g carbs • {day.total_fat}g fat
                                </p>
                              </div>
                            </div>
                            {expandedDays.has(day.daily_plan_id) ? (
                              <ChevronDown className="w-5 h-5 text-gray-600" />
                            ) : (
                              <ChevronRight className="w-5 h-5 text-gray-600" />
                            )}
                          </div>
                        </div>

                        {/* Day Details */}
                        {expandedDays.has(day.daily_plan_id) && (
                          <div className="p-4 bg-white">
                            {day.meals && day.meals.map((meal: Meal) => (
                              <div key={meal.meal_id} className="mb-4 last:mb-0">
                                <div className="flex items-center justify-between mb-2">
                                  <div className="flex items-center">
                                    <Utensils className="w-4 h-4 text-gray-600 mr-2" />
                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getMealTypeColor(meal.meal_type)}`}>
                                      {meal.meal_type}
                                    </span>
                                    <span className="ml-2 text-sm text-gray-600">{meal.meal_time}</span>
                                  </div>
                                  <div className="text-sm text-gray-600">
                                    {meal.calories} cal
                                  </div>
                                </div>
                                
                                <h5 className="font-medium text-gray-900 mb-2">{meal.meal_name}</h5>
                                
                                {/* Meal Nutrition */}
                                <div className="grid grid-cols-4 gap-2 mb-3 text-xs">
                                  <div className="text-center p-2 bg-blue-50 rounded">
                                    <span className="font-medium text-blue-900">{meal.protein}g</span>
                                    <p className="text-blue-600">Protein</p>
                                  </div>
                                  <div className="text-center p-2 bg-green-50 rounded">
                                    <span className="font-medium text-green-900">{meal.carbs}g</span>
                                    <p className="text-green-600">Carbs</p>
                                  </div>
                                  <div className="text-center p-2 bg-yellow-50 rounded">
                                    <span className="font-medium text-yellow-900">{meal.fat}g</span>
                                    <p className="text-yellow-600">Fat</p>
                                  </div>
                                  <div className="text-center p-2 bg-purple-50 rounded">
                                    <span className="font-medium text-purple-900">{meal.fiber}g</span>
                                    <p className="text-purple-600">Fiber</p>
                                  </div>
                                </div>

                                {/* Food Items */}
                                {meal.food_items && meal.food_items.length > 0 && (
                                  <div className="mb-3">
                                    <h6 className="text-sm font-medium text-gray-700 mb-2">Ingredients:</h6>
                                    <div className="space-y-1">
                                      {meal.food_items.map((item: FoodItem) => (
                                        <div key={item.food_id} className="flex items-center justify-between text-sm">
                                          <span className="text-gray-600">
                                            {item.food_name} ({item.quantity} {item.unit})
                                          </span>
                                          <span className="text-gray-500">{item.calories} cal</span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Instructions */}
                                {meal.instructions && (
                                  <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                                    <span className="font-medium text-gray-700">Instructions:</span> {meal.instructions}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Progress Tracking */}
              {planDetails.progress_tracking && planDetails.progress_tracking.length > 0 && (
                <div className="p-6 border-t border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Progress Tracking</h3>
                  <div className="space-y-3">
                    {planDetails.progress_tracking.map((progress: ProgressTracking) => (
                      <div key={progress.progress_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center">
                          <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                          <div>
                            <p className="font-medium text-gray-900">{formatDate(progress.date)}</p>
                            <p className="text-sm text-gray-600">
                              Weight: {progress.weight_kg}kg • Waist: {progress.waist_cm}cm • Energy: {progress.energy_level}/10
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <span className="inline-block px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                            {progress.compliance_percentage}% compliance
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DietPlans;
