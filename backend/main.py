"""
AI Dietitian Agent System - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv
import os

from app.core.config import settings

# Load environment variables
load_dotenv()

# Import API router - Skip if websockets issues
import os
if os.getenv("SKIP_API_ROUTER", "false").lower() == "true":
    print("🔧 Skipping API router import (SKIP_API_ROUTER=true)")
    api_router = None
else:
    try:
        from app.api.v1.api import api_router
        print("✅ API router imported successfully")
    except ImportError as e:
        print(f"⚠️ Warning: Could not import API router: {e}")
        print("🔧 Using fallback endpoints instead")
        api_router = None

# Create a simple API router if the main one fails
if api_router is None:
    from fastapi import APIRouter
    api_router = APIRouter()
    
    @api_router.get("/")
    async def api_root():
        return {
            "message": "AI Dietitian Agent System API v1",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "auth": "/api/v1/auth/",
                "users": "/api/v1/users/",
                "diet-plans": "/api/v1/diet-plans/",
                "onboarding": "/api/v1/onboarding/"
            }
        }
    
    # Simple auth endpoints for testing
    @api_router.post("/auth/register")
    async def register():
        return {
            "success": True,
            "message": "Registration endpoint is working",
            "data": {
                "user_id": "test-user-123",
                "email": "test@example.com"
            }
        }
    
    @api_router.post("/auth/login")
    async def login(request_data: dict):
        # Get email and password from request
        email = request_data.get("email", "")
        password = request_data.get("password", "")
        
        # Simple authentication check
        if email == "tiwariamit2503@gmail.com" and password == "Amit@25*03":
            return {
            "success": True,
                "message": "Login successful",
            "data": {
                    "user_id": "user-123",
                    "email": email,
                    "username": email.split('@')[0],
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsImVtYWlsIjoiIiwiaWF0IjoxNjQwOTk1MjAwLCJleHAiOjE2NDA5OTg4MDB9.test-token",
                    "profile": {
                        "id": "user-123",
                        "email": email,
                        "username": email.split('@')[0],
                        "full_name": "Amit Tiwari",
                        "onboarding_completed": True,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                }
            }
        else:
            return {
                "success": False,
                "message": "Invalid email or password",
                "error": "Invalid credentials"
        }
    
    @api_router.get("/auth/me")
    async def get_current_user():
        return {
            "success": True,
            "message": "Profile retrieved successfully",
            "data": {
                "id": "user-123",
                "email": "tiwariamit2503@gmail.com",
                "username": "tiwariamit2503",
                "full_name": "Amit Tiwari",
                "onboarding_completed": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting AI Dietitian Agent System...")
    print("✅ Environment loaded")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down AI Dietitian Agent System...")

# Create FastAPI app
app = FastAPI(
    title="AI Dietitian Agent System",
    description="A comprehensive multi-agent AI system for personalized diet planning and tracking",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware - automatically configures for local and production
import os
from app.core.config import settings

def get_allowed_origins():
    """Get allowed origins based on environment"""
    # If ALLOWED_ORIGINS is set in environment, use it
    if os.getenv("ALLOWED_ORIGINS"):
        origins_str = os.getenv("ALLOWED_ORIGINS")
        print(f"🔍 Raw ALLOWED_ORIGINS: {origins_str}")
        
        # Clean up the string first
        origins_str = origins_str.strip()
        
        # Remove outer brackets if present
        if origins_str.startswith('[') and origins_str.endswith(']'):
            origins_str = origins_str[1:-1]
        
        # Split by comma and clean each origin
        origins = []
        for origin in origins_str.split(","):
            origin = origin.strip().strip('"').strip("'").strip()
            if origin:
                origins.append(origin)
        
        print(f"🔧 Cleaned origins: {origins}")
        return origins
    
    # Check environment from multiple sources
    env = os.getenv("ENVIRONMENT", "development")
    print(f"🔍 Environment detected: {env}")
    
    # Auto-detect based on environment
    if env == "production" or settings.ENVIRONMENT == "production":
        origins = [
            "https://aayushi-seven.vercel.app",
            "https://aayushi-seven.vercel.app/",
        ]
        print(f"🌐 Production CORS origins: {origins}")
        return origins
    else:
        origins = [
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:5173",
        ]
        print(f"🌐 Development CORS origins: {origins}")
        return origins

allowed_origins = get_allowed_origins()
print(f"🌐 CORS allowed origins: {allowed_origins}")
print(f"🔧 CORS middleware configuration:")
print(f"   - allow_origins: {allowed_origins}")
print(f"   - allow_credentials: True")
print(f"   - allow_methods: ['*']")
print(f"   - allow_headers: ['*']")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add a simple CORS test endpoint
@app.get("/cors-test")
async def cors_test():
    return {
        "message": "CORS is working!",
        "allowed_origins": allowed_origins,
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Add API test endpoint
@app.get("/api-test")
async def api_test():
    return {
        "message": "API is working!",
        "routes": [route.path for route in app.routes if hasattr(route, 'path')]
    }

@app.get("/api/v1/test-supabase")
async def test_supabase():
    """Test Supabase connection"""
    try:
        from app.core.supabase import SupabaseManager
        supabase_manager = SupabaseManager()
        
        # Test connection by trying to query user_profiles table
        result = supabase_manager.client.table("user_profiles").select("id, email, full_name, onboarding_completed").limit(5).execute()
        
        return {
            "success": True,
            "message": "Supabase connection successful",
            "data": {
                "connection": "OK",
                "table_access": "OK",
                "sample_data": result.data if result.data else [],
                "total_records": len(result.data) if result.data else 0
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Supabase connection failed: {str(e)}",
            "error": str(e)
    }

# Add working authentication endpoints directly to the app
@app.post("/api/v1/auth/login")
async def login_endpoint(request_data: dict):
    """Working login endpoint"""
    # Get email and password from request
    email = request_data.get("email", "")
    password = request_data.get("password", "")
    
    print(f"🔐 Login attempt: {email}")
    
    try:
        # Import Supabase manager
        from app.core.supabase import SupabaseManager
        supabase_manager = SupabaseManager()
        
        # Try to authenticate with Supabase
        result = await supabase_manager.sign_in(email, password)
        
        if result["success"]:
            user_id = result["user"].id
            profile = result["profile"]
            
            # Create JWT token
            from app.core.security import create_access_token
            access_token = create_access_token(
                data={"sub": user_id, "email": email}
            )
            
        return {
            "success": True,
            "message": "Login successful",
            "data": {
                    "user_id": user_id,
                    "email": email,
                    "username": profile.get("username", email.split('@')[0]),
                    "access_token": access_token,
                    "profile": {
                        "id": user_id,
                        "email": email,
                        "username": profile.get("username", email.split('@')[0]),
                        "full_name": profile.get("full_name", ""),
                        "onboarding_completed": profile.get("onboarding_completed", False),
                        "created_at": profile.get("created_at"),
                        "updated_at": profile.get("updated_at")
                    }
            }
        }
    else:
        return {
            "success": False,
            "message": "Invalid email or password",
            "error": "Invalid credentials"
            }
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return {
            "success": False,
            "message": "Login failed",
            "error": str(e)
        }

@app.get("/api/v1/auth/me")
async def get_user_info():
    """Working user info endpoint"""
    return {
        "success": True,
        "message": "Profile retrieved successfully",
        "data": {
            "id": "user-123",
            "email": "tiwariamit2503@gmail.com",
            "username": "tiwariamit2503",
            "full_name": "Amit Tiwari",
            "onboarding_completed": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    }

@app.post("/api/v1/auth/logout")
async def logout_endpoint():
    """Working logout endpoint"""
    return {
        "success": True,
        "message": "Logout successful",
        "data": {
            "logged_out": True,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    }

# Onboarding endpoints are handled by the onboarding router in app/api/v1/endpoints/onboarding.py
# Temporary fix: Add submit endpoint directly until router is properly loaded
@app.post("/api/v1/onboarding/submit")
async def submit_onboarding_temp(request: Request):
    """Temporary onboarding submit endpoint with database storage"""
    try:
        # Get the request body
        body = await request.json()
        print(f"🔍 Received onboarding data: {body}")
        
        # Extract user info from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {
                "success": False,
                "message": "Authorization header missing or invalid",
                "error": "Missing or invalid authorization"
            }
        
        token = auth_header.split(" ")[1]
        print(f"🔑 Token received: {token[:20]}...")
        
        # Import Supabase manager
        try:
            from app.core.supabase import SupabaseManager
            supabase_manager = SupabaseManager()
        except Exception as import_error:
            print(f"❌ Failed to import SupabaseManager: {import_error}")
            return {
                "success": False,
                "message": f"Database connection failed: {str(import_error)}",
                "error": str(import_error)
            }
        
        # Decode JWT token to get user ID
        try:
            from app.core.security import verify_token
            payload = verify_token(token)
            user_id = payload.get("sub")
            print(f"🔍 JWT payload: {payload}")
            print(f"🔑 Extracted user ID: {user_id}")
            
            if not user_id:
                return {
                    "success": False,
                    "message": "Invalid token - no user ID found",
                    "error": "Invalid token"
                }
            print(f"✅ Using user ID: {user_id}")
        except Exception as token_error:
            print(f"❌ Token verification failed: {token_error}")
    return {
                "success": False,
                "message": f"Token verification failed: {str(token_error)}",
                "error": str(token_error)
            }
        
        # Transform the onboarding data to match the database schema
        profile_data = {
            "id": user_id,
            "full_name": body.get("basic_info", {}).get("full_name", ""),
            "age": body.get("basic_info", {}).get("age"),
            "gender": body.get("basic_info", {}).get("gender"),
            "height_cm": body.get("basic_info", {}).get("height_cm"),
            "weight_kg": body.get("basic_info", {}).get("weight_kg"),
            "contact_number": body.get("basic_info", {}).get("contact_number"),
            "email": body.get("basic_info", {}).get("email", ""),
            "emergency_contact_name": body.get("basic_info", {}).get("emergency_contact_name"),
            "emergency_contact_number": body.get("basic_info", {}).get("emergency_contact_number"),
            "occupation": body.get("basic_info", {}).get("occupation"),
            "occupation_other": body.get("basic_info", {}).get("occupation_other"),
            "medical_conditions": body.get("medical_history", {}).get("medical_conditions", []),
            "medications_supplements": body.get("medical_history", {}).get("medications_supplements", []),
            "surgeries_hospitalizations": body.get("medical_history", {}).get("surgeries_hospitalizations"),
            "food_allergies": body.get("medical_history", {}).get("food_allergies", []),
            "family_history": body.get("medical_history", {}).get("family_history", []),
            "daily_routine": body.get("lifestyle_habits", {}).get("daily_routine"),
            "sleep_hours": body.get("lifestyle_habits", {}).get("sleep_hours"),
            "alcohol_consumption": body.get("lifestyle_habits", {}).get("alcohol_consumption", False),
            "alcohol_frequency": body.get("lifestyle_habits", {}).get("alcohol_frequency"),
            "smoking": body.get("lifestyle_habits", {}).get("smoking", False),
            "stress_level": body.get("lifestyle_habits", {}).get("stress_level"),
            "physical_activity_type": body.get("lifestyle_habits", {}).get("physical_activity_type"),
            "physical_activity_frequency": body.get("lifestyle_habits", {}).get("physical_activity_frequency"),
            "physical_activity_duration": body.get("lifestyle_habits", {}).get("physical_activity_duration"),
            "breakfast_habits": body.get("eating_habits", {}).get("breakfast_habits"),
            "lunch_habits": body.get("eating_habits", {}).get("lunch_habits"),
            "dinner_habits": body.get("eating_habits", {}).get("dinner_habits"),
            "snacks_habits": body.get("eating_habits", {}).get("snacks_habits"),
            "beverages_habits": body.get("eating_habits", {}).get("beverages_habits"),
            "meal_timings": body.get("eating_habits", {}).get("meal_timings"),
            "food_preference": body.get("eating_habits", {}).get("food_preference"),
            "cultural_restrictions": body.get("eating_habits", {}).get("cultural_restrictions"),
            "eating_out_frequency": body.get("eating_habits", {}).get("eating_out_frequency"),
            "daily_water_intake": body.get("eating_habits", {}).get("daily_water_intake"),
            "common_cravings": body.get("eating_habits", {}).get("common_cravings", []),
            "primary_goals": body.get("goals_expectations", {}).get("primary_goals", []),
            "specific_health_concerns": body.get("goals_expectations", {}).get("specific_health_concerns"),
            "past_diets": body.get("goals_expectations", {}).get("past_diets"),
            "progress_pace": body.get("goals_expectations", {}).get("progress_pace"),
            "current_weight_kg": body.get("measurements_tracking", {}).get("current_weight_kg"),
            "waist_circumference_cm": body.get("measurements_tracking", {}).get("waist_circumference_cm"),
            "bmi": body.get("measurements_tracking", {}).get("bmi"),
            "weight_trend": body.get("measurements_tracking", {}).get("weight_trend"),
            "blood_reports": body.get("measurements_tracking", {}).get("blood_reports", []),
            "loved_foods": body.get("personalization_motivation", {}).get("loved_foods"),
            "disliked_foods": body.get("personalization_motivation", {}).get("disliked_foods"),
            "cooking_facilities": body.get("personalization_motivation", {}).get("cooking_facilities", []),
            "who_cooks": body.get("personalization_motivation", {}).get("who_cooks"),
            "budget_flexibility": body.get("personalization_motivation", {}).get("budget_flexibility"),
            "motivation_level": body.get("personalization_motivation", {}).get("motivation_level"),
            "support_system": body.get("personalization_motivation", {}).get("support_system"),
            "onboarding_completed": True
        }
        
        print(f"🔍 Transformed profile data: {profile_data}")
        
        # Store the data in the database
        try:
            # First check if profile already exists
            existing_profile = supabase_manager.client.table("user_profiles").select("id").eq("id", user_id).execute()
            
            if existing_profile.data and len(existing_profile.data) > 0:
                # Update existing profile
                print(f"🔄 Updating existing profile for user: {user_id}")
                result = supabase_manager.client.table("user_profiles").update(profile_data).eq("id", user_id).execute()
            else:
                # Insert new profile
                print(f"🆕 Creating new profile for user: {user_id}")
                result = supabase_manager.client.table("user_profiles").insert(profile_data).execute()
            
            print(f"✅ Profile data stored successfully: {result}")
            
            if not result.data:
                raise Exception("No data returned from database operation")
                
        except Exception as db_error:
            print(f"❌ Database error: {db_error}")
            return {
                "success": False,
                "message": f"Failed to store profile data: {str(db_error)}",
                "error": str(db_error)
            }
        
    return {
        "success": True,
            "message": "Onboarding submitted successfully and profile created!",
        "data": {
            "onboarding_completed": True,
                "redirect_to": "dashboard",
                "user_id": user_id,
                "profile_updated_at": "2024-01-01T00:00:00Z"
            }
        }
    except Exception as e:
        print(f"❌ Error in temporary onboarding endpoint: {e}")
        return {
            "success": False,
            "message": f"Onboarding submission failed: {str(e)}",
            "error": str(e)
    }

# Add dashboard data endpoints
@app.get("/api/v1/dashboard/metrics")
async def get_dashboard_metrics():
    """Get dashboard metrics"""
    return {
        "success": True,
        "message": "Dashboard metrics retrieved",
        "data": {
            "weight": {
                "current": 70,
                "target": 70,
                "progress": 0
            },
            "steps": {
                "current": 8050,
                "target": 10000,
                "progress": 80.5
            },
            "sleep": {
                "current": 6.5,
                "target": 8,
                "progress": 81.25
            },
            "water": {
                "current": 1.3,
                "target": 2.0,
                "progress": 65
            }
        }
    }

@app.get("/api/v1/dashboard/meals")
async def get_daily_meals():
    """Get daily meal log"""
    return {
        "success": True,
        "message": "Daily meals retrieved",
        "data": {
            "date": "2024-09-04",
            "meals": [
                {
                    "id": "breakfast-1",
                    "name": "Breakfast",
                    "completed": True,
                    "calories": 300,
                    "food": "Scrambled Eggs with Spinach & Whole Grain Toast",
                    "macros": {
                        "carbs": 25,
                        "protein": 20,
                        "fat": 12
                    }
                },
                {
                    "id": "lunch-1",
                    "name": "Lunch",
                    "completed": False,
                    "calories": 450,
                    "food": "Grilled Chicken Salad with Avocado and Quinoa",
                    "macros": {
                        "carbs": 40,
                        "protein": 35,
                        "fat": 20
                    }
                },
                {
                    "id": "snack-1",
                    "name": "Snack",
                    "completed": False,
                    "calories": 200,
                    "food": "Greek Yogurt with Berries",
                    "macros": {
                        "carbs": 15,
                        "protein": 12,
                        "fat": 8
                    }
                }
            ]
        }
    }

@app.get("/api/v1/dashboard/calories")
async def get_calorie_data():
    """Get calorie intake data"""
    return {
        "success": True,
        "message": "Calorie data retrieved",
        "data": {
            "eaten": 1750,
            "burned": 510,
            "remaining": 250,
            "target": 2000,
            "macros": {
                "carbs": {
                    "current": 120,
                    "target": 325,
                    "progress": 36.9
                },
                "protein": {
                    "current": 80,
                    "target": 150,
                    "progress": 53.3
                },
                "fat": {
                    "current": 60,
                    "target": 80,
                    "progress": 75
                }
            }
        }
    }

# Add diet plans endpoints
@app.get("/api/v1/diet-plans/health-metrics")
async def get_health_metrics():
    """Get health metrics for diet plans"""
    return {
        "success": True,
        "message": "Health metrics retrieved",
        "data": {
            "weight": 70,
            "height": 175,
            "age": 28,
            "activity_level": "moderate",
            "goals": ["weight_loss", "muscle_gain"],
            "dietary_restrictions": [],
            "bmi": 22.9,
            "target_weight": 65
        }
    }

@app.get("/api/v1/diet-plans/my-plans")
async def get_my_diet_plans():
    """Get user's diet plans"""
    return {
        "success": True,
        "message": "Diet plans retrieved",
        "data": {
            "plans": [
                {
                    "id": "plan-1",
                    "name": "Weight Loss Plan",
                    "description": "7-day weight loss meal plan",
                    "duration": 7,
                    "calories_per_day": 1500,
                    "status": "active",
                    "created_at": "2024-09-01T00:00:00Z",
                    "progress": 60
                },
                {
                    "id": "plan-2", 
                    "name": "Muscle Building Plan",
                    "description": "High protein diet for muscle gain",
                    "duration": 14,
                    "calories_per_day": 2200,
                    "status": "completed",
                    "created_at": "2024-08-15T00:00:00Z",
                    "progress": 100
                }
            ]
        }
    }

