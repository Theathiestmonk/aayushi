"""
Health Tools - MCP tools for health insights and recommendations
"""

from typing import List
from ..schemas import MCPTool, ToolParameter, ToolCategory, ParameterType

class HealthTools:
    """Tools for health insights and recommendations"""
    
    def get_tools(self) -> List[MCPTool]:
        """Get all health-related tools"""
        return [
            self._get_health_insights_tool(),
            self._get_goal_tracking_tool(),
            self._get_wellness_recommendations_tool()
        ]
    
    def _get_health_insights_tool(self) -> MCPTool:
        """Get health insights based on user data"""
        return MCPTool(
            name="get_health_insights",
            description="Analyze user data and provide health insights and recommendations",
            category=ToolCategory.HEALTH,
            parameters={
                "user_data": ToolParameter(
                    name="user_data",
                    type=ParameterType.OBJECT,
                    description="User profile and health data",
                    required=True
                ),
                "health_metrics": ToolParameter(
                    name="health_metrics",
                    type=ParameterType.OBJECT,
                    description="Current health metrics and measurements",
                    required=False
                ),
                "goals": ToolParameter(
                    name="goals",
                    type=ParameterType.ARRAY,
                    description="User health and fitness goals",
                    required=False
                )
            },
            required_params=["user_data"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["health", "insights", "analysis", "recommendations"]
        )
    
    def _get_goal_tracking_tool(self) -> MCPTool:
        """Track progress towards health goals"""
        return MCPTool(
            name="track_goals",
            description="Track progress towards health and fitness goals",
            category=ToolCategory.HEALTH,
            parameters={
                "goal_type": ToolParameter(
                    name="goal_type",
                    type=ParameterType.STRING,
                    description="Type of goal to track",
                    required=True,
                    enum=["weight", "fitness", "nutrition", "wellness"]
                ),
                "current_progress": ToolParameter(
                    name="current_progress",
                    type=ParameterType.OBJECT,
                    description="Current progress data",
                    required=True
                ),
                "target_values": ToolParameter(
                    name="target_values",
                    type=ParameterType.OBJECT,
                    description="Target values for the goal",
                    required=False
                )
            },
            required_params=["goal_type", "current_progress"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["goals", "tracking", "progress", "health"]
        )
    
    def _get_wellness_recommendations_tool(self) -> MCPTool:
        """Get wellness recommendations"""
        return MCPTool(
            name="get_wellness_recommendations",
            description="Get personalized wellness recommendations based on user profile",
            category=ToolCategory.HEALTH,
            parameters={
                "user_profile": ToolParameter(
                    name="user_profile",
                    type=ParameterType.OBJECT,
                    description="User health profile and preferences",
                    required=True
                ),
                "focus_area": ToolParameter(
                    name="focus_area",
                    type=ParameterType.STRING,
                    description="Area of wellness to focus on",
                    required=False,
                    enum=["sleep", "stress", "energy", "mood", "overall"]
                )
            },
            required_params=["user_profile"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["wellness", "recommendations", "lifestyle", "health"]
        )




