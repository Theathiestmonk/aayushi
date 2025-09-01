#!/usr/bin/env python3
"""
Simple Startup Script for AI Dietitian Backend
This script starts the backend with fallback support for missing dependencies
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def check_dependencies():
    """Check which dependencies are available"""
    available = {}
    
    # Core dependencies
    try:
        import fastapi
        available['fastapi'] = fastapi.__version__
    except ImportError:
        available['fastapi'] = None
    
    try:
        import uvicorn
        available['uvicorn'] = uvicorn.__version__
    except ImportError:
        available['uvicorn'] = None
    
    try:
        import pydantic
        available['pydantic'] = pydantic.__version__
    except ImportError:
        available['pydantic'] = None
    
    # AI dependencies
    try:
        import openai
        available['openai'] = openai.__version__
    except ImportError:
        available['openai'] = None
    
    try:
        import langgraph
        available['langgraph'] = langgraph.__version__
    except ImportError:
        available['langgraph'] = None
    
    try:
        import langchain
        available['langchain'] = langchain.__version__
    except ImportError:
        available['langchain'] = None
    
    # Database dependencies
    try:
        import supabase
        available['supabase'] = supabase.__version__
    except ImportError:
        available['supabase'] = None
    
    return available

def print_dependency_status(available):
    """Print the status of available dependencies"""
    print("🔍 Dependency Status:")
    print("-" * 30)
    
    for dep, version in available.items():
        if version:
            print(f"✅ {dep}: {version}")
        else:
            print(f"❌ {dep}: Not available")
    
    print()

def create_simple_app():
    """Create a simple FastAPI app with fallback support"""
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI(
            title="AI Dietitian Agent System (Simple Mode)",
            description="Running with fallback support for missing dependencies",
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
            return {
                "message": "AI Dietitian Agent System API (Simple Mode)",
                "version": "1.0.0",
                "status": "running",
                "mode": "fallback"
            }
        
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "mode": "fallback",
                "dependencies": check_dependencies()
            }
        
        @app.get("/api/test")
        async def test_endpoint():
            return {
                "message": "API is working in fallback mode",
                "endpoint": "/api/test",
                "note": "Some features may be limited due to missing dependencies"
            }
        
        @app.get("/dependencies")
        async def dependencies_status():
            return {
                "available": check_dependencies(),
                "mode": "fallback"
            }
        
        return app
        
    except ImportError as e:
        print(f"❌ Critical error: {e}")
        print("FastAPI is not available. Please install core dependencies first.")
        return None

def main():
    """Main startup function"""
    print("🚀 AI Dietitian Backend - Simple Startup")
    print("=" * 50)
    
    # Check dependencies
    available = check_dependencies()
    print_dependency_status(available)
    
    # Check if we have minimum requirements
    if not available.get('fastapi') or not available.get('uvicorn'):
        print("❌ Critical dependencies missing!")
        print("Please run: python install_deps.py")
        print("Or install manually: pip install fastapi uvicorn")
        return 1
    
    # Create the app
    app = create_simple_app()
    if not app:
        return 1
    
    print("✅ Backend app created successfully")
    print("🌐 Starting server...")
    print("📖 API docs will be available at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/health")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    try:
        import uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())





