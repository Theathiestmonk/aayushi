"""
Grocery List Generator Agent - Creates grocery lists from meal plans
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class GroceryListAgent(BaseAgent):
    """
    Grocery List Generator Agent responsible for:
    - Creating grocery lists from meal plans
    - Organizing items by category
    - Estimating quantities and costs
    - Coordinating with Grocery Ordering Agent
    """
    
    def __init__(self):
        super().__init__("GroceryListAgent")
        self.grocery_categories = {
            "proteins": ["meat", "fish", "poultry", "eggs", "tofu", "legumes"],
            "vegetables": ["leafy_greens", "root_vegetables", "cruciferous", "nightshades"],
            "fruits": ["berries", "citrus", "tropical", "stone_fruits"],
            "grains": ["whole_grains", "pasta", "bread", "cereals"],
            "dairy": ["milk", "yogurt", "cheese", "butter"],
            "pantry": ["oils", "vinegars", "spices", "herbs", "condiments"],
            "frozen": ["frozen_vegetables", "frozen_fruits", "frozen_meals"]
        }
        
        self.quantity_estimates = {
            "proteins": {"per_serving": 0.25, "unit": "pounds"},
            "vegetables": {"per_serving": 0.5, "unit": "cups"},
            "fruits": {"per_serving": 0.5, "unit": "pieces"},
            "grains": {"per_serving": 0.5, "unit": "cups"},
            "dairy": {"per_serving": 0.5, "unit": "cups"},
            "pantry": {"per_serving": 0.1, "unit": "tablespoons"},
            "frozen": {"per_serving": 0.5, "unit": "cups"}
        }
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for grocery list generation
        
        Args:
            state: Current workflow state containing meal plan and grocery data
            
        Returns:
            Updated state with grocery list
        """
        try:
            await self.update_status("processing")
            
            # Extract grocery data and meal plan
            grocery_data = state.get("grocery_data", {})
            meal_plan = state.get("meal_plan", {})
            user_data = state.get("user_data", {})
            user_id = user_data.get("user_id")
            
            if not user_id:
                raise ValueError("User ID is required for grocery list generation")
            
            # Initialize MCP client if available
            if user_id:
                self.initialize_mcp_client(user_id)
            
            # Generate grocery list
            if grocery_data and meal_plan:
                grocery_list = await self._generate_grocery_list(user_id, grocery_data, meal_plan)
                state["grocery_list"] = grocery_list
                
                # Organize by shopping categories
                organized_list = await self._organize_grocery_list(grocery_list)
                state["organized_grocery_list"] = organized_list
                
                # Estimate costs
                cost_estimate = await self._estimate_grocery_costs(grocery_list)
                state["grocery_cost_estimate"] = cost_estimate
                
                # Prepare data for Grocery Ordering Agent
                ordering_data = await self._prepare_ordering_data(grocery_list, organized_list, cost_estimate)
                state["ordering_data"] = ordering_data
            
            await self.increment_success()
            return state
            
        except Exception as e:
            error_response = await self.handle_error(e, "Grocery list generation")
            state["grocery_list_error"] = error_response
            return state
    
    async def _generate_grocery_list(self, user_id: str, grocery_data: Dict[str, Any], meal_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive grocery list from meal plan"""
        try:
            ingredients_summary = grocery_data.get("ingredients_summary", {})
            shopping_categories = grocery_data.get("shopping_categories", {})
            
            grocery_list = {
                "list_id": f"grocery_{user_id}_{datetime.utcnow().timestamp()}",
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "meal_plan_duration": meal_plan.get("duration", "7 days"),
                "total_items": 0,
                "estimated_cost": 0.0,
                "items": []
            }
            
            # Process ingredients by category
            for category, ingredients in shopping_categories.items():
                for ingredient in ingredients:
                    item = await self._create_grocery_item(
                        ingredient, ingredients_summary.get(ingredient, 1), category
                    )
                    if item:
                        grocery_list["items"].append(item)
                        grocery_list["total_items"] += 1
            
            # Use MCP tools for enhanced grocery planning if available
            if self.mcp_client:
                try:
                    # Get grocery store information
                    store_info = await self.find_grocery_stores(location="user_location")
                    if store_info.get("success"):
                        grocery_list["store_recommendations"] = store_info.get("result", {})
                except Exception as e:
                    logger.warning(f"Could not get store information: {str(e)}")
            
            logger.info(f"Generated grocery list with {grocery_list['total_items']} items for user {user_id}")
            return grocery_list
            
        except Exception as e:
            logger.error(f"Failed to generate grocery list for user {user_id}: {str(e)}")
            return {}
    
    async def _create_grocery_item(self, ingredient: str, quantity_needed: int, category: str) -> Optional[Dict[str, Any]]:
        """Create a grocery item with quantity and pricing information"""
        try:
            # Determine quantity and unit
            quantity_info = self._calculate_quantity(ingredient, quantity_needed, category)
            
            # Create item
            item = {
                "ingredient": ingredient,
                "category": category,
                "quantity": quantity_info["quantity"],
                "unit": quantity_info["unit"],
                "priority": self._determine_priority(category, ingredient),
                "estimated_price": self._estimate_item_price(ingredient, quantity_info["quantity"]),
                "notes": self._generate_item_notes(ingredient, category),
                "alternatives": self._suggest_alternatives(ingredient, category)
            }
            
            return item
            
        except Exception as e:
            logger.error(f"Failed to create grocery item for {ingredient}: {str(e)}")
            return None
    
    def _calculate_quantity(self, ingredient: str, quantity_needed: int, category: str) -> Dict[str, Any]:
        """Calculate appropriate quantity for grocery item"""
        try:
            # Get base quantity estimate for category
            base_estimate = self.quantity_estimates.get(category, {"per_serving": 0.5, "unit": "units"})
            
            # Calculate total quantity needed
            total_quantity = quantity_needed * base_estimate["per_serving"]
            
            # Round to reasonable amounts
            if base_estimate["unit"] == "pounds":
                total_quantity = round(total_quantity, 2)
            elif base_estimate["unit"] == "cups":
                total_quantity = round(total_quantity, 1)
            else:
                total_quantity = round(total_quantity)
            
            return {
                "quantity": total_quantity,
                "unit": base_estimate["unit"]
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate quantity for {ingredient}: {str(e)}")
            return {"quantity": 1, "unit": "units"}
    
    def _determine_priority(self, category: str, ingredient: str) -> str:
        """Determine priority level for grocery item"""
        try:
            # High priority items
            high_priority = ["milk", "bread", "eggs", "vegetables", "fruits"]
            if ingredient in high_priority:
                return "high"
            
            # Medium priority items
            medium_priority = ["meat", "fish", "poultry", "grains"]
            if ingredient in medium_priority:
                return "medium"
            
            # Low priority items (can be substituted or skipped)
            return "low"
            
        except Exception as e:
            logger.error(f"Failed to determine priority for {ingredient}: {str(e)}")
            return "medium"
    
    def _estimate_item_price(self, ingredient: str, quantity: float) -> float:
        """Estimate price for grocery item"""
        try:
            # Base price estimates (in USD)
            base_prices = {
                "milk": 4.50,
                "bread": 3.00,
                "eggs": 5.00,
                "chicken": 8.00,
                "vegetables": 2.50,
                "fruits": 3.00,
                "grains": 2.00,
                "dairy": 4.00
            }
            
            # Get base price for ingredient category
            base_price = base_prices.get(ingredient, 3.00)
            
            # Adjust for quantity
            estimated_price = base_price * quantity
            
            return round(estimated_price, 2)
            
        except Exception as e:
            logger.error(f"Failed to estimate price for {ingredient}: {str(e)}")
            return 3.00
    
    def _generate_item_notes(self, ingredient: str, category: str) -> str:
        """Generate helpful notes for grocery item"""
        try:
            notes = ""
            
            if category == "proteins":
                if ingredient in ["chicken", "fish"]:
                    notes = "Look for fresh, not frozen"
                elif ingredient == "tofu":
                    notes = "Check expiration date"
            
            elif category == "vegetables":
                if ingredient in ["lettuce", "spinach"]:
                    notes = "Choose crisp, vibrant leaves"
                elif ingredient in ["tomatoes", "bell_peppers"]:
                    notes = "Select firm, unblemished pieces"
            
            elif category == "fruits":
                if ingredient in ["bananas", "avocados"]:
                    notes = "Choose based on ripeness preference"
                elif ingredient == "berries":
                    notes = "Check for mold, avoid crushed packages"
            
            return notes
            
        except Exception as e:
            logger.error(f"Failed to generate notes for {ingredient}: {str(e)}")
            return ""
    
    def _suggest_alternatives(self, ingredient: str, category: str) -> List[str]:
        """Suggest alternative ingredients"""
        try:
            alternatives = []
            
            if category == "proteins":
                if ingredient == "chicken":
                    alternatives = ["turkey", "pork", "beef"]
                elif ingredient == "fish":
                    alternatives = ["shrimp", "salmon", "tilapia"]
            
            elif category == "vegetables":
                if ingredient == "broccoli":
                    alternatives = ["cauliflower", "asparagus", "green_beans"]
                elif ingredient == "spinach":
                    alternatives = ["kale", "arugula", "mixed_greens"]
            
            elif category == "grains":
                if ingredient == "quinoa":
                    alternatives = ["rice", "couscous", "farro"]
                elif ingredient == "oats":
                    alternatives = ["granola", "cereal", "bread"]
            
            return alternatives
            
        except Exception as e:
            logger.error(f"Failed to suggest alternatives for {ingredient}: {str(e)}")
            return []
    
    async def _organize_grocery_list(self, grocery_list: Dict[str, Any]) -> Dict[str, Any]:
        """Organize grocery list by shopping categories"""
        try:
            organized_list = {
                "list_id": grocery_list.get("list_id"),
                "user_id": grocery_list.get("user_id"),
                "organized_by": "shopping_categories",
                "categories": {}
            }
            
            # Group items by category
            for item in grocery_list.get("items", []):
                category = item.get("category", "other")
                
                if category not in organized_list["categories"]:
                    organized_list["categories"][category] = {
                        "category_name": category,
                        "items": [],
                        "total_items": 0,
                        "estimated_cost": 0.0
                    }
                
                organized_list["categories"][category]["items"].append(item)
                organized_list["categories"][category]["total_items"] += 1
                organized_list["categories"][category]["estimated_cost"] += item.get("estimated_price", 0)
            
            # Sort categories by priority
            organized_list["categories"] = dict(sorted(
                organized_list["categories"].items(),
                key=lambda x: self._get_category_priority(x[0])
            ))
            
            return organized_list
            
        except Exception as e:
            logger.error(f"Failed to organize grocery list: {str(e)}")
            return {}
    
    def _get_category_priority(self, category: str) -> int:
        """Get priority order for shopping categories"""
        try:
            priority_order = {
                "proteins": 1,
                "vegetables": 2,
                "fruits": 3,
                "dairy": 4,
                "grains": 5,
                "pantry": 6,
                "frozen": 7
            }
            
            return priority_order.get(category, 8)
            
        except Exception as e:
            logger.error(f"Failed to get category priority for {category}: {str(e)}")
            return 8
    
    async def _estimate_grocery_costs(self, grocery_list: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate total grocery costs"""
        try:
            items = grocery_list.get("items", [])
            
            total_cost = sum(item.get("estimated_price", 0) for item in items)
            category_costs = {}
            
            # Calculate costs by category
            for item in items:
                category = item.get("category", "other")
                if category not in category_costs:
                    category_costs[category] = 0
                category_costs[category] += item.get("estimated_price", 0)
            
            cost_estimate = {
                "total_estimated_cost": round(total_cost, 2),
                "cost_by_category": category_costs,
                "average_item_cost": round(total_cost / len(items), 2) if items else 0,
                "budget_recommendations": self._generate_budget_recommendations(total_cost)
            }
            
            return cost_estimate
            
        except Exception as e:
            logger.error(f"Failed to estimate grocery costs: {str(e)}")
            return {}
    
    def _generate_budget_recommendations(self, total_cost: float) -> List[str]:
        """Generate budget-saving recommendations"""
        try:
            recommendations = []
            
            if total_cost > 100:
                recommendations.append("Consider buying in bulk for frequently used items")
                recommendations.append("Look for store brand alternatives")
                recommendations.append("Plan meals around seasonal produce")
            
            elif total_cost > 75:
                recommendations.append("Check for coupons and sales")
                recommendations.append("Consider meal prep to reduce waste")
            
            else:
                recommendations.append("Great budget planning! Keep up the good work")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate budget recommendations: {str(e)}")
            return []
    
    async def _prepare_ordering_data(self, grocery_list: Dict[str, Any], organized_list: Dict[str, Any], cost_estimate: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for Grocery Ordering Agent"""
        try:
            ordering_data = {
                "grocery_list": grocery_list,
                "organized_list": organized_list,
                "cost_estimate": cost_estimate,
                "ordering_ready": True,
                "delivery_preferences": {
                    "preferred_delivery_time": "anytime",
                    "delivery_address": "user_address",
                    "contact_number": "user_phone"
                },
                "payment_method": "user_payment_method",
                "special_instructions": "Handle with care, check expiration dates"
            }
            
            return ordering_data
            
        except Exception as e:
            logger.error(f"Failed to prepare ordering data: {str(e)}")
            return {}
    
    async def get_grocery_list(self, user_id: str) -> Dict[str, Any]:
        """Get grocery list for a user"""
        try:
            # This would typically retrieve from database
            # For now, return empty dict
            return {}
        except Exception as e:
            logger.error(f"Failed to get grocery list for user {user_id}: {str(e)}")
            return {}
    
    async def get_organized_list(self, user_id: str) -> Dict[str, Any]:
        """Get organized grocery list for a user"""
        try:
            # This would typically retrieve from database
            # For now, return empty dict
            return {}
        except Exception as e:
            logger.error(f"Failed to get organized list for user {user_id}: {str(e)}")
            return {}




