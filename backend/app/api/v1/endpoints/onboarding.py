"""
Onboarding endpoints for user profile creation and updates
Handles sensitive health and personal information with strict security measures
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, validator
import logging
from datetime import datetime

from app.api.v1.endpoints.auth import get_current_user, AuthResponse
from app.core.supabase import SupabaseManager

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Supabase manager
supabase_manager = SupabaseManager()

# Pydantic models for onboarding data
class BasicInformation(BaseModel):
    """Basic personal information"""
    full_name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=1, le=150)
    gender: str = Field(..., pattern="^(male|female|other)$")
    height_cm: float = Field(..., ge=50, le=300)
    weight_kg: float = Field(..., ge=20, le=500)
    contact_number: Optional[str] = Field(None, max_length=20)
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_number: Optional[str] = Field(None, max_length=20)
    occupation: str = Field(..., pattern="^(student|professional|homemaker|retired|other)$")
    occupation_other: Optional[str] = Field(None, max_length=100)

class MedicalHistory(BaseModel):
    """Medical and health history"""
    medical_conditions: List[str] = Field(default_factory=list)
    medications_supplements: List[str] = Field(default_factory=list)
    surgeries_hospitalizations: Optional[str] = Field(None, max_length=500)
    food_allergies: List[str] = Field(default_factory=list)
    family_history: List[str] = Field(default_factory=list)

class LifestyleHabits(BaseModel):
    """Lifestyle and daily habits"""
    daily_routine: str = Field(..., pattern="^(sedentary|moderately_active|highly_active)$")
    sleep_hours: str = Field(..., pattern="^(<5|5-6|7-8|>8)$")
    alcohol_consumption: bool = False
    alcohol_frequency: Optional[str] = Field(None, max_length=100)
    smoking: bool = False
    stress_level: str = Field(..., pattern="^(low|moderate|high)$")
    physical_activity_type: Optional[str] = Field(None, max_length=200)
    physical_activity_frequency: Optional[str] = Field(None, max_length=100)
    physical_activity_duration: Optional[str] = Field(None, max_length=100)

class EatingHabits(BaseModel):
    """Eating habits and preferences"""
    breakfast_habits: Optional[str] = Field(None, max_length=300)
    lunch_habits: Optional[str] = Field(None, max_length=300)
    dinner_habits: Optional[str] = Field(None, max_length=300)
    snacks_habits: Optional[str] = Field(None, max_length=300)
    beverages_habits: Optional[str] = Field(None, max_length=300)
    meal_timings: str = Field(..., pattern="^(regular|irregular)$")
    food_preference: str = Field(..., pattern="^(vegetarian|vegan|non_vegetarian|eggetarian)$")
    cultural_restrictions: Optional[str] = Field(None, max_length=300)
    eating_out_frequency: str = Field(..., pattern="^(rare|weekly|2-3_times_week|daily)$")
    daily_water_intake: str = Field(..., pattern="^(<1L|1-2L|2-3L|>3L)$")
    common_cravings: List[str] = Field(default_factory=list)

class GoalsExpectations(BaseModel):
    """Health goals and expectations"""
    primary_goals: List[str] = Field(default_factory=list)
    specific_health_concerns: Optional[str] = Field(None, max_length=500)
    past_diets: Optional[str] = Field(None, max_length=300)
    progress_pace: str = Field(..., pattern="^(gradual|moderate|aggressive)$")

class MeasurementsTracking(BaseModel):
    """Body measurements and tracking data"""
    current_weight_kg: Optional[float] = Field(None, ge=20, le=500)
    waist_circumference_cm: Optional[float] = Field(None, ge=30, le=200)
    bmi: Optional[float] = Field(None, ge=10, le=100)
    weight_trend: str = Field(..., pattern="^(increased|decreased|stable)$")
    blood_reports: List[str] = Field(default_factory=list)

class PersonalizationMotivation(BaseModel):
    """Personal preferences and motivation"""
    loved_foods: Optional[str] = Field(None, max_length=300)
    disliked_foods: Optional[str] = Field(None, max_length=300)
    cooking_facilities: List[str] = Field(default_factory=list)
    who_cooks: str = Field(..., pattern="^(self|family_member|cook_helper)$")
    budget_flexibility: str = Field(..., pattern="^(limited|flexible|high)$")
    motivation_level: int = Field(..., ge=1, le=10)
    support_system: str = Field(..., pattern="^(strong|moderate|weak)$")

class OnboardingData(BaseModel):
    """Complete onboarding data model"""
    basic_info: BasicInformation
    medical_history: MedicalHistory
    lifestyle_habits: LifestyleHabits
    eating_habits: EatingHabits
    goals_expectations: GoalsExpectations
    measurements_tracking: MeasurementsTracking
    personalization_motivation: PersonalizationMotivation

class OnboardingResponse(BaseModel):
    """Response model for onboarding operations"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/submit", response_model=OnboardingResponse, summary="Submit complete onboarding data")
async def submit_onboarding(
    onboarding_data: OnboardingData,
    request: Request,
    current_user: AuthResponse = Depends(get_current_user)
):
    """
    Submit complete onboarding data for user profile creation
    
    This endpoint handles sensitive health and personal information.
    All data is stored securely with Row Level Security (RLS) enabled.
    """
    try:
        # Extract user info from AuthResponse
        if not current_user.success or not current_user.data:
            raise HTTPException(status_code=401, detail="Invalid user session")
        
        user_id = current_user.data.get("id")
        email = current_user.data.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid user information")
        
        logger.info(f"🔐 Processing onboarding data for user: {email}")
        
        # Check if profile already exists
        existing_profile = await supabase_manager.get_user_profile(user_id)
        
        # Prepare profile data for database
        profile_data = {
            "id": user_id,
            "email": email,
            "onboarding_completed": True,
            "updated_at": datetime.utcnow().isoformat(),
            
            # Basic Information
            "full_name": onboarding_data.basic_info.full_name,
            "age": onboarding_data.basic_info.age,
            "gender": onboarding_data.basic_info.gender,
            "height_cm": onboarding_data.basic_info.height_cm,
            "weight_kg": onboarding_data.basic_info.weight_kg,
            "contact_number": onboarding_data.basic_info.contact_number,
            "emergency_contact_name": onboarding_data.basic_info.emergency_contact_name,
            "emergency_contact_number": onboarding_data.basic_info.emergency_contact_number,
            "occupation": onboarding_data.basic_info.occupation,
            "occupation_other": onboarding_data.basic_info.occupation_other,
            
            # Medical & Health History
            "medical_conditions": onboarding_data.medical_history.medical_conditions,
            "medications_supplements": onboarding_data.medical_history.medications_supplements,
            "surgeries_hospitalizations": onboarding_data.medical_history.surgeries_hospitalizations,
            "food_allergies": onboarding_data.medical_history.food_allergies,
            "family_history": onboarding_data.medical_history.family_history,
            
            # Lifestyle & Habits
            "daily_routine": onboarding_data.lifestyle_habits.daily_routine,
            "sleep_hours": onboarding_data.lifestyle_habits.sleep_hours,
            "alcohol_consumption": onboarding_data.lifestyle_habits.alcohol_consumption,
            "alcohol_frequency": onboarding_data.lifestyle_habits.alcohol_frequency,
            "smoking": onboarding_data.lifestyle_habits.smoking,
            "stress_level": onboarding_data.lifestyle_habits.stress_level,
            "physical_activity_type": onboarding_data.lifestyle_habits.physical_activity_type,
            "physical_activity_frequency": onboarding_data.lifestyle_habits.physical_activity_frequency,
            "physical_activity_duration": onboarding_data.lifestyle_habits.physical_activity_duration,
            
            # Eating Habits
            "breakfast_habits": onboarding_data.eating_habits.breakfast_habits,
            "lunch_habits": onboarding_data.eating_habits.lunch_habits,
            "dinner_habits": onboarding_data.eating_habits.dinner_habits,
            "snacks_habits": onboarding_data.eating_habits.snacks_habits,
            "beverages_habits": onboarding_data.eating_habits.beverages_habits,
            "meal_timings": onboarding_data.eating_habits.meal_timings,
            "food_preference": onboarding_data.eating_habits.food_preference,
            "cultural_restrictions": onboarding_data.eating_habits.cultural_restrictions,
            "eating_out_frequency": onboarding_data.eating_habits.eating_out_frequency,
            "daily_water_intake": onboarding_data.eating_habits.daily_water_intake,
            "common_cravings": onboarding_data.eating_habits.common_cravings,
            
            # Goals & Expectations
            "primary_goals": onboarding_data.goals_expectations.primary_goals,
            "specific_health_concerns": onboarding_data.goals_expectations.specific_health_concerns,
            "past_diets": onboarding_data.goals_expectations.past_diets,
            "progress_pace": onboarding_data.goals_expectations.progress_pace,
            
            # Measurements & Tracking
            "current_weight_kg": onboarding_data.measurements_tracking.current_weight_kg,
            "waist_circumference_cm": onboarding_data.measurements_tracking.waist_circumference_cm,
            "bmi": onboarding_data.measurements_tracking.bmi,
            "weight_trend": onboarding_data.measurements_tracking.weight_trend,
            "blood_reports": onboarding_data.measurements_tracking.blood_reports,
            
            # Personalization & Motivation
            "loved_foods": onboarding_data.personalization_motivation.loved_foods,
            "disliked_foods": onboarding_data.personalization_motivation.disliked_foods,
            "cooking_facilities": onboarding_data.personalization_motivation.cooking_facilities,
            "who_cooks": onboarding_data.personalization_motivation.who_cooks,
            "budget_flexibility": onboarding_data.personalization_motivation.budget_flexibility,
            "motivation_level": onboarding_data.personalization_motivation.motivation_level,
            "support_system": onboarding_data.personalization_motivation.support_system,
        }
        
        # Only add created_at for new profiles
        if not existing_profile["success"]:
            profile_data["created_at"] = datetime.utcnow().isoformat()
        
        # Store profile data in Supabase (create or update)
        result = await supabase_manager.upsert_user_profile(user_id, profile_data)
        
        if result["success"]:
            logger.info(f"✅ Onboarding completed successfully for user: {email}")
            
            # Log data access for audit trail
            operation_type = "update" if existing_profile["success"] else "create"
            await supabase_manager.log_profile_access(
                user_id, 
                operation_type, 
                str(request.client.host) if request.client else None,
                request.headers.get("user-agent")
            )
            
            # Determine if this was a create or update operation
            operation_type = "updated" if existing_profile["success"] else "created"
            
            return OnboardingResponse(
                success=True,
                message=f"Onboarding completed successfully! Your profile has been {operation_type}.",
                data={
                    "user_id": user_id,
                    "onboarding_completed": True,
                    "profile_updated_at": profile_data.get("updated_at", profile_data.get("created_at"))
                }
            )
        else:
            logger.error(f"❌ Failed to create user profile: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create profile: {result.get('error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Onboarding submission failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Onboarding failed: {str(e)}"
        )