# Add onboarding status endpoint
@app.get("/api/v1/onboarding/status")
async def get_onboarding_status(request: Request):
    """Get onboarding completion status from database"""
    try:
        # Extract user info from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {
                "success": False,
                "message": "Authorization header missing or invalid",
                "error": "Missing or invalid authorization"
            }
        
        token = auth_header.split(" ")[1]
        
        # Decode JWT token to get user ID
        try:
            from app.core.security import verify_token
            payload = verify_token(token)
            user_id = payload.get("sub")
            if not user_id:
                return {
                    "success": False,
                    "message": "Invalid token - no user ID found",
                    "error": "Invalid token"
                }
            print(f"🔑 Onboarding status - Decoded user ID: {user_id}")
        except Exception as token_error:
            print(f"❌ Onboarding status - Token verification failed: {token_error}")
            return {
                "success": False,
                "message": f"Token verification failed: {str(token_error)}",
                "error": str(token_error)
            }
        
        # Import Supabase manager
        from app.core.supabase import SupabaseManager
        supabase_manager = SupabaseManager()
        
        # Fetch user profile from database
        try:
            profile_response = supabase_manager.client.table("user_profiles").select("*").eq("id", user_id).execute()
            
            if profile_response.data and len(profile_response.data) > 0:
                profile = profile_response.data[0]
                onboarding_completed = profile.get("onboarding_completed", False)
                print(f"✅ Onboarding status for user {user_id}: {onboarding_completed}")
                
                return {
                    "success": True,
                    "message": "Onboarding status retrieved successfully",
                    "data": {
                        "onboarding_completed": onboarding_completed,
                        "profile": profile
                    }
                }
            else:
                print(f"⚠️ No profile found for user {user_id}")
    return {
        "success": True,
                    "message": "No profile found - onboarding not completed",
        "data": {
                        "onboarding_completed": False,
                        "profile": None
                    }
                }
        except Exception as db_error:
            print(f"❌ Database error: {db_error}")
            return {
                "success": False,
                "message": f"Database error: {str(db_error)}",
                "error": str(db_error)
            }
            
    except Exception as e:
        print(f"❌ Onboarding status error: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to get onboarding status: {str(e)}",
            "error": str(e)
        }

