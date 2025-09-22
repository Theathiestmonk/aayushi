import React, { useState, useEffect } from 'react';
import { useAuthStore, apiRequest } from '../stores/authStore';
import { useWorkoutStore } from '../stores/workoutStore';
import { 
  Calendar, 
  Activity, 
  Target, 
  TrendingUp, 
  BarChart3,
  Plus,
  Play,
  Clock,
  Flame,
  Award,
  Users,
  Zap,
  BookOpen,
  Edit,
  Trash2
} from 'lucide-react';
import WorkoutPlanner from '../components/WorkoutPlanner';
import WorkoutTracker from '../components/WorkoutTracker';
import MetricCard from '../components/ui/MetricCard';
import ProgressChart from '../components/ui/ProgressChart';

interface WorkoutPlan {
  id: string;
  name: string;
  description: string;
  fitness_level: 'beginner' | 'intermediate' | 'advanced';
  environment: 'home' | 'gym' | 'outdoor' | 'sports' | 'athletic';
  duration_weeks: number;
  days_per_week: number;
  session_duration: number;
  goals: string[];
  exercises: any[];
  schedule: {
    [key: string]: {
      type: string;
      exercises: any[];
      duration: number;
    };
  };
  created_at: string;
}

interface WorkoutSession {
  id: string;
  name: string;
  date: string;
  start_time: string;
  end_time?: string;
  duration: number;
  exercises: any[];
  total_calories_burned: number;
  status: 'planned' | 'in_progress' | 'completed' | 'paused';
}

interface TrackingStats {
  total_workouts: number;
  total_duration: number;
  total_calories_burned: number;
  current_streak: number;
  weekly_goal: number;
  weekly_progress: number;
  favorite_exercise: string;
  improvement_areas: string[];
}

