import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Pause, 
  Square, 
  RotateCcw, 
  Clock, 
  Flame, 
  Target, 
  CheckCircle,
  Plus,
  Minus,
  Timer,
  Activity,
  Dumbbell,
  Heart,
  Zap,
  Calendar,
  TrendingUp,
  BarChart3,
  Award,
  List,
  BookOpen
} from 'lucide-react';
import { useWorkoutStore } from '../stores/workoutStore';

interface Exercise {
  id: string;
  name: string;
  category: 'strength' | 'cardio' | 'flexibility';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  equipment: string;
  muscles: string[];
  instructions: string[];
  duration?: number;
  reps?: number;
  sets?: number;
  rest_time?: number;
  weight?: number;
}

interface WorkoutSession {
  id: string;
  workout_plan_id?: string;
  name: string;
  date: string;
  start_time: string;
  end_time?: string;
  duration: number;
  exercises: ExerciseSession[];
  total_calories_burned: number;
  status: 'planned' | 'in_progress' | 'completed' | 'paused';
  notes?: string;
}

interface ExerciseSession {
  exercise: Exercise;
  sets_completed: number;
  reps_completed: number[];
  weight_used: number[];
  duration_completed: number;
  rest_taken: number;
  notes: string;
  completed: boolean;
}

interface WorkoutTrackerProps {
  workoutSession?: WorkoutSession | null;
  onSessionUpdate?: (session: WorkoutSession) => void;
  onSessionComplete?: (session: WorkoutSession) => void;
  className?: string;
}

