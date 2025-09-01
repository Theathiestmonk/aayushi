"""
Tool Registry for managing MCP tools and their handlers
"""

import logging
from typing import Dict, Any, Callable, List, Optional
from .mcp_server import mcp_server
from .schemas import MCPTool
from .exceptions import ToolNotFoundError

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Registry for managing MCP tools and their handlers"""
    
    def __init__(self):
        self.registered_tools: Dict[str, Dict[str, Any]] = {}
        self.tool_handlers: Dict[str, Callable] = {}
        self.tool_categories: Dict[str, List[str]] = {}
        self.tool_metadata: Dict[str, Dict[str, Any]] = {}
    
    def register_tool(self, tool: MCPTool, handler: Optional[Callable] = None):
        """Register a new tool with optional handler"""
        try:
            # Register with MCP server
            mcp_server.register_tool(tool)
            
            # Store in registry
            self.registered_tools[tool.name] = {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category.value,
                "version": tool.version,
                "author": tool.author,
                "tags": tool.tags
            }
            
            # Store metadata
            self.tool_metadata[tool.name] = {
                "parameters": tool.parameters,
                "required_params": tool.required_params,
                "created_at": tool.created_at if hasattr(tool, 'created_at') else None
            }
            
            # Add to category index
            category = tool.category.value
            if category not in self.tool_categories:
                self.tool_categories[category] = []
            self.tool_categories[category].append(tool.name)
            
            # Register handler if provided
            if handler:
                self.register_handler(tool.name, handler)
            
            logger.info(f"✅ Tool registered successfully: {tool.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register tool {tool.name}: {str(e)}")
            return False
    
    def register_handler(self, tool_name: str, handler: Callable):
        """Register a handler for a tool"""
        try:
            if tool_name not in self.registered_tools:
                raise ToolNotFoundError(tool_name)
            
            mcp_server.register_handler(tool_name, handler)
            self.tool_handlers[tool_name] = handler
            logger.info(f"✅ Handler registered for tool: {tool_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to register handler for {tool_name}: {str(e)}")
            return False
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool"""
        if tool_name not in self.registered_tools:
            return None
        
        tool_info = self.registered_tools[tool_name].copy()
        tool_info.update(self.tool_metadata.get(tool_name, {}))
        
        # Add handler status
        tool_info["has_handler"] = tool_name in self.tool_handlers
        
        return tool_info
    
    def list_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all tools, optionally filtered by category"""
        if category:
            if category not in self.tool_categories:
                return []
            tool_names = self.tool_categories[category]
            return [
                self.get_tool_info(name) for name in tool_names
                if self.get_tool_info(name) is not None
            ]
        
        return [
            self.get_tool_info(name) for name in self.registered_tools.keys()
            if self.get_tool_info(name) is not None
        ]
    
    def get_tool_categories(self) -> List[str]:
        """Get list of all tool categories"""
        return sorted(list(self.tool_categories.keys()))
    
    def get_tools_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get tools filtered by tag"""
        matching_tools = []
        
        for tool_name, tool_info in self.registered_tools.items():
            if tag in tool_info.get("tags", []):
                tool_detail = self.get_tool_info(tool_name)
                if tool_detail:
                    matching_tools.append(tool_detail)
        
        return matching_tools
    
    def search_tools(self, query: str) -> List[Dict[str, Any]]:
        """Search tools by name, description, or tags"""
        query_lower = query.lower()
        matching_tools = []
        
        for tool_name, tool_info in self.registered_tools.items():
            # Search in name
            if query_lower in tool_name.lower():
                tool_detail = self.get_tool_info(tool_name)
                if tool_detail:
                    matching_tools.append(tool_detail)
                continue
            
            # Search in description
            if query_lower in tool_info.get("description", "").lower():
                tool_detail = self.get_tool_info(tool_name)
                if tool_detail and tool_detail not in matching_tools:
                    matching_tools.append(tool_detail)
                continue
            
            # Search in tags
            if any(query_lower in tag.lower() for tag in tool_info.get("tags", [])):
                tool_detail = self.get_tool_info(tool_name)
                if tool_detail and tool_detail not in matching_tools:
                    matching_tools.append(tool_detail)
        
        return matching_tools
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Get comprehensive tool statistics"""
        total_tools = len(self.registered_tools)
        tools_with_handlers = len(self.tool_handlers)
        
        # Category distribution
        category_distribution = {
            category: len(tools) for category, tools in self.tool_categories.items()
        }
        
        # Tag distribution
        tag_distribution = {}
        for tool_info in self.registered_tools.values():
            for tag in tool_info.get("tags", []):
                tag_distribution[tag] = tag_distribution.get(tag, 0) + 1
        
        return {
            "total_tools": total_tools,
            "tools_with_handlers": tools_with_handlers,
            "tools_without_handlers": total_tools - tools_with_handlers,
            "handler_coverage": (tools_with_handlers / total_tools * 100) if total_tools > 0 else 0,
            "category_distribution": category_distribution,
            "tag_distribution": tag_distribution,
            "categories": list(self.tool_categories.keys())
        }
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool"""
        try:
            if tool_name not in self.registered_tools:
                return False
            
            # Remove from MCP server
            if tool_name in mcp_server.tools:
                del mcp_server.tools[tool_name]
            
            # Remove from registry
            tool_info = self.registered_tools[tool_name]
            category = tool_info["category"]
            
            # Remove from category index
            if category in self.tool_categories and tool_name in self.tool_categories[category]:
                self.tool_categories[category].remove(tool_name)
                if not self.tool_categories[category]:
                    del self.tool_categories[category]
            
            # Remove from registries
            del self.registered_tools[tool_name]
            if tool_name in self.tool_handlers:
                del self.tool_handlers[tool_name]
            if tool_name in self.tool_metadata:
                del self.tool_metadata[tool_name]
            
            logger.info(f"✅ Tool unregistered: {tool_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to unregister tool {tool_name}: {str(e)}")
            return False
    
    def validate_tool_registration(self) -> Dict[str, Any]:
        """Validate tool registration integrity"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check for tools without handlers
        tools_without_handlers = [
            name for name in self.registered_tools.keys()
            if name not in self.tool_handlers
        ]
        
        if tools_without_handlers:
            validation_results["warnings"].append(
                f"Tools without handlers: {', '.join(tools_without_handlers)}"
            )
        
        # Check for orphaned handlers
        orphaned_handlers = [
            name for name in self.tool_handlers.keys()
            if name not in self.registered_tools
        ]
        
        if orphaned_handlers:
            validation_results["errors"].append(
                f"Orphaned handlers: {', '.join(orphaned_handlers)}"
            )
            validation_results["valid"] = False
        
        # Check category consistency
        for category, tool_names in self.tool_categories.items():
            for tool_name in tool_names:
                if tool_name not in self.registered_tools:
                    validation_results["errors"].append(
                        f"Tool {tool_name} in category {category} not found in registry"
                    )
                    validation_results["valid"] = False
        
        return validation_results
    
    def export_tool_specifications(self) -> Dict[str, Any]:
        """Export tool specifications for external use"""
        specifications = {
            "version": "1.0.0",
            "exported_at": None,  # Will be set by caller
            "total_tools": len(self.registered_tools),
            "categories": {},
            "tools": {}
        }
        
        # Export by category
        for category, tool_names in self.tool_categories.items():
            specifications["categories"][category] = {
                "tool_count": len(tool_names),
                "tools": tool_names
            }
        
        # Export tool details
        for tool_name in self.registered_tools.keys():
            tool_info = self.get_tool_info(tool_name)
            if tool_info:
                specifications["tools"][tool_name] = tool_info
        
        return specifications

# Global tool registry instance
tool_registry = ToolRegistry()




