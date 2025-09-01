"""
Nutrition Tools - MCP tools for nutrition and food data
"""

from typing import List, Dict, Any
from ..schemas import MCPTool, ToolParameter, ToolCategory, ParameterType

class NutritionTools:
    """Tools for nutrition and food data access"""
    
    def get_tools(self) -> List[MCPTool]:
        """Get all nutrition-related tools"""
        return [
            self._get_nutrition_info_tool(),
            self._get_food_search_tool(),
            self._get_nutrition_analysis_tool(),
            self._get_dietary_restrictions_tool(),
            self._get_calorie_calculator_tool()
        ]
    
    def _get_nutrition_info_tool(self) -> MCPTool:
        """Get nutrition information for food items"""
        return MCPTool(
            name="get_nutrition_info",
            description="Get detailed nutrition information for food items including calories, macronutrients, vitamins, and minerals",
            category=ToolCategory.NUTRITION,
            parameters={
                "food_name": ToolParameter(
                    name="food_name",
                    type=ParameterType.STRING,
                    description="Name of the food item",
                    required=True
                ),
                "quantity": ToolParameter(
                    name="quantity",
                    type=ParameterType.FLOAT,
                    description="Quantity of the food item",
                    required=False,
                    default=1.0
                ),
                "unit": ToolParameter(
                    name="unit",
                    type=ParameterType.STRING,
                    description="Unit of measurement (grams, ounces, cups, etc.)",
                    required=False,
                    default="serving"
                ),
                "brand": ToolParameter(
                    name="brand",
                    type=ParameterType.STRING,
                    description="Brand name of the food item",
                    required=False
                ),
                "cooking_method": ToolParameter(
                    name="cooking_method",
                    type=ParameterType.STRING,
                    description="Cooking method (raw, cooked, fried, etc.)",
                    required=False,
                    default="raw"
                )
            },
            required_params=["food_name"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["nutrition", "food", "calories", "macronutrients"]
        )
    
    def _get_food_search_tool(self) -> MCPTool:
        """Search for foods by various criteria"""
        return MCPTool(
            name="search_foods",
            description="Search for foods based on name, category, nutrients, or dietary restrictions",
            category=ToolCategory.NUTRITION,
            parameters={
                "query": ToolParameter(
                    name="query",
                    type=ParameterType.STRING,
                    description="Search query (food name, category, etc.)",
                    required=True
                ),
                "category": ToolParameter(
                    name="category",
                    type=ParameterType.STRING,
                    description="Food category (fruits, vegetables, proteins, etc.)",
                    required=False
                ),
                "min_calories": ToolParameter(
                    name="min_calories",
                    type=ParameterType.INTEGER,
                    description="Minimum calories per serving",
                    required=False
                ),
                "max_calories": ToolParameter(
                    name="max_calories",
                    type=ParameterType.INTEGER,
                    description="Maximum calories per serving",
                    required=False
                ),
                "dietary_restrictions": ToolParameter(
                    name="dietary_restrictions",
                    type=ParameterType.ARRAY,
                    description="List of dietary restrictions to consider",
                    required=False
                ),
                "limit": ToolParameter(
                    name="limit",
                    type=ParameterType.INTEGER,
                    description="Maximum number of results to return",
                    required=False,
                    default=10
                )
            },
            required_params=["query"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["search", "food", "dietary", "filtering"]
        )
    
    def _get_nutrition_analysis_tool(self) -> MCPTool:
        """Analyze nutrition content of meals or food combinations"""
        return MCPTool(
            name="analyze_nutrition",
            description="Analyze the nutritional content of a meal or combination of foods",
            category=ToolCategory.NUTRITION,
            parameters={
                "foods": ToolParameter(
                    name="foods",
                    type=ParameterType.ARRAY,
                    description="List of foods with quantities and units",
                    required=True
                ),
                "meal_type": ToolParameter(
                    name="meal_type",
                    type=ParameterType.STRING,
                    description="Type of meal (breakfast, lunch, dinner, snack)",
                    required=False
                ),
                "target_calories": ToolParameter(
                    name="target_calories",
                    type=ParameterType.INTEGER,
                    description="Target calories for the meal",
                    required=False
                ),
                "nutritional_goals": ToolParameter(
                    name="nutritional_goals",
                    type=ParameterType.OBJECT,
                    description="Nutritional goals (protein, carbs, fat targets)",
                    required=False
                )
            },
            required_params=["foods"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["analysis", "meal", "nutrition", "goals"]
        )
    
    def _get_dietary_restrictions_tool(self) -> MCPTool:
        """Get information about dietary restrictions and alternatives"""
        return MCPTool(
            name="get_dietary_alternatives",
            description="Find alternative foods for specific dietary restrictions",
            category=ToolCategory.NUTRITION,
            parameters={
                "restriction": ToolParameter(
                    name="restriction",
                    type=ParameterType.STRING,
                    description="Dietary restriction (vegetarian, vegan, gluten-free, etc.)",
                    required=True
                ),
                "food_to_replace": ToolParameter(
                    name="food_to_replace",
                    type=ParameterType.STRING,
                    description="Food item to find alternatives for",
                    required=False
                ),
                "nutrient_focus": ToolParameter(
                    name="nutrient_focus",
                    type=ParameterType.STRING,
                    description="Primary nutrient to focus on in alternatives",
                    required=False
                ),
                "cuisine_preference": ToolParameter(
                    name="cuisine_preference",
                    type=ParameterType.STRING,
                    description="Preferred cuisine style",
                    required=False
                )
            },
            required_params=["restriction"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["dietary", "alternatives", "restrictions", "substitutions"]
        )
    
    def _get_calorie_calculator_tool(self) -> MCPTool:
        """Calculate daily calorie needs based on user profile"""
        return MCPTool(
            name="calculate_calorie_needs",
            description="Calculate daily calorie needs based on age, weight, height, activity level, and goals",
            category=ToolCategory.NUTRITION,
            parameters={
                "age": ToolParameter(
                    name="age",
                    type=ParameterType.INTEGER,
                    description="Age in years",
                    required=True
                ),
                "gender": ToolParameter(
                    name="gender",
                    type=ParameterType.STRING,
                    description="Gender (male, female, other)",
                    required=True,
                    enum=["male", "female", "other"]
                ),
                "weight_kg": ToolParameter(
                    name="weight_kg",
                    type=ParameterType.FLOAT,
                    description="Weight in kilograms",
                    required=True
                ),
                "height_cm": ToolParameter(
                    name="height_cm",
                    type=ParameterType.FLOAT,
                    description="Height in centimeters",
                    required=True
                ),
                "activity_level": ToolParameter(
                    name="activity_level",
                    type=ParameterType.STRING,
                    description="Activity level",
                    required=True,
                    enum=["sedentary", "lightly_active", "moderately_active", "very_active", "extremely_active"]
                ),
                "goal": ToolParameter(
                    name="goal",
                    type=ParameterType.STRING,
                    description="Weight goal (lose, maintain, gain)",
                    required=True,
                    enum=["lose", "maintain", "gain"]
                ),
                "target_weight_change_kg": ToolParameter(
                    name="target_weight_change_kg",
                    type=ParameterType.FLOAT,
                    description="Target weight change in kg per week",
                    required=False,
                    default=0.5
                )
            },
            required_params=["age", "gender", "weight_kg", "height_cm", "activity_level", "goal"],
            version="1.0.0",
            author="AI Dietitian System",
            tags=["calories", "calculation", "bmr", "tdee", "goals"]
        )




