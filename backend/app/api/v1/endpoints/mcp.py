"""
MCP (Model Context Protocol) endpoints for tool management
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from app.mcp.mcp_server import mcp_server
from app.mcp.tool_registry import tool_registry
from app.mcp.schemas import MCPCall, MCPResponse, ToolCategory
from app.mcp.exceptions import MCPError, ToolNotFoundError, InvalidParametersError

router = APIRouter()

class ToolCallRequest(BaseModel):
    """Request model for tool execution"""
    tool_name: str
    parameters: Dict[str, Any]
    user_id: str
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    priority: int = 1

class ToolCallResponse(BaseModel):
    """Response model for tool execution"""
    success: bool
    result: Optional[Dict[str, Any]] = None
    tool_name: str
    timestamp: str
    request_id: str
    session_id: str
    user_id: str
    error: Optional[str] = None

class ToolInfo(BaseModel):
    """Tool information model"""
    name: str
    description: str
    category: str
    version: str
    author: str
    tags: List[str]
    has_handler: bool
    parameters: Dict[str, Any]
    required_params: List[str]

class ToolSearchRequest(BaseModel):
    """Request model for tool search"""
    query: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 20

@router.get("/tools", response_model=List[Dict[str, Any]])
async def get_available_tools():
    """Get list of all available MCP tools"""
    try:
        return mcp_server.get_available_tools()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve tools: {str(e)}")

@router.get("/tools/{category}", response_model=List[Dict[str, Any]])
async def get_tools_by_category(category: str):
    """Get tools filtered by category"""
    try:
        # Validate category
        valid_categories = [cat.value for cat in ToolCategory]
        if category not in valid_categories:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
            )
        
        return mcp_server.get_tools_by_category(ToolCategory(category))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve tools: {str(e)}")

@router.get("/tools/details/{tool_name}", response_model=Optional[Dict[str, Any]])
async def get_tool_details(tool_name: str):
    """Get detailed information about a specific tool"""
    try:
        tool_details = mcp_server.get_tool_details(tool_name)
        if not tool_details:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        return tool_details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve tool details: {str(e)}")

@router.post("/execute", response_model=ToolCallResponse)
async def execute_tool(request: ToolCallRequest):
    """Execute an MCP tool call"""
    try:
        # Generate request ID if not provided
        if not request.request_id:
            request.request_id = str(uuid.uuid4())
        
        # Generate session ID if not provided
        if not request.session_id:
            request.session_id = f"session_{request.user_id}_{uuid.uuid4().hex[:8]}"
        
        # Create MCP call
        from app.mcp.schemas import MCPCall
        tool_call = MCPCall(
            tool_name=request.tool_name,
            parameters=request.parameters,
            user_id=request.user_id,
            session_id=request.session_id,
            request_id=request.request_id,
            priority=request.priority
        )
        
        # Execute the tool
        result = await mcp_server.execute_tool(tool_call)
        
        # Convert to response format
        return ToolCallResponse(
            success=result.success,
            result=result.result.result if result.success else None,
            tool_name=result.tool_name,
            timestamp=result.timestamp,
            request_id=result.request_id,
            session_id=result.session_id,
            user_id=result.user_id,
            error=result.result.error if not result.success else None
        )
        
    except ToolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidParametersError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MCPError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

@router.post("/execute/async")
async def execute_tool_async(request: ToolCallRequest, background_tasks: BackgroundTasks):
    """Execute an MCP tool call asynchronously"""
    try:
        # Generate request ID if not provided
        if not request.request_id:
            request.request_id = str(uuid.uuid4())
        
        # Generate session ID if not provided
        if not request.session_id:
            request.session_id = f"session_{request.user_id}_{uuid.uuid4().hex[:8]}"
        
        # Create MCP call
        from app.mcp.schemas import MCPCall
        tool_call = MCPCall(
            tool_name=request.tool_name,
            parameters=request.parameters,
            user_id=request.user_id,
            session_id=request.session_id,
            request_id=request.request_id,
            priority=request.priority
        )
        
        # Execute in background
        background_tasks.add_task(mcp_server.execute_tool, tool_call)
        
        return {
            "success": True,
            "message": "Tool execution started asynchronously",
            "request_id": request.request_id,
            "session_id": request.session_id,
            "status": "processing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start async execution: {str(e)}")

@router.get("/categories")
async def get_tool_categories():
    """Get list of all tool categories"""
    try:
        return tool_registry.get_tool_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve categories: {str(e)}")

@router.get("/search", response_model=List[ToolInfo])
async def search_tools(query: str, category: Optional[str] = None, limit: int = 20):
    """Search tools by query, category, or tags"""
    try:
        if category:
            # Search within specific category
            tools = tool_registry.list_tools(category)
            # Filter by query
            matching_tools = [
                tool for tool in tools
                if query.lower() in tool.get("name", "").lower() or
                   query.lower() in tool.get("description", "").lower() or
                   any(query.lower() in tag.lower() for tag in tool.get("tags", []))
            ]
        else:
            # Search across all tools
            matching_tools = tool_registry.search_tools(query)
        
        # Limit results
        limited_tools = matching_tools[:limit]
        
        # Convert to ToolInfo format
        tool_infos = []
        for tool in limited_tools:
            tool_infos.append(ToolInfo(
                name=tool["name"],
                description=tool["description"],
                category=tool["category"],
                version=tool["version"],
                author=tool["author"],
                tags=tool["tags"],
                has_handler=tool.get("has_handler", False),
                parameters=tool.get("parameters", {}),
                required_params=tool.get("required_params", [])
            ))
        
        return tool_infos
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/statistics")
async def get_tool_statistics():
    """Get comprehensive tool statistics"""
    try:
        return tool_registry.get_tool_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")

@router.get("/server/status")
async def get_server_status():
    """Get MCP server status and health information"""
    try:
        return mcp_server.get_server_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve server status: {str(e)}")

@router.get("/server/health")
async def get_server_health():
    """Get MCP server health status"""
    try:
        stats = mcp_server.get_server_stats()
        return {
            "status": stats["server_status"]["health"],
            "uptime_seconds": stats["server_status"]["uptime_seconds"],
            "tools_count": stats["tools"]["total"],
            "active_sessions": stats["sessions"]["active"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve health status: {str(e)}")

@router.post("/tools/register")
async def register_tool(tool_data: Dict[str, Any]):
    """Register a new tool (admin only)"""
    try:
        # This would typically require admin authentication
        # For now, we'll just return a message
        return {
            "message": "Tool registration endpoint - requires admin authentication",
            "note": "Use the tool registry directly in code for development"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool registration failed: {str(e)}")

@router.delete("/tools/{tool_name}")
async def unregister_tool(tool_name: str):
    """Unregister a tool (admin only)"""
    try:
        # This would typically require admin authentication
        success = tool_registry.unregister_tool(tool_name)
        if success:
            return {"message": f"Tool '{tool_name}' unregistered successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool unregistration failed: {str(e)}")

@router.get("/validation")
async def validate_tool_registration():
    """Validate tool registration integrity"""
    try:
        return tool_registry.validate_tool_registration()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.get("/export")
async def export_tool_specifications():
    """Export tool specifications for external use"""
    try:
        specs = tool_registry.export_tool_specifications()
        specs["exported_at"] = datetime.utcnow().isoformat()
        return specs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