const WorkoutTracker: React.FC<WorkoutTrackerProps> = ({
  workoutSession,
  onSessionUpdate,
  onSessionComplete,
  className = ''
}) => {
  const { 
    activeWorkoutPlan, 
    workoutPlans, 
    currentSession, 
    setCurrentSession,
    addWorkoutSession,
    updateWorkoutSession
  } = useWorkoutStore();
  
  const [selectedPlan, setSelectedPlan] = useState(activeWorkoutPlan);
  const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
  const [isActive, setIsActive] = useState(false);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [restTimer, setRestTimer] = useState(0);
  const [isResting, setIsResting] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [showPlanSelector, setShowPlanSelector] = useState(false);
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const restIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Sample workout session for demonstration
  const sampleWorkout: WorkoutSession = {
    id: 'workout_1',
    name: 'Upper Body Strength',
    date: new Date().toISOString().split('T')[0],
    start_time: new Date().toISOString(),
    duration: 0,
    exercises: [
      {
        exercise: {
          id: 'push_ups',
          name: 'Push-ups',
          category: 'strength',
          difficulty: 'beginner',
          equipment: 'none',
          muscles: ['chest', 'triceps', 'shoulders'],
          instructions: ['Start in plank position', 'Lower body until chest nearly touches floor', 'Push back up'],
          reps: 10,
          sets: 3,
          rest_time: 60
        },
        sets_completed: 0,
        reps_completed: [],
        weight_used: [],
        duration_completed: 0,
        rest_taken: 0,
        notes: '',
        completed: false
      },
      {
        exercise: {
          id: 'squats',
          name: 'Squats',
          category: 'strength',
          difficulty: 'beginner',
          equipment: 'none',
          muscles: ['quads', 'glutes', 'hamstrings'],
          instructions: ['Stand with feet shoulder-width apart', 'Lower body as if sitting back', 'Return to standing'],
          reps: 15,
          sets: 3,
          rest_time: 60
        },
        sets_completed: 0,
        reps_completed: [],
        weight_used: [],
        duration_completed: 0,
        rest_taken: 0,
        notes: '',
        completed: false
      },
      {
        exercise: {
          id: 'planks',
          name: 'Planks',
          category: 'strength',
          difficulty: 'beginner',
          equipment: 'none',
          muscles: ['abs', 'core'],
          instructions: ['Start in push-up position', 'Hold body in straight line', 'Engage core'],
          duration: 30,
          sets: 3,
          rest_time: 60
        },
        sets_completed: 0,
        reps_completed: [],
        weight_used: [],
        duration_completed: 0,
        rest_taken: 0,
        notes: '',
        completed: false
      }
    ],
    total_calories_burned: 0,
    status: 'planned'
  };

  useEffect(() => {
    if (!currentSession && selectedPlan) {
      // Create a new session from the selected plan
      const newSession: WorkoutSession = {
        id: `session_${Date.now()}`,
        workout_plan_id: selectedPlan.id,
        name: selectedPlan.name,
        date: new Date().toISOString().split('T')[0],
        start_time: new Date().toISOString(),
        duration: 0,
        exercises: selectedPlan.exercises.map(ex => ({
          exercise: ex,
          sets_completed: 0,
          reps_completed: [],
          weight_used: [],
          duration_completed: 0,
          rest_taken: 0,
          notes: '',
          completed: false
        })),
        total_calories_burned: 0,
        status: 'planned'
      };
      
      setCurrentSession(newSession);
      addWorkoutSession(newSession);
    }
  }, [selectedPlan, currentSession, setCurrentSession, addWorkoutSession]);

  useEffect(() => {
    if (isActive && !isResting) {
      intervalRef.current = setInterval(() => {
        setTimeElapsed(prev => prev + 1);
      }, 1000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isActive, isResting]);

  useEffect(() => {
    if (isResting && restTimer > 0) {
      restIntervalRef.current = setInterval(() => {
        setRestTimer(prev => {
          if (prev <= 1) {
            setIsResting(false);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      if (restIntervalRef.current) {
        clearInterval(restIntervalRef.current);
      }
    }

    return () => {
      if (restIntervalRef.current) {
        clearInterval(restIntervalRef.current);
      }
    };
  }, [isResting, restTimer]);

  const startWorkout = () => {
    if (!currentSession) return;
    
    const updatedSession = {
      ...currentSession,
      status: 'in_progress' as const,
      start_time: new Date().toISOString()
    };
    
    setCurrentSession(updatedSession);
    updateWorkoutSession(currentSession.id, updatedSession);
    setIsActive(true);
    onSessionUpdate?.(updatedSession);
  };

  const pauseWorkout = () => {
    setIsActive(false);
    if (currentSession) {
      const updatedSession = {
        ...currentSession,
        status: 'paused' as const
      };
      setCurrentSession(updatedSession);
      updateWorkoutSession(currentSession.id, updatedSession);
      onSessionUpdate?.(updatedSession);
    }
  };

  const resumeWorkout = () => {
    setIsActive(true);
    if (currentSession) {
      const updatedSession = {
        ...currentSession,
        status: 'in_progress' as const
      };
      setCurrentSession(updatedSession);
      updateWorkoutSession(currentSession.id, updatedSession);
      onSessionUpdate?.(updatedSession);
    }
  };

  const completeSet = (exerciseIndex: number) => {
    if (!currentSession) return;
    
    const updatedExercises = [...currentSession.exercises];
    const exercise = updatedExercises[exerciseIndex];
    
    exercise.sets_completed += 1;
    
    if (exercise.exercise.reps) {
      exercise.reps_completed.push(exercise.exercise.reps);
    }
    
    if (exercise.sets_completed >= (exercise.exercise.sets || 1)) {
      exercise.completed = true;
      if (exerciseIndex < currentSession.exercises.length - 1) {
        setCurrentExerciseIndex(exerciseIndex + 1);
      }
    }
    
    const updatedSession = {
      ...currentSession,
      exercises: updatedExercises,
      duration: timeElapsed
    };
    
    setCurrentSession(updatedSession);
    updateWorkoutSession(currentSession.id, updatedSession);
    onSessionUpdate?.(updatedSession);
    
    // Start rest timer
    if (exercise.exercise.rest_time && exercise.sets_completed < (exercise.exercise.sets || 1)) {
      setRestTimer(exercise.exercise.rest_time);
      setIsResting(true);
    }
  };

  const completeWorkout = () => {
    if (!currentSession) return;
    
    const updatedSession = {
      ...currentSession,
      status: 'completed' as const,
      end_time: new Date().toISOString(),
      duration: timeElapsed,
      total_calories_burned: Math.round(timeElapsed * 0.1) // Simple calculation
    };
    
    setCurrentSession(updatedSession);
    updateWorkoutSession(currentSession.id, updatedSession);
    setIsActive(false);
    onSessionComplete?.(updatedSession);
  };

  const resetWorkout = () => {
    setCurrentSession(sampleWorkout);
    setCurrentExerciseIndex(0);
    setIsActive(false);
    setTimeElapsed(0);
    setRestTimer(0);
    setIsResting(false);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getCurrentExercise = () => {
    if (!currentSession) return null;
    return currentSession.exercises[currentExerciseIndex];
  };

  const getWorkoutProgress = () => {
    if (!currentSession) return 0;
    const completedExercises = currentSession.exercises.filter(ex => ex.completed).length;
    return (completedExercises / currentSession.exercises.length) * 100;
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'strength': return Dumbbell;
      case 'cardio': return Heart;
      case 'flexibility': return Activity;
      default: return Target;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'strength': return 'text-orange-600 bg-orange-100';
      case 'cardio': return 'text-red-600 bg-red-100';
      case 'flexibility': return 'text-purple-600 bg-purple-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (!currentSession) {
    return (
      <div className={`bg-white rounded-xl border border-gray-200 p-6 ${className}`}>
        <div className="text-center">
          <Activity className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Workout Session</h3>
          <p className="text-gray-600">Start a new workout to begin tracking</p>
        </div>
      </div>
    );
  }

  const currentExercise = getCurrentExercise();
  const progress = getWorkoutProgress();

  return (
    <div className={`bg-white rounded-xl border border-gray-200 p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h2 className="text-xl font-bold text-gray-900">{currentSession?.name || 'No Workout Selected'}</h2>
            {workoutPlans.length > 0 && (
              <button
                onClick={() => setShowPlanSelector(!showPlanSelector)}
                className="p-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
                title="Select Workout Plan"
              >
                <BookOpen className="w-5 h-5" />
              </button>
            )}
          </div>
          <p className="text-gray-600">
            {currentSession ? `${currentSession.exercises.length} exercises • ${formatTime(timeElapsed)}` : 'Select a workout plan to begin'}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowStats(!showStats)}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
          >
            <BarChart3 className="w-5 h-5" />
          </button>
          <button
            onClick={resetWorkout}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
          >
            <RotateCcw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Workout Plan Selector */}
      {showPlanSelector && (
        <div className="mb-6 bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Select Workout Plan</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {workoutPlans.map((plan) => (
              <button
                key={plan.id}
                onClick={() => {
                  setSelectedPlan(plan);
                  setShowPlanSelector(false);
                  // Reset current session to create new one from selected plan
                  setCurrentSession(null);
                }}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  selectedPlan?.id === plan.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{plan.name}</h4>
                  {selectedPlan?.id === plan.id && <CheckCircle className="w-5 h-5 text-blue-600" />}
                </div>
                <p className="text-sm text-gray-600 mb-2">{plan.description}</p>
                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <span className="capitalize">{plan.fitness_level}</span>
                  <span>•</span>
                  <span className="capitalize">{plan.environment}</span>
                  <span>•</span>
                  <span>{plan.days_per_week} days/week</span>
                </div>
              </button>
            ))}
          </div>
          {workoutPlans.length === 0 && (
            <div className="text-center py-8">
              <BookOpen className="w-12 h-12 mx-auto text-gray-400 mb-3" />
              <p className="text-gray-600">No workout plans available</p>
              <p className="text-sm text-gray-500">Create a workout plan first to start tracking</p>
            </div>
          )}
        </div>
      )}

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Progress</span>
          <span className="text-sm text-gray-600">{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Timer and Controls */}
      <div className="flex items-center justify-center mb-8">
        <div className="text-center">
          <div className="text-4xl font-bold text-gray-900 mb-2">
            {isResting ? formatTime(restTimer) : formatTime(timeElapsed)}
          </div>
          <div className="text-sm text-gray-600 mb-4">
            {isResting ? 'Rest Time' : 'Workout Time'}
          </div>
          
          <div className="flex items-center space-x-3">
            {currentSession.status === 'planned' && (
              <button
                onClick={startWorkout}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-2"
              >
                <Play className="w-5 h-5" />
                <span>Start Workout</span>
              </button>
            )}
            
            {currentSession.status === 'in_progress' && !isResting && (
              <button
                onClick={pauseWorkout}
                className="px-6 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 flex items-center space-x-2"
              >
                <Pause className="w-5 h-5" />
                <span>Pause</span>
              </button>
            )}
            
            {currentSession.status === 'paused' && (
              <button
                onClick={resumeWorkout}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-2"
              >
                <Play className="w-5 h-5" />
                <span>Resume</span>
              </button>
            )}
            
            {currentSession.status === 'in_progress' && (
              <button
                onClick={completeWorkout}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
              >
                <CheckCircle className="w-5 h-5" />
                <span>Complete</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Current Exercise */}
      {currentExercise && (
        <div className="mb-8">
          <div className="bg-gray-50 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                {(() => {
                  const Icon = getCategoryIcon(currentExercise.exercise.category);
                  return <Icon className={`w-6 h-6 ${getCategoryColor(currentExercise.exercise.category).split(' ')[0]}`} />;
                })()}
                <h3 className="text-lg font-semibold text-gray-900">
                  {currentExercise.exercise.name}
                </h3>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getCategoryColor(currentExercise.exercise.category)}`}>
                {currentExercise.exercise.category}
              </span>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {currentExercise.sets_completed}/{currentExercise.exercise.sets || 1}
                </div>
                <div className="text-sm text-gray-600">Sets</div>
              </div>
              {currentExercise.exercise.reps && (
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {currentExercise.exercise.reps}
                  </div>
                  <div className="text-sm text-gray-600">Reps</div>
                </div>
              )}
              {currentExercise.exercise.duration && (
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {currentExercise.exercise.duration}s
                  </div>
                  <div className="text-sm text-gray-600">Duration</div>
                </div>
              )}
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {currentExercise.exercise.rest_time || 0}s
                </div>
                <div className="text-sm text-gray-600">Rest</div>
              </div>
            </div>
            
            <div className="flex justify-center">
              <button
                onClick={() => completeSet(currentExerciseIndex)}
                disabled={isResting || currentExercise.completed}
                className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <CheckCircle className="w-5 h-5" />
                <span>
                  {currentExercise.completed ? 'Completed' : 'Complete Set'}
                </span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Exercise List */}
      <div className="space-y-3">
        <h3 className="text-lg font-semibold text-gray-900">Exercise List</h3>
        {currentSession.exercises.map((exercise, index) => {
          const Icon = getCategoryIcon(exercise.exercise.category);
          const isCurrent = index === currentExerciseIndex;
          const isCompleted = exercise.completed;
          
          return (
            <div
              key={exercise.exercise.id}
              className={`p-4 rounded-lg border-2 transition-all ${
                isCurrent
                  ? 'border-blue-500 bg-blue-50'
                  : isCompleted
                  ? 'border-green-500 bg-green-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Icon className={`w-5 h-5 ${getCategoryColor(exercise.exercise.category).split(' ')[0]}`} />
                  <div>
                    <h4 className="font-medium text-gray-900">{exercise.exercise.name}</h4>
                    <p className="text-sm text-gray-600">
                      {exercise.sets_completed}/{exercise.exercise.sets || 1} sets
                      {exercise.exercise.reps && ` • ${exercise.exercise.reps} reps`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {isCompleted && <CheckCircle className="w-5 h-5 text-green-600" />}
                  {isCurrent && !isCompleted && <div className="w-3 h-3 bg-blue-600 rounded-full animate-pulse" />}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Stats Modal */}
      {showStats && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Workout Stats</h3>
              <button
                onClick={() => setShowStats(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Duration</span>
                <span className="font-semibold">{formatTime(timeElapsed)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Exercises Completed</span>
                <span className="font-semibold">
                  {currentSession.exercises.filter(ex => ex.completed).length}/{currentSession.exercises.length}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Calories Burned</span>
                <span className="font-semibold">{Math.round(timeElapsed * 0.1)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Progress</span>
                <span className="font-semibold">{Math.round(progress)}%</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkoutTracker;
