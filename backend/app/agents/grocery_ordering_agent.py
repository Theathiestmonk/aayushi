"""
Grocery Ordering Agent - Manages grocery ordering and delivery
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class GroceryOrderingAgent(BaseAgent):
    """
    Grocery Ordering Agent responsible for:
    - Processing grocery orders
    - Managing delivery services (Zepto, Blinkit)
    - Handling payment processing
    - Tracking delivery status
    """
    
    def __init__(self):
        super().__init__("GroceryOrderingAgent")
        self.delivery_services = ["zepto", "blinkit", "instamart", "dunzo"]
        self.order_statuses = ["pending", "confirmed", "preparing", "out_for_delivery", "delivered", "cancelled"]
        self.payment_methods = ["card", "upi", "net_banking", "wallet", "cod"]
        
        # Mock delivery service data
        self.delivery_service_info = {
            "zepto": {"delivery_time": "10 minutes", "min_order": 99, "delivery_fee": 0},
            "blinkit": {"delivery_time": "10 minutes", "min_order": 99, "delivery_fee": 0},
            "instamart": {"delivery_time": "15 minutes", "min_order": 149, "delivery_fee": 20},
            "dunzo": {"delivery_time": "20 minutes", "min_order": 199, "delivery_fee": 30}
        }
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]):
        """
        Main processing method for grocery ordering
        
        Args:
            state: Current workflow state containing ordering data
            
        Returns:
            Updated state with order details and confirmation
        """
        try:
            await self.update_status("processing")
            
            # Extract ordering data
            ordering_data = state.get("ordering_data", {})
            user_data = state.get("user_data", {})
            user_id = user_data.get("user_id")
            
            if not user_id:
                raise ValueError("User ID is required for grocery ordering")
            
            # Initialize MCP client if available
            if user_id:
                self.initialize_mcp_client(user_id)
            
            # Process grocery order
            if ordering_data and ordering_data.get("ordering_ready"):
                order_result = await self._process_grocery_order(user_id, ordering_data, user_data)
                state["grocery_order"] = order_result
                
                # Generate order confirmation
                if order_result.get("order_created"):
                    confirmation = await self._generate_order_confirmation(order_result)
                    state["order_confirmation"] = confirmation
                    
                    # Prepare delivery tracking
                    tracking_info = await self._prepare_delivery_tracking(order_result)
                    state["delivery_tracking"] = tracking_info
            
            await self.increment_success()
            return state
            
        except Exception as e:
            error_response = await self.handle_error(e, "Grocery ordering")
            state["grocery_ordering_error"] = error_response
            return state
    
    async def _process_grocery_order(self, user_id: str, ordering_data: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the grocery order"""
        try:
            grocery_list = ordering_data.get("grocery_list", {})
            cost_estimate = ordering_data.get("cost_estimate", {})
            
            # Select delivery service
            selected_service = await self._select_delivery_service(ordering_data, user_data)
            
            # Create order
            order = await self._create_order(user_id, grocery_list, cost_estimate, selected_service)
            
            # Process payment
            payment_result = await self._process_payment(order, user_data)
            
            # Send order to delivery service
            delivery_result = await self._send_order_to_service(order, selected_service)
            
            order_result = {
                "order_id": order.get("order_id"),
                "user_id": user_id,
                "order_created": True,
                "order_details": order,
                "delivery_service": selected_service,
                "payment_status": payment_result.get("status"),
                "delivery_status": delivery_result.get("status"),
                "estimated_delivery": delivery_result.get("estimated_delivery"),
                "tracking_id": delivery_result.get("tracking_id")
            }
            
            # Use MCP tools for enhanced ordering if available
            if self.mcp_client:
                try:
                    # Get delivery service recommendations
                    service_recs = await self.find_grocery_stores(location="user_location")
                    if service_recs.get("success"):
                        order_result["service_recommendations"] = service_recs.get("result", {})
                except Exception as e:
                    logger.warning(f"Could not get service recommendations: {str(e)}")
            
            logger.info(f"Processed grocery order {order.get('order_id')} for user {user_id}")
            return order_result
            
        except Exception as e:
            logger.error(f"Failed to process grocery order for user {user_id}: {str(e)}")
            return {"order_created": False, "error": str(e)}
    
    async def _select_delivery_service(self, ordering_data: Dict[str, Any], user_data: Dict[str, Any]) -> str:
        """Select the best delivery service for the order"""
        try:
            grocery_list = ordering_data.get("grocery_list", {})
            cost_estimate = ordering_data.get("cost_estimate", {})
            total_cost = cost_estimate.get("total_estimated_cost", 0)
            
            # Filter services based on order requirements
            available_services = []
            
            for service, info in self.delivery_service_info.items():
                if total_cost >= info["min_order"]:
                    available_services.append({
                        "service": service,
                        "delivery_time": info["delivery_time"],
                        "delivery_fee": info["delivery_fee"],
                        "total_cost": total_cost + info["delivery_fee"]
                    })
            
            if not available_services:
                # If no service meets minimum order, select the one with lowest minimum
                available_services = [{
                    "service": "zepto",
                    "delivery_time": "10 minutes",
                    "delivery_fee": 0,
                    "total_cost": total_cost
                }]
            
            # Select service based on user preferences
            user_preference = user_data.get("preferred_delivery_service", "zepto")
            
            # Check if user preference is available
            for service_info in available_services:
                if service_info["service"] == user_preference:
                    return user_preference
            
            # If user preference not available, select fastest delivery
            fastest_service = min(available_services, key=lambda x: int(x["delivery_time"].split()[0]))
            return fastest_service["service"]
            
        except Exception as e:
            logger.error(f"Failed to select delivery service: {str(e)}")
            return "zepto"
    
    async def _create_order(self, user_id: str, grocery_list: Dict[str, Any], cost_estimate: Dict[str, Any], delivery_service: str) -> Dict[str, Any]:
        """Create the grocery order"""
        try:
            order = {
                "order_id": f"order_{user_id}_{datetime.utcnow().timestamp()}",
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "delivery_service": delivery_service,
                "items": grocery_list.get("items", []),
                "total_items": grocery_list.get("total_items", 0),
                "subtotal": cost_estimate.get("total_estimated_cost", 0),
                "delivery_fee": self.delivery_service_info.get(delivery_service, {}).get("delivery_fee", 0),
                "total_amount": cost_estimate.get("total_estimated_cost", 0) + 
                              self.delivery_service_info.get(delivery_service, {}).get("delivery_fee", 0),
                "status": "pending",
                "estimated_delivery": (datetime.utcnow() + timedelta(minutes=10)).isoformat()
            }
            
            return order
            
        except Exception as e:
            logger.error(f"Failed to create order: {str(e)}")
            return {}
    
    async def _process_payment(self, order: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment for the order"""
        try:
            # Mock payment processing
            payment_result = {
                "payment_id": f"payment_{order.get('order_id')}",
                "amount": order.get("total_amount", 0),
                "currency": "INR",
                "method": user_data.get("payment_method", "card"),
                "status": "success",
                "transaction_id": f"txn_{datetime.utcnow().timestamp()}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return payment_result
            
        except Exception as e:
            logger.error(f"Failed to process payment: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def _send_order_to_service(self, order: Dict[str, Any], delivery_service: str) -> Dict[str, Any]:
        """Send order to the selected delivery service"""
        try:
            # Mock delivery service integration
            delivery_result = {
                "service_order_id": f"{delivery_service}_{order.get('order_id')}",
                "status": "confirmed",
                "estimated_delivery": order.get("estimated_delivery"),
                "tracking_id": f"track_{delivery_service}_{datetime.utcnow().timestamp()}",
                "delivery_partner": f"{delivery_service}_partner",
                "special_instructions": "Handle with care, check expiration dates"
            }
            
            return delivery_result
            
        except Exception as e:
            logger.error(f"Failed to send order to service: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def _generate_order_confirmation(self, order_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate order confirmation for the user"""
        try:
            order_details = order_result.get("order_details", {})
            delivery_service = order_result.get("delivery_service", "")
            
            confirmation = {
                "order_id": order_details.get("order_id"),
                "confirmation_number": f"CONF-{order_details.get('order_id')[-8:]}",
                "timestamp": datetime.utcnow().isoformat(),
                "delivery_service": delivery_service,
                "estimated_delivery": order_result.get("estimated_delivery"),
                "order_summary": {
                    "total_items": order_details.get("total_items", 0),
                    "subtotal": order_details.get("subtotal", 0),
                    "delivery_fee": order_details.get("delivery_fee", 0),
                    "total_amount": order_details.get("total_amount", 0)
                },
                "delivery_address": "user_delivery_address",
                "contact_number": "user_contact_number",
                "tracking_id": order_result.get("tracking_id"),
                "next_steps": [
                    "Order confirmed and being prepared",
                    "You'll receive updates on preparation and delivery",
                    "Track your order using the tracking ID"
                ]
            }
            
            return confirmation
            
        except Exception as e:
            logger.error(f"Failed to generate order confirmation: {str(e)}")
            return {}
    
    async def _prepare_delivery_tracking(self, order_result: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare delivery tracking information"""
        try:
            tracking_info = {
                "order_id": order_result.get("order_id"),
                "tracking_id": order_result.get("tracking_id"),
                "delivery_service": order_result.get("delivery_service"),
                "current_status": order_result.get("delivery_status"),
                "estimated_delivery": order_result.get("estimated_delivery"),
                "status_updates": [
                    {
                        "status": "order_confirmed",
                        "timestamp": datetime.utcnow().isoformat(),
                        "description": "Order confirmed and sent to delivery service"
                    }
                ],
                "delivery_timeline": [
                    {
                        "stage": "order_confirmed",
                        "estimated_time": "0 minutes",
                        "description": "Order received and confirmed"
                    },
                    {
                        "stage": "preparing",
                        "estimated_time": "5 minutes",
                        "description": "Items being prepared and packed"
                    },
                    {
                        "stage": "out_for_delivery",
                        "estimated_time": "10 minutes",
                        "description": "Order out for delivery"
                    },
                    {
                        "stage": "delivered",
                        "estimated_time": "10-15 minutes",
                        "description": "Order delivered to your doorstep"
                    }
                ]
            }
            
            return tracking_info
            
        except Exception as e:
            logger.error(f"Failed to prepare delivery tracking: {str(e)}")
            return {}
    
    async def track_delivery(self, tracking_id: str) -> Dict[str, Any]:
        """Track delivery status"""
        try:
            # Mock delivery tracking
            # In production, this would integrate with delivery service APIs
            
            tracking_status = {
                "tracking_id": tracking_id,
                "current_status": "out_for_delivery",
                "last_update": datetime.utcnow().isoformat(),
                "estimated_delivery": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
                "delivery_partner": "delivery_partner_name",
                "location": "Near delivery location",
                "status_history": [
                    {
                        "status": "order_confirmed",
                        "timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
                        "description": "Order confirmed"
                    },
                    {
                        "status": "preparing",
                        "timestamp": (datetime.utcnow() - timedelta(minutes=8)).isoformat(),
                        "description": "Items being prepared"
                    },
                    {
                        "status": "out_for_delivery",
                        "timestamp": (datetime.utcnow() - timedelta(minutes=3)).isoformat(),
                        "description": "Order out for delivery"
                    }
                ]
            }
            
            return tracking_status
            
        except Exception as e:
            logger.error(f"Failed to track delivery: {str(e)}")
            return {}
    
    async def cancel_order(self, order_id: str, user_id: str) -> Dict[str, Any]:
        """Cancel a grocery order"""
        try:
            # Mock order cancellation
            cancellation_result = {
                "order_id": order_id,
                "user_id": user_id,
                "cancelled_at": datetime.utcnow().isoformat(),
                "status": "cancelled",
                "refund_status": "processing",
                "refund_amount": 0,  # Would be calculated based on order status
                "cancellation_reason": "user_requested",
                "message": "Order cancelled successfully. Refund will be processed within 3-5 business days."
            }
            
            return cancellation_result
            
        except Exception as e:
            logger.error(f"Failed to cancel order: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def get_order_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get order history for a user"""
        try:
            # Mock order history
            # In production, this would retrieve from database
            
            order_history = [
                {
                    "order_id": f"order_{user_id}_1",
                    "date": (datetime.utcnow() - timedelta(days=7)).isoformat(),
                    "status": "delivered",
                    "total_amount": 450.00,
                    "delivery_service": "zepto"
                },
                {
                    "order_id": f"order_{user_id}_2",
                    "date": (datetime.utcnow() - timedelta(days=14)).isoformat(),
                    "status": "delivered",
                    "total_amount": 320.00,
                    "delivery_service": "blinkit"
                }
            ]
            
            return order_history
            
        except Exception as e:
            logger.error(f"Failed to get order history for user {user_id}: {str(e)}")
            return []
    
    async def get_delivery_services(self, location: str) -> List[Dict[str, Any]]:
        """Get available delivery services for a location"""
        try:
            available_services = []
            
            for service, info in self.delivery_service_info.items():
                available_services.append({
                    "service_name": service.title(),
                    "delivery_time": info["delivery_time"],
                    "minimum_order": info["min_order"],
                    "delivery_fee": info["delivery_fee"],
                    "available": True
                })
            
            return available_services
            
        except Exception as e:
            logger.error(f"Failed to get delivery services: {str(e)}")
            return []
    
    async def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """Get detailed information about an order"""
        try:
            # Mock order details
            # In production, this would retrieve from database
            
            order_details = {
                "order_id": order_id,
                "user_id": "user_123",
                "created_at": datetime.utcnow().isoformat(),
                "delivery_service": "zepto",
                "items": [
                    {"name": "Milk", "quantity": 1, "price": 45.00},
                    {"name": "Bread", "quantity": 1, "price": 35.00},
                    {"name": "Eggs", "quantity": 1, "price": 60.00}
                ],
                "total_items": 3,
                "subtotal": 140.00,
                "delivery_fee": 0.00,
                "total_amount": 140.00,
                "status": "confirmed",
                "estimated_delivery": (datetime.utcnow() + timedelta(minutes=10)).isoformat()
            }
            
            return order_details
            
        except Exception as e:
            logger.error(f"Failed to get order details for {order_id}: {str(e)}")
            return {}




