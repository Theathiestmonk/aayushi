"""
Progress tracking endpoints for the AI Dietitian Agent System
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.core.database import get_supabase_client
from app.core.security import get_current_user

router = APIRouter()

class MealTracking(BaseModel):
    id: str
    user_id: str
    date: date
    meal_type: str
    meal_name: Optional[str] = None
    calories_consumed: Optional[int] = None
    protein_g: Optional[int] = None
    carbs_g: Optional[int] = None
    fat_g: Optional[int] = None
    compliance_score: Optional[float] = None

class WorkoutTracking(BaseModel):
    id: str
    user_id: str
    date: date
    workout_name: Optional[str] = None
    workout_type: Optional[str] = None
    duration_minutes: Optional[int] = None
    calories_burned: Optional[int] = None
    compliance_score: Optional[float] = None

class CreateMealTracking(BaseModel):
    meal_type: str
    meal_name: Optional[str] = None
    calories_consumed: Optional[int] = None
    protein_g: Optional[int] = None
    carbs_g: Optional[int] = None
    fat_g: Optional[int] = None

class CreateWorkoutTracking(BaseModel):
    workout_name: Optional[str] = None
    workout_type: Optional[str] = None
    duration_minutes: Optional[int] = None
    calories_burned: Optional[int] = None

# Health Metrics Models
class DailyHealthMetrics(BaseModel):
    id: str
    user_id: str
    date: date
    steps_today: int = 0
    steps_goal: int = 0
    sleep_hours: float = 0.0
    sleep_goal: float = 0.0
    sleep_quality: Optional[int] = None
    water_intake_l: float = 0.0
    water_goal_l: float = 0.0
    calories_eaten: int = 0
    calories_goal: int = 0
    calories_burned: int = 0
    carbs_g: float = 0.0
    carbs_goal: float = 0.0
    protein_g: float = 0.0
    protein_goal: float = 0.0
    fat_g: float = 0.0
    fat_goal: float = 0.0
    weight_kg: Optional[float] = None
    target_weight_kg: Optional[float] = None
    created_at: datetime
    updated_at: datetime

class UpdateHealthMetrics(BaseModel):
    steps_today: Optional[int] = None
    steps_goal: Optional[int] = None
    sleep_hours: Optional[float] = None
    sleep_goal: Optional[float] = None
    sleep_quality: Optional[int] = None
    water_intake_l: Optional[float] = None
    water_goal_l: Optional[float] = None
    calories_eaten: Optional[int] = None
    calories_goal: Optional[int] = None
    calories_burned: Optional[int] = None
    carbs_g: Optional[float] = None
    carbs_goal: Optional[float] = None
    protein_g: Optional[float] = None
    protein_goal: Optional[float] = None
    fat_g: Optional[float] = None
    fat_goal: Optional[float] = None
    weight_kg: Optional[float] = None
    target_weight_kg: Optional[float] = None

class HealthMetricsResponse(BaseModel):
    success: bool
    data: Optional[DailyHealthMetrics] = None
    message: Optional[str] = None

@router.get("/meals", response_model=List[MealTracking])
async def get_meal_tracking():
    """Get meal tracking data for current user"""
    # TODO: Implement actual meal tracking retrieval
    return [
        MealTracking(
            id="meal_123",
            user_id="user_123",
            date=date.today(),
            meal_type="breakfast",
            meal_name="Oatmeal with berries",
            calories_consumed=300,
            protein_g=12,
            carbs_g=45,
            fat_g=8,
            compliance_score=0.9
        )
    ]

@router.get("/workouts", response_model=List[WorkoutTracking])
async def get_workout_tracking():
    """Get workout tracking data for current user"""
    # TODO: Implement actual workout tracking retrieval
    return [
        WorkoutTracking(
            id="workout_123",
            user_id="user_123",
            date=date.today(),
            workout_name="Morning Cardio",
            workout_type="cardio",
            duration_minutes=30,
            calories_burned=250,
            compliance_score=0.8
        )
    ]

@router.post("/meals", response_model=MealTracking)
async def create_meal_tracking(meal_data: CreateMealTracking):
    """Log a meal"""
    # TODO: Implement actual meal tracking creation
    return MealTracking(
        id="new_meal_123",
        user_id="user_123",
        date=date.today(),
        meal_type=meal_data.meal_type,
        meal_name=meal_data.meal_name,
        calories_consumed=meal_data.calories_consumed,
        protein_g=meal_data.protein_g,
        carbs_g=meal_data.carbs_g,
        fat_g=meal_data.fat_g
    )

@router.post("/workouts", response_model=WorkoutTracking)
async def create_workout_tracking(workout_data: CreateWorkoutTracking):
    """Log a workout"""
    # TODO: Implement actual workout tracking creation
    return WorkoutTracking(
        id="new_workout_123",
        user_id="user_123",
        date=date.today(),
        workout_name=workout_data.workout_name,
        workout_type=workout_data.workout_type,
        duration_minutes=workout_data.duration_minutes,
        calories_burned=workout_data.calories_burned
    )

@router.get("/progress")
async def get_progress_summary():
    """Get progress summary for current user"""
    # TODO: Implement actual progress calculation
    return {
        "date": date.today().isoformat(),
        "total_calories_consumed": 1500,
        "total_calories_burned": 250,
        "net_calories": 1250,
        "diet_compliance": 0.85,
        "workout_compliance": 0.80,
        "overall_score": 0.83
    }

@router.get("/weekly-report")
async def get_weekly_report():
    """Get weekly progress report"""
    # TODO: Implement actual weekly report generation
    return {
        "week_start": "2024-01-01",
        "week_end": "2024-01-07",
        "total_calories_consumed": 10500,
        "total_calories_burned": 1750,
        "net_calories": 8750,
        "average_diet_compliance": 0.87,
        "average_workout_compliance": 0.82,
        "weight_change_kg": -0.5
    }

# Health Metrics Endpoints
@router.get("/health-metrics", response_model=HealthMetricsResponse)
async def get_health_metrics(
    target_date: Optional[date] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get daily health metrics for the current user"""
    try:
        client = get_supabase_client()
        user_id = current_user.get("id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Use today's date if no date specified
        if not target_date:
            target_date = date.today()

        # First: try most recent record within last 24 hours
        window_start_iso = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        response = client.table("daily_health_metrics")\
            .select("*")\
            .eq("user_id", user_id)\
            .gte("updated_at", window_start_iso)\
            .order("updated_at", desc=True)\
            .limit(1)\
            .execute()
        
        if response.data:
            metrics_data = response.data[0]
            return HealthMetricsResponse(
                success=True,
                data=DailyHealthMetrics(**metrics_data),
                message="Health metrics retrieved successfully"
            )
        else:
            # Second: try today's date row
            today_resp = client.table("daily_health_metrics")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("date", target_date.isoformat())\
                .limit(1)\
                .execute()

            if today_resp.data:
                metrics_data = today_resp.data[0]
                return HealthMetricsResponse(
                    success=True,
                    data=DailyHealthMetrics(**metrics_data),
                    message="Health metrics for today"
                )

            # Otherwise auto-create zero-initialized record for this user/date
            zero_data = {
                "user_id": user_id,
                "date": target_date.isoformat(),
                "steps_today": 0,
                "steps_goal": 0,
                "sleep_hours": 0,
                "sleep_goal": 0,
                "sleep_quality": 0,
                "water_intake_l": 0,
                "water_goal_l": 0,
                "calories_eaten": 0,
                "calories_burned": 0,
                "calories_goal": 0,
                "carbs_g": 0,
                "carbs_goal": 0,
                "protein_g": 0,
                "protein_goal": 0,
                "fat_g": 0,
                "fat_goal": 0,
                "weight_kg": 0,
                "target_weight_kg": 0,
            }
            create_resp = client.table("daily_health_metrics").insert(zero_data).execute()
            created = create_resp.data[0] if create_resp.data else zero_data
            # Fetch again to include generated fields like id, timestamps
            return HealthMetricsResponse(
                success=True,
                data=DailyHealthMetrics(**created),
                message="Initialized daily health metrics with zeros"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch health metrics: {str(e)}")

@router.post("/health-metrics", response_model=HealthMetricsResponse)
async def create_or_update_health_metrics(
    metrics_data: UpdateHealthMetrics,
    target_date: Optional[date] = None,
    current_user: dict = Depends(get_current_user)
):
    """Create or update daily health metrics for the current user"""
    try:
        client = get_supabase_client()
        user_id = current_user.get("id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Use today's date if no date specified
        if not target_date:
            target_date = date.today()
        
        # Prepare data for upsert
        upsert_data = {
            "user_id": user_id,
            "date": target_date.isoformat(),
            **metrics_data.dict(exclude_unset=True)
        }
        
        # Upsert the data (insert or update)
        response = client.table("daily_health_metrics")\
            .upsert(upsert_data)\
            .execute()
        
        if response.data:
            metrics_data = response.data[0]
            return HealthMetricsResponse(
                success=True,
                data=DailyHealthMetrics(**metrics_data),
                message="Health metrics updated successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to save health metrics")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save health metrics: {str(e)}")

@router.get("/health-metrics/history", response_model=List[DailyHealthMetrics])
async def get_health_metrics_history(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get health metrics history for the current user"""
    try:
        client = get_supabase_client()
        user_id = current_user.get("id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Set default date range if not provided
        if not start_date:
            start_date = date.today()
        if not end_date:
            end_date = start_date
        
        # Query the daily_health_metrics table
        query = client.table("daily_health_metrics")\
            .select("*")\
            .eq("user_id", user_id)\
            .gte("date", start_date.isoformat())\
            .lte("date", end_date.isoformat())\
            .order("date", desc=True)\
            .limit(limit)
        
        response = query.execute()
        
        if response.data:
            return [DailyHealthMetrics(**item) for item in response.data]
        else:
            return []
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch health metrics history: {str(e)}")





