"""
Grocery Tools - MCP tools for grocery list management and store integration
"""

from typing import List
from ..schemas import MCPTool, ToolParameter, ToolCategory, ParameterType

class GroceryTools:
    """Tools for grocery list management and store integration"""
    
    def get_tools(self) -> List[MCPTool]:
        """Get all grocery-related tools"""
        return [
            self._get_grocery_list_generator_tool(),
            self._get_store_finder_tool(),
            self._get_price_comparison_tool(),
            self._get_inventory_tracker_tool()
        ]
    
    def _get_grocery_list_generator_tool(self) -> MCPTool:
        """Generate grocery lists from meal plans"""
        return MCPTool(
            name="generate_grocery_list",
            description="Generate a comprehensive grocery list from meal plans and recipes",
            category=ToolCategory.GROCERY,
            parameters={
                "meal_plan": ToolParameter(
                    name="meal_plan",
                    type=ParameterType.OBJECT,
                    description="Meal plan to generate list from",
                    required=True
                ),
                "household_size": ToolParameter(
                    name="household_size",
                    type=ParameterType.INTEGER,
                    description="Number of people in household",
                    required=False,
                    default=1
                ),
                "budget_limit": ToolParameter(
                    name="budget_limit",
                    type=ParameterType.FLOAT,
                    description="Budget limit for groceries",
                    required=False
                ),
                "preferred_stores": ToolParameter(
                    name="preferred_stores",
                    type=ParameterType.ARRAY,
                    description="Preferred grocery stores",
                    required=False
                )
            },
            required_params=["meal_plan"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["grocery", "list", "meal_plan", "shopping"]
        )
    
    def _get_store_finder_tool(self) -> MCPTool:
        """Find nearby grocery stores"""
        return MCPTool(
            name="find_grocery_stores",
            description="Find nearby grocery stores based on location and preferences",
            category=ToolCategory.GROCERY,
            parameters={
                "location": ToolParameter(
                    name="location",
                    type=ParameterType.STRING,
                    description="Location (address, coordinates, or city)",
                    required=True
                ),
                "radius_km": ToolParameter(
                    name="radius_km",
                    type=ParameterType.FLOAT,
                    description="Search radius in kilometers",
                    required=False,
                    default=10.0
                ),
                "store_types": ToolParameter(
                    name="store_types",
                    type=ParameterType.ARRAY,
                    description="Types of stores to include",
                    required=False,
                    default=["supermarket", "grocery", "convenience"]
                ),
                "features": ToolParameter(
                    name="features",
                    type=ParameterType.ARRAY,
                    description="Desired store features",
                    required=False
                )
            },
            required_params=["location"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["stores", "location", "search", "grocery"]
        )
    
    def _get_price_comparison_tool(self) -> MCPTool:
        """Compare prices across different stores"""
        return MCPTool(
            name="compare_prices",
            description="Compare grocery prices across different stores",
            category=ToolCategory.GROCERY,
            parameters={
                "items": ToolParameter(
                    name="items",
                    type=ParameterType.ARRAY,
                    description="List of grocery items to compare",
                    required=True
                ),
                "stores": ToolParameter(
                    name="stores",
                    type=ParameterType.ARRAY,
                    description="Stores to compare prices at",
                    required=True
                ),
                "location": ToolParameter(
                    name="location",
                    type=ParameterType.STRING,
                    description="User location for delivery costs",
                    required=False
                )
            },
            required_params=["items", "stores"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["prices", "comparison", "stores", "savings"]
        )
    
    def _get_inventory_tracker_tool(self) -> MCPTool:
        """Track household grocery inventory"""
        return MCPTool(
            name="track_inventory",
            description="Track household grocery inventory and suggest restocking",
            category=ToolCategory.GROCERY,
            parameters={
                "action": ToolParameter(
                    name="action",
                    type=ParameterType.STRING,
                    description="Action to perform",
                    required=True,
                    enum=["check", "add", "remove", "update"]
                ),
                "items": ToolParameter(
                    name="items",
                    type=ParameterType.ARRAY,
                    description="Items to track",
                    required=False
                ),
                "quantities": ToolParameter(
                    name="quantities",
                    type=ParameterType.OBJECT,
                    description="Quantities for items",
                    required=False
                )
            },
            required_params=["action"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["inventory", "tracking", "management", "restocking"]
        )




