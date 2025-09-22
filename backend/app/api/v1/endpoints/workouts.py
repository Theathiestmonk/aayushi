"""
Workout-specific API endpoints for the AI Dietitian Agent System
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import logging

from app.core.database import get_db
from app.agents.workout_planner_agent import WorkoutPlannerAgent

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models
class Exercise(BaseModel):
    id: str
    name: str
    category: str  # strength, cardio, flexibility
    difficulty: str  # beginner, intermediate, advanced
    equipment: str
    muscles: List[str]
    instructions: List[str]
    duration: Optional[int] = None
    reps: Optional[int] = None
    sets: Optional[int] = None
    rest_time: Optional[int] = None

class WorkoutPlan(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    fitness_level: str
    environment: str
    duration_weeks: int
    days_per_week: int
    session_duration: int
    goals: List[str]
    exercises: List[Exercise]
    schedule: Dict[str, Any]
    created_at: str
    updated_at: Optional[str] = None

class WorkoutSession(BaseModel):
    id: str
    user_id: str
    workout_plan_id: Optional[str] = None
    name: str
    date: date
    start_time: str
    end_time: Optional[str] = None
    duration: int  # in seconds
    exercises: List[Dict[str, Any]]
    total_calories_burned: int
    status: str  # planned, in_progress, completed, paused
    notes: Optional[str] = None

class CreateWorkoutPlan(BaseModel):
    name: str
    description: str
    fitness_level: str
    environment: str
    duration_weeks: int
    days_per_week: int
    session_duration: int
    goals: List[str]
    exercises: List[Exercise]

class CreateWorkoutSession(BaseModel):
    workout_plan_id: Optional[str] = None
    name: str
    exercises: List[Dict[str, Any]]
    notes: Optional[str] = None

class UpdateWorkoutSession(BaseModel):
    exercises: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = None
    notes: Optional[str] = None

# Initialize workout planner agent
workout_planner = WorkoutPlannerAgent()

@router.get("/exercises", response_model=List[Exercise])
async def get_exercises(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    equipment: Optional[str] = None,
    limit: int = 50
):
    """Get available exercises with optional filtering"""
    try:
        # Get exercises from the workout planner agent
        exercises = []
        
        # Sample exercises database
        sample_exercises = [
            {
                "id": "push_ups",
                "name": "Push-ups",
                "category": "strength",
                "difficulty": "beginner",
                "equipment": "none",
                "muscles": ["chest", "triceps", "shoulders"],
                "instructions": [
                    "Start in plank position",
                    "Lower body until chest nearly touches floor",
                    "Push back up to starting position"
                ],
                "reps": 10,
                "sets": 3,
                "rest_time": 60
            },
            {
                "id": "squats",
                "name": "Squats",
                "category": "strength",
                "difficulty": "beginner",
                "equipment": "none",
                "muscles": ["quads", "glutes", "hamstrings"],
                "instructions": [
                    "Stand with feet shoulder-width apart",
                    "Lower body as if sitting back into chair",
                    "Return to standing position"
                ],
                "reps": 15,
                "sets": 3,
                "rest_time": 60
            },
            {
                "id": "planks",
                "name": "Planks",
                "category": "strength",
                "difficulty": "beginner",
                "equipment": "none",
                "muscles": ["abs", "core"],
                "instructions": [
                    "Start in push-up position",
                    "Hold body in straight line",
                    "Engage core throughout"
                ],
                "duration": 30,
                "sets": 3,
                "rest_time": 60
            },
            {
                "id": "jumping_jacks",
                "name": "Jumping Jacks",
                "category": "cardio",
                "difficulty": "beginner",
                "equipment": "none",
                "muscles": ["full_body"],
                "instructions": [
                    "Stand with feet together",
                    "Jump while spreading legs and raising arms",
                    "Return to starting position"
                ],
                "duration": 60,
                "sets": 3,
                "rest_time": 30
            },
            {
                "id": "burpees",
                "name": "Burpees",
                "category": "cardio",
                "difficulty": "intermediate",
                "equipment": "none",
                "muscles": ["full_body"],
                "instructions": [
                    "Start standing",
                    "Drop to push-up position",
                    "Do push-up",
                    "Jump feet to hands",
                    "Jump up with arms overhead"
                ],
                "reps": 8,
                "sets": 3,
                "rest_time": 90
            },
            {
                "id": "hamstring_stretch",
                "name": "Hamstring Stretch",
                "category": "flexibility",
                "difficulty": "beginner",
                "equipment": "none",
                "muscles": ["hamstrings"],
                "instructions": [
                    "Sit with legs extended",
                    "Reach forward toward toes",
                    "Hold stretch without bouncing"
                ],
                "duration": 30,
                "sets": 2,
                "rest_time": 30
            }
        ]
        
        # Apply filters
        filtered_exercises = sample_exercises
        
        if category:
            filtered_exercises = [ex for ex in filtered_exercises if ex["category"] == category]
        
        if difficulty:
            filtered_exercises = [ex for ex in filtered_exercises if ex["difficulty"] == difficulty]
        
        if equipment:
            filtered_exercises = [ex for ex in filtered_exercises if ex["equipment"] == equipment]
        
        # Limit results
        filtered_exercises = filtered_exercises[:limit]
        
        return [Exercise(**exercise) for exercise in filtered_exercises]
        
    except Exception as e:
        logger.error(f"Failed to get exercises: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve exercises")

@router.post("/workout-planner", response_model=WorkoutPlan)
async def create_workout_plan(
    plan_data: CreateWorkoutPlan,
    user_id: str = "demo_user"  # In real implementation, get from auth
):
    """Create a personalized workout plan using the workout planner agent"""
    try:
        # Prepare user data for the agent
        user_data = {
            "user_id": user_id,
            "fitness_level": plan_data.fitness_level,
            "workout_environment": plan_data.environment,
            "workout_goals": plan_data.goals,
            "preferred_duration": plan_data.session_duration,
            "days_per_week": plan_data.days_per_week
        }
        
        # Use the workout planner agent to create a plan
        state = {"user_data": user_data}
        result = await workout_planner.process(state)
        
        if "workout_plan" in result:
            workout_plan_data = result["workout_plan"]
            
            # Create the workout plan response
            workout_plan = WorkoutPlan(
                id=f"workout_{user_id}_{int(datetime.utcnow().timestamp())}",
                user_id=user_id,
                name=plan_data.name,
                description=plan_data.description,
                fitness_level=plan_data.fitness_level,
                environment=plan_data.environment,
                duration_weeks=plan_data.duration_weeks,
                days_per_week=plan_data.days_per_week,
                session_duration=plan_data.session_duration,
                goals=plan_data.goals,
                exercises=plan_data.exercises,
                schedule=workout_plan_data.get("schedule", {}),
                created_at=datetime.utcnow().isoformat()
            )
            
            return workout_plan
        else:
            raise HTTPException(status_code=500, detail="Failed to generate workout plan")
            
    except Exception as e:
        logger.error(f"Failed to create workout plan: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create workout plan")

@router.get("/workout-plans", response_model=List[WorkoutPlan])
async def get_workout_plans(
    user_id: str = "demo_user",  # In real implementation, get from auth
    limit: int = 20
):
    """Get workout plans for a user"""
    try:
        # In real implementation, fetch from database
        # For now, return empty list
        return []
        
    except Exception as e:
        logger.error(f"Failed to get workout plans: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve workout plans")

@router.get("/workout-plans/{plan_id}", response_model=WorkoutPlan)
async def get_workout_plan(
    plan_id: str,
    user_id: str = "demo_user"  # In real implementation, get from auth
):
    """Get a specific workout plan"""
    try:
        # In real implementation, fetch from database
        raise HTTPException(status_code=404, detail="Workout plan not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workout plan: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve workout plan")

@router.post("/workout-sessions", response_model=WorkoutSession)
async def create_workout_session(
    session_data: CreateWorkoutSession,
    user_id: str = "demo_user"  # In real implementation, get from auth
):
    """Create a new workout session"""
    try:
        session = WorkoutSession(
            id=f"session_{user_id}_{int(datetime.utcnow().timestamp())}",
            user_id=user_id,
            workout_plan_id=session_data.workout_plan_id,
            name=session_data.name,
            date=date.today(),
            start_time=datetime.utcnow().isoformat(),
            duration=0,
            exercises=session_data.exercises,
            total_calories_burned=0,
            status="planned",
            notes=session_data.notes
        )
        
        # In real implementation, save to database
        return session
        
    except Exception as e:
        logger.error(f"Failed to create workout session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create workout session")

@router.get("/workout-sessions", response_model=List[WorkoutSession])
async def get_workout_sessions(
    user_id: str = "demo_user",  # In real implementation, get from auth
    limit: int = 20,
    status: Optional[str] = None
):
    """Get workout sessions for a user"""
    try:
        # In real implementation, fetch from database
        # For now, return sample data
        sample_sessions = [
            WorkoutSession(
                id="session_1",
                user_id=user_id,
                name="Upper Body Strength",
                date=date.today(),
                start_time=datetime.utcnow().isoformat(),
                duration=1800,  # 30 minutes
                exercises=[],
                total_calories_burned=250,
                status="completed"
            )
        ]
        
        if status:
            sample_sessions = [s for s in sample_sessions if s.status == status]
        
        return sample_sessions[:limit]
        
    except Exception as e:
        logger.error(f"Failed to get workout sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve workout sessions")

@router.put("/workout-sessions/{session_id}", response_model=WorkoutSession)
async def update_workout_session(
    session_id: str,
    update_data: UpdateWorkoutSession,
    user_id: str = "demo_user"  # In real implementation, get from auth
):
    """Update a workout session"""
    try:
        # In real implementation, fetch from database and update
        # For now, return a mock updated session
        session = WorkoutSession(
            id=session_id,
            user_id=user_id,
            name="Updated Workout",
            date=date.today(),
            start_time=datetime.utcnow().isoformat(),
            duration=1800,
            exercises=update_data.exercises or [],
            total_calories_burned=250,
            status=update_data.status or "in_progress",
            notes=update_data.notes
        )
        
        return session
        
    except Exception as e:
        logger.error(f"Failed to update workout session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update workout session")

@router.get("/workout-sessions/{session_id}", response_model=WorkoutSession)
async def get_workout_session(
    session_id: str,
    user_id: str = "demo_user"  # In real implementation, get from auth
):
    """Get a specific workout session"""
    try:
        # In real implementation, fetch from database
        raise HTTPException(status_code=404, detail="Workout session not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workout session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve workout session")

@router.get("/stats")
async def get_workout_stats(
    user_id: str = "demo_user"  # In real implementation, get from auth
):
    """Get workout statistics for a user"""
    try:
        # In real implementation, calculate from database
        stats = {
            "total_workouts": 24,
            "total_duration": 1800,  # 30 hours in seconds
            "total_calories_burned": 12000,
            "current_streak": 7,
            "weekly_goal": 5,
            "weekly_progress": 3,
            "favorite_exercise": "Push-ups",
            "improvement_areas": ["Consistency", "Endurance"],
            "average_session_duration": 45,  # minutes
            "most_active_day": "Monday",
            "longest_streak": 14,
            "total_exercises_completed": 156
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get workout stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve workout statistics")

@router.get("/progress")
async def get_workout_progress(
    user_id: str = "demo_user",  # In real implementation, get from auth
    days: int = 30
):
    """Get workout progress over time"""
    try:
        # In real implementation, calculate from database
        progress_data = {
            "period_days": days,
            "total_workouts": 12,
            "total_duration": 900,  # 15 hours
            "total_calories_burned": 6000,
            "average_daily_workouts": 0.4,
            "consistency_score": 0.8,
            "progress_trend": "increasing",
            "weekly_data": [
                {"week": "Week 1", "workouts": 3, "duration": 180, "calories": 1200},
                {"week": "Week 2", "workouts": 4, "duration": 240, "calories": 1600},
                {"week": "Week 3", "workouts": 3, "duration": 200, "calories": 1400},
                {"week": "Week 4", "workouts": 2, "duration": 120, "calories": 800}
            ]
        }
        
        return progress_data
        
    except Exception as e:
        logger.error(f"Failed to get workout progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve workout progress")

@router.delete("/workout-sessions/{session_id}")
async def delete_workout_session(
    session_id: str,
    user_id: str = "demo_user"  # In real implementation, get from auth
):
    """Delete a workout session"""
    try:
        # In real implementation, delete from database
        return {"message": "Workout session deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete workout session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete workout session")