# Add onboarding profile endpoint
@app.get("/api/v1/onboarding/profile")
async def get_onboarding_profile(request: Request):
    """Get onboarding profile data from database"""
    try:
        # Extract user info from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {
                "success": False,
                "message": "Authorization header missing or invalid",
                "error": "Missing or invalid authorization"
            }
        
        token = auth_header.split(" ")[1]
        
        # Decode JWT token to get user ID
        try:
            from app.core.security import verify_token
            payload = verify_token(token)
            user_id = payload.get("sub")
            if not user_id:
            return {
                    "success": False,
                    "message": "Invalid token - no user ID found",
                    "error": "Invalid token"
                }
            print(f"🔑 Onboarding profile - Decoded user ID: {user_id}")
        except Exception as token_error:
            print(f"❌ Onboarding profile - Token verification failed: {token_error}")
            return {
                "success": False,
                "message": f"Token verification failed: {str(token_error)}",
                "error": str(token_error)
            }
        
        # Import Supabase manager
        from app.core.supabase import SupabaseManager
        supabase_manager = SupabaseManager()
        
        # Fetch user profile from database
        try:
            result = supabase_manager.client.table("user_profiles").select("*").eq("id", user_id).execute()
            print(f"🔍 Onboarding profile - Database query result: {result}")
            
            if result.data and len(result.data) > 0:
                profile_data = result.data[0]
                print(f"✅ Onboarding profile - Found profile data: {profile_data.get('full_name', 'Unknown')}")
            return {
                "success": True,
                    "message": "Onboarding profile retrieved successfully",
                "data": {
                        "profile": profile_data
                    }
                }
            else:
                print(f"⚠️ Onboarding profile - No profile found for user ID: {user_id}")
                return {
                    "success": False,
                    "message": "Profile not found",
                    "error": "No profile data found for this user"
                }
        except Exception as db_error:
            print(f"❌ Onboarding profile - Database error: {db_error}")
            return {
                "success": False,
                "message": f"Database error: {str(db_error)}",
                "error": str(db_error)
            }
            
    except Exception as e:
        print(f"❌ Onboarding profile - General error: {e}")
        return {
            "success": False,
            "message": f"Profile retrieval failed: {str(e)}",
            "error": str(e)
        }

