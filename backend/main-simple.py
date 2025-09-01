"""
AI Dietitian Agent System - Simplified Main FastAPI Application
For initial development and testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AI Dietitian Agent System",
    description="A comprehensive multi-agent AI system for personalized diet planning and tracking",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint for development"""
    return {
        "message": "API is working correctly",
        "endpoint": "/api/test"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main-simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )





