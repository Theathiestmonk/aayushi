"""
Recipe Tools - MCP tools for recipe generation and management
"""

from typing import List
from ..schemas import MCPTool, ToolParameter, ToolCategory, ParameterType

class RecipeTools:
    """Tools for recipe generation and management"""
    
    def get_tools(self) -> List[MCPTool]:
        """Get all recipe-related tools"""
        return [
            self._get_recipe_search_tool(),
            self._get_recipe_generation_tool(),
            self._get_recipe_adaptation_tool(),
            self._get_meal_planning_tool()
        ]
    
    def _get_recipe_search_tool(self) -> MCPTool:
        """Search for recipes based on various criteria"""
        return MCPTool(
            name="search_recipes",
            description="Search for recipes based on ingredients, cuisine, diet type, and cooking time",
            category=ToolCategory.RECIPES,
            parameters={
                "ingredients": ToolParameter(
                    name="ingredients",
                    type=ParameterType.ARRAY,
                    description="List of available ingredients",
                    required=True
                ),
                "cuisine": ToolParameter(
                    name="cuisine",
                    type=ParameterType.STRING,
                    description="Preferred cuisine style",
                    required=False
                ),
                "diet_type": ToolParameter(
                    name="diet_type",
                    type=ParameterType.STRING,
                    description="Dietary requirements",
                    required=False
                ),
                "max_time": ToolParameter(
                    name="max_time",
                    type=ParameterType.INTEGER,
                    description="Maximum cooking time in minutes",
                    required=False
                ),
                "difficulty": ToolParameter(
                    name="difficulty",
                    type=ParameterType.STRING,
                    description="Cooking difficulty level",
                    required=False,
                    enum=["easy", "medium", "hard"]
                )
            },
            required_params=["ingredients"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["recipes", "search", "ingredients", "cuisine"]
        )
    
    def _get_recipe_generation_tool(self) -> MCPTool:
        """Generate custom recipes based on requirements"""
        return MCPTool(
            name="generate_recipe",
            description="Generate a custom recipe based on available ingredients and preferences",
            category=ToolCategory.RECIPES,
            parameters={
                "ingredients": ToolParameter(
                    name="ingredients",
                    type=ParameterType.ARRAY,
                    description="Available ingredients",
                    required=True
                ),
                "target_calories": ToolParameter(
                    name="target_calories",
                    type=ParameterType.INTEGER,
                    description="Target calories for the recipe",
                    required=False
                ),
                "servings": ToolParameter(
                    name="servings",
                    type=ParameterType.INTEGER,
                    description="Number of servings",
                    required=False,
                    default=2
                ),
                "cooking_skill": ToolParameter(
                    name="cooking_skill",
                    type=ParameterType.STRING,
                    description="Cooking skill level",
                    required=False,
                    enum=["beginner", "intermediate", "advanced"]
                )
            },
            required_params=["ingredients"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["recipe", "generation", "custom", "ingredients"]
        )
    
    def _get_recipe_adaptation_tool(self) -> MCPTool:
        """Adapt recipes for dietary restrictions"""
        return MCPTool(
            name="adapt_recipe",
            description="Adapt an existing recipe for dietary restrictions or preferences",
            category=ToolCategory.RECIPES,
            parameters={
                "original_recipe": ToolParameter(
                    name="original_recipe",
                    type=ParameterType.OBJECT,
                    description="Original recipe to adapt",
                    required=True
                ),
                "dietary_restrictions": ToolParameter(
                    name="dietary_restrictions",
                    type=ParameterType.ARRAY,
                    description="Dietary restrictions to accommodate",
                    required=True
                ),
                "allergies": ToolParameter(
                    name="allergies",
                    type=ParameterType.ARRAY,
                    description="Food allergies to avoid",
                    required=False
                ),
                "preferences": ToolParameter(
                    name="preferences",
                    type=ParameterType.OBJECT,
                    description="Cooking preferences and style",
                    required=False
                )
            },
            required_params=["original_recipe", "dietary_restrictions"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["recipe", "adaptation", "dietary", "restrictions"]
        )
    
    def _get_meal_planning_tool(self) -> MCPTool:
        """Plan meals for a specific period"""
        return MCPTool(
            name="plan_meals",
            description="Create a meal plan for a specific period with recipes and shopping lists",
            category=ToolCategory.RECIPES,
            parameters={
                "duration_days": ToolParameter(
                    name="duration_days",
                    type=ParameterType.INTEGER,
                    description="Number of days to plan",
                    required=True
                ),
                "daily_meals": ToolParameter(
                    name="daily_meals",
                    type=ParameterType.INTEGER,
                    description="Number of meals per day",
                    required=False,
                    default=3
                ),
                "calorie_target": ToolParameter(
                    name="calorie_target",
                    type=ParameterType.INTEGER,
                    description="Daily calorie target",
                    required=False
                ),
                "cuisine_preferences": ToolParameter(
                    name="cuisine_preferences",
                    type=ParameterType.ARRAY,
                    description="Preferred cuisine styles",
                    required=False
                )
            },
            required_params=["duration_days"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["meal", "planning", "recipes", "organization"]
        )




