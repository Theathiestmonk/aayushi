"""
MCP (Model Context Protocol) Server for AI Dietitian
Handles external tool calls and API integrations with best practices
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import httpx
from collections import defaultdict

from .schemas import (
    MCPTool, MCPCall, MCPResponse, ToolExecutionResult, 
    ToolUsageStats, SessionInfo, ToolCategory
)
from .exceptions import (
    ToolNotFoundError, InvalidParametersError, ToolExecutionError,
    ToolTimeoutError, SessionError, MCPError, ToolRateLimitError
)

logger = logging.getLogger(__name__)

class MCPServer:
    """Main MCP server for handling external tool calls with best practices"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.tools: Dict[str, MCPTool] = {}
        self.tool_handlers: Dict[str, Callable] = {}
        self.active_sessions: Dict[str, SessionInfo] = {}
        self.tool_stats: Dict[str, ToolUsageStats] = defaultdict(lambda: ToolUsageStats(tool_name=""))
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        self.health_status = "healthy"
        self.startup_time = datetime.utcnow()
        
        # Configuration
        self.max_concurrent_calls = self.config.get("max_concurrent_calls", 100)
        self.default_timeout = self.config.get("default_timeout", 30.0)
        self.enable_rate_limiting = self.config.get("enable_rate_limiting", True)
        self.max_requests_per_minute = self.config.get("max_requests_per_minute", 60)
        
        # Semaphore for limiting concurrent calls
        self._concurrent_semaphore = asyncio.Semaphore(self.max_concurrent_calls)
        
        # Initialize core tools
        self._register_core_tools()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        asyncio.create_task(self._cleanup_expired_sessions())
        asyncio.create_task(self._update_health_status())
    
    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        while True:
            try:
                current_time = datetime.utcnow()
                expired_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    # Sessions expire after 24 hours of inactivity
                    if current_time - session.last_activity > timedelta(hours=24):
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    del self.active_sessions[session_id]
                    logger.info(f"Cleaned up expired session: {session_id}")
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in session cleanup: {str(e)}")
                await asyncio.sleep(60)
    
    async def _update_health_status(self):
        """Update server health status"""
        while True:
            try:
                # Check if any tools are failing consistently
                failed_tools = [
                    tool_name for tool_name, stats in self.tool_stats.items()
                    if stats.error_rate > 50 and stats.total_calls > 10
                ]
                
                if failed_tools:
                    self.health_status = "degraded"
                    logger.warning(f"Server health degraded due to failing tools: {failed_tools}")
                else:
                    self.health_status = "healthy"
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error updating health status: {str(e)}")
                await asyncio.sleep(60)
    
    def _register_core_tools(self):
        """Register all available MCP tools with proper schemas"""
        from .tools import (
            NutritionTools, RecipeTools, GroceryTools, 
            HealthTools, OrderingTools, TrackingTools
        )
        
        # Register tool categories
        tool_categories = [
            NutritionTools(),
            RecipeTools(),
            GroceryTools(),
            HealthTools(),
            OrderingTools(),
            TrackingTools()
        ]
        
        for category in tool_categories:
            for tool in category.get_tools():
                self.register_tool(tool)
                logger.info(f"✅ Registered MCP tool: {tool.name}")
    
    def register_tool(self, tool: MCPTool):
        """Register a new MCP tool"""
        if tool.name in self.tools:
            logger.warning(f"Tool {tool.name} already registered, overwriting")
        
        self.tools[tool.name] = tool
        
        # Initialize stats for the tool
        if tool.name not in self.tool_stats:
            self.tool_stats[tool.name] = ToolUsageStats(tool_name=tool.name)
        
        # Set up rate limiting
        if self.enable_rate_limiting:
            self.rate_limits[tool.name] = {
                "requests": [],
                "max_requests": self.max_requests_per_minute,
                "window": 60  # 1 minute window
            }
    
    def register_handler(self, tool_name: str, handler: Callable[[Dict[str, Any], str], Awaitable[Any]]):
        """Register a handler function for a tool"""
        if tool_name not in self.tools:
            raise ToolNotFoundError(tool_name)
        
        self.tool_handlers[tool_name] = handler
        logger.info(f"✅ Handler registered for tool: {tool_name}")
    
    async def execute_tool(self, tool_call: MCPCall) -> MCPResponse:
        """Execute an MCP tool call with comprehensive error handling"""
        start_time = time.time()
        request_id = tool_call.request_id or str(uuid.uuid4())
        
        try:
            # Validate session
            await self._validate_session(tool_call.session_id, tool_call.user_id)
            
            # Check rate limiting
            if self.enable_rate_limiting:
                await self._check_rate_limit(tool_call.tool_name, tool_call.user_id)
            
            # Validate tool exists
            if tool_call.tool_name not in self.tools:
                raise ToolNotFoundError(tool_call.tool_name)
            
            tool = self.tools[tool_call.tool_name]
            
            # Validate parameters
            await self._validate_parameters(tool, tool_call.parameters)
            
            # Execute tool with timeout and concurrency control
            async with self._concurrent_semaphore:
                result = await asyncio.wait_for(
                    self._execute_tool_internal(tool_call),
                    timeout=self.default_timeout
                )
            
            # Update statistics
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            await self._update_tool_stats(tool_call.tool_name, True, execution_time)
            
            # Update session activity
            await self._update_session_activity(tool_call.session_id)
            
            return MCPResponse(
                success=True,
                tool_name=tool_call.tool_name,
                result=ToolExecutionResult(
                    success=True,
                    result=result,
                    execution_time_ms=execution_time
                ),
                timestamp=datetime.utcnow(),
                request_id=request_id,
                session_id=tool_call.session_id,
                user_id=tool_call.user_id
            )
            
        except asyncio.TimeoutError:
            execution_time = (time.time() - start_time) * 1000
            await self._update_tool_stats(tool_call.tool_name, False, execution_time)
            raise ToolTimeoutError(tool_call.tool_name, self.default_timeout)
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            await self._update_tool_stats(tool_call.tool_name, False, execution_time)
            
            # Convert to MCP error if not already
            if not isinstance(e, MCPError):
                e = ToolExecutionError(tool_call.tool_name, e)
            
            logger.error(f"Tool execution failed: {str(e)}")
            
            return MCPResponse(
                success=False,
                tool_name=tool_call.tool_name,
                result=ToolExecutionResult(
                    success=False,
                    error=str(e),
                    execution_time_ms=execution_time
                ),
                timestamp=datetime.utcnow(),
                request_id=request_id,
                session_id=tool_call.session_id,
                user_id=tool_call.user_id
            )
    
    async def _execute_tool_internal(self, tool_call: MCPCall) -> Any:
        """Internal tool execution logic"""
        tool_name = tool_call.tool_name
        
        if tool_name in self.tool_handlers:
            # Use custom handler
            handler = self.tool_handlers[tool_name]
            result = await handler(tool_call.parameters, tool_call.user_id)
        else:
            # Use default implementation
            result = await self._default_tool_handler(tool_call)
        
        return result
    
    async def _validate_session(self, session_id: str, user_id: str):
        """Validate session and create if needed"""
        if session_id not in self.active_sessions:
            # Create new session
            self.active_sessions[session_id] = SessionInfo(
                session_id=session_id,
                user_id=user_id
            )
            logger.info(f"Created new session: {session_id} for user: {user_id}")
    
    async def _validate_parameters(self, tool: MCPTool, parameters: Dict[str, Any]):
        """Validate tool parameters"""
        missing_params = []
        invalid_params = {}
        
        for param_name in tool.required_params:
            if param_name not in parameters:
                missing_params.append(param_name)
            elif parameters[param_name] is None:
                missing_params.append(param_name)
        
        if missing_params:
            raise InvalidParametersError(tool.name, missing_params, invalid_params)
    
    async def _check_rate_limit(self, tool_name: str, user_id: str):
        """Check rate limiting for tool and user"""
        if tool_name not in self.rate_limits:
            return
        
        rate_limit = self.rate_limits[tool_name]
        current_time = time.time()
        
        # Clean old requests outside the window
        rate_limit["requests"] = [
            req for req in rate_limit["requests"]
            if current_time - req["timestamp"] < rate_limit["window"]
        ]
        
        # Check if limit exceeded
        user_requests = [
            req for req in rate_limit["requests"]
            if req["user_id"] == user_id
        ]
        
        if len(user_requests) >= rate_limit["max_requests"]:
            raise ToolRateLimitError(tool_name, retry_after=rate_limit["window"])
        
        # Add current request
        rate_limit["requests"].append({
            "user_id": user_id,
            "timestamp": current_time
        })
    
    async def _update_tool_stats(self, tool_name: str, success: bool, execution_time: float):
        """Update tool usage statistics"""
        if tool_name not in self.tool_stats:
            self.tool_stats[tool_name] = ToolUsageStats(tool_name=tool_name)
        
        stats = self.tool_stats[tool_name]
        stats.total_calls += 1
        
        if success:
            stats.successful_calls += 1
        else:
            stats.failed_calls += 1
        
        # Update average execution time
        if stats.total_calls == 1:
            stats.average_execution_time_ms = execution_time
        else:
            stats.average_execution_time_ms = (
                (stats.average_execution_time_ms * (stats.total_calls - 1) + execution_time) 
                / stats.total_calls
            )
        
        stats.last_used = datetime.utcnow()
    
    async def _update_session_activity(self, session_id: str):
        """Update session last activity time"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].last_activity = datetime.utcnow()
    
    async def _default_tool_handler(self, tool_call: MCPCall) -> Any:
        """Default handler for tools without custom implementations"""
        # This will be implemented by individual tool categories
        return {"message": f"Default handler for {tool_call.tool_name} not implemented"}
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of all available tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category.value,
                "version": tool.version,
                "author": tool.author,
                "tags": tool.tags
            }
            for tool in self.tools.values()
        ]
    
    def get_tools_by_category(self, category: ToolCategory) -> List[Dict[str, Any]]:
        """Get tools filtered by category"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category.value,
                "version": tool.version,
                "author": tool.author,
                "tags": tool.tags
            }
            for tool in self.tools.values()
            if tool.category == category
        ]
    
    def get_tool_details(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific tool"""
        if tool_name not in self.tools:
            return None
        
        tool = self.tools[tool_name]
        stats = self.tool_stats.get(tool_name, ToolUsageStats(tool_name=tool_name))
        
        return {
            "name": tool.name,
            "description": tool.description,
            "category": tool.category.value,
            "version": tool.version,
            "author": tool.author,
            "tags": tool.tags,
            "parameters": {
                name: {
                    "type": param.type.value,
                    "description": param.description,
                    "required": param.required,
                    "default": param.default
                }
                for name, param in tool.parameters.items()
            },
            "required_params": tool.required_params,
            "stats": stats.dict()
        }
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get comprehensive server statistics"""
        total_tools = len(self.tools)
        total_sessions = len(self.active_sessions)
        total_calls = sum(stats.total_calls for stats in self.tool_stats.values())
        successful_calls = sum(stats.successful_calls for stats in self.tool_stats.values())
        
        return {
            "server_status": {
                "health": self.health_status,
                "uptime_seconds": (datetime.utcnow() - self.startup_time).total_seconds(),
                "startup_time": self.startup_time.isoformat()
            },
            "tools": {
                "total": total_tools,
                "by_category": {
                    category.value: len(self.get_tools_by_category(category))
                    for category in ToolCategory
                }
            },
            "sessions": {
                "total": total_sessions,
                "active": len([s for s in self.active_sessions.values() if s.active])
            },
            "calls": {
                "total": total_calls,
                "successful": successful_calls,
                "failed": total_calls - successful_calls,
                "success_rate": (successful_calls / total_calls * 100) if total_calls > 0 else 0
            },
            "performance": {
                "max_concurrent_calls": self.max_concurrent_calls,
                "current_concurrent_calls": self.max_concurrent_calls - self._concurrent_semaphore._value,
                "default_timeout": self.default_timeout
            }
        }
    
    async def shutdown(self):
        """Gracefully shutdown the MCP server"""
        logger.info("🛑 Shutting down MCP server...")
        
        # Close all active sessions
        for session_id in list(self.active_sessions.keys()):
            if session_id in self.active_sessions:
                self.active_sessions[session_id].active = False
        
        # Wait for ongoing operations to complete
        await asyncio.sleep(1)
        
        logger.info("✅ MCP server shutdown complete")

# Global MCP server instance
mcp_server = MCPServer()




