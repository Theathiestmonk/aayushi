import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { apiRequest } from '../utils/api';
import { 
  Target, 
  Activity, 
  Scale, 
  Heart, 
  Brain, 
  Zap,
  ChefHat,
  ShoppingCart,
  Clock3,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Loader2,
  Calendar,

  Trash2
} from 'lucide-react';

interface HealthMetrics {
  bmi: number;
  bmi_category: string;
  bmr: number;
  tdee: number;
  target_calories: number;
  activity_level: string;
  macronutrients: {
    protein_g: number;
    protein_calories: number;
    fat_g: number;
    fat_calories: number;
    carb_g: number;
    carb_calories: number;
    protein_percentage: number;
    fat_percentage: number;
    carb_percentage: number;
  };
  height_cm: number;
  weight_kg: number;
  age: number;
  gender: string;
}

interface DietPlan {
  plan_name: string;
  duration_days: number;
  target_calories_per_day: number;
  health_metrics: HealthMetrics;
  daily_meals: any[];
  nutritional_summary: any;
  shopping_list: string[];
  meal_prep_instructions: string;
  hydration_schedule: string;
  progress_tracking: string[];
  notes: string;
  compliance_tips: string[];
  adaptation_tips: string[];
  created_at: string;
}

const DietPlanner: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  const [healthMetrics, setHealthMetrics] = useState<HealthMetrics | null>(null);
  const [dietPlan, setDietPlan] = useState<DietPlan | null>(null);
  const [savedPlans, setSavedPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [cleaning, setCleaning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    fetchHealthMetrics();
    fetchSavedPlans();
  }, [isAuthenticated, navigate]);

  const fetchHealthMetrics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiRequest('/diet-plans/health-metrics');
      
      if (response.success) {
        setHealthMetrics(response.health_metrics);
      } else {
        setError('Failed to fetch health metrics');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch health metrics');
    } finally {
      setLoading(false);
    }
  };

  const fetchSavedPlans = async () => {
    try {
      const response = await apiRequest('/diet-plans/my-plans');
      
      if (response.success) {
        setSavedPlans(response.plans || []);
      } else {
        console.log('No saved plans found or error occurred');
      }
    } catch (err: any) {
      console.log('Failed to fetch saved plans:', err.message);
    }
  };

  const cleanupExistingData = async () => {
    try {
      setCleaning(true);
      setError(null);
      
      // Show confirmation dialog
      const confirmed = window.confirm(
        '⚠️ WARNING: This will permanently delete ALL your existing diet plans, daily plans, meals, and food items.\n\n' +
        'This action cannot be undone. Are you sure you want to continue?'
      );
      
      if (!confirmed) {
        return;
      }
      
      // Call the force-clear endpoint
      const response = await apiRequest('/diet-plans/force-clear', {
        method: 'POST'
      });
      
      if (response.success) {
        // Show success message
        const deletedPlans = response.deleted_plans || 0;
        const deletedDailyPlans = response.deleted_daily_plans || 0;
        const deletedMeals = response.deleted_meals || 0;
        const deletedFoodItems = response.deleted_food_items || 0;
        
        setSuccessMessage(
          `✅ Cleanup completed successfully! Deleted ${deletedPlans} diet plans, ${deletedDailyPlans} daily plans, ${deletedMeals} meals, and ${deletedFoodItems} food items. Your database is now clean and ready for new diet plans.`
        );
        
        // Clear error if any
        setError(null);
        
        // Refresh saved plans to show empty state
        await fetchSavedPlans();
        
        // Clear any existing diet plan display
        setDietPlan(null);
        
        // Clear success message after 5 seconds
        setTimeout(() => setSuccessMessage(null), 5000);
        
      } else {
        setError(`Failed to cleanup data: ${response.error || 'Unknown error'}`);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to cleanup existing data');
    } finally {
      setCleaning(false);
    }
  };

  const generateDietPlan = async () => {
    try {
      setGenerating(true);
      setError(null);
      
      const response = await apiRequest('/diet-plans/generate', {
        method: 'POST',
        body: JSON.stringify({
          plan_duration_days: 7,
          include_meal_prep: true,
          include_shopping_list: true
        })
      });
      
      if (response.success) {
        setDietPlan(response.data.diet_plan);
        // Refresh health metrics and saved plans
        await fetchHealthMetrics();
        await fetchSavedPlans();
      } else {
        setError('Failed to generate diet plan');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate diet plan');
    } finally {
      setGenerating(false);
    }
  };

  const getBMICategoryColor = (category: string) => {
    switch (category) {
      case 'underweight': return 'text-blue-600 bg-blue-100';
      case 'normal_weight': return 'text-green-600 bg-green-100';
      case 'overweight': return 'text-yellow-600 bg-yellow-100';
      case 'obese_class_1': return 'text-orange-600 bg-orange-100';
      case 'obese_class_2': return 'text-red-600 bg-red-100';
      case 'obese_class_3': return 'text-red-800 bg-red-200';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getBMICategoryLabel = (category: string) => {
    return category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading health metrics...</span>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">AI Dietitian Agent</h1>
        <p className="text-gray-600 text-lg">Your personalized nutrition and health companion</p>
      </div>

      {/* Health Metrics Section */}
      {healthMetrics && (
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
            <Heart className="w-6 h-6 mr-2 text-red-500" />
            Health Metrics & Analysis
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* BMI Card */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <Scale className="w-8 h-8 text-blue-500" />
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getBMICategoryColor(healthMetrics.bmi_category)}`}>
                  {getBMICategoryLabel(healthMetrics.bmi_category)}
                </span>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">{healthMetrics.bmi}</h3>
              <p className="text-gray-600">BMI</p>
              <p className="text-sm text-gray-500 mt-2">
                Height: {healthMetrics.height_cm}cm | Weight: {healthMetrics.weight_kg}kg
              </p>
            </div>

            {/* Target Calories Card */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <Target className="w-8 h-8 text-green-500" />
                <span className="px-3 py-1 rounded-full text-sm font-medium text-green-600 bg-green-100">
                  Daily Target
                </span>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">{healthMetrics.target_calories}</h3>
              <p className="text-gray-600">Calories</p>
              <p className="text-sm text-gray-500 mt-2">
                Based on {healthMetrics.activity_level.replace('_', ' ')} lifestyle
              </p>
            </div>

            {/* BMR Card */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <Zap className="w-8 h-8 text-yellow-500" />
                <span className="px-3 py-1 rounded-full text-sm font-medium text-yellow-600 bg-yellow-100">
                  Resting
                </span>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">{healthMetrics.bmr}</h3>
              <p className="text-gray-600">BMR (calories)</p>
              <p className="text-sm text-gray-500 mt-2">
                Age: {healthMetrics.age} | {healthMetrics.gender}
              </p>
            </div>

            {/* TDEE Card */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <Activity className="w-8 h-8 text-purple-500" />
                <span className="px-3 py-1 rounded-full text-sm font-medium text-purple-600 bg-purple-100">
                  Active
                </span>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">{healthMetrics.tdee}</h3>
              <p className="text-gray-600">TDEE (calories)</p>
              <p className="text-sm text-gray-500 mt-2">
                Total Daily Energy Expenditure
              </p>
            </div>
          </div>

          {/* Macronutrient Breakdown */}
          <div className="mt-8 bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <Brain className="w-5 h-5 mr-2 text-indigo-500" />
              Macronutrient Distribution
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Protein */}
              <div className="text-center">
                <div className="w-20 h-20 mx-auto mb-3 rounded-full bg-red-100 flex items-center justify-center">
                  <span className="text-xl font-bold text-red-600">
                    {healthMetrics.macronutrients.protein_percentage}%
                  </span>
                </div>
                <h4 className="font-semibold text-gray-800">Protein</h4>
                <p className="text-2xl font-bold text-red-600">
                  {healthMetrics.macronutrients.protein_g}g
                </p>
                <p className="text-sm text-gray-500">
                  {healthMetrics.macronutrients.protein_calories} calories
                </p>
              </div>

              {/* Carbohydrates */}
              <div className="text-center">
                <div className="w-20 h-20 mx-auto mb-3 rounded-full bg-green-100 flex items-center justify-center">
                  <span className="text-xl font-bold text-green-600">
                    {healthMetrics.macronutrients.carb_percentage}%
                  </span>
                </div>
                <h4 className="font-semibold text-gray-800">Carbohydrates</h4>
                <p className="text-2xl font-bold text-green-600">
                  {healthMetrics.macronutrients.carb_g}g
                </p>
                <p className="text-sm text-gray-500">
                  {healthMetrics.macronutrients.carb_calories} calories
                </p>
              </div>

              {/* Fat */}
              <div className="text-center">
                <div className="w-20 h-20 mx-auto mb-3 rounded-full bg-yellow-100 flex items-center justify-center">
                  <span className="text-xl font-bold text-yellow-600">
                    {healthMetrics.macronutrients.fat_percentage}%
                  </span>
                </div>
                <h4 className="font-semibold text-gray-800">Fat</h4>
                <p className="text-2xl font-bold text-yellow-600">
                  {healthMetrics.macronutrients.fat_g}g
                </p>
                <p className="text-sm text-gray-500">
                  {healthMetrics.macronutrients.fat_calories} calories
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Diet Plan Generation Section */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
          <ChefHat className="w-6 h-6 mr-2 text-orange-500" />
          Personalized Diet Plan
        </h2>
        
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
          <div className="text-center">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
              Generate Your 7-Day Personalized Diet Plan
            </h3>
            <p className="text-gray-600 mb-6">
              Our AI Dietitian Agent will analyze your profile and create a comprehensive 7-day meal plan 
              with structured meals: Breakfast, Snack, Lunch, Snack, and Dinner. Each day includes specific 
              timings, quantities, and nutritional breakdown.
            </p>
            
            {/* Cleanup Button Section */}
            <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="text-center">
                <h3 className="text-lg font-semibold text-yellow-800 mb-2 flex items-center justify-center">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  Clear Existing Data
                </h3>
                <p className="text-yellow-700 text-sm mb-4">
                  If you have existing diet plans, click the button below to clear them before generating a new one.
                </p>
                <button
                  onClick={cleanupExistingData}
                  disabled={cleaning}
                  className="bg-yellow-600 hover:bg-yellow-700 text-white font-semibold py-2 px-6 rounded-lg shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center mx-auto"
                >
                  {cleaning ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Cleaning...
                    </>
                  ) : (
                    <>
                      <Trash2 className="w-4 h-4 mr-2" />
                      Clear All Diet Data
                    </>
                  )}
                </button>
              </div>
            </div>
            
            <button
              onClick={generateDietPlan}
              disabled={generating}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-8 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center mx-auto"
            >
              {generating ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Generating Diet Plan...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5 mr-2" />
                  Generate Diet Plan
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Success Message Display */}
      {successMessage && (
        <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
            <span className="text-green-700">{successMessage}</span>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
            <span className="text-red-700">{error}</span>
          </div>
        </div>
      )}

      {/* Saved Diet Plans Section */}
      {savedPlans.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
            <Calendar className="w-6 h-6 mr-2 text-green-500" />
            Your Saved Diet Plans
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {savedPlans.map((plan) => (
              <div key={plan.plan_id} className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
                <div className="mb-4">
                  <h3 className="text-xl font-semibold text-gray-800 mb-2">{plan.plan_name}</h3>
                  <p className="text-gray-600 text-sm">
                    {new Date(plan.start_date).toLocaleDateString()} - {new Date(plan.end_date).toLocaleDateString()}
                  </p>
                  <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium mt-2 ${
                    plan.status === 'active' ? 'bg-green-100 text-green-800' :
                    plan.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {plan.status}
                  </span>
                </div>
                
                <div className="space-y-3 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Calories:</span>
                    <span className="font-medium">{plan.calorie_target}/day</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Protein:</span>
                    <span className="font-medium">{plan.protein_target}g/day</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Carbs:</span>
                    <span className="font-medium">{plan.carb_target}g/day</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Fat:</span>
                    <span className="font-medium">{plan.fat_target}g/day</span>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <button 
                    onClick={() => window.open(`/diet-plans/plan/${plan.plan_id}`, '_blank')}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-3 rounded-lg transition-colors duration-200"
                  >
                    View Details
                  </button>
                  <button className="flex-1 bg-green-600 hover:bg-green-700 text-white text-sm font-medium py-2 px-3 rounded-lg transition-colors duration-200">
                    Track Progress
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Generated Diet Plan Display */}
      {dietPlan && (
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
            <CheckCircle className="w-6 h-6 mr-2 text-green-500" />
            Your Personalized Diet Plan
          </h2>
          
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <div className="mb-6">
              <h3 className="text-xl font-semibold text-gray-800 mb-2">{dietPlan.plan_name}</h3>
              <p className="text-gray-600">
                {dietPlan.duration_days}-day plan • {dietPlan.target_calories_per_day} calories per day
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Generated on {new Date(dietPlan.created_at).toLocaleDateString()}
              </p>
            </div>

            {/* Plan Highlights */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="flex items-center p-3 bg-blue-50 rounded-lg">
                <Clock3 className="w-5 h-5 text-blue-500 mr-2" />
                <span className="text-blue-700 font-medium">Meal Timings</span>
              </div>
              <div className="flex items-center p-3 bg-green-50 rounded-lg">
                <Scale className="w-5 h-5 text-green-500 mr-2" />
                <span className="text-green-700 font-medium">Portion Control</span>
              </div>
              <div className="flex items-center p-3 bg-purple-50 rounded-lg">
                <TrendingUp className="w-5 h-5 text-purple-500 mr-2" />
                <span className="text-purple-700 font-medium">Progress Tracking</span>
              </div>
            </div>

            {/* Compliance Tips */}
            {dietPlan.compliance_tips && dietPlan.compliance_tips.length > 0 && (
              <div className="mb-6">
                <h4 className="font-semibold text-gray-800 mb-3">Tips for Success</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {dietPlan.compliance_tips.slice(0, 6).map((tip, index) => (
                    <div key={index} className="flex items-start">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{tip}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Shopping List Preview */}
            {dietPlan.shopping_list && dietPlan.shopping_list.length > 0 && (
              <div className="mb-6">
                <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                  <ShoppingCart className="w-4 h-4 mr-2" />
                  Shopping List Preview
                </h4>
                <div className="flex flex-wrap gap-2">
                  {dietPlan.shopping_list.slice(0, 10).map((item, index) => (
                    <span key={index} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                      {item}
                    </span>
                  ))}
                  {dietPlan.shopping_list.length > 10 && (
                    <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                      +{dietPlan.shopping_list.length - 10} more items
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* View Full Plan Button */}
            <div className="text-center">
              <button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors duration-200">
                View Complete 7-Day Plan
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DietPlanner;
