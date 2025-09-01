"""
Base Agent Class - Common functionality for all specialized agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
import asyncio
from datetime import datetime
import json

from app.core.config import settings

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base class for all specialized agents in the system
    """
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.status = "initialized"
        self.last_activity = datetime.utcnow()
        self.error_count = 0
        self.success_count = 0
        
        # Initialize OpenAI client if available
        self.openai_client = None
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info(f"✅ OpenAI client initialized for {agent_name}")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI client not available for {agent_name}: {str(e)}")
        
        # Initialize MCP client
        self.mcp_client = None
    
    def initialize_mcp_client(self, user_id: str, session_id: Optional[str] = None):
        """Initialize MCP client for this agent"""
        try:
            from app.mcp.mcp_client import MCPClient
            self.mcp_client = MCPClient(user_id, session_id)
            logger.info(f"✅ MCP client initialized for {self.agent_name}")
        except Exception as e:
            logger.warning(f"⚠️ MCP client not available for {self.agent_name}: {str(e)}")
    
    async def use_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Use an MCP tool through the client"""
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized. Call initialize_mcp_client first.")
        
        return await self.mcp_client.call_tool(tool_name, parameters)
    
    async def use_mcp_tool_async(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Use an MCP tool asynchronously"""
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized. Call initialize_mcp_client first.")
        
        return await self.mcp_client.call_tool_async(tool_name, parameters)
    
    async def get_mcp_result(self, request_id: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Get result from async MCP tool call"""
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized. Call initialize_mcp_client first.")
        
        return await self.mcp_client.get_async_result(request_id, timeout)
    
    # Convenience methods for common MCP tools
    
    async def get_nutrition_info(self, food_name: str, quantity: float = 1, unit: str = "serving") -> Dict[str, Any]:
        """Get nutrition information for a food item using MCP"""
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized")
        return await self.mcp_client.get_nutrition_info(food_name, quantity, unit)
    
    async def search_recipes(self, ingredients: List[str], **kwargs) -> Dict[str, Any]:
        """Search for recipes using MCP"""
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized")
        return await self.mcp_client.search_recipes(ingredients, **kwargs)
    
    async def generate_grocery_list(self, meal_plan: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate grocery list using MCP"""
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized")
        return await self.mcp_client.generate_grocery_list(meal_plan, **kwargs)
    
    async def order_groceries(self, grocery_list: List[str], delivery_address: str, **kwargs) -> Dict[str, Any]:
        """Order groceries using MCP"""
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized")
        return await self.mcp_client.order_groceries(grocery_list, delivery_address, **kwargs)
    
    async def get_health_insights(self, user_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Get health insights using MCP"""
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized")
        return await self.mcp_client.get_health_insights(user_data, **kwargs)
    
    async def calculate_calorie_needs(self, **kwargs) -> Dict[str, Any]:
        """Calculate calorie needs using MCP"""
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized")
        return await self.mcp_client.calculate_calorie_needs(**kwargs)
    
    async def track_progress(self, goal_type: str, progress_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Track progress using MCP"""
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized")
        return await self.mcp_client.track_progress(goal_type, progress_data, **kwargs)
    
    async def analyze_data(self, data_type: str, **kwargs) -> Dict[str, Any]:
        """Analyze data using MCP"""
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized")
        return await self.mcp_client.analyze_data(data_type, **kwargs)
    
    @abstractmethod
    async def process(self, state) -> Any:
        """
        Main processing method that each agent must implement
        
        Args:
            state: Current state from the workflow
            
        Returns:
            Processed result
        """
        pass
    
    async def get_status(self) -> str:
        """Get current status of the agent"""
        return self.status
    
    async def call_openai(self, prompt: str, system_message: str = None, max_tokens: int = None) -> str:
        """
        Make a call to OpenAI API
        
        Args:
            prompt: User prompt
            system_message: System message for context
            max_tokens: Maximum tokens for response
            
        Returns:
            AI response
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI client not available")
        
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            response = self.openai_client.chat.completions.create(
                model=getattr(settings, 'OPENAI_MODEL', 'gpt-4-turbo-preview'),
                messages=messages,
                max_tokens=max_tokens or getattr(settings, 'OPENAI_MAX_TOKENS', 4000),
                temperature=getattr(settings, 'OPENAI_TEMPERATURE', 0.7)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise
    
    async def validate_input(self, required_fields: List[str], input_data: Dict[str, Any]) -> bool:
        """
        Validate input data against required fields
        
        Args:
            required_fields: List of required field names
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        missing_fields = [field for field in required_fields if field not in input_data]
        if missing_fields:
            logger.warning(f"Missing required fields: {missing_fields}")
            return False
        return True
    
    async def handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """
        Handle errors gracefully and return error response
        
        Args:
            error: The exception that occurred
            context: Additional context about the error
            
        Returns:
            Error response dictionary
        """
        self.error_count += 1
        self.status = "error"
        
        error_response = {
            "success": False,
            "error": str(error),
            "context": context,
            "agent": self.agent_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.error(f"Error in {self.agent_name}: {str(error)} - Context: {context}")
        return error_response
    
    async def update_status(self, new_status: str):
        """Update agent status"""
        self.status = new_status
        self.last_activity = datetime.utcnow()
        logger.debug(f"Agent {self.agent_name} status updated to: {new_status}")
    
    async def increment_success(self):
        """Increment success counter"""
        self.success_count += 1
        self.status = "active"
        self.last_activity = datetime.utcnow()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the agent"""
        return {
            "agent_name": self.agent_name,
            "status": self.status,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "last_activity": self.last_activity.isoformat(),
            "success_rate": self.success_count / (self.success_count + self.error_count) if (self.success_count + self.error_count) > 0 else 0,
            "mcp_client_available": self.mcp_client is not None
        }
    
    async def cleanup(self):
        """Cleanup resources when agent is shut down"""
        try:
            self.status = "shutdown"
            
            # Cleanup MCP client if available
            if self.mcp_client:
                await self.mcp_client.cleanup()
            
            logger.info(f"Agent {self.agent_name} cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup of {self.agent_name}: {str(e)}")