@router.get("/status", response_model=OnboardingResponse, summary="Check onboarding status")
async def get_onboarding_status(
    current_user: AuthResponse = Depends(get_current_user)
):
    """Check if user has completed onboarding"""
    try:
        # Extract user info from AuthResponse
        if not current_user.success or not current_user.data:
            raise HTTPException(status_code=401, detail="Invalid user session")
        
        user_id = current_user.data.get("id")
        email = current_user.data.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid user information")
        
        # Check if profile exists and onboarding is completed
        profile_result = await supabase_manager.get_user_profile(user_id)
        
        if profile_result["success"]:
            profile = profile_result["profile"]
            onboarding_completed = profile.get("onboarding_completed", False)
            
            return OnboardingResponse(
                success=True,
                message="Profile status retrieved successfully",
                data={
                    "onboarding_completed": onboarding_completed,
                    "profile_exists": True,
                    "last_updated": profile.get("updated_at")
                }
            )
        else:
            return OnboardingResponse(
                success=True,
                message="Profile status retrieved successfully",
                data={
                    "onboarding_completed": False,
                    "profile_exists": False
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Failed to get onboarding status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get onboarding status: {str(e)}"
        )

@router.get("/profile", response_model=OnboardingResponse, summary="Get user profile data")
async def get_user_profile(
    current_user: AuthResponse = Depends(get_current_user)
):
    """Get complete user profile data (sensitive information)"""
    try:
        # Extract user info from AuthResponse
        if not current_user.success or not current_user.data:
            raise HTTPException(status_code=401, detail="Invalid user session")
        
        user_id = current_user.data.get("id")
        email = current_user.data.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid user information")
        
        # Get user profile
        profile_result = await supabase_manager.get_user_profile(user_id)
        
        if profile_result["success"]:
            profile = profile_result["profile"]
            
            # Log data access for audit trail
            await supabase_manager.log_profile_access(user_id, "view")
            
            return OnboardingResponse(
                success=True,
                message="Profile retrieved successfully",
                data={
                    "profile": profile,
                    "onboarding_completed": profile.get("onboarding_completed", False)
                }
            )
        else:
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get user profile: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get profile: {str(e)}"
        )
