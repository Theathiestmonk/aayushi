"""
Diet plan management endpoints for the AI Dietitian Agent System
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date
import logging

from app.api.v1.endpoints.auth import get_current_user, AuthResponse
from app.agents.diet_planner_agent import DietPlannerAgent
from app.core.supabase import SupabaseManager

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Supabase manager
supabase_manager = SupabaseManager()

# Specific routes must come before catch-all routes
@router.get("/health-metrics", response_model=Dict[str, Any], summary="Get user health metrics")
async def get_health_metrics(
    current_user: AuthResponse = Depends(get_current_user)
):
    """
    Get calculated health metrics for the user including BMI, BMR, TDEE, and target calories
    """
    try:
        user_id = current_user.data.get("id")
        email = current_user.data.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid user information")
        
        # Get user profile data
        profile_result = await supabase_manager.get_user_profile(user_id)
        if not profile_result["success"]:
            raise HTTPException(
                status_code=404, 
                detail="User profile not found. Please complete onboarding first."
            )
        
        profile_data = profile_result["profile"]
        
        # Initialize diet planner agent to calculate metrics
        diet_agent = DietPlannerAgent()
        health_metrics = diet_agent._calculate_health_metrics(profile_data)
        
        return {
            "success": True,
            "health_metrics": health_metrics,
            "profile_summary": {
                "name": profile_data.get("full_name"),
                "age": profile_data.get("age"),
                "gender": profile_data.get("gender"),
                "height_cm": profile_data.get("height_cm"),
                "weight_kg": profile_data.get("current_weight_kg", profile_data.get("weight_kg")),
                "bmi": health_metrics.get("bmi"),
                "bmi_category": health_metrics.get("bmi_category"),
                "target_calories": health_metrics.get("target_calories"),
                "macronutrients": health_metrics.get("macronutrients", {})
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get health metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get health metrics: {str(e)}"
        )

@router.get("/check-existing", response_model=Dict[str, Any], summary="Check if user has existing diet plans")
async def check_existing_diet_plans(
    current_user: AuthResponse = Depends(get_current_user)
):
    """
    Check if the current user has existing diet plans
    """
    try:
        user_id = current_user.data.get("id")
        email = current_user.data.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid user information")
        
        # Check for existing diet plans
        check_result = await supabase_manager.has_existing_diet_plans(user_id)
        
        if not check_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to check for existing diet plans: {check_result.get('error')}"
            )
        
        return check_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to check for existing diet plans: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check for existing diet plans: {str(e)}"
        )

@router.get("/count", response_model=Dict[str, Any], summary="Get count of user's diet plans")
async def get_diet_plan_count(
    current_user: AuthResponse = Depends(get_current_user)
):
    """
    Get the count of existing diet plans for the current user
    """
    try:
        user_id = current_user.data.get("id")
        email = current_user.data.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid user information")
        
        # Get diet plan count
        count_result = await supabase_manager.get_diet_plan_count(user_id)
        
        if not count_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get diet plan count: {count_result.get('error')}"
            )
        
        return count_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get diet plan count: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get diet plan count: {str(e)}"
        )

@router.post("/archive-existing", response_model=Dict[str, Any], summary="Archive existing diet plans")
async def archive_existing_diet_plans(
    current_user: AuthResponse = Depends(get_current_user)
):
    """
    Archive all existing diet plans for the current user
    """
    try:
        user_id = current_user.data.get("id")
        email = current_user.data.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid user information")
        
        # Archive existing diet plans
        archive_result = await supabase_manager.archive_user_diet_plans(user_id)
        
        if not archive_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to archive existing diet plans: {archive_result.get('error')}"
            )
        
        return archive_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to archive existing diet plans: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to archive existing diet plans: {str(e)}"
        )

@router.post("/force-clear", response_model=Dict[str, Any], summary="Force clear all diet data")
async def force_clear_all_diet_data(
    current_user: AuthResponse = Depends(get_current_user)
):
    """
    Force clear ALL diet-related data for the current user (nuclear option)
    This will completely remove all diet plans, daily plans, meals, and food items
    """
    try:
        user_id = current_user.data.get("id")
        email = current_user.data.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid user information")
        
        # Force clear all diet data
        force_clear_result = await supabase_manager.force_clear_all_user_data(user_id)
        
        if not force_clear_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to force clear diet data: {force_clear_result.get('error')}"
            )
        
        return force_clear_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to force clear diet data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to force clear diet data: {str(e)}"
        )

@router.get("/verify-clear", response_model=Dict[str, Any], summary="Verify data has been cleared")
async def verify_data_cleared(
    current_user: AuthResponse = Depends(get_current_user)
):
    """
    Verify that all diet-related data has been cleared for the current user
    """
    try:
        user_id = current_user.data.get("id")
        email = current_user.data.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid user information")
        
        # Verify data clearance
        verify_result = await supabase_manager.verify_user_data_cleared(user_id)
        
        if not verify_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to verify data clearance: {verify_result.get('error')}"
            )
        
        return verify_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to verify data clearance: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify data clearance: {str(e)}"
        )

@router.post("/test-cleanup", response_model=Dict[str, Any], summary="Test cleanup functionality")
async def test_cleanup_functionality(
    current_user: AuthResponse = Depends(get_current_user)
):
    """
    Test endpoint to manually trigger cleanup and verify it works
    """
    try:
        user_id = current_user.data.get("id")
        email = current_user.data.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid user information")
        
        logger.info(f"🧪 TEST CLEANUP: Testing cleanup for user: {email}")
        
        # Step 1: Check current data
        logger.info("🔍 Step 1: Checking current data...")
        check_result = await supabase_manager.has_existing_diet_plans(user_id)
        count_result = await supabase_manager.get_diet_plan_count(user_id)
        
        # Step 2: Force clear all data
        logger.info("🧹 Step 2: Force clearing all data...")
        force_clear_result = await supabase_manager.force_clear_all_user_data(user_id)
        
        # Step 3: Verify data was cleared
        logger.info("🔍 Step 3: Verifying data was cleared...")
        verify_result = await supabase_manager.verify_user_data_cleared(user_id)
        
        return {
            "success": True,
            "test_results": {
                "step1_check": check_result,
                "step1_count": count_result,
                "step2_clear": force_clear_result,
                "step3_verify": verify_result
            },
            "message": "Cleanup test completed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Cleanup test failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Cleanup test failed: {str(e)}"
        )

@router.get("/my-plans", response_model=Dict[str, Any], summary="Get user's diet plans")
async def get_user_diet_plans(
    current_user: AuthResponse = Depends(get_current_user)
):
    """
    Get all diet plans for the current user
    """
    try:
        user_id = current_user.data.get("id")
        email = current_user.data.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid user information")
        
        # Get user's diet plans from database
        plans_result = await supabase_manager.get_user_diet_plans(user_id)
        
        if not plans_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve diet plans: {plans_result.get('error')}"
            )
        
        return {
            "success": True,
            "plans": plans_result["plans"],
            "total_plans": len(plans_result["plans"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get user diet plans: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user diet plans: {str(e)}"
        )

@router.get("/plan/{plan_id}", response_model=Dict[str, Any], summary="Get detailed diet plan")
async def get_diet_plan_details(
    plan_id: str,
    current_user: AuthResponse = Depends(get_current_user)
):
    """
    Get detailed diet plan with daily plans, meals, and food items
    """
    try:
        user_id = current_user.data.get("id")
        email = current_user.data.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid user information")
        
        # Get detailed diet plan from database
        plan_result = await supabase_manager.get_diet_plan_details(plan_id)
        
        if not plan_result["success"]:
            raise HTTPException(
                status_code=404,
                detail=f"Diet plan not found: {plan_result.get('error')}"
            )
        
        return {
            "success": True,
            "plan": plan_result["plan"],
            "daily_plans": plan_result["daily_plans"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get diet plan details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get diet plan details: {str(e)}"
        )

@router.post("/progress", response_model=Dict[str, Any], summary="Track daily progress")
async def track_progress(
    progress_data: Dict[str, Any],
    current_user: AuthResponse = Depends(get_current_user)
):
    """
    Track daily progress including weight, energy, and compliance
    """
    try:
        user_id = current_user.data.get("id")
        email = current_user.data.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid user information")
        
        # Add user_id to progress data
        progress_data["user_id"] = user_id
        
        # Insert progress tracking data
        progress_result = await supabase_manager.create_progress_tracking(user_id, progress_data)
        
        if not progress_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to track progress: {progress_result.get('error')}"
            )
        
        return {
            "success": True,
            "progress_id": progress_result["progress_id"],
            "message": "Progress tracked successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to track progress: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to track progress: {str(e)}"
        )

class DietPlan(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    status: str = "active"
    total_calories: Optional[int] = None
    total_protein_g: Optional[int] = None
    total_carbs_g: Optional[int] = None
    total_fat_g: Optional[int] = None

class CreateDietPlan(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    total_calories: Optional[int] = None

@router.get("/", response_model=List[DietPlan])
async def get_diet_plans():
    """Get all diet plans for current user"""
    # TODO: Implement actual diet plan retrieval
    return [
        DietPlan(
            id="plan_123",
            user_id="user_123",
            name="Weight Loss Plan",
            description="7-day weight loss diet plan",
            start_date=date.today(),
            end_date=date.today(),
            total_calories=1500,
            total_protein_g=120,
            total_carbs_g=150,
            total_fat_g=50
        )
    ]

@router.get("/{plan_id}", response_model=DietPlan)
async def get_diet_plan(plan_id: str):
    """Get diet plan by ID"""
    # TODO: Implement actual diet plan retrieval
    return DietPlan(
        id=plan_id,
        user_id="user_123",
        name="Weight Loss Plan",
        description="7-day weight loss diet plan",
        start_date=date.today(),
        end_date=date.today(),
        total_calories=1500,
        total_protein_g=120,
        total_carbs_g=150,
        total_fat_g=50
    )

@router.post("/", response_model=DietPlan)
async def create_diet_plan(plan_data: CreateDietPlan):
    """Create new diet plan"""
    # TODO: Implement actual diet plan creation
    return DietPlan(
        id="new_plan_123",
        user_id="user_123",
        name=plan_data.name,
        description=plan_data.description,
        start_date=plan_data.start_date,
        end_date=plan_data.end_date,
        total_calories=plan_data.total_calories
    )

@router.put("/{plan_id}", response_model=DietPlan)
async def update_diet_plan(plan_id: str, plan_data: CreateDietPlan):
    """Update diet plan"""
    # TODO: Implement actual diet plan update
    return DietPlan(
        id=plan_id,
        user_id="user_123",
        name=plan_data.name,
        description=plan_data.description,
        start_date=plan_data.start_date,
        end_date=plan_data.end_date,
        total_calories=plan_data.total_calories
    )

@router.delete("/{plan_id}")
async def delete_diet_plan(
    plan_id: str,
    current_user: AuthResponse = Depends(get_current_user)
):
    """Delete diet plan"""
    try:
        # Extract user information
        user_id = current_user.data.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user information")
        
        # Delete the diet plan
        delete_result = await supabase_manager.delete_diet_plan(plan_id)
        
        if not delete_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete diet plan: {delete_result.get('error')}"
            )
        
        return {"message": f"Diet plan {plan_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete diet plan: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete diet plan: {str(e)}"
        )

class DietPlanRequest(BaseModel):
    """Request model for diet plan generation"""
    plan_duration_days: int = 30
    include_meal_prep: bool = True
    include_shopping_list: bool = True
    specific_preferences: Optional[Dict[str, Any]] = None

class DietPlanResponse(BaseModel):
    """Response model for diet plan generation"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/generate", response_model=DietPlanResponse, summary="Generate personalized diet plan")
