import React, { useState, useEffect } from 'react';
import { 
  Target, 
  Activity, 
  Clock, 
  Dumbbell, 
  Heart, 
  Zap,
  CheckCircle,
  Plus,
  Minus,
  Play,
  Pause,
  RotateCcw,
  Calendar,
  TrendingUp,
  Users,
  Home,
  Building,
  TreePine,
  Gamepad2,
  Trophy
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
}

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
  exercises: Exercise[];
  schedule: {
    [key: string]: {
      type: string;
      exercises: Exercise[];
      duration: number;
    };
  };
  training_split?: string;
  intensity_preference?: string;
  rest_preference?: string;
  progression_style?: string;
  created_at: string;
  is_active?: boolean;
}

interface WorkoutPlannerProps {
  onPlanCreated?: (plan: WorkoutPlan) => void;
  onPlanUpdated?: (plan: WorkoutPlan) => void;
  existingPlan?: WorkoutPlan | null;
  className?: string;
}

const WorkoutPlanner: React.FC<WorkoutPlannerProps> = ({
  onPlanCreated,
  onPlanUpdated,
  existingPlan,
  className = ''
}) => {
  const { addWorkoutPlan, updateWorkoutPlan, setActiveWorkoutPlan } = useWorkoutStore();
  const [currentStep, setCurrentStep] = useState(1);
  const [isGenerating, setIsGenerating] = useState(false);
  const [workoutPlan, setWorkoutPlan] = useState<Partial<WorkoutPlan>>(
    existingPlan || {
      fitness_level: 'beginner',
      environment: 'home',
      duration_weeks: 8,
      days_per_week: 3,
      session_duration: 45,
      goals: [],
      exercises: []
    }
  );

  const [availableExercises, setAvailableExercises] = useState<Exercise[]>([]);
  const [selectedExercises, setSelectedExercises] = useState<Exercise[]>([]);

  const fitnessLevels = [
    { value: 'beginner', label: 'Beginner', description: 'New to fitness or returning after a break', icon: Target },
    { value: 'intermediate', label: 'Intermediate', description: 'Consistent fitness experience', icon: Activity },
    { value: 'advanced', label: 'Advanced', description: 'Experienced athlete or fitness enthusiast', icon: Trophy }
  ];

  const environments = [
    { value: 'home', label: 'Home Gym', description: 'Limited equipment, bodyweight focus', icon: Home },
    { value: 'gym', label: 'Commercial Gym', description: 'Full equipment access', icon: Building },
    { value: 'outdoor', label: 'Outdoor', description: 'Park, beach, or outdoor spaces', icon: TreePine },
    { value: 'sports', label: 'Sports-Specific', description: 'Court, field, or sports facility', icon: Gamepad2 },
    { value: 'athletic', label: 'Athletic Training', description: 'Performance and competition focus', icon: Trophy }
  ];

  const workoutGoals = [
    { id: 'weight_loss', label: 'Weight Loss', icon: Target },
    { id: 'muscle_gain', label: 'Muscle Gain', icon: Dumbbell },
    { id: 'endurance', label: 'Endurance', icon: Heart },
    { id: 'strength', label: 'Strength', icon: Zap },
    { id: 'flexibility', label: 'Flexibility', icon: Activity },
    { id: 'general_fitness', label: 'General Fitness', icon: TrendingUp }
  ];

  const sampleExercises: Exercise[] = [
    // Strength Exercises - Beginner
    {
      id: 'push_ups',
      name: 'Push-ups',
      category: 'strength',
      difficulty: 'beginner',
      equipment: 'none',
      muscles: ['chest', 'triceps', 'shoulders'],
      instructions: ['Start in plank position', 'Lower body until chest nearly touches floor', 'Push back up to starting position'],
      reps: 10,
      sets: 3,
      rest_time: 60
    },
    {
      id: 'squats',
      name: 'Squats',
      category: 'strength',
      difficulty: 'beginner',
      equipment: 'none',
      muscles: ['quads', 'glutes', 'hamstrings'],
      instructions: ['Stand with feet shoulder-width apart', 'Lower body as if sitting back into chair', 'Return to standing position'],
      reps: 15,
      sets: 3,
      rest_time: 60
    },
    {
      id: 'planks',
      name: 'Planks',
      category: 'strength',
      difficulty: 'beginner',
      equipment: 'none',
      muscles: ['abs', 'core'],
      instructions: ['Start in push-up position', 'Hold body in straight line', 'Engage core throughout'],
      duration: 30,
      sets: 3,
      rest_time: 60
    },
    {
      id: 'lunges',
      name: 'Lunges',
      category: 'strength',
      difficulty: 'beginner',
      equipment: 'none',
      muscles: ['quads', 'glutes', 'hamstrings'],
      instructions: ['Step forward with one leg', 'Lower hips until both knees are bent', 'Push back to starting position'],
      reps: 12,
      sets: 3,
      rest_time: 60
    },
    {
      id: 'mountain_climbers',
      name: 'Mountain Climbers',
      category: 'strength',
      difficulty: 'intermediate',
      equipment: 'none',
      muscles: ['core', 'shoulders', 'legs'],
      instructions: ['Start in plank position', 'Bring knees alternately to chest', 'Maintain plank position'],
      duration: 30,
      sets: 3,
      rest_time: 60
    },
    {
      id: 'dips',
      name: 'Tricep Dips',
      category: 'strength',
      difficulty: 'intermediate',
      equipment: 'chair',
      muscles: ['triceps', 'shoulders'],
      instructions: ['Sit on edge of chair', 'Lower body by bending arms', 'Push back up to starting position'],
      reps: 10,
      sets: 3,
      rest_time: 60
    },
    {
      id: 'pull_ups',
      name: 'Pull-ups',
      category: 'strength',
      difficulty: 'advanced',
      equipment: 'bar',
      muscles: ['back', 'biceps'],
      instructions: ['Hang from bar with overhand grip', 'Pull body up until chin over bar', 'Lower with control'],
      reps: 8,
      sets: 3,
      rest_time: 90
    },
    {
      id: 'handstand_pushups',
      name: 'Handstand Push-ups',
      category: 'strength',
      difficulty: 'advanced',
      equipment: 'wall',
      muscles: ['shoulders', 'triceps', 'core'],
      instructions: ['Kick up to handstand against wall', 'Lower head toward ground', 'Push back up'],
      reps: 5,
      sets: 3,
      rest_time: 120
    },
    // Cardio Exercises
    {
      id: 'jumping_jacks',
      name: 'Jumping Jacks',
      category: 'cardio',
      difficulty: 'beginner',
      equipment: 'none',
      muscles: ['full_body'],
      instructions: ['Stand with feet together', 'Jump while spreading legs and raising arms', 'Return to starting position'],
      duration: 60,
      sets: 3,
      rest_time: 30
    },
    {
      id: 'burpees',
      name: 'Burpees',
      category: 'cardio',
      difficulty: 'intermediate',
      equipment: 'none',
      muscles: ['full_body'],
      instructions: ['Start standing', 'Drop to push-up position', 'Do push-up', 'Jump feet to hands', 'Jump up with arms overhead'],
      reps: 8,
      sets: 3,
      rest_time: 90
    },
    {
      id: 'high_knees',
      name: 'High Knees',
      category: 'cardio',
      difficulty: 'beginner',
      equipment: 'none',
      muscles: ['legs', 'core'],
      instructions: ['Run in place', 'Bring knees up to chest level', 'Pump arms naturally'],
      duration: 30,
      sets: 3,
      rest_time: 30
    },
    {
      id: 'box_jumps',
      name: 'Box Jumps',
      category: 'cardio',
      difficulty: 'intermediate',
      equipment: 'box',
      muscles: ['legs', 'glutes'],
      instructions: ['Stand in front of box', 'Jump onto box with both feet', 'Step down carefully'],
      reps: 10,
      sets: 3,
      rest_time: 60
    },
    {
      id: 'sprint_intervals',
      name: 'Sprint Intervals',
      category: 'cardio',
      difficulty: 'advanced',
      equipment: 'none',
      muscles: ['legs', 'glutes', 'core'],
      instructions: ['Sprint at maximum effort', 'Rest for equal time', 'Repeat for specified rounds'],
      duration: 20,
      sets: 8,
      rest_time: 20
    },
    // Flexibility Exercises
    {
      id: 'hamstring_stretch',
      name: 'Hamstring Stretch',
      category: 'flexibility',
      difficulty: 'beginner',
      equipment: 'none',
      muscles: ['hamstrings'],
      instructions: ['Sit with legs extended', 'Reach forward toward toes', 'Hold stretch without bouncing'],
      duration: 30,
      sets: 2,
      rest_time: 30
    },
    {
      id: 'hip_flexor_stretch',
      name: 'Hip Flexor Stretch',
      category: 'flexibility',
      difficulty: 'beginner',
      equipment: 'none',
      muscles: ['hip_flexors'],
      instructions: ['Step forward into lunge position', 'Lower back knee to ground', 'Push hips forward'],
      duration: 30,
      sets: 2,
      rest_time: 30
    },
    {
      id: 'pigeon_pose',
      name: 'Pigeon Pose',
      category: 'flexibility',
      difficulty: 'intermediate',
      equipment: 'none',
      muscles: ['hips', 'glutes'],
      instructions: ['Start in downward dog', 'Bring knee forward', 'Extend back leg straight'],
      duration: 45,
      sets: 2,
      rest_time: 30
    },
    {
      id: 'splits',
      name: 'Splits',
      category: 'flexibility',
      difficulty: 'advanced',
      equipment: 'none',
      muscles: ['hamstrings', 'hip_flexors'],
      instructions: ['Extend legs in opposite directions', 'Lower body gradually', 'Hold position'],
      duration: 60,
      sets: 2,
      rest_time: 60
    }
  ];

  useEffect(() => {
    // Filter exercises based on selected environment and fitness level
    const filtered = sampleExercises.filter(exercise => {
      const levelMatch = exercise.difficulty === workoutPlan.fitness_level || 
                        (workoutPlan.fitness_level === 'intermediate' && exercise.difficulty === 'beginner') ||
                        (workoutPlan.fitness_level === 'advanced' && ['beginner', 'intermediate'].includes(exercise.difficulty));
      
      const equipmentMatch = workoutPlan.environment === 'home' ? 
                            exercise.equipment === 'none' : true;
      
      return levelMatch && equipmentMatch;
    });
    
    setAvailableExercises(filtered);
  }, [workoutPlan.fitness_level, workoutPlan.environment]);

  const handleGoalToggle = (goalId: string) => {
    setWorkoutPlan(prev => ({
      ...prev,
      goals: prev.goals?.includes(goalId) 
        ? prev.goals.filter(g => g !== goalId)
        : [...(prev.goals || []), goalId]
    }));
  };

  const handleExerciseToggle = (exercise: Exercise) => {
    setSelectedExercises(prev => 
      prev.find(e => e.id === exercise.id)
        ? prev.filter(e => e.id !== exercise.id)
        : [...prev, exercise]
    );
  };

  const generateWorkoutPlan = async () => {
    setIsGenerating(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Auto-select exercises for beginners based on goals and environment
      let finalExercises = selectedExercises;
      if (workoutPlan.fitness_level === 'beginner') {
        finalExercises = getRecommendedExercisesForBeginners();
      }
      
      const newPlan: WorkoutPlan = {
        id: `workout_${Date.now()}`,
        name: `${workoutPlan.fitness_level?.charAt(0).toUpperCase()}${workoutPlan.fitness_level?.slice(1)} ${workoutPlan.environment?.charAt(0).toUpperCase()}${workoutPlan.environment?.slice(1)} Workout`,
        description: `A ${workoutPlan.fitness_level} level workout plan for ${workoutPlan.environment} environment`,
        fitness_level: workoutPlan.fitness_level!,
        environment: workoutPlan.environment!,
        duration_weeks: workoutPlan.duration_weeks!,
        days_per_week: workoutPlan.days_per_week!,
        session_duration: workoutPlan.session_duration!,
        goals: workoutPlan.goals!,
        exercises: finalExercises,
        schedule: generateSchedule(finalExercises),
        training_split: workoutPlan.training_split,
        intensity_preference: workoutPlan.intensity_preference,
        rest_preference: workoutPlan.rest_preference,
        progression_style: workoutPlan.progression_style,
        created_at: new Date().toISOString(),
        is_active: true
      };
      
      // Save to store
      addWorkoutPlan(newPlan);
      setActiveWorkoutPlan(newPlan);
      
      setWorkoutPlan(newPlan);
      onPlanCreated?.(newPlan);
      setCurrentStep(4);
    } catch (error) {
      console.error('Failed to generate workout plan:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const getRecommendedExercisesForBeginners = (): Exercise[] => {
    const recommendedExercises: Exercise[] = [];
    
    // Always include basic exercises for beginners
    const basicExercises = [
      'push_ups', 'squats', 'planks', 'jumping_jacks', 'hamstring_stretch'
    ];
    
    // Add exercises based on goals
    if (workoutPlan.goals?.includes('weight_loss')) {
      recommendedExercises.push(
        sampleExercises.find(ex => ex.id === 'jumping_jacks')!,
        sampleExercises.find(ex => ex.id === 'burpees')!
      );
    }
    
    if (workoutPlan.goals?.includes('muscle_gain') || workoutPlan.goals?.includes('strength')) {
      recommendedExercises.push(
        sampleExercises.find(ex => ex.id === 'push_ups')!,
        sampleExercises.find(ex => ex.id === 'squats')!,
        sampleExercises.find(ex => ex.id === 'planks')!
      );
    }
    
    if (workoutPlan.goals?.includes('flexibility')) {
      recommendedExercises.push(
        sampleExercises.find(ex => ex.id === 'hamstring_stretch')!
      );
    }
    
    // Add basic exercises if not already included
    basicExercises.forEach(exerciseId => {
      const exercise = sampleExercises.find(ex => ex.id === exerciseId);
      if (exercise && !recommendedExercises.find(ex => ex.id === exerciseId)) {
        recommendedExercises.push(exercise);
      }
    });
    
    // Limit to 6 exercises for beginners to avoid overwhelm
    return recommendedExercises.slice(0, 6);
  };

  const generateSchedule = (exercises: Exercise[] = selectedExercises) => {
    const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
    const schedule: any = {};
    
    const strengthExercises = exercises.filter(e => e.category === 'strength');
    const cardioExercises = exercises.filter(e => e.category === 'cardio');
    const flexibilityExercises = exercises.filter(e => e.category === 'flexibility');
    
    // Determine workout split based on fitness level and preferences
    let workoutTypes: string[] = [];
    
    if (workoutPlan.fitness_level === 'beginner') {
      // Beginners: Simple full-body workouts
      workoutTypes = ['full_body', 'cardio', 'full_body', 'flexibility', 'full_body', 'cardio', 'rest'];
    } else if (workoutPlan.training_split === 'upper_lower') {
      workoutTypes = ['upper_body', 'lower_body', 'rest', 'upper_body', 'lower_body', 'cardio', 'rest'];
    } else if (workoutPlan.training_split === 'push_pull_legs') {
      workoutTypes = ['push', 'pull', 'legs', 'rest', 'push', 'pull', 'rest'];
    } else if (workoutPlan.training_split === 'body_part_split') {
      workoutTypes = ['chest', 'back', 'legs', 'shoulders', 'arms', 'cardio', 'rest'];
    } else {
      // Default: Mix of strength and cardio
      workoutTypes = ['strength', 'cardio', 'strength', 'flexibility', 'strength', 'cardio', 'rest'];
    }
    
    days.forEach((day, index) => {
      if (index < workoutPlan.days_per_week!) {
        const workoutType = workoutTypes[index];
        let dayExercises: Exercise[] = [];
        
        switch (workoutType) {
          case 'full_body':
            dayExercises = [
              ...strengthExercises.slice(0, 2),
              ...cardioExercises.slice(0, 1),
              ...flexibilityExercises.slice(0, 1)
            ];
            break;
          case 'strength':
            dayExercises = strengthExercises.slice(0, 4);
            break;
          case 'cardio':
            dayExercises = cardioExercises.slice(0, 3);
            break;
          case 'flexibility':
            dayExercises = flexibilityExercises.slice(0, 4);
            break;
          case 'upper_body':
            dayExercises = strengthExercises.filter(e => 
              e.muscles.some(muscle => ['chest', 'triceps', 'shoulders', 'biceps'].includes(muscle))
            ).slice(0, 4);
            break;
          case 'lower_body':
            dayExercises = strengthExercises.filter(e => 
              e.muscles.some(muscle => ['quads', 'glutes', 'hamstrings', 'calves'].includes(muscle))
            ).slice(0, 4);
            break;
          case 'push':
            dayExercises = strengthExercises.filter(e => 
              e.muscles.some(muscle => ['chest', 'triceps', 'shoulders'].includes(muscle))
            ).slice(0, 4);
            break;
          case 'pull':
            dayExercises = strengthExercises.filter(e => 
              e.muscles.some(muscle => ['back', 'biceps'].includes(muscle))
            ).slice(0, 4);
            break;
          case 'legs':
            dayExercises = strengthExercises.filter(e => 
              e.muscles.some(muscle => ['quads', 'glutes', 'hamstrings', 'calves'].includes(muscle))
            ).slice(0, 4);
            break;
          case 'chest':
            dayExercises = strengthExercises.filter(e => 
              e.muscles.includes('chest')
            ).slice(0, 3);
            break;
          case 'back':
            dayExercises = strengthExercises.filter(e => 
              e.muscles.includes('back')
            ).slice(0, 3);
            break;
          case 'shoulders':
            dayExercises = strengthExercises.filter(e => 
              e.muscles.includes('shoulders')
            ).slice(0, 3);
            break;
          case 'arms':
            dayExercises = strengthExercises.filter(e => 
              e.muscles.some(muscle => ['biceps', 'triceps'].includes(muscle))
            ).slice(0, 3);
            break;
          default:
            dayExercises = strengthExercises.slice(0, 3);
        }
        
        schedule[day] = {
          type: workoutType,
          exercises: dayExercises,
          duration: workoutPlan.session_duration
        };
      } else {
        schedule[day] = {
          type: 'rest',
          exercises: [],
          duration: 0
        };
      }
    });
    
    return schedule;
  };

  const renderStep1 = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Choose Your Fitness Level</h2>
        <p className="text-gray-600">This helps us create the perfect workout plan for you</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {fitnessLevels.map((level) => {
          const Icon = level.icon;
          return (
            <button
              key={level.value}
              onClick={() => setWorkoutPlan(prev => ({ ...prev, fitness_level: level.value as any }))}
              className={`p-6 rounded-xl border-2 transition-all ${
                workoutPlan.fitness_level === level.value
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <Icon className="w-8 h-8 mx-auto mb-3 text-blue-600" />
              <h3 className="font-semibold text-gray-900 mb-2">{level.label}</h3>
              <p className="text-sm text-gray-600">{level.description}</p>
            </button>
          );
        })}
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Select Your Workout Environment</h2>
        <p className="text-gray-600">Where will you be working out most often?</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {environments.map((env) => {
          const Icon = env.icon;
          return (
            <button
              key={env.value}
              onClick={() => setWorkoutPlan(prev => ({ ...prev, environment: env.value as any }))}
              className={`p-6 rounded-xl border-2 transition-all ${
                workoutPlan.environment === env.value
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <Icon className="w-8 h-8 mx-auto mb-3 text-blue-600" />
              <h3 className="font-semibold text-gray-900 mb-2">{env.label}</h3>
              <p className="text-sm text-gray-600">{env.description}</p>
            </button>
          );
        })}
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Set Your Goals & Preferences</h2>
        <p className="text-gray-600">What do you want to achieve with your workouts?</p>
      </div>
      
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Workout Goals</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {workoutGoals.map((goal) => {
              const Icon = goal.icon;
              const isSelected = workoutPlan.goals?.includes(goal.id);
              return (
                <button
                  key={goal.id}
                  onClick={() => handleGoalToggle(goal.id)}
                  className={`p-4 rounded-lg border-2 transition-all flex items-center space-x-3 ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-5 h-5 text-blue-600" />
                  <span className="font-medium text-gray-900">{goal.label}</span>
                </button>
              );
            })}
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Duration (weeks)
            </label>
            <select
              value={workoutPlan.duration_weeks}
              onChange={(e) => setWorkoutPlan(prev => ({ ...prev, duration_weeks: parseInt(e.target.value) }))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={4}>4 weeks</option>
              <option value={8}>8 weeks</option>
              <option value={12}>12 weeks</option>
              <option value={16}>16 weeks</option>
              <option value={20}>20 weeks</option>
              <option value={24}>24 weeks</option>
              <option value={32}>32 weeks</option>
              <option value={40}>40 weeks</option>
              <option value={48}>48 weeks</option>
              <option value={52}>52 weeks</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Days per week
            </label>
            <select
              value={workoutPlan.days_per_week}
              onChange={(e) => setWorkoutPlan(prev => ({ ...prev, days_per_week: parseInt(e.target.value) }))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={2}>2 days</option>
              <option value={3}>3 days</option>
              <option value={4}>4 days</option>
              <option value={5}>5 days</option>
              <option value={6}>6 days</option>
              <option value={7}>7 days</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Session duration (minutes)
            </label>
            <select
              value={workoutPlan.session_duration}
              onChange={(e) => setWorkoutPlan(prev => ({ ...prev, session_duration: parseInt(e.target.value) }))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={15}>15 minutes</option>
              <option value={20}>20 minutes</option>
              <option value={30}>30 minutes</option>
              <option value={45}>45 minutes</option>
              <option value={60}>60 minutes</option>
              <option value={75}>75 minutes</option>
              <option value={90}>90 minutes</option>
              <option value={105}>105 minutes</option>
              <option value={120}>120 minutes</option>
              <option value={150}>150 minutes</option>
              <option value={180}>180 minutes</option>
              <option value={210}>210 minutes</option>
              <option value={240}>240 minutes</option>
            </select>
          </div>
        </div>
        
        {/* Additional Questions for Intermediate and Advanced Users */}
        {workoutPlan.fitness_level !== 'beginner' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">Advanced Preferences</h3>
            
            {/* Training Split Preference */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Training Split Preference
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {[
                  { value: 'full_body', label: 'Full Body', description: 'Work all muscle groups each session' },
                  { value: 'upper_lower', label: 'Upper/Lower Split', description: 'Alternate between upper and lower body' },
                  { value: 'push_pull_legs', label: 'Push/Pull/Legs', description: 'Push muscles, pull muscles, and legs' },
                  { value: 'body_part_split', label: 'Body Part Split', description: 'Focus on specific muscle groups per day' }
                ].map((split) => (
                  <button
                    key={split.value}
                    onClick={() => setWorkoutPlan(prev => ({ ...prev, training_split: split.value }))}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${
                      workoutPlan.training_split === split.value
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <h4 className="font-medium text-gray-900">{split.label}</h4>
                    <p className="text-sm text-gray-600">{split.description}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Intensity Preference */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Workout Intensity Preference
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {[
                  { value: 'low', label: 'Low Intensity', description: 'Steady pace, longer duration' },
                  { value: 'moderate', label: 'Moderate Intensity', description: 'Balanced effort and recovery' },
                  { value: 'high', label: 'High Intensity', description: 'Maximum effort, shorter duration' }
                ].map((intensity) => (
                  <button
                    key={intensity.value}
                    onClick={() => setWorkoutPlan(prev => ({ ...prev, intensity_preference: intensity.value }))}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${
                      workoutPlan.intensity_preference === intensity.value
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <h4 className="font-medium text-gray-900">{intensity.label}</h4>
                    <p className="text-sm text-gray-600">{intensity.description}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Rest Day Preference */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rest Day Preference
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {[
                  { value: 'active_recovery', label: 'Active Recovery', description: 'Light activities on rest days' },
                  { value: 'complete_rest', label: 'Complete Rest', description: 'No physical activity on rest days' },
                  { value: 'flexible', label: 'Flexible', description: 'Mix of active and complete rest' }
                ].map((rest) => (
                  <button
                    key={rest.value}
                    onClick={() => setWorkoutPlan(prev => ({ ...prev, rest_preference: rest.value }))}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${
                      workoutPlan.rest_preference === rest.value
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <h4 className="font-medium text-gray-900">{rest.label}</h4>
                    <p className="text-sm text-gray-600">{rest.description}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Progression Preference */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Progression Style
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {[
                  { value: 'linear', label: 'Linear Progression', description: 'Gradual increase in weight/reps' },
                  { value: 'periodized', label: 'Periodized', description: 'Structured phases of training' },
                  { value: 'undulating', label: 'Undulating', description: 'Varied intensity throughout the week' },
                  { value: 'autoregulated', label: 'Auto-regulated', description: 'Based on daily performance' }
                ].map((progression) => (
                  <button
                    key={progression.value}
                    onClick={() => setWorkoutPlan(prev => ({ ...prev, progression_style: progression.value }))}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${
                      workoutPlan.progression_style === progression.value
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <h4 className="font-medium text-gray-900">{progression.label}</h4>
                    <p className="text-sm text-gray-600">{progression.description}</p>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {workoutPlan.fitness_level === 'beginner' 
              ? 'Recommended Exercises (Auto-selected)' 
              : 'Select Exercises'
            }
          </h3>
          
          {workoutPlan.fitness_level === 'beginner' ? (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <div className="flex items-center space-x-2">
                <Zap className="w-5 h-5 text-blue-600" />
                <p className="text-blue-800 font-medium">
                  For beginners, we'll automatically select the best exercises based on your goals and environment.
                </p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-64 overflow-y-auto">
              {availableExercises.map((exercise) => {
                const isSelected = selectedExercises.find(e => e.id === exercise.id);
                return (
                  <button
                    key={exercise.id}
                    onClick={() => handleExerciseToggle(exercise)}
                    className={`p-4 rounded-lg border-2 transition-all text-left ${
                      isSelected
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900">{exercise.name}</h4>
                        <p className="text-sm text-gray-600 capitalize">
                          {exercise.category} • {exercise.difficulty} • {exercise.equipment}
                        </p>
                      </div>
                      {isSelected && <CheckCircle className="w-5 h-5 text-blue-600" />}
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Your Workout Plan is Ready!</h2>
        <p className="text-gray-600">Here's your personalized workout plan</p>
      </div>
      
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-gray-900">{workoutPlan.name}</h3>
          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
            {workoutPlan.fitness_level?.charAt(0).toUpperCase()}{workoutPlan.fitness_level?.slice(1)}
          </span>
        </div>
        
        <p className="text-gray-600 mb-4">{workoutPlan.description}</p>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{workoutPlan.duration_weeks}</div>
            <div className="text-sm text-gray-600">Weeks</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{workoutPlan.days_per_week}</div>
            <div className="text-sm text-gray-600">Days/Week</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{workoutPlan.session_duration}</div>
            <div className="text-sm text-gray-600">Minutes</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{selectedExercises.length}</div>
            <div className="text-sm text-gray-600">Exercises</div>
          </div>
        </div>
        
        <div className="space-y-4">
          <h4 className="font-semibold text-gray-900">Weekly Schedule</h4>
          {Object.entries(workoutPlan.schedule || {}).map(([day, schedule]) => (
            <div key={day} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium text-gray-900 capitalize">{day}</span>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">
                  {schedule.type === 'rest' ? 'Rest Day' : `${schedule.exercises.length} exercises`}
                </span>
                {schedule.type !== 'rest' && (
                  <span className="text-sm text-gray-500">• {schedule.duration} min</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className={`bg-white rounded-xl border border-gray-200 p-6 ${className}`}>
      {/* Progress Steps */}
      <div className="flex items-center justify-center mb-8">
        {[1, 2, 3, 4].map((step) => (
          <div key={step} className="flex items-center">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step <= currentStep
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-600'
              }`}
            >
              {step}
            </div>
            {step < 4 && (
              <div
                className={`w-16 h-1 mx-2 ${
                  step < currentStep ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step Content */}
      <div className="min-h-[400px]">
        {currentStep === 1 && renderStep1()}
        {currentStep === 2 && renderStep2()}
        {currentStep === 3 && renderStep3()}
        {currentStep === 4 && renderStep4()}
      </div>

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between mt-8">
        <button
          onClick={() => setCurrentStep(prev => Math.max(1, prev - 1))}
          disabled={currentStep === 1}
          className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        
        <div className="flex space-x-3">
          {currentStep < 3 && (
            <button
              onClick={() => setCurrentStep(prev => prev + 1)}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Next
            </button>
          )}
          
          {currentStep === 3 && (
            <button
              onClick={generateWorkoutPlan}
              disabled={isGenerating || (workoutPlan.fitness_level !== 'beginner' && selectedExercises.length === 0)}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isGenerating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  <span>Generate Plan</span>
                </>
              )}
            </button>
          )}
          
          {currentStep === 4 && (
            <button
              onClick={() => {
                onPlanCreated?.(workoutPlan as WorkoutPlan);
                setCurrentStep(1);
                setWorkoutPlan({
                  fitness_level: 'beginner',
                  environment: 'home',
                  duration_weeks: 8,
                  days_per_week: 3,
                  session_duration: 45,
                  goals: [],
                  exercises: []
                });
                setSelectedExercises([]);
              }}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Start Workout Plan
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default WorkoutPlanner;
