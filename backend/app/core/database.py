"""
Database connection and initialization for Supabase
"""

from supabase import create_client, Client
from app.core.config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global Supabase client
supabase_client: Optional[Client] = None

async def init_db():
    """Initialize database connection"""
    global supabase_client
    
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase credentials not provided. Using mock client for development.")
            supabase_client = None
            return
        
        supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        
        # Test connection
        response = supabase_client.table("users").select("id").limit(1).execute()
        logger.info("✅ Database connection established successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {str(e)}")
        raise

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    if supabase_client is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return supabase_client

async def close_db():
    """Close database connection"""
    global supabase_client
    if supabase_client:
        supabase_client = None
        logger.info("Database connection closed")

# Database utility functions
async def execute_query(query: str, params: dict = None):
    """Execute a raw SQL query"""
    client = get_supabase_client()
    try:
        # Note: Supabase doesn't support raw SQL queries directly
        # This is a placeholder for future implementation
        logger.warning("Raw SQL queries not supported in Supabase. Use table operations instead.")
        return None
    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        raise

async def health_check():
    """Check database health"""
    try:
        client = get_supabase_client()
        response = client.table("users").select("id").limit(1).execute()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}




