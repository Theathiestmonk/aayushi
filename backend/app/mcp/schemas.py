"""
MCP Schemas - Pydantic models for data validation and serialization
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

class ToolCategory(str, Enum):
    """Categories for MCP tools"""
    NUTRITION = "nutrition"
    RECIPES = "recipes"
    GROCERY = "grocery"
    HEALTH = "health"
    ORDERING = "ordering"
    TRACKING = "tracking"
    ANALYSIS = "analysis"
    EXTERNAL = "external"

class ParameterType(str, Enum):
    """Types for tool parameters"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"

class ToolParameter(BaseModel):
    """Schema for tool parameter definition"""
    name: str = Field(..., description="Parameter name")
    type: ParameterType = Field(..., description="Parameter data type")
    description: str = Field(..., description="Parameter description")
    required: bool = Field(default=False, description="Whether parameter is required")
    default: Optional[Any] = Field(default=None, description="Default value")
    enum: Optional[List[Any]] = Field(default=None, description="Allowed values")
    minimum: Optional[Union[int, float]] = Field(default=None, description="Minimum value")
    maximum: Optional[Union[int, float]] = Field(default=None, description="Maximum value")
    pattern: Optional[str] = Field(default=None, description="Regex pattern for validation")

class MCPTool(BaseModel):
    """Schema for MCP tool definition"""
    name: str = Field(..., description="Unique tool name")
    description: str = Field(..., description="Tool description")
    category: ToolCategory = Field(..., description="Tool category")
    parameters: Dict[str, ToolParameter] = Field(..., description="Tool parameters")
    required_params: List[str] = Field(..., description="Required parameter names")
    version: str = Field(default="1.0.0", description="Tool version")
    author: str = Field(default="AI Dietitian System", description="Tool author")
    tags: List[str] = Field(default_factory=list, description="Tool tags")
    
    @validator('required_params')
    def validate_required_params(cls, v, values):
        """Ensure required params exist in parameters dict"""
        if 'parameters' in values:
            param_names = set(values['parameters'].keys())
            missing = [p for p in v if p not in param_names]
            if missing:
                raise ValueError(f"Required parameters not found in parameters dict: {missing}")
        return v

class MCPCall(BaseModel):
    """Schema for MCP tool call request"""
    tool_name: str = Field(..., description="Name of the tool to call")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")
    user_id: str = Field(..., description="User ID making the call")
    session_id: str = Field(..., description="Session ID for tracking")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Call timestamp")
    request_id: Optional[str] = Field(default=None, description="Unique request ID")
    priority: int = Field(default=1, description="Call priority (1-10)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ToolExecutionResult(BaseModel):
    """Schema for tool execution result"""
    success: bool = Field(..., description="Whether execution was successful")
    result: Optional[Any] = Field(default=None, description="Tool execution result")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time_ms: Optional[float] = Field(default=None, description="Execution time in milliseconds")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class MCPResponse(BaseModel):
    """Schema for MCP response"""
    success: bool = Field(..., description="Overall success status")
    tool_name: str = Field(..., description="Name of the executed tool")
    result: ToolExecutionResult = Field(..., description="Tool execution result")
    timestamp: datetime = Field(..., description="Response timestamp")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracking")
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ToolUsageStats(BaseModel):
    """Schema for tool usage statistics"""
    tool_name: str = Field(..., description="Tool name")
    total_calls: int = Field(default=0, description="Total number of calls")
    successful_calls: int = Field(default=0, description="Number of successful calls")
    failed_calls: int = Field(default=0, description="Number of failed calls")
    average_execution_time_ms: float = Field(default=0.0, description="Average execution time")
    last_used: Optional[datetime] = Field(default=None, description="Last usage timestamp")
    error_rate: float = Field(default=0.0, description="Error rate percentage")
    
    @validator('error_rate')
    def calculate_error_rate(cls, v, values):
        """Calculate error rate based on total and failed calls"""
        if values.get('total_calls', 0) > 0:
            return (values.get('failed_calls', 0) / values.get('total_calls', 1)) * 100
        return 0.0

class SessionInfo(BaseModel):
    """Schema for session information"""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation time")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity time")
    tool_calls: List[MCPCall] = Field(default_factory=list, description="Tool calls in this session")
    active: bool = Field(default=True, description="Whether session is active")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }




