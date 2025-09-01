"""
Recipe Generator Agent - Generates recipes based on diet plans
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class RecipeGeneratorAgent(BaseAgent):
    """
    Recipe Generator Agent responsible for:
    - Creating recipes based on diet plans
    - Adapting recipes to dietary restrictions
    - Coordinating with Grocery List Generator
    - Managing recipe database
    """
    
    def __init__(self):
        super().__init__("RecipeGeneratorAgent")
        self.recipe_templates = {}
        self.ingredient_substitutions = {}
        self.meal_categories = ["breakfast", "lunch", "dinner", "snacks"]
        
        # Initialize recipe components
        self._initialize_recipe_templates()
        self._initialize_ingredient_substitutions()
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for recipe generation
        
        Args:
            state: Current workflow state containing diet plan and preferences
            
        Returns:
            Updated state with generated recipes
        """
        try:
            await self.update_status("processing")
            
            # Extract diet plan and user data
            diet_plan = state.get("diet_plan", {})
            user_data = state.get("user_data", {})
            user_id = user_data.get("user_id")
            
            if not user_id:
                raise ValueError("User ID is required for recipe generation")
            
            # Initialize MCP client if available
            if user_id:
                self.initialize_mcp_client(user_id)
            
            # Generate recipes for each meal
            if diet_plan:
                recipes = await self._generate_recipes(user_id, diet_plan, user_data)
                state["recipes"] = recipes
                
                # Generate meal plan
                meal_plan = await self._create_meal_plan(recipes, diet_plan)
                state["meal_plan"] = meal_plan
                
                # Prepare data for Grocery List Generator
                grocery_data = await self._prepare_grocery_data(recipes, meal_plan)
                state["grocery_data"] = grocery_data
            
            await self.increment_success()
            return state
            
        except Exception as e:
            error_response = await self.handle_error(e, "Recipe generation")
            state["recipe_generation_error"] = error_response
            return state
    
    def _initialize_recipe_templates(self):
        """Initialize recipe templates for different meal types"""
        try:
            self.recipe_templates = {
                "breakfast": {
                    "oatmeal_bowl": {
                        "name": "Customizable Oatmeal Bowl",
                        "base_ingredients": ["oats", "milk", "honey"],
                        "optional_additions": ["berries", "nuts", "seeds", "banana"],
                        "cooking_time": "10 minutes",
                        "difficulty": "easy"
                    },
                    "smoothie_bowl": {
                        "name": "Nutrient-Rich Smoothie Bowl",
                        "base_ingredients": ["frozen_fruits", "yogurt", "milk"],
                        "optional_additions": ["granola", "coconut", "chia_seeds"],
                        "cooking_time": "5 minutes",
                        "difficulty": "easy"
                    }
                },
                "lunch": {
                    "quinoa_salad": {
                        "name": "Protein-Packed Quinoa Salad",
                        "base_ingredients": ["quinoa", "vegetables", "protein_source"],
                        "optional_additions": ["dressing", "herbs", "cheese"],
                        "cooking_time": "20 minutes",
                        "difficulty": "easy"
                    },
                    "wraps": {
                        "name": "Healthy Veggie Wraps",
                        "base_ingredients": ["tortilla", "vegetables", "protein"],
                        "optional_additions": ["sauce", "cheese", "avocado"],
                        "cooking_time": "15 minutes",
                        "difficulty": "easy"
                    }
                },
                "dinner": {
                    "stir_fry": {
                        "name": "Quick Vegetable Stir Fry",
                        "base_ingredients": ["vegetables", "protein", "sauce"],
                        "optional_additions": ["rice", "noodles", "garnishes"],
                        "cooking_time": "25 minutes",
                        "difficulty": "medium"
                    },
                    "baked_protein": {
                        "name": "Herb-Roasted Protein with Vegetables",
                        "base_ingredients": ["protein", "vegetables", "herbs"],
                        "optional_additions": ["sauce", "grains", "salad"],
                        "cooking_time": "35 minutes",
                        "difficulty": "medium"
                    }
                },
                "snacks": {
                    "energy_bites": {
                        "name": "Homemade Energy Bites",
                        "base_ingredients": ["dates", "nuts", "oats"],
                        "optional_additions": ["coconut", "chocolate_chips", "seeds"],
                        "cooking_time": "15 minutes",
                        "difficulty": "easy"
                    },
                    "veggie_sticks": {
                        "name": "Fresh Vegetable Sticks with Dip",
                        "base_ingredients": ["vegetables", "yogurt", "herbs"],
                        "optional_additions": ["hummus", "guacamole", "ranch"],
                        "cooking_time": "10 minutes",
                        "difficulty": "easy"
                    }
                }
            }
            
            logger.info("Recipe templates initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize recipe templates: {str(e)}")
    
    def _initialize_ingredient_substitutions(self):
        """Initialize ingredient substitutions for dietary restrictions"""
        try:
            self.ingredient_substitutions = {
                "dairy_free": {
                    "milk": ["almond_milk", "soy_milk", "oat_milk", "coconut_milk"],
                    "yogurt": ["coconut_yogurt", "almond_yogurt", "soy_yogurt"],
                    "cheese": ["nutritional_yeast", "dairy_free_cheese", "avocado"]
                },
                "gluten_free": {
                    "bread": ["gluten_free_bread", "lettuce_wraps", "corn_tortillas"],
                    "pasta": ["quinoa", "rice", "zucchini_noodles", "spaghetti_squash"],
                    "flour": ["almond_flour", "coconut_flour", "rice_flour"]
                },
                "vegan": {
                    "meat": ["tofu", "tempeh", "seitan", "legumes"],
                    "eggs": ["flax_eggs", "chia_eggs", "banana", "applesauce"],
                    "honey": ["maple_syrup", "agave_nectar", "date_syrup"]
                },
                "low_carb": {
                    "rice": ["cauliflower_rice", "broccoli_rice", "zucchini"],
                    "pasta": ["zucchini_noodles", "spaghetti_squash", "cauliflower"],
                    "bread": ["lettuce_wraps", "coconut_wraps", "eggplant_slices"]
                }
            }
            
            logger.info("Ingredient substitutions initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ingredient substitutions: {str(e)}")
    
    async def _generate_recipes(self, user_id: str, diet_plan: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recipes based on diet plan and user preferences"""
        try:
            recipes = {}
            
            # Extract meal information from diet plan
            meals = diet_plan.get("meals", [])
            dietary_restrictions = diet_plan.get("dietary_restrictions", [])
            nutritional_goals = diet_plan.get("nutritional_goals", {})
            
            # Generate recipes for each meal category
            for meal_category in self.meal_categories:
                category_recipes = await self._generate_category_recipes(
                    meal_category, meals, dietary_restrictions, nutritional_goals, user_data
                )
                recipes[meal_category] = category_recipes
            
            # Use MCP tools for enhanced recipe generation if available
            if self.mcp_client:
                try:
                    # Get recipe suggestions from external APIs
                    recipe_suggestions = await self.search_recipes(
                        ingredients=meals,
                        dietary_restrictions=dietary_restrictions
                    )
                    if recipe_suggestions.get("success"):
                        recipes["external_suggestions"] = recipe_suggestions.get("result", {})
                except Exception as e:
                    logger.warning(f"Could not get external recipe suggestions: {str(e)}")
            
            logger.info(f"Generated {sum(len(recs) for recs in recipes.values())} recipes for user {user_id}")
            return recipes
            
        except Exception as e:
            logger.error(f"Failed to generate recipes for user {user_id}: {str(e)}")
            return {}
    
    async def _generate_category_recipes(self, meal_category: str, meals: List[str], 
                                       dietary_restrictions: List[str], nutritional_goals: Dict[str, Any], 
                                       user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recipes for a specific meal category"""
        try:
            category_recipes = []
            
            # Get templates for this category
            templates = self.recipe_templates.get(meal_category, {})
            
            # Generate recipes based on available ingredients and restrictions
            for template_name, template in templates.items():
                recipe = await self._create_recipe_from_template(
                    template_name, template, meals, dietary_restrictions, nutritional_goals, user_data
                )
                if recipe:
                    category_recipes.append(recipe)
            
            # Generate additional custom recipes
            custom_recipes = await self._generate_custom_recipes(
                meal_category, meals, dietary_restrictions, nutritional_goals
            )
            category_recipes.extend(custom_recipes)
            
            return category_recipes
            
        except Exception as e:
            logger.error(f"Failed to generate category recipes for {meal_category}: {str(e)}")
            return []
    
    async def _create_recipe_from_template(self, template_name: str, template: Dict[str, Any], 
                                         meals: List[str], dietary_restrictions: List[str], 
                                         nutritional_goals: Dict[str, Any], user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a recipe from a template"""
        try:
            # Check if template is suitable for dietary restrictions
            if not self._is_template_suitable(template, dietary_restrictions):
                return None
            
            # Adapt ingredients based on restrictions
            adapted_ingredients = self._adapt_ingredients_for_restrictions(
                template["base_ingredients"], dietary_restrictions
            )
            
            # Create recipe
            recipe = {
                "recipe_id": f"recipe_{template_name}_{datetime.utcnow().timestamp()}",
                "name": template["name"],
                "category": template_name,
                "ingredients": adapted_ingredients,
                "optional_ingredients": template["optional_additions"],
                "cooking_time": template["cooking_time"],
                "difficulty": template["difficulty"],
                "dietary_restrictions": dietary_restrictions,
                "nutritional_info": await self._calculate_nutritional_info(adapted_ingredients),
                "instructions": self._generate_cooking_instructions(template_name, adapted_ingredients),
                "servings": 2,
                "tags": self._generate_recipe_tags(template_name, dietary_restrictions)
            }
            
            return recipe
            
        except Exception as e:
            logger.error(f"Failed to create recipe from template {template_name}: {str(e)}")
            return None
    
    def _is_template_suitable(self, template: Dict[str, Any], dietary_restrictions: List[str]) -> bool:
        """Check if template is suitable for dietary restrictions"""
        try:
            # Simple suitability check
            # In production, this would be more sophisticated
            
            if "dairy_free" in dietary_restrictions:
                dairy_ingredients = ["milk", "yogurt", "cheese"]
                if any(ingredient in str(template) for ingredient in dairy_ingredients):
                    return False
            
            if "gluten_free" in dietary_restrictions:
                gluten_ingredients = ["bread", "pasta", "flour"]
                if any(ingredient in str(template) for ingredient in gluten_ingredients):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check template suitability: {str(e)}")
            return True
    
    def _adapt_ingredients_for_restrictions(self, ingredients: List[str], dietary_restrictions: List[str]) -> List[str]:
        """Adapt ingredients based on dietary restrictions"""
        try:
            adapted_ingredients = ingredients.copy()
            
            for restriction in dietary_restrictions:
                if restriction in self.ingredient_substitutions:
                    substitutions = self.ingredient_substitutions[restriction]
                    
                    for i, ingredient in enumerate(adapted_ingredients):
                        if ingredient in substitutions:
                            # Replace with first available substitution
                            adapted_ingredients[i] = substitutions[ingredient][0]
            
            return adapted_ingredients
            
        except Exception as e:
            logger.error(f"Failed to adapt ingredients: {str(e)}")
            return ingredients
    
    async def _calculate_nutritional_info(self, ingredients: List[str]) -> Dict[str, Any]:
        """Calculate nutritional information for recipe"""
        try:
            # This would typically use a nutrition database
            # For now, return estimated values
            
            nutritional_info = {
                "calories": len(ingredients) * 150,  # Rough estimate
                "protein": len(ingredients) * 8,
                "carbohydrates": len(ingredients) * 20,
                "fat": len(ingredients) * 5,
                "fiber": len(ingredients) * 3
            }
            
            return nutritional_info
            
        except Exception as e:
            logger.error(f"Failed to calculate nutritional info: {str(e)}")
            return {}
    
    def _generate_cooking_instructions(self, template_name: str, ingredients: List[str]) -> List[str]:
        """Generate cooking instructions for recipe"""
        try:
            instructions = []
            
            if "oatmeal" in template_name:
                instructions = [
                    "Bring milk to a gentle boil in a saucepan",
                    "Add oats and reduce heat to low",
                    "Cook for 5-7 minutes, stirring occasionally",
                    "Add honey and optional toppings",
                    "Serve hot"
                ]
            elif "smoothie" in template_name:
                instructions = [
                    "Add frozen fruits to blender",
                    "Pour in yogurt and milk",
                    "Blend until smooth",
                    "Pour into bowl and add toppings",
                    "Serve immediately"
                ]
            elif "salad" in template_name:
                instructions = [
                    "Cook quinoa according to package instructions",
                    "Chop vegetables and prepare protein",
                    "Combine all ingredients in a large bowl",
                    "Add dressing and toss gently",
                    "Serve chilled or at room temperature"
                ]
            else:
                instructions = [
                    "Prepare all ingredients as specified",
                    "Follow cooking method for best results",
                    "Adjust seasoning to taste",
                    "Serve when ready"
                ]
            
            return instructions
            
        except Exception as e:
            logger.error(f"Failed to generate cooking instructions: {str(e)}")
            return ["Follow standard cooking methods"]
    
    def _generate_recipe_tags(self, template_name: str, dietary_restrictions: List[str]) -> List[str]:
        """Generate tags for recipe categorization"""
        try:
            tags = [template_name]
            
            # Add dietary restriction tags
            tags.extend(dietary_restrictions)
            
            # Add meal type tags
            if "breakfast" in template_name:
                tags.append("morning")
            elif "lunch" in template_name:
                tags.append("midday")
            elif "dinner" in template_name:
                tags.append("evening")
            elif "snack" in template_name:
                tags.append("quick")
            
            # Add difficulty tags
            if "easy" in template_name:
                tags.append("beginner_friendly")
            elif "medium" in template_name:
                tags.append("intermediate")
            
            return tags
            
        except Exception as e:
            logger.error(f"Failed to generate recipe tags: {str(e)}")
            return []
    
    async def _generate_custom_recipes(self, meal_category: str, meals: List[str], 
                                     dietary_restrictions: List[str], nutritional_goals: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate custom recipes based on available ingredients"""
        try:
            custom_recipes = []
            
            # Simple custom recipe generation
            if meal_category == "breakfast" and "eggs" in meals:
                custom_recipes.append({
                    "recipe_id": f"custom_breakfast_{datetime.utcnow().timestamp()}",
                    "name": "Scrambled Eggs with Vegetables",
                    "category": "custom",
                    "ingredients": ["eggs", "vegetables", "herbs"],
                    "cooking_time": "15 minutes",
                    "difficulty": "easy",
                    "dietary_restrictions": dietary_restrictions,
                    "servings": 1
                })
            
            elif meal_category == "lunch" and "chicken" in meals:
                custom_recipes.append({
                    "recipe_id": f"custom_lunch_{datetime.utcnow().timestamp()}",
                    "name": "Grilled Chicken Salad",
                    "category": "custom",
                    "ingredients": ["chicken", "lettuce", "vegetables", "dressing"],
                    "cooking_time": "25 minutes",
                    "difficulty": "easy",
                    "dietary_restrictions": dietary_restrictions,
                    "servings": 1
                })
            
            return custom_recipes
            
        except Exception as e:
            logger.error(f"Failed to generate custom recipes: {str(e)}")
            return []
    
    async def _create_meal_plan(self, recipes: Dict[str, Any], diet_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive meal plan"""
        try:
            meal_plan = {
                "plan_id": f"meal_plan_{datetime.utcnow().timestamp()}",
                "created_at": datetime.utcnow().isoformat(),
                "duration": "7 days",
                "meals_per_day": 4,
                "daily_plans": {}
            }
            
            # Create daily meal plans
            for day in range(1, 8):
                daily_plan = await self._create_daily_plan(day, recipes, diet_plan)
                meal_plan["daily_plans"][f"day_{day}"] = daily_plan
            
            return meal_plan
            
        except Exception as e:
            logger.error(f"Failed to create meal plan: {str(e)}")
            return {}
    
    async def _create_daily_plan(self, day: int, recipes: Dict[str, Any], diet_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create meal plan for a specific day"""
        try:
            daily_plan = {
                "day": day,
                "breakfast": recipes.get("breakfast", [])[:1],
                "lunch": recipes.get("lunch", [])[:1],
                "dinner": recipes.get("dinner", [])[:1],
                "snacks": recipes.get("snacks", [])[:2],
                "total_calories": 0,
                "nutritional_summary": {}
            }
            
            # Calculate nutritional summary
            all_meals = daily_plan["breakfast"] + daily_plan["lunch"] + daily_plan["dinner"] + daily_plan["snacks"]
            daily_plan["total_calories"] = sum(meal.get("nutritional_info", {}).get("calories", 0) for meal in all_meals)
            
            return daily_plan
            
        except Exception as e:
            logger.error(f"Failed to create daily plan for day {day}: {str(e)}")
            return {}
    
    async def _prepare_grocery_data(self, recipes: Dict[str, Any], meal_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for Grocery List Generator"""
        try:
            grocery_data = {
                "recipes": recipes,
                "meal_plan": meal_plan,
                "ingredients_summary": {},
                "shopping_categories": {}
            }
            
            # Collect all ingredients from recipes
            all_ingredients = []
            for category_recipes in recipes.values():
                for recipe in category_recipes:
                    all_ingredients.extend(recipe.get("ingredients", []))
                    all_ingredients.extend(recipe.get("optional_ingredients", []))
            
            # Count ingredient occurrences
            ingredient_counts = {}
            for ingredient in all_ingredients:
                ingredient_counts[ingredient] = ingredient_counts.get(ingredient, 0) + 1
            
            grocery_data["ingredients_summary"] = ingredient_counts
            
            # Categorize ingredients for shopping
            grocery_data["shopping_categories"] = self._categorize_ingredients(ingredient_counts)
            
            return grocery_data
            
        except Exception as e:
            logger.error(f"Failed to prepare grocery data: {str(e)}")
            return {}
    
    def _categorize_ingredients(self, ingredient_counts: Dict[str, int]) -> Dict[str, List[str]]:
        """Categorize ingredients for shopping organization"""
        try:
            categories = {
                "proteins": [],
                "vegetables": [],
                "fruits": [],
                "grains": [],
                "dairy_alternatives": [],
                "pantry_items": [],
                "spices_herbs": []
            }
            
            # Simple categorization logic
            for ingredient, count in ingredient_counts.items():
                if ingredient in ["chicken", "fish", "tofu", "eggs"]:
                    categories["proteins"].append(ingredient)
                elif ingredient in ["lettuce", "tomatoes", "carrots", "broccoli"]:
                    categories["vegetables"].append(ingredient)
                elif ingredient in ["apples", "bananas", "berries"]:
                    categories["fruits"].append(ingredient)
                elif ingredient in ["oats", "quinoa", "rice"]:
                    categories["grains"].append(ingredient)
                elif ingredient in ["almond_milk", "coconut_yogurt"]:
                    categories["dairy_alternatives"].append(ingredient)
                elif ingredient in ["honey", "olive_oil", "vinegar"]:
                    categories["pantry_items"].append(ingredient)
                else:
                    categories["spices_herbs"].append(ingredient)
            
            return categories
            
        except Exception as e:
            logger.error(f"Failed to categorize ingredients: {str(e)}")
            return {}
    
    async def get_recipes(self, user_id: str) -> Dict[str, Any]:
        """Get recipes for a user"""
        try:
            # This would typically retrieve from database
            # For now, return empty dict
            return {}
        except Exception as e:
            logger.error(f"Failed to get recipes for user {user_id}: {str(e)}")
            return {}
    
    async def get_meal_plan(self, user_id: str) -> Dict[str, Any]:
        """Get meal plan for a user"""
        try:
            # This would typically retrieve from database
            # For now, return empty dict
            return {}
        except Exception as e:
            logger.error(f"Failed to get meal plan for user {user_id}: {str(e)}")
            return {}




