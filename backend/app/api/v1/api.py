"""
Main API router for the AI Dietitian Agent System
"""

from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)
api_router = APIRouter()

# Include endpoint modules with error handling
try:
    from app.api.v1.endpoints import auth
    api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    logger.info("✅ Auth router included successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import auth endpoints: {e}")

try:
    from app.api.v1.endpoints import users
    api_router.include_router(users.router, prefix="/users", tags=["Users"])
    logger.info("✅ Users router included successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import users endpoints: {e}")

try:
    from app.api.v1.endpoints import diet_plans
    api_router.include_router(diet_plans.router, prefix="/diet-plans", tags=["Diet Plans"])
    logger.info("✅ Diet plans router included successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import diet_plans endpoints: {e}")

try:
    from app.api.v1.endpoints import onboarding
    api_router.include_router(onboarding.router, prefix="/onboarding", tags=["Onboarding"])
    logger.info("✅ Onboarding router included successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import onboarding endpoints: {e}")

# Comment out problematic modules for now
# try:
#     from app.api.v1.endpoints import agents
#     api_router.include_router(agents.router, prefix="/agents", tags=["AI Agents"])
#     logger.info("✅ Agents router included successfully")
# except ImportError as e:
#     logger.warning(f"⚠️ Agents endpoints not available: {e}")

try:
    from app.api.v1.endpoints import tracking
    api_router.include_router(tracking.router, prefix="/tracking", tags=["Tracking"])
    logger.info("✅ Tracking router included successfully")
except ImportError as e:
    logger.warning(f"⚠️ Tracking endpoints not available: {e}")

# try:
#     from app.api.v1.endpoints import mcp
#     api_router.include_router(mcp.router, prefix="/mcp", tags=["MCP Tools"])
#     logger.info("✅ MCP router included successfully")
# except ImportError as e:
#     logger.warning(f"⚠️ MCP endpoints not available: {e}")

logger.info(f"🚀 API router configured with {len(api_router.routes)} routes")

