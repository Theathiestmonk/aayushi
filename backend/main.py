"""
AI Dietitian Agent System - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv
import os

from app.core.config import settings

# Load environment variables
load_dotenv()

# Import API router
try:
    from app.api.v1.api import api_router
    print("✅ API router imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import API router: {e}")
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
    async def login():
        return {
            "success": True,
            "message": "Login endpoint is working",
            "data": {
                "access_token": "test-token-123",
                "token_type": "bearer",
                "expires_in": 3600,
                "user_id": "test-user-123",
                "email": "test@example.com",
                "username": "testuser"
            }
        }
    
    @api_router.get("/auth/me")
    async def get_current_user():
        return {
            "success": True,
            "message": "User info endpoint is working",
            "data": {
                "user_id": "test-user-123",
                "email": "test@example.com",
                "full_name": "Test User"
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

