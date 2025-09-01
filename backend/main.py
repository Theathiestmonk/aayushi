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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router if available
if api_router:
    app.include_router(api_router, prefix="/api/v1")
    print("✅ API router included successfully")
else:
    print("⚠️ API router not available - auth endpoints will not work")

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
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