async def generate_diet_plan(
    request: DietPlanRequest,
    current_user: AuthResponse = Depends(get_current_user),
    http_request: Request = None
):
    """
    Generate a personalized diet plan based on user profile data using the AI Dietitian Agent
    """
    try:
        # Extract user information
        user_id = current_user.data.get("id")
        email = current_user.data.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid user information")
        
        logger.info(f"🍽️ Generating diet plan for user: {email}")
        
        # Get user profile data
        profile_result = await supabase_manager.get_user_profile(user_id)
        if not profile_result["success"]:
            raise HTTPException(
                status_code=404, 
                detail="User profile not found. Please complete onboarding first."
            )
        
        profile_data = profile_result["profile"]
        
        # MANUAL CLEANUP: Force clear existing diet data before generating new plan
        logger.info(f"🧹 MANUAL CLEANUP: Force clearing existing diet data for user: {user_id}")
        try:
            cleanup_result = await supabase_manager.force_clear_all_user_data(user_id)
            if cleanup_result["success"]:
                deleted_plans = cleanup_result.get("deleted_plans", 0)
                deleted_daily_plans = cleanup_result.get("deleted_daily_plans", 0)
                deleted_meals = cleanup_result.get("deleted_meals", 0)
                deleted_food_items = cleanup_result.get("deleted_food_items", 0)
                logger.info(f"✅ MANUAL CLEANUP SUCCESS: Deleted {deleted_plans} plans, {deleted_daily_plans} daily plans, {deleted_meals} meals, {deleted_food_items} food items")
            else:
                logger.warning(f"⚠️ MANUAL CLEANUP FAILED: {cleanup_result.get('error')}")
        except Exception as e:
            logger.error(f"❌ MANUAL CLEANUP ERROR: {str(e)}")
        
        # Initialize diet planner agent
        diet_agent = DietPlannerAgent()
        
        # Prepare state for agent processing
        state = {
            "user_data": {
                "user_id": user_id,
                "email": email,
                **profile_data
            },
            "request_data": request.dict(),
            "results": {}
        }
        
        # Process diet plan generation
        logger.info(f"🔄 Starting diet plan generation with DietPlannerAgent...")
        result_state = await diet_agent.process(state)
        logger.info(f"✅ DietPlannerAgent processing completed")
        
        # VERIFICATION: Check if data was actually cleared
        logger.info(f"🔍 VERIFICATION: Checking if data was actually cleared for user: {user_id}")
        try:
            verify_result = await supabase_manager.verify_user_data_cleared(user_id)
            if verify_result["success"]:
                is_cleared = verify_result.get("is_cleared", False)
                remaining_plans = verify_result.get("remaining_plans", 0)
                remaining_daily_plans = verify_result.get("remaining_daily_plans", 0)
                remaining_meals = verify_result.get("remaining_meals", 0)
                remaining_food_items = verify_result.get("remaining_food_items", 0)
                logger.info(f"🔍 VERIFICATION RESULT: Data cleared: {is_cleared}, Remaining: {remaining_plans} plans, {remaining_daily_plans} daily plans, {remaining_meals} meals, {remaining_food_items} food items")
            else:
                logger.warning(f"⚠️ VERIFICATION FAILED: {verify_result.get('error')}")
        except Exception as e:
            logger.error(f"❌ VERIFICATION ERROR: {str(e)}")
        
        # Extract results
        diet_planner_result = result_state.get("results", {}).get("diet_planner", {})
        logger.info(f"📊 Diet planner result: {diet_planner_result}")
        
        if not diet_planner_result.get("success"):
            error_msg = diet_planner_result.get("error", "Failed to generate diet plan")
            logger.error(f"❌ Diet plan generation failed: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Log data access for audit trail
        await supabase_manager.log_profile_access(
            user_id, 
            "diet_plan_generation", 
            str(http_request.client.host) if http_request and http_request.client else None,
            http_request.headers.get("user-agent") if http_request else None
        )
        
        return DietPlanResponse(
            success=True,
            message="Diet plan generated successfully",
            data={
                "diet_plan": diet_planner_result.get("diet_plan"),
                "health_metrics": diet_planner_result.get("health_metrics"),
                "generated_at": diet_planner_result.get("diet_plan", {}).get("created_at")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Diet plan generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate diet plan: {str(e)}"
        )

@router.get("/{plan_id}/details", response_model=Dict[str, Any], summary="Get detailed diet plan information")
async def get_diet_plan_details(
    plan_id: str,
    current_user: AuthResponse = Depends(get_current_user)
):
    """
    Get detailed information about a specific diet plan including daily plans, meals, and food items
    """
    try:
        # Extract user information
        user_id = current_user.data.get("id")
        email = current_user.data.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid user information")
        
        logger.info(f"📋 Getting details for diet plan: {plan_id}")
        
        # Get diet plan details from database
        plan_details = await supabase_manager.get_diet_plan_details(plan_id, user_id)
        
        if not plan_details["success"]:
            raise HTTPException(
                status_code=404,
                detail=f"Diet plan not found: {plan_details.get('error')}"
            )
        
        return {
            "success": True,
            "data": plan_details["plan_details"],
            "message": "Diet plan details retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get diet plan details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get diet plan details: {str(e)}"
        )

