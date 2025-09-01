"""
MCP Client for AI Agents to use external tools
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from .mcp_server import mcp_server
from .schemas import MCPCall, MCPResponse
from .exceptions import MCPError, ToolNotFoundError, InvalidParametersError

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for agents to interact with MCP tools"""
    
    def __init__(self, user_id: str, session_id: Optional[str] = None):
        self.user_id = user_id
        self.session_id = session_id or f"session_{user_id}_{uuid.uuid4().hex[:8]}"
        self.call_history: List[MCPCall] = []
        self.active_requests: Dict[str, asyncio.Task] = {}
        
        logger.info(f"MCP client initialized for user {user_id} with session {self.session_id}")
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any], 
                       request_id: Optional[str] = None, priority: int = 1) -> Dict[str, Any]:
        """Call an MCP tool with comprehensive error handling"""
        try:
            # Create tool call
            tool_call = MCPCall(
                tool_name=tool_name,
                parameters=parameters,
                user_id=self.user_id,
                session_id=self.session_id,
                request_id=request_id or str(uuid.uuid4()),
                priority=priority
            )
            
            # Execute the tool
            result = await mcp_server.execute_tool(tool_call)
            
            # Log the call
            self.call_history.append(tool_call)
            
            logger.info(f"MCP tool {tool_name} called successfully for user {self.user_id}")
            return result.dict()
            
        except Exception as e:
            logger.error(f"Failed to call MCP tool {tool_name}: {str(e)}")
            
            # Convert to standard error format
            if isinstance(e, MCPError):
                raise e
            else:
                raise MCPError(f"Tool call failed: {str(e)}")
    
    async def call_tool_async(self, tool_name: str, parameters: Dict[str, Any], 
                             request_id: Optional[str] = None, priority: int = 1) -> str:
        """Call an MCP tool asynchronously and return request ID"""
        request_id = request_id or str(uuid.uuid4())
        
        # Create tool call
        tool_call = MCPCall(
            tool_name=tool_name,
            parameters=parameters,
            user_id=self.user_id,
            session_id=self.session_id,
            request_id=request_id,
            priority=priority
        )
        
        # Create async task
        task = asyncio.create_task(self._execute_tool_async(tool_call))
        self.active_requests[request_id] = task
        
        logger.info(f"Async MCP tool call initiated: {tool_name} with request ID {request_id}")
        return request_id
    
    async def _execute_tool_async(self, tool_call: MCPCall):
        """Execute tool call asynchronously"""
        try:
            result = await mcp_server.execute_tool(tool_call)
            self.call_history.append(tool_call)
            logger.info(f"Async MCP tool {tool_call.tool_name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Async MCP tool {tool_call.tool_name} failed: {str(e)}")
            raise e
        finally:
            # Clean up active request
            if tool_call.request_id in self.active_requests:
                del self.active_requests[tool_call.request_id]
    
    async def get_async_result(self, request_id: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Get result from async tool call"""
        if request_id not in self.active_requests:
            raise ValueError(f"Request ID {request_id} not found in active requests")
        
        task = self.active_requests[request_id]
        
        try:
            if timeout:
                result = await asyncio.wait_for(task, timeout=timeout)
            else:
                result = await task
            
            return result.dict() if hasattr(result, 'dict') else result
            
        except asyncio.TimeoutError:
            raise MCPError(f"Async tool call {request_id} timed out after {timeout} seconds")
        except Exception as e:
            raise MCPError(f"Async tool call {request_id} failed: {str(e)}")
    
    async def cancel_async_call(self, request_id: str) -> bool:
        """Cancel an async tool call"""
        if request_id not in self.active_requests:
            return False
        
        task = self.active_requests[request_id]
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        del self.active_requests[request_id]
        logger.info(f"Async MCP tool call {request_id} cancelled")
        return True
    
    # Convenience methods for common tool calls
    
    async def get_nutrition_info(self, food_name: str, quantity: float = 1, 
                               unit: str = "serving", **kwargs) -> Dict[str, Any]:
        """Get nutrition information for a food item"""
        return await self.call_tool("get_nutrition_info", {
            "food_name": food_name,
            "quantity": quantity,
            "unit": unit,
            **kwargs
        })
    
    async def search_recipes(self, ingredients: List[str], cuisine: str = "any", 
                           diet_type: str = "any", max_time: int = 60, **kwargs) -> Dict[str, Any]:
        """Search for recipes"""
        return await self.call_tool("search_recipes", {
            "ingredients": ingredients,
            "cuisine": cuisine,
            "diet_type": diet_type,
            "max_time": max_time,
            **kwargs
        })
    
    async def generate_grocery_list(self, meal_plan: Dict[str, Any], 
                                  household_size: int = 1, **kwargs) -> Dict[str, Any]:
        """Generate grocery list from meal plan"""
        return await self.call_tool("generate_grocery_list", {
            "meal_plan": meal_plan,
            "household_size": household_size,
            **kwargs
        })
    
    async def check_grocery_availability(self, items: List[str], location: str, 
                                       store_preference: str = "any", **kwargs) -> Dict[str, Any]:
        """Check grocery availability"""
        return await self.call_tool("check_grocery_availability", {
            "items": items,
            "location": location,
            "store_preference": store_preference,
            **kwargs
        })
    
    async def order_groceries(self, grocery_list: List[str], delivery_address: str,
                             delivery_time: str = "asap", payment_method: str = "card", **kwargs) -> Dict[str, Any]:
        """Order groceries"""
        return await self.call_tool("order_groceries", {
            "grocery_list": grocery_list,
            "delivery_address": delivery_address,
            "delivery_time": delivery_time,
            "payment_method": payment_method,
            **kwargs
        })
    
    async def get_health_insights(self, user_data: Dict[str, Any], 
                                health_metrics: Optional[Dict[str, Any]] = None, 
                                goals: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get health insights"""
        return await self.call_tool("get_health_insights", {
            "user_data": user_data,
            "health_metrics": health_metrics or {},
            "goals": goals or []
        })
    
    async def calculate_calorie_needs(self, age: int, gender: str, weight_kg: float, 
                                    height_cm: float, activity_level: str, goal: str, **kwargs) -> Dict[str, Any]:
        """Calculate daily calorie needs"""
        return await self.call_tool("calculate_calorie_needs", {
            "age": age,
            "gender": gender,
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "activity_level": activity_level,
            "goal": goal,
            **kwargs
        })
    
    async def track_progress(self, goal_type: str, progress_data: Dict[str, Any], 
                           time_period: str = "weekly") -> Dict[str, Any]:
        """Track progress towards goals"""
        return await self.call_tool("track_progress", {
            "user_id": self.user_id,
            "goal_type": goal_type,
            "progress_data": progress_data,
            "time_period": time_period
        })
    
    async def analyze_data(self, data_type: str, time_range: str = "last_30_days", 
                          analysis_type: str = "trends") -> Dict[str, Any]:
        """Analyze user data"""
        return await self.call_tool("analyze_data", {
            "user_id": self.user_id,
            "data_type": data_type,
            "time_range": time_range,
            "analysis_type": analysis_type
        })
    
    def get_call_history(self) -> List[Dict[str, Any]]:
        """Get history of tool calls"""
        return [
            {
                "tool_name": call.tool_name,
                "parameters": call.parameters,
                "timestamp": call.timestamp.isoformat(),
                "request_id": call.request_id,
                "priority": call.priority
            }
            for call in self.call_history
        ]
    
    def get_tool_usage_stats(self) -> Dict[str, int]:
        """Get statistics on tool usage"""
        stats = {}
        for call in self.call_history:
            stats[call.tool_name] = stats.get(call.tool_name, 0) + 1
        return stats
    
    def get_active_requests(self) -> List[str]:
        """Get list of active request IDs"""
        return list(self.active_requests.keys())
    
    async def cleanup(self):
        """Clean up client resources"""
        # Cancel any pending async calls
        for request_id in list(self.active_requests.keys()):
            await self.cancel_async_call(request_id)
        
        logger.info(f"MCP client cleaned up for user {self.user_id}")
    
    def __enter__(self):
        return self
    
    def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()