const Tracking: React.FC = () => {
  const { isAuthenticated } = useAuthStore();
  const { 
    workoutPlans, 
    activeWorkoutPlan, 
    workoutSessions, 
    currentSession,
    setActiveWorkoutPlan,
    setCurrentSession,
    getRecentSessions
  } = useWorkoutStore();
  
  const [activeTab, setActiveTab] = useState<'planner' | 'tracker' | 'stats' | 'plans'>('tracker');
  const [trackingStats, setTrackingStats] = useState<TrackingStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) return;
    
    fetchTrackingData();
  }, [isAuthenticated]);

  const fetchTrackingData = async () => {
    try {
      setLoading(true);
      
      // Fetch tracking stats
      const statsResponse = await apiRequest('/tracking/stats');
      if (statsResponse.success) {
        setTrackingStats(statsResponse.stats);
      }
      
    } catch (error) {
      console.error('Failed to fetch tracking data:', error);
      
      // Mock data for demonstration
      setTrackingStats({
        total_workouts: 24,
        total_duration: 1800, // 30 hours
        total_calories_burned: 12000,
        current_streak: 7,
        weekly_goal: 5,
        weekly_progress: 3,
        favorite_exercise: 'Push-ups',
        improvement_areas: ['Consistency', 'Endurance']
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePlanCreated = (plan: WorkoutPlan) => {
    setActiveTab('plans');
  };

  const handleSessionUpdate = (session: WorkoutSession) => {
    // Session updates are handled by the store
  };

  const handleSessionComplete = (session: WorkoutSession) => {
    // Session completion is handled by the store
    // Refresh stats
    fetchTrackingData();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your tracking data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Workout Tracking</h1>
            <p className="text-gray-600">Plan, track, and analyze your fitness journey</p>
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* Tab Navigation */}
        <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg w-fit">
          <button
            onClick={() => setActiveTab('tracker')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'tracker'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Activity className="w-4 h-4 inline mr-2" />
            Workout Tracker
          </button>
          <button
            onClick={() => setActiveTab('plans')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'plans'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <BookOpen className="w-4 h-4 inline mr-2" />
            My Plans
          </button>
          <button
            onClick={() => setActiveTab('planner')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'planner'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Target className="w-4 h-4 inline mr-2" />
            Create Plan
          </button>
          <button
            onClick={() => setActiveTab('stats')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'stats'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <BarChart3 className="w-4 h-4 inline mr-2" />
            Statistics
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'tracker' && (
          <div className="space-y-6">
            <WorkoutTracker
              workoutSession={currentSession}
              onSessionUpdate={handleSessionUpdate}
              onSessionComplete={handleSessionComplete}
            />
          </div>
        )}

        {activeTab === 'plans' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">My Workout Plans</h2>
              <button
                onClick={() => setActiveTab('planner')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>Create New Plan</span>
              </button>
            </div>
            
            {workoutPlans.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {workoutPlans.map((plan) => (
                  <div key={plan.id} className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">{plan.name}</h3>
                        <p className="text-gray-600 text-sm mb-3">{plan.description}</p>
                        <div className="flex items-center space-x-4 text-xs text-gray-500 mb-4">
                          <span className="capitalize bg-gray-100 px-2 py-1 rounded">{plan.fitness_level}</span>
                          <span className="capitalize bg-gray-100 px-2 py-1 rounded">{plan.environment}</span>
                          <span className="bg-gray-100 px-2 py-1 rounded">{plan.days_per_week} days/week</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => {
                            setActiveWorkoutPlan(plan);
                            setActiveTab('tracker');
                          }}
                          className="p-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg"
                          title="Use this plan"
                        >
                          <Play className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            // TODO: Implement edit functionality
                          }}
                          className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-lg"
                          title="Edit plan"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            // TODO: Implement delete functionality
                          }}
                          className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg"
                          title="Delete plan"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Duration</span>
                        <span className="font-medium">{plan.duration_weeks} weeks</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Session Length</span>
                        <span className="font-medium">{plan.session_duration} min</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Exercises</span>
                        <span className="font-medium">{plan.exercises.length}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Goals</span>
                        <span className="font-medium">{plan.goals.length}</span>
                      </div>
                    </div>
                    
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500">
                          Created {new Date(plan.created_at).toLocaleDateString()}
                        </span>
                        {plan.is_active && (
                          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                            Active
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
                <BookOpen className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No Workout Plans</h3>
                <p className="text-gray-600 mb-6">Create your first workout plan to get started</p>
                <button
                  onClick={() => setActiveTab('planner')}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2 mx-auto"
                >
                  <Plus className="w-5 h-5" />
                  <span>Create Workout Plan</span>
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'planner' && (
          <WorkoutPlanner
            onPlanCreated={handlePlanCreated}
            existingPlan={activeWorkoutPlan}
          />
        )}

        {activeTab === 'stats' && trackingStats && (
          <div className="space-y-6">
            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
                title="Total Workouts"
                value={trackingStats.total_workouts}
                icon={Activity}
                iconColor="text-blue-600"
                iconBgColor="bg-blue-100"
              />
              <MetricCard
                title="Total Duration"
                value={`${Math.floor(trackingStats.total_duration / 60)}h ${trackingStats.total_duration % 60}m`}
                icon={Clock}
                iconColor="text-green-600"
                iconBgColor="bg-green-100"
              />
              <MetricCard
                title="Calories Burned"
                value={trackingStats.total_calories_burned.toLocaleString()}
                icon={Flame}
                iconColor="text-orange-600"
                iconBgColor="bg-orange-100"
              />
              <MetricCard
                title="Current Streak"
                value={`${trackingStats.current_streak} days`}
                icon={Award}
                iconColor="text-purple-600"
                iconBgColor="bg-purple-100"
              />
            </div>

            {/* Weekly Progress */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Progress</h3>
              <div className="flex items-center space-x-6">
                <ProgressChart
                  type="circle"
                  value={trackingStats.weekly_progress}
                  maxValue={trackingStats.weekly_goal}
                  size={120}
                  color="#3b82f6"
                  label={`${trackingStats.weekly_progress}/${trackingStats.weekly_goal}`}
                  subtitle="workouts"
                />
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">This Week</span>
                    <span className="text-sm text-gray-600">
                      {trackingStats.weekly_progress} of {trackingStats.weekly_goal} workouts
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(trackingStats.weekly_progress / trackingStats.weekly_goal) * 100}%` }}
                    />
                  </div>
                  <p className="text-sm text-gray-600 mt-2">
                    {trackingStats.weekly_goal - trackingStats.weekly_progress} workouts remaining this week
                  </p>
                </div>
              </div>
            </div>

            {/* Recent Workouts */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Workouts</h3>
              <div className="space-y-3">
                {getRecentSessions(5).map((session) => (
                  <div key={session.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Activity className="w-5 h-5 text-blue-600" />
                      <div>
                        <h4 className="font-medium text-gray-900">{session.name}</h4>
                        <p className="text-sm text-gray-600">
                          {new Date(session.date).toLocaleDateString()} • {Math.floor(session.duration / 60)}m {session.duration % 60}s
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        session.status === 'completed' ? 'bg-green-100 text-green-800' :
                        session.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {session.status}
                      </span>
                      {session.total_calories_burned > 0 && (
                        <span className="text-sm text-gray-600">
                          {session.total_calories_burned} cal
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Tracking;