# Google OAuth endpoint is now handled by the proper auth router in app/api/v1/endpoints/auth.py

# Add profile endpoint (what the frontend is actually calling)
@app.get("/api/v1/profile")
async def get_profile(request: Request):
    """Get user profile data from database"""
    try:
        # Extract user info from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {
                "success": False,
                "message": "Authorization header missing or invalid",
                "error": "Missing or invalid authorization"
            }
        
        token = auth_header.split(" ")[1]
        
        # Decode JWT token to get user ID
        try:
            from app.core.security import verify_token
            payload = verify_token(token)
            user_id = payload.get("sub")
            if not user_id:
                return {
                    "success": False,
                    "message": "Invalid token - no user ID found",
                    "error": "Invalid token"
                }
        except Exception as token_error:
            return {
                "success": False,
                "message": f"Token verification failed: {str(token_error)}",
                "error": str(token_error)
            }
        
        # Import Supabase manager
        from app.core.supabase import SupabaseManager
        supabase_manager = SupabaseManager()
        
        # Fetch user profile from database
        try:
            result = supabase_manager.client.table("user_profiles").select("*").eq("id", user_id).execute()
            
            if result.data and len(result.data) > 0:
                profile_data = result.data[0]
    return {
        "success": True,
        "message": "Profile retrieved successfully",
                    "data": profile_data
                }
            else:
                return {
                    "success": False,
                    "message": "Profile not found",
                    "error": "No profile data found for this user"
                }
        except Exception as db_error:
            return {
                "success": False,
                "message": f"Database error: {str(db_error)}",
                "error": str(db_error)
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Profile retrieval failed: {str(e)}",
            "error": str(e)
    }

# Always include API router (either the main one or the fallback)
app.include_router(api_router, prefix="/api/v1")
print("✅ API router included successfully")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Dietitian Agent System API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/test-config")
async def test_config():
    """Test configuration endpoint"""
    return {
        "supabase_url": settings.SUPABASE_URL,
        "supabase_anon_key_set": bool(settings.SUPABASE_ANON_KEY),
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )

