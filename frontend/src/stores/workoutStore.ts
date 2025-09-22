import { create } from 'zustand';
import { persist } from 'zustand/middleware';

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
  updated_at?: string;
  is_active?: boolean;
}

interface WorkoutSession {
  id: string;
  workout_plan_id?: string;
  name: string;
  date: string;
  start_time: string;
  end_time?: string;
  duration: number;
  exercises: any[];
  total_calories_burned: number;
  status: 'planned' | 'in_progress' | 'completed' | 'paused';
  notes?: string;
}

interface WorkoutStore {
  // Workout Plans
  workoutPlans: WorkoutPlan[];
  activeWorkoutPlan: WorkoutPlan | null;
  
  // Workout Sessions
  workoutSessions: WorkoutSession[];
  currentSession: WorkoutSession | null;
  
  // Actions for Workout Plans
  addWorkoutPlan: (plan: WorkoutPlan) => void;
  updateWorkoutPlan: (id: string, updates: Partial<WorkoutPlan>) => void;
  deleteWorkoutPlan: (id: string) => void;
  setActiveWorkoutPlan: (plan: WorkoutPlan | null) => void;
  getWorkoutPlanById: (id: string) => WorkoutPlan | undefined;
  
  // Actions for Workout Sessions
  addWorkoutSession: (session: WorkoutSession) => void;
  updateWorkoutSession: (id: string, updates: Partial<WorkoutSession>) => void;
  deleteWorkoutSession: (id: string) => void;
  setCurrentSession: (session: WorkoutSession | null) => void;
  getWorkoutSessionById: (id: string) => WorkoutSession | undefined;
  
  // Utility functions
  getPlansByFitnessLevel: (level: string) => WorkoutPlan[];
  getRecentSessions: (limit?: number) => WorkoutSession[];
  getSessionsByPlan: (planId: string) => WorkoutSession[];
}

export const useWorkoutStore = create<WorkoutStore>()(
  persist(
    (set, get) => ({
      // Initial state
      workoutPlans: [],
      activeWorkoutPlan: null,
      workoutSessions: [],
      currentSession: null,

      // Workout Plan Actions
      addWorkoutPlan: (plan: WorkoutPlan) => {
        set((state) => ({
          workoutPlans: [plan, ...state.workoutPlans],
          activeWorkoutPlan: plan
        }));
      },

      updateWorkoutPlan: (id: string, updates: Partial<WorkoutPlan>) => {
        set((state) => ({
          workoutPlans: state.workoutPlans.map((plan) =>
            plan.id === id ? { ...plan, ...updates, updated_at: new Date().toISOString() } : plan
          ),
          activeWorkoutPlan: state.activeWorkoutPlan?.id === id 
            ? { ...state.activeWorkoutPlan, ...updates, updated_at: new Date().toISOString() }
            : state.activeWorkoutPlan
        }));
      },

      deleteWorkoutPlan: (id: string) => {
        set((state) => ({
          workoutPlans: state.workoutPlans.filter((plan) => plan.id !== id),
          activeWorkoutPlan: state.activeWorkoutPlan?.id === id ? null : state.activeWorkoutPlan
        }));
      },

      setActiveWorkoutPlan: (plan: WorkoutPlan | null) => {
        set({ activeWorkoutPlan: plan });
      },

      getWorkoutPlanById: (id: string) => {
        return get().workoutPlans.find((plan) => plan.id === id);
      },

      // Workout Session Actions
      addWorkoutSession: (session: WorkoutSession) => {
        set((state) => ({
          workoutSessions: [session, ...state.workoutSessions]
        }));
      },

      updateWorkoutSession: (id: string, updates: Partial<WorkoutSession>) => {
        set((state) => ({
          workoutSessions: state.workoutSessions.map((session) =>
            session.id === id ? { ...session, ...updates } : session
          ),
          currentSession: state.currentSession?.id === id 
            ? { ...state.currentSession, ...updates }
            : state.currentSession
        }));
      },

      deleteWorkoutSession: (id: string) => {
        set((state) => ({
          workoutSessions: state.workoutSessions.filter((session) => session.id !== id),
          currentSession: state.currentSession?.id === id ? null : state.currentSession
        }));
      },

      setCurrentSession: (session: WorkoutSession | null) => {
        set({ currentSession: session });
      },

      getWorkoutSessionById: (id: string) => {
        return get().workoutSessions.find((session) => session.id === id);
      },

      // Utility functions
      getPlansByFitnessLevel: (level: string) => {
        return get().workoutPlans.filter((plan) => plan.fitness_level === level);
      },

      getRecentSessions: (limit: number = 10) => {
        return get().workoutSessions
          .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
          .slice(0, limit);
      },

      getSessionsByPlan: (planId: string) => {
        return get().workoutSessions.filter((session) => session.workout_plan_id === planId);
      }
    }),
    {
      name: 'workout-storage',
      partialize: (state) => ({
        workoutPlans: state.workoutPlans,
        activeWorkoutPlan: state.activeWorkoutPlan,
        workoutSessions: state.workoutSessions
      })
    }
  )
);

export type { WorkoutPlan, WorkoutSession, Exercise };
