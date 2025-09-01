"""
Ordering Tools - MCP tools for grocery ordering and delivery services
"""

from typing import List
from ..schemas import MCPTool, ToolParameter, ToolCategory, ParameterType

class OrderingTools:
    """Tools for grocery ordering and delivery services"""
    
    def get_tools(self) -> List[MCPTool]:
        """Get all ordering-related tools"""
        return [
            self._get_grocery_ordering_tool(),
            self._get_delivery_tracking_tool(),
            self._get_payment_processing_tool()
        ]
    
    def _get_grocery_ordering_tool(self) -> MCPTool:
        """Place grocery orders through delivery services"""
        return MCPTool(
            name="order_groceries",
            description="Place grocery orders through external delivery services like Zepto or Blinkit",
            category=ToolCategory.ORDERING,
            parameters={
                "grocery_list": ToolParameter(
                    name="grocery_list",
                    type=ParameterType.ARRAY,
                    description="List of grocery items to order",
                    required=True
                ),
                "delivery_address": ToolParameter(
                    name="delivery_address",
                    type=ParameterType.STRING,
                    description="Delivery address",
                    required=True
                ),
                "delivery_time": ToolParameter(
                    name="delivery_time",
                    type=ParameterType.STRING,
                    description="Preferred delivery time",
                    required=False,
                    default="asap"
                ),
                "payment_method": ToolParameter(
                    name="payment_method",
                    type=ParameterType.STRING,
                    description="Payment method",
                    required=False,
                    default="card"
                ),
                "service_provider": ToolParameter(
                    name="service_provider",
                    type=ParameterType.STRING,
                    description="Delivery service provider",
                    required=False,
                    enum=["zepto", "blinkit", "any"]
                )
            },
            required_params=["grocery_list", "delivery_address"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["ordering", "grocery", "delivery", "payment"]
        )
    
    def _get_delivery_tracking_tool(self) -> MCPTool:
        """Track delivery status"""
        return MCPTool(
            name="track_delivery",
            description="Track the status of grocery deliveries",
            category=ToolCategory.ORDERING,
            parameters={
                "order_id": ToolParameter(
                    name="order_id",
                    type=ParameterType.STRING,
                    description="Order ID to track",
                    required=True
                ),
                "service_provider": ToolParameter(
                    name="service_provider",
                    type=ParameterType.STRING,
                    description="Delivery service provider",
                    required=False
                )
            },
            required_params=["order_id"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["tracking", "delivery", "orders", "status"]
        )
    
    def _get_payment_processing_tool(self) -> MCPTool:
        """Process payments for orders"""
        return MCPTool(
            name="process_payment",
            description="Process payments for grocery orders",
            category=ToolCategory.ORDERING,
            parameters={
                "order_id": ToolParameter(
                    name="order_id",
                    type=ParameterType.STRING,
                    description="Order ID for payment",
                    required=True
                ),
                "amount": ToolParameter(
                    name="amount",
                    type=ParameterType.FLOAT,
                    description="Payment amount",
                    required=True
                ),
                "payment_method": ToolParameter(
                    name="payment_method",
                    type=ParameterType.STRING,
                    description="Payment method to use",
                    required=True
                ),
                "payment_details": ToolParameter(
                    name="payment_details",
                    type=ParameterType.OBJECT,
                    description="Payment method details",
                    required=False
                )
            },
            required_params=["order_id", "amount", "payment_method"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["payment", "processing", "orders", "financial"]
        )

