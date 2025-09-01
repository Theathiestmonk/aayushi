"""
Tracking Tools - MCP tools for progress monitoring and data analysis
"""

from typing import List
from ..schemas import MCPTool, ToolParameter, ToolCategory, ParameterType

class TrackingTools:
    """Tools for progress monitoring and data analysis"""
    
    def get_tools(self) -> List[MCPTool]:
        """Get all tracking-related tools"""
        return [
            self._get_progress_tracking_tool(),
            self._get_data_analysis_tool(),
            self._get_goal_assessment_tool()
        ]
    
    def _get_progress_tracking_tool(self) -> MCPTool:
        """Track user progress towards goals"""
        return MCPTool(
            name="track_progress",
            description="Track user progress towards health and fitness goals",
            category=ToolCategory.TRACKING,
            parameters={
                "user_id": ToolParameter(
                    name="user_id",
                    type=ParameterType.STRING,
                    description="User ID to track progress for",
                    required=True
                ),
                "goal_type": ToolParameter(
                    name="goal_type",
                    type=ParameterType.STRING,
                    description="Type of goal to track",
                    required=True,
                    enum=["weight", "fitness", "nutrition", "wellness"]
                ),
                "progress_data": ToolParameter(
                    name="progress_data",
                    type=ParameterType.OBJECT,
                    description="Current progress data",
                    required=True
                ),
                "time_period": ToolParameter(
                    name="time_period",
                    type=ParameterType.STRING,
                    description="Time period for tracking",
                    required=False,
                    default="weekly"
                )
            },
            required_params=["user_id", "goal_type", "progress_data"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["tracking", "progress", "goals", "monitoring"]
        )
    
    def _get_data_analysis_tool(self) -> MCPTool:
        """Analyze user data and provide insights"""
        return MCPTool(
            name="analyze_data",
            description="Analyze user data and provide insights and recommendations",
            category=ToolCategory.TRACKING,
            parameters={
                "user_id": ToolParameter(
                    name="user_id",
                    type=ParameterType.STRING,
                    description="User ID for data analysis",
                    required=True
                ),
                "data_type": ToolParameter(
                    name="data_type",
                    type=ParameterType.STRING,
                    description="Type of data to analyze",
                    required=True,
                    enum=["nutrition", "fitness", "weight", "overall"]
                ),
                "time_range": ToolParameter(
                    name="time_range",
                    type=ParameterType.STRING,
                    description="Time range for analysis",
                    required=False,
                    default="last_30_days"
                ),
                "analysis_type": ToolParameter(
                    name="analysis_type",
                    type=ParameterType.STRING,
                    description="Type of analysis to perform",
                    required=False,
                    default="trends"
                )
            },
            required_params=["user_id", "data_type"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["analysis", "data", "insights", "trends"]
        )
    
    def _get_goal_assessment_tool(self) -> MCPTool:
        """Assess progress towards goals"""
        return MCPTool(
            name="assess_goals",
            description="Assess progress towards health and fitness goals",
            category=ToolCategory.TRACKING,
            parameters={
                "user_id": ToolParameter(
                    name="user_id",
                    type=ParameterType.STRING,
                    description="User ID for goal assessment",
                    required=True
                ),
                "goal_id": ToolParameter(
                    name="goal_id",
                    type=ParameterType.STRING,
                    description="Specific goal ID to assess",
                    required=False
                ),
                "assessment_criteria": ToolParameter(
                    name="assessment_criteria",
                    type=ParameterType.OBJECT,
                    description="Criteria for goal assessment",
                    required=False
                )
            },
            required_params=["user_id"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["assessment", "goals", "progress", "evaluation"]
        )




