"""
MCP Configuration Settings
"""

from pydantic import BaseSettings
from typing import Dict, Any, List
import os

class MCPSettings(BaseSettings):
    """MCP configuration settings"""
    
    # Server Configuration
    MCP_ENABLED: bool = True
    MCP_HOST: str = "0.0.0.0"
    MCP_PORT: int = 8001  # Separate port for MCP if needed
    MCP_DEBUG: bool = False
    
    # Tool Configuration
    MCP_MAX_CONCURRENT_CALLS: int = 100
    MCP_DEFAULT_TIMEOUT: float = 30.0
    MCP_ENABLE_RATE_LIMITING: bool = True
    MCP_MAX_REQUESTS_PER_MINUTE: int = 60
    
    # Session Configuration
    MCP_SESSION_TIMEOUT_HOURS: int = 24
    MCP_MAX_SESSIONS_PER_USER: int = 5
    
    # External Service Configuration
    MCP_NUTRITION_API_KEY: str = os.getenv("NUTRITION_API_KEY", "")
    MCP_RECIPE_API_KEY: str = os.getenv("RECIPE_API_KEY", "")
    MCP_GROCERY_API_KEY: str = os.getenv("GROCERY_API_KEY", "")
    MCP_ZEPTO_API_KEY: str = os.getenv("ZEPTO_API_KEY", "")
    MCP_BLINKIT_API_KEY: str = os.getenv("BLINKIT_API_KEY", "")
    
    # Health Check Configuration
    MCP_HEALTH_CHECK_INTERVAL: int = 60  # seconds
    MCP_HEALTH_CHECK_TIMEOUT: float = 5.0  # seconds
    
    # Logging Configuration
    MCP_LOG_LEVEL: str = "INFO"
    MCP_LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security Configuration
    MCP_ENABLE_AUTHENTICATION: bool = True
    MCP_REQUIRE_USER_AUTH: bool = True
    MCP_ALLOW_ANONYMOUS_TOOLS: List[str] = ["get_nutrition_info", "search_recipes"]
    
    # Performance Configuration
    MCP_ENABLE_CACHING: bool = True
    MCP_CACHE_TTL: int = 300  # seconds
    MCP_ENABLE_METRICS: bool = True
    MCP_METRICS_PORT: int = 9090
    
    # Tool Categories Configuration
    MCP_ENABLED_CATEGORIES: List[str] = [
        "nutrition", "recipes", "grocery", "health", "ordering", "tracking"
    ]
    
    # Default Tool Handlers
    MCP_DEFAULT_HANDLERS: Dict[str, str] = {
        "get_nutrition_info": "nutrition",
        "search_recipes": "recipes",
        "generate_grocery_list": "grocery",
        "order_groceries": "ordering",
        "get_health_insights": "health",
        "track_progress": "tracking"
    }
    
    class Config:
        env_prefix = "MCP_"
        case_sensitive = False

# Global MCP settings instance
mcp_settings = MCPSettings()

def get_mcp_config() -> Dict[str, Any]:
    """Get MCP configuration as dictionary"""
    return {
        "enabled": mcp_settings.MCP_ENABLED,
        "max_concurrent_calls": mcp_settings.MCP_MAX_CONCURRENT_CALLS,
        "default_timeout": mcp_settings.MCP_DEFAULT_TIMEOUT,
        "enable_rate_limiting": mcp_settings.MCP_ENABLE_RATE_LIMITING,
        "max_requests_per_minute": mcp_settings.MCP_MAX_REQUESTS_PER_MINUTE,
        "session_timeout_hours": mcp_settings.MCP_SESSION_TIMEOUT_HOURS,
        "max_sessions_per_user": mcp_settings.MCP_MAX_SESSIONS_PER_USER,
        "enable_caching": mcp_settings.MCP_ENABLE_CACHING,
        "cache_ttl": mcp_settings.MCP_CACHE_TTL,
        "enable_metrics": mcp_settings.MCP_ENABLE_METRICS,
        "metrics_port": mcp_settings.MCP_METRICS_PORT
    }

def is_mcp_enabled() -> bool:
    """Check if MCP is enabled"""
    return mcp_settings.MCP_ENABLED

def get_enabled_categories() -> List[str]:
    """Get list of enabled tool categories"""
    return mcp_settings.MCP_ENABLED_CATEGORIES

def get_default_handlers() -> Dict[str, str]:
    """Get default tool handlers mapping"""
    return mcp_settings.MCP_DEFAULT_HANDLERS

def get_api_keys() -> Dict[str, str]:
    """Get external service API keys"""
    return {
        "nutrition": mcp_settings.MCP_NUTRITION_API_KEY,
        "recipe": mcp_settings.MCP_RECIPE_API_KEY,
        "grocery": mcp_settings.MCP_GROCERY_API_KEY,
        "zepto": mcp_settings.MCP_ZEPTO_API_KEY,
        "blinkit": mcp_settings.MCP_BLINKIT_API_KEY
    }




