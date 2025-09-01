"""
Diet Planner Agent - Creates personalized diet plans based on user profile and requirements
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import json
import math

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class DietPlannerAgent(BaseAgent):
    """
    Agent responsible for creating personalized diet plans based on user profile data
    """
    
    def __init__(self):
        super().__init__("diet_planner")
        self.system_message = """
        You are an expert dietitian AI agent specializing in creating personalized diet plans. 
        You have extensive knowledge of nutrition, dietary requirements, and meal planning.
        
        Your responsibilities include:
        1. Analyzing user profiles and health goals
        2. Calculating appropriate calorie and macronutrient needs
        3. Creating balanced, nutritious meal plans with specific timings and quantities
        4. Considering dietary restrictions, allergies, and medical conditions
        5. Ensuring variety and sustainability in meal options
        6. Providing detailed nutritional analysis and shopping lists
        
        Always prioritize health, safety, and individual preferences when creating diet plans.
        Provide specific meal timings, portion sizes, and calorie counts for each meal.
        """
    
    async def process(self, state) -> Dict[str, Any]:
        """
        Process diet planning request
        
        Args:
            state: Current workflow state
            
        Returns:
            Diet plan and recommendations
        """
        try:
            await self.update_status("processing")
            
            # Extract user data from state
            user_data = state.get("user_data", {})
            user_id = user_data.get("user_id")
            
            if not user_id:
                raise ValueError("User ID is required")
            
            # Get user profile data from state (already passed from API)
            profile_data = user_data
            if not profile_data:
                raise ValueError("User profile not found")
            
            # Calculate health metrics
            health_metrics = self._calculate_health_metrics(profile_data)
            
            # Create comprehensive diet plan
            diet_plan = await self._create_comprehensive_diet_plan(profile_data, health_metrics)
            
            # Save diet plan to database
            saved_plan = await self._save_diet_plan_to_database(user_id, diet_plan, health_metrics, profile_data)
            
            # Update state with results
            if "results" not in state:
                state["results"] = {}
            
            state["results"]["diet_planner"] = {
                "success": True,
                "diet_plan": diet_plan,
                "health_metrics": health_metrics,
                "saved_plan": saved_plan,
                "message": "Comprehensive diet plan created and saved successfully"
            }
            
            await self.increment_success()
            return state
            
        except Exception as e:
            error_response = await self.handle_error(e, "Diet planning process")
            if "results" not in state:
                state["results"] = {}
            state["results"]["diet_planner"] = error_response
            return state
    
    async def _get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile data from the database"""
        try:
            # This would typically come from the database through an API call
            # For now, we'll use the data passed in the state
            # In a real implementation, you'd call the profile API endpoint
            return None  # Placeholder - will be implemented with actual API call
        except Exception as e:
            logger.error(f"Failed to get user profile: {str(e)}")
            return None
    
    def _calculate_health_metrics(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate health metrics including BMI, BMR, and calorie needs"""
        try:
            height_cm = float(profile_data.get("height_cm", 0))
            weight_kg = float(profile_data.get("current_weight_kg", profile_data.get("weight_kg", 0)))
            age = int(profile_data.get("age", 25))
            gender = profile_data.get("gender", "male").lower()
            activity_level = profile_data.get("daily_routine", "moderately_active")
            
            # Calculate BMI
            height_m = height_cm / 100
            bmi = weight_kg / (height_m * height_m) if height_m > 0 else 0
            
            # BMI Category
            bmi_category = self._get_bmi_category(bmi)
            
            # Calculate BMR using Mifflin-St Jeor Equation
            if gender == "male":
                bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
            else:
                bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
            
            # Activity Multiplier
            activity_multipliers = {
                "sedentary": 1.2,
                "moderately_active": 1.55,
                "highly_active": 1.725
            }
            activity_multiplier = activity_multipliers.get(activity_level, 1.55)
            
            # Total Daily Energy Expenditure (TDEE)
            tdee = bmr * activity_multiplier
            
            # Calculate target calories based on goals
            primary_goals = profile_data.get("primary_goals", [])
            progress_pace = profile_data.get("progress_pace", "moderate")
            
            target_calories = self._calculate_target_calories(tdee, primary_goals, progress_pace, bmi_category)
            
            # Calculate macronutrient distribution
            macros = self._calculate_macronutrients(target_calories, primary_goals, profile_data)
            
            return {
                "bmi": round(bmi, 2),
                "bmi_category": bmi_category,
                "bmr": round(bmr),
                "tdee": round(tdee),
                "target_calories": round(target_calories),
                "activity_level": activity_level,
                "macronutrients": macros,
                "height_cm": height_cm,
                "weight_kg": weight_kg,
                "age": age,
                "gender": gender
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate health metrics: {str(e)}")
            return {}
    
    def _get_bmi_category(self, bmi: float) -> str:
        """Get BMI category based on BMI value"""
        if bmi < 18.5:
            return "underweight"
        elif bmi < 25:
            return "normal_weight"
        elif bmi < 30:
            return "overweight"
        elif bmi < 35:
            return "obese_class_1"
        elif bmi < 40:
            return "obese_class_2"
        else:
            return "obese_class_3"
    
    def _calculate_target_calories(self, tdee: float, goals: List[str], progress_pace: str, bmi_category: str) -> float:
        """Calculate target calories based on goals and progress pace"""
        # Base calorie adjustment based on goals
        if "weight_loss" in goals:
            if progress_pace == "aggressive":
                calorie_deficit = 0.25  # 25% deficit
            elif progress_pace == "moderate":
                calorie_deficit = 0.20  # 20% deficit
            else:  # gradual
                calorie_deficit = 0.15  # 15% deficit
            target_calories = tdee * (1 - calorie_deficit)
        elif "weight_gain" in goals:
            if progress_pace == "aggressive":
                calorie_surplus = 0.25  # 25% surplus
            elif progress_pace == "moderate":
                calorie_surplus = 0.20  # 20% surplus
            else:  # gradual
                calorie_surplus = 0.15  # 15% surplus
            target_calories = tdee * (1 + calorie_surplus)
        else:
            # Maintenance or other goals
            target_calories = tdee
        
        # Ensure minimum safe calories
        min_calories = 1200 if "female" in goals else 1500
        return max(target_calories, min_calories)
    
    def _calculate_macronutrients(self, target_calories: float, goals: List[str], profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate macronutrient distribution"""
        # Protein: 1.6-2.2g per kg for weight loss, 1.2-1.6g for maintenance
        weight_kg = float(profile_data.get("current_weight_kg", profile_data.get("weight_kg", 70)))
        
        if "weight_loss" in goals:
            protein_g = weight_kg * 2.0  # 2.0g per kg
        else:
            protein_g = weight_kg * 1.4  # 1.4g per kg
        
        protein_calories = protein_g * 4
        
        # Fat: 20-35% of total calories
        fat_percentage = 0.25  # 25%
        fat_calories = target_calories * fat_percentage
        fat_g = fat_calories / 9
        
        # Remaining calories go to carbs
        carb_calories = target_calories - protein_calories - fat_calories
        carb_g = carb_calories / 4
        
        return {
            "protein_g": round(protein_g, 1),
            "protein_calories": round(protein_calories),
            "fat_g": round(fat_g, 1),
            "fat_calories": round(fat_calories),
            "carb_g": round(carb_g, 1),
            "carb_calories": round(carb_calories),
            "protein_percentage": round((protein_calories / target_calories) * 100, 1),
            "fat_percentage": round((fat_calories / target_calories) * 100, 1),
            "carb_percentage": round((carb_calories / target_calories) * 100, 1)
        }
    
    async def _create_comprehensive_diet_plan(self, profile_data: Dict[str, Any], health_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive month-long diet plan"""
        try:
            # Prepare detailed prompt for AI
            prompt = self._build_comprehensive_diet_plan_prompt(profile_data, health_metrics)
            
            # Get AI response if OpenAI is available
            try:
                ai_response = await self.call_openai(
                    prompt=prompt,
                    system_message=self.system_message,
                    max_tokens=4000  # Reduced to 4000 as per model limits
                )
                diet_plan = self._parse_ai_response(ai_response)
            except Exception as e:
                logger.warning(f"OpenAI call failed, using enhanced mock response: {str(e)}")
                diet_plan = self._create_enhanced_mock_diet_plan(profile_data, health_metrics)
            
            # Validate and enhance diet plan
            enhanced_plan = await self._enhance_comprehensive_diet_plan(diet_plan, profile_data, health_metrics)
            
            return enhanced_plan
            
        except Exception as e:
            logger.error(f"Failed to create comprehensive diet plan: {str(e)}")
            raise
    
    def _build_comprehensive_diet_plan_prompt(self, profile_data: Dict[str, Any], health_metrics: Dict[str, Any]) -> str:
        """Build comprehensive prompt for AI diet planning"""
        
        # Format medical conditions and allergies
        medical_conditions = profile_data.get("medical_conditions", [])
        food_allergies = profile_data.get("food_allergies", [])
        family_history = profile_data.get("family_history", [])
        
        prompt = f"""
        Create a comprehensive 7-day personalized diet plan for the following user:
        
        USER PROFILE:
        - Name: {profile_data.get('full_name', 'User')}
        - Age: {profile_data.get('age', 'Not specified')} years
        - Gender: {profile_data.get('gender', 'Not specified')}
        - Height: {health_metrics.get('height_cm', 'Not specified')} cm
        - Current Weight: {health_metrics.get('weight_kg', 'Not specified')} kg
        - BMI: {health_metrics.get('bmi', 'Not specified')} ({health_metrics.get('bmi_category', 'Not specified')})
        
        HEALTH METRICS:
        - BMR: {health_metrics.get('bmr', 'Not specified')} calories/day
        - TDEE: {health_metrics.get('tdee', 'Not specified')} calories/day
        - Target Calories: {health_metrics.get('target_calories', 'Not specified')} calories/day
        - Activity Level: {health_metrics.get('activity_level', 'Not specified')}
        
        MACRONUTRIENT TARGETS:
        - Protein: {health_metrics.get('macronutrients', {}).get('protein_g', 'Not specified')}g ({health_metrics.get('macronutrients', {}).get('protein_percentage', 'Not specified')}%)
        - Fat: {health_metrics.get('macronutrients', {}).get('fat_g', 'Not specified')}g ({health_metrics.get('macronutrients', {}).get('fat_percentage', 'Not specified')}%)
        - Carbohydrates: {health_metrics.get('macronutrients', {}).get('carb_g', 'Not specified')}g ({health_metrics.get('macronutrients', {}).get('carb_percentage', 'Not specified')}%)
        
        MEDICAL & DIETARY CONSIDERATIONS:
        - Medical Conditions: {', '.join(medical_conditions) if medical_conditions else 'None'}
        - Food Allergies: {', '.join(food_allergies) if food_allergies else 'None'}
        - Family History: {', '.join(family_history) if family_history else 'None'}
        - Food Preference: {profile_data.get('food_preference', 'Not specified')}
        - Cultural Restrictions: {profile_data.get('cultural_restrictions', 'None')}
        
        LIFESTYLE & HABITS:
        - Daily Routine: {profile_data.get('daily_routine', 'Not specified')}
        - Sleep Pattern: {profile_data.get('sleep_hours', 'Not specified')} hours
        - Stress Level: {profile_data.get('stress_level', 'Not specified')}
        - Physical Activity: {profile_data.get('physical_activity_type', 'Not specified')} - {profile_data.get('physical_activity_frequency', 'Not specified')} - {profile_data.get('physical_activity_duration', 'Not specified')}
        
        EATING HABITS:
        - Meal Timings: {profile_data.get('meal_timings', 'Not specified')}
        - Eating Out Frequency: {profile_data.get('eating_out_frequency', 'Not specified')}
        - Water Intake: {profile_data.get('daily_water_intake', 'Not specified')}
        - Common Cravings: {', '.join(profile_data.get('common_cravings', [])) if profile_data.get('common_cravings') else 'None'}
        
        GOALS & PREFERENCES:
        - Primary Goals: {', '.join(profile_data.get('primary_goals', [])) if profile_data.get('primary_goals') else 'Not specified'}
        - Progress Pace: {profile_data.get('progress_pace', 'Not specified')}
        - Loved Foods: {profile_data.get('loved_foods', 'Not specified')}
        - Disliked Foods: {profile_data.get('disliked_foods', 'Not specified')}
        - Cooking Facilities: {', '.join(profile_data.get('cooking_facilities', [])) if profile_data.get('cooking_facilities') else 'Not specified'}
        - Who Cooks: {profile_data.get('who_cooks', 'Not specified')}
        - Budget: {profile_data.get('budget_flexibility', 'Not specified')}
        - Motivation Level: {profile_data.get('motivation_level', 'Not specified')}/10
        
        REQUIREMENTS:
        Create a detailed 7-day diet plan that includes:
        
        1. DAILY MEAL STRUCTURE (for each of the 7 days):
           - Breakfast (with specific timing, e.g., "7:00 AM")
           - Morning Snack (with timing)
           - Lunch (with specific timing, e.g., "12:30 PM")
           - Afternoon Snack (with timing)
           - Dinner (with specific timing, e.g., "7:00 PM")
        
        2. FOR EACH MEAL, SPECIFY ALL REQUIRED FIELDS:
           - meal_type: One of ["Breakfast", "Snack", "Lunch", "Evening Snack", "Dinner"]
           - meal_time: Specific time in "HH:MM" format (e.g., "07:00", "12:30", "19:00")
           - meal_name: Descriptive name of the meal
           - calories: Exact calorie count (integer)
           - protein: Protein content in grams (decimal)
           - carbs: Carbohydrate content in grams (decimal)
           - fat: Fat content in grams (decimal)
           - fiber: Fiber content in grams (decimal, optional)
           - instructions: Step-by-step cooking/preparation instructions
           - difficulty_level: One of ["beginner", "intermediate", "advanced"]
           - prep_time_minutes: Preparation time in minutes (integer)
           - cooking_time_minutes: Cooking time in minutes (integer)
           - cost_category: One of ["budget", "moderate", "premium"]
           - ingredients: Array of food items with:
             * item: Food name
             * quantity: Amount (decimal)
             * unit: One of ["g", "ml", "pieces", "cups", "tbsp", "tsp", "medium", "large", "small"]
             * calories: Calories per ingredient (integer)
             * protein: Protein per ingredient in grams (decimal)
             * carbs: Carbs per ingredient in grams (decimal)
             * fat: Fat per ingredient in grams (decimal)
             * fiber: Fiber per ingredient in grams (decimal, optional)
        
        3. NUTRITIONAL TARGETS PER DAY:
           - Total calories: {health_metrics.get('target_calories', 'Not specified')}
           - Protein: {health_metrics.get('macronutrients', {}).get('protein_g', 'Not specified')}g
           - Fat: {health_metrics.get('macronutrients', {}).get('fat_g', 'Not specified')}g
           - Carbohydrates: {health_metrics.get('macronutrients', {}).get('carb_g', 'Not specified')}g
           - Water intake target: 2.5-3.0 liters per day
        
        4. WEEKLY PLAN STRUCTURE:
           - Create 7 days (Monday through Sunday)
           - Each day should have the same meal structure: Breakfast, Snack, Lunch, Snack, Dinner
           - Ensure variety across the week while maintaining nutritional balance
        
        5. DAILY PLAN STRUCTURE:
           - date: Date in YYYY-MM-DD format
           - total_calories: Sum of all meal calories for the day
           - total_protein: Sum of all meal protein for the day
           - total_carbs: Sum of all meal carbs for the day
           - total_fat: Sum of all meal fat for the day
           - water_intake_target: Daily water goal in liters
           - notes: Special instructions for the day (e.g., "High protein day", "Light dinner day")
        
        6. ADDITIONAL COMPONENTS:
           - Weekly shopping lists
           - Meal prep instructions
           - Hydration schedule
           - Progress tracking metrics
           - Adaptation tips for different scenarios
        
        CRITICAL: Ensure ALL fields are populated with realistic values. Do not leave any fields empty or null.
        Format the response as a structured JSON object with clear organization.
        The response must be valid JSON that can be parsed directly.
        
        RESPONSE FORMAT EXAMPLE:
        ```json
        {{
          "plan_name": "Personalized Diet Plan",
          "daily_meals": [
            {{
              "date": "2024-01-01",
              "total_calories": 1539,
              "total_protein": 91.0,
              "total_carbs": 197.6,
              "total_fat": 42.8,
              "water_intake_target": 2.5,
              "notes": "Day 1 - High protein breakfast to start the day",
              "meals": [
                {{
                  "type": "Breakfast",
                  "timing": "07:00",
                  "name": "High-Protein Oatmeal Bowl",
                  "calories": 385,
                  "protein": 22.8,
                  "carbs": 49.4,
                  "fat": 10.7,
                  "fiber": 8.0,
                  "instructions": "Cook 60g oats with 240ml milk for 10 minutes. Stir in 30g protein powder. Top with 15g almonds and 50g berries.",
                  "difficulty_level": "beginner",
                  "prep_time_minutes": 10,
                  "cooking_time_minutes": 15,
                  "cost_category": "budget",
                  "ingredients": [
                    {{
                      "item": "rolled oats",
                      "quantity": 60.0,
                      "unit": "g",
                      "calories": 228,
                      "protein": 8.0,
                      "carbs": 40.0,
                      "fat": 4.0,
                      "fiber": 6.0
                    }},
                    {{
                      "item": "protein powder",
                      "quantity": 30.0,
                      "unit": "g",
                      "calories": 120,
                      "protein": 24.0,
                      "carbs": 3.0,
                      "fat": 1.0,
                      "fiber": 0.0
                    }},
                    {{
                      "item": "almonds",
                      "quantity": 15.0,
                      "unit": "g",
                      "calories": 87,
                      "protein": 3.0,
                      "carbs": 3.0,
                      "fat": 8.0,
                      "fiber": 2.0
                    }},
                    {{
                      "item": "berries",
                      "quantity": 50.0,
                      "unit": "g",
                      "calories": 25,
                      "protein": 0.5,
                      "carbs": 6.0,
                      "fat": 0.0,
                      "fiber": 2.5
                    }},
                    {{
                      "item": "milk",
                      "quantity": 240.0,
                      "unit": "ml",
                      "calories": 120,
                      "protein": 8.0,
                      "carbs": 12.0,
                      "fat": 5.0,
                      "fiber": 0.0
                    }}
                  ]
                }},
                {{
                  "type": "Lunch",
                  "timing": "12:30",
                  "name": "Grilled Chicken Quinoa Bowl",
                  "calories": 539,
                  "protein": 31.9,
                  "carbs": 69.2,
                  "fat": 15.0,
                  "fiber": 12.0,
                  "instructions": "Grill 120g chicken breast. Cook 80g quinoa. Mix with 150g mixed vegetables. Drizzle with 5ml olive oil.",
                  "difficulty_level": "beginner",
                  "prep_time_minutes": 15,
                  "cooking_time_minutes": 20,
                  "cost_category": "budget",
                  "ingredients": [
                    {{
                      "item": "chicken breast",
                      "quantity": 120.0,
                      "unit": "g",
                      "calories": 198,
                      "protein": 37.2,
                      "carbs": 0.0,
                      "fat": 4.3,
                      "fiber": 0.0
                    }},
                    {{
                      "item": "quinoa",
                      "quantity": 80.0,
                      "unit": "g",
                      "calories": 120,
                      "protein": 4.0,
                      "carbs": 22.0,
                      "fat": 2.0,
                      "fiber": 2.0
                    }},
                    {{
                      "item": "mixed vegetables",
                      "quantity": 150.0,
                      "unit": "g",
                      "calories": 75,
                      "protein": 4.5,
                      "carbs": 15.0,
                      "fat": 0.0,
                      "fiber": 6.0
                    }},
                    {{
                      "item": "olive oil",
                      "quantity": 5.0,
                      "unit": "ml",
                      "calories": 45,
                      "protein": 0.0,
                      "carbs": 0.0,
                      "fat": 5.0,
                      "fiber": 0.0
                    }}
                  ]
                }},
                {{
                  "type": "Dinner",
                  "timing": "19:00",
                  "name": "Salmon with Roasted Vegetables",
                  "calories": 615,
                  "protein": 36.3,
                  "carbs": 79.0,
                  "fat": 17.1,
                  "fiber": 10.0,
                  "instructions": "Bake 100g salmon fillet at 400°F for 15 minutes. Roast 200g mixed vegetables with herbs and 5ml olive oil.",
                  "difficulty_level": "beginner",
                  "prep_time_minutes": 12,
                  "cooking_time_minutes": 18,
                  "cost_category": "moderate",
                  "ingredients": [
                    {{
                      "item": "salmon",
                      "quantity": 100.0,
                      "unit": "g",
                      "calories": 200,
                      "protein": 20.0,
                      "carbs": 0.0,
                      "fat": 12.0,
                      "fiber": 0.0
                    }},
                    {{
                      "item": "mixed vegetables",
                      "quantity": 200.0,
                      "unit": "g",
                      "calories": 100,
                      "protein": 6.0,
                      "carbs": 20.0,
                      "fat": 0.0,
                      "fiber": 8.0
                    }},
                    {{
                      "item": "olive oil",
                      "quantity": 5.0,
                      "unit": "ml",
                      "calories": 45,
                      "protein": 0.0,
                      "carbs": 0.0,
                      "fat": 5.0,
                      "fiber": 0.0
                    }},
                    {{
                      "item": "brown rice",
                      "quantity": 100.0,
                      "unit": "g",
                      "calories": 111,
                      "protein": 2.6,
                      "carbs": 23.0,
                      "fat": 0.9,
                      "fiber": 1.8
                    }}
                  ]
                }}
              ]
            }}
          ],
          "nutritional_summary": {{
            "daily_average_calories": 1539,
            "daily_average_protein": 91.0,
            "daily_average_carbs": 197.6,
            "daily_average_fat": 42.8,
            "daily_average_fiber": 30.0
          }},
          "shopping_list": [
            "rolled oats - 1.8kg",
            "protein powder - 900g",
            "almonds - 450g",
            "berries - 1.5kg",
            "milk - 7.2L",
            "chicken breast - 3.6kg",
            "quinoa - 2.4kg",
            "mixed vegetables - 4.5kg",
            "olive oil - 150ml",
            "salmon - 3.0kg",
            "brown rice - 3.0kg"
          ],
          "meal_prep_instructions": "Prep ingredients on Sundays. Cook quinoa and rice in bulk. Portion protein into containers. Wash and chop vegetables.",
          "hydration_schedule": [
            {{"time": "07:00", "water_intake": "250 ml"}},
            {{"time": "09:00", "water_intake": "250 ml"}},
            {{"time": "11:00", "water_intake": "250 ml"}},
            {{"time": "13:00", "water_intake": "250 ml"}},
            {{"time": "15:00", "water_intake": "250 ml"}},
            {{"time": "17:00", "water_intake": "250 ml"}},
            {{"time": "19:00", "water_intake": "250 ml"}},
            {{"time": "21:00", "water_intake": "250 ml"}}
          ],
          "progress_tracking": [
            {{
              "date": "2024-01-01",
              "weight_kg": 65.0,
              "waist_cm": 80.0,
              "energy_level": 8,
              "compliance_percentage": 100,
              "notes": "Day 1 completed successfully"
            }}
          ],
          "notes": "Focus on high protein intake for satiety. Stay hydrated throughout the day. Adjust portion sizes if needed.",
          "compliance_tips": [
            "Track meals daily using a food diary",
            "Prepare meals in advance on Sundays",
            "Keep healthy snacks readily available",
            "Stay hydrated by carrying a water bottle"
          ],
          "adaptation_tips": [
            "Travel: Pack healthy snacks and research restaurant options",
            "Work stress: Have backup meal options for busy days",
            "Social events: Eat a healthy snack before going out"
          ]
        }}
        ```
        
        IMPORTANT: Follow this exact JSON structure. Include ALL required fields for each meal. Do not skip any fields or leave them empty.
        """
        
        return prompt
    
    def _create_enhanced_mock_diet_plan(self, profile_data: Dict[str, Any], health_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create an enhanced mock diet plan with realistic data personalized to user profile"""
        
        # Calculate meal calorie distribution based on user goals
        target_calories = health_metrics.get("target_calories", 2000)
        primary_goals = profile_data.get("primary_goals", [])
        
        # Adjust meal distribution based on goals
        if "weight_loss" in primary_goals:
            # Higher protein, lower carbs for weight loss
            breakfast_calories = int(target_calories * 0.30)  # 30%
            morning_snack_calories = int(target_calories * 0.10)  # 10%
            lunch_calories = int(target_calories * 0.25)  # 25%
            afternoon_snack_calories = int(target_calories * 0.15)  # 15%
            dinner_calories = int(target_calories * 0.20)  # 20%
        elif "muscle_gain" in primary_goals:
            # Higher protein distribution for muscle building
            breakfast_calories = int(target_calories * 0.25)  # 25%
            morning_snack_calories = int(target_calories * 0.20)  # 20%
            lunch_calories = int(target_calories * 0.25)  # 25%
            afternoon_snack_calories = int(target_calories * 0.15)  # 15%
            dinner_calories = int(target_calories * 0.15)  # 15%
        else:
            # Balanced distribution
            breakfast_calories = int(target_calories * 0.25)  # 25%
            morning_snack_calories = int(target_calories * 0.15)  # 15%
            lunch_calories = int(target_calories * 0.30)  # 30%
            afternoon_snack_calories = int(target_calories * 0.10)  # 10%
            dinner_calories = int(target_calories * 0.20)  # 20%
        
        # Get user preferences for meal personalization
        food_preference = profile_data.get("food_preference", "vegetarian")
        loved_foods = profile_data.get("loved_foods", "")
        disliked_foods = profile_data.get("disliked_foods", "")
        cooking_facilities = profile_data.get("cooking_facilities", [])
        who_cooks = profile_data.get("who_cooks", "self")
        
        # Adjust water intake based on user's current habit
        current_water_intake = profile_data.get("daily_water_intake", "2-3L")
        if ">3L" in current_water_intake:
            water_intake_target = 3.5
        elif "2-3L" in current_water_intake:
            water_intake_target = 2.5
        elif "1-2L" in current_water_intake:
            water_intake_target = 2.0
        else:
            water_intake_target = 1.5
        
        # Sample day structure with all required fields
        sample_day = {
            "date": "2024-01-01",
            "total_calories": target_calories,
            "total_protein": health_metrics.get("macronutrients", {}).get("protein_g", 150),
            "total_carbs": health_metrics.get("macronutrients", {}).get("carb_g", 200),
            "total_fat": health_metrics.get("macronutrients", {}).get("fat_g", 67),
            "water_intake_target": water_intake_target,
            "notes": f"Personalized {food_preference} meal plan with focus on {', '.join(primary_goals) if primary_goals else 'balanced nutrition'}",
            "meals": [
                {
                    "type": "Breakfast",
                    "timing": "07:00",
                    "name": self._get_personalized_breakfast_name(food_preference, primary_goals),
                    "calories": breakfast_calories,
                    "protein": round(breakfast_calories * 0.25 / 4, 1),
                    "carbs": round(breakfast_calories * 0.55 / 4, 1),
                    "fat": round(breakfast_calories * 0.20 / 9, 1),
                    "fiber": 8.5,
                    "ingredients": self._get_personalized_breakfast_ingredients(food_preference, breakfast_calories),
                    "instructions": self._get_personalized_breakfast_instructions(food_preference, who_cooks),
                    "difficulty": "beginner" if who_cooks in ["self", "family_member"] else "beginner",
                    "prep_time": 5,
                    "cooking_time": 10,
                    "cost_category": "budget" if profile_data.get("budget_flexibility") == "limited" else "moderate"
                },
                {
                    "type": "Snack",
                    "timing": "10:00",
                    "name": "Greek Yogurt with Nuts",
                    "calories": morning_snack_calories,
                    "protein": round(morning_snack_calories * 0.40 / 4, 1),
                    "carbs": round(morning_snack_calories * 0.30 / 4, 1),
                    "fat": round(morning_snack_calories * 0.30 / 9, 1),
                    "fiber": 2.0,
                    "ingredients": [
                        {"item": "Greek yogurt", "quantity": 150.0, "unit": "g", "calories": 90, "protein": 15.0, "carbs": 6.0, "fat": 0.0, "fiber": 0.0},
                        {"item": "mixed nuts", "quantity": 20.0, "unit": "g", "calories": 120, "protein": 4.0, "carbs": 4.0, "fat": 10.0, "fiber": 2.0},
                        {"item": "honey", "quantity": 5.0, "unit": "g", "calories": 15, "protein": 0.0, "carbs": 4.0, "fat": 0.0, "fiber": 0.0}
                    ],
                    "instructions": "Mix yogurt with honey, top with nuts",
                    "difficulty": "beginner",
                    "prep_time": 2,
                    "cooking_time": 0,
                    "cost_category": "moderate"
                },
                {
                    "type": "Lunch",
                    "timing": "13:00",
                    "name": "Grilled Chicken Salad",
                    "calories": lunch_calories,
                    "protein": round(lunch_calories * 0.35 / 4, 1),
                    "carbs": round(lunch_calories * 0.35 / 4, 1),
                    "fat": round(lunch_calories * 0.30 / 9, 1),
                    "fiber": 12.0,
                    "ingredients": [
                        {"item": "chicken breast", "quantity": 150.0, "unit": "g", "calories": 165, "protein": 31.0, "carbs": 0.0, "fat": 3.6, "fiber": 0.0},
                        {"item": "mixed greens", "quantity": 100.0, "unit": "g", "calories": 25, "protein": 2.0, "carbs": 4.0, "fat": 0.0, "fiber": 2.0},
                        {"item": "olive oil", "quantity": 15.0, "unit": "ml", "calories": 135, "protein": 0.0, "carbs": 0.0, "fat": 15.0, "fiber": 0.0},
                        {"item": "tomatoes", "quantity": 50.0, "unit": "g", "calories": 9, "protein": 0.5, "carbs": 2.0, "fat": 0.0, "fiber": 1.0},
                        {"item": "cucumber", "quantity": 50.0, "unit": "g", "calories": 8, "protein": 0.5, "carbs": 2.0, "fat": 0.0, "fiber": 1.0}
                    ],
                    "instructions": "Grill chicken breast for 15 minutes, serve with mixed greens, tomatoes, cucumber, and olive oil dressing",
                    "difficulty": "beginner",
                    "prep_time": 10,
                    "cooking_time": 15,
                    "cost_category": "moderate"
                },
                {
                    "type": "Snack",
                    "timing": "16:00",
                    "name": "Apple with Peanut Butter",
                    "calories": afternoon_snack_calories,
                    "protein": round(afternoon_snack_calories * 0.20 / 4, 1),
                    "carbs": round(afternoon_snack_calories * 0.60 / 4, 1),
                    "fat": round(afternoon_snack_calories * 0.20 / 9, 1),
                    "fiber": 5.0,
                    "ingredients": [
                        {"item": "apple", "quantity": 1.0, "unit": "medium", "calories": 95, "protein": 0.5, "carbs": 25.0, "fat": 0.0, "fiber": 4.0},
                        {"item": "peanut butter", "quantity": 15.0, "unit": "g", "calories": 90, "protein": 3.5, "carbs": 3.0, "fat": 8.0, "fiber": 1.0}
                    ],
                    "instructions": "Slice apple and serve with natural peanut butter",
                    "difficulty": "beginner",
                    "prep_time": 3,
                    "cooking_time": 0,
                    "cost_category": "budget"
                },
                {
                    "type": "Dinner",
                    "timing": "19:00",
                    "name": "Salmon with Quinoa and Vegetables",
                    "calories": dinner_calories,
                    "protein": round(dinner_calories * 0.30 / 4, 1),
                    "carbs": round(dinner_calories * 0.40 / 4, 1),
                    "fat": round(dinner_calories * 0.30 / 9, 1),
                    "fiber": 8.0,
                    "ingredients": [
                        {"item": "salmon fillet", "quantity": 120.0, "unit": "g", "calories": 240, "protein": 25.0, "carbs": 0.0, "fat": 14.0, "fiber": 0.0},
                        {"item": "quinoa", "quantity": 80.0, "unit": "g", "calories": 120, "protein": 4.0, "carbs": 22.0, "fat": 2.0, "fiber": 2.0},
                        {"item": "broccoli", "quantity": 100.0, "unit": "g", "calories": 34, "protein": 2.8, "carbs": 7.0, "fat": 0.4, "fiber": 2.6},
                        {"item": "carrots", "quantity": 50.0, "unit": "g", "calories": 21, "protein": 0.5, "carbs": 5.0, "fat": 0.0, "fiber": 1.5}
                    ],
                    "instructions": "Bake salmon for 20 minutes, cook quinoa separately, steam vegetables for 10 minutes",
                    "difficulty": "intermediate",
                    "prep_time": 15,
                    "cooking_time": 20,
                    "cost_category": "premium"
                }
            ]
        }
        
        return {
            "plan_name": f"Personalized 30-Day Diet Plan for {profile_data.get('full_name', 'User')}",
            "duration_days": 30,
            "target_calories_per_day": target_calories,
            "health_metrics": health_metrics,
            "daily_meals": [sample_day],  # In real implementation, this would be 30 days
            "nutritional_summary": {
                "daily_average": {
                    "calories": target_calories,
                    "protein": health_metrics.get("macronutrients", {}).get("protein_g", 0),
                    "carbs": health_metrics.get("macronutrients", {}).get("carb_g", 0),
                    "fat": health_metrics.get("macronutrients", {}).get("fat_g", 0)
                }
            },
            "shopping_list": ["rolled oats", "protein powder", "almonds", "berries", "milk", "Greek yogurt", "mixed nuts", "honey"],
            "meal_prep_instructions": "Prepare oatmeal ingredients the night before, portion out yogurt and nuts for the week",
            "hydration_schedule": "8 glasses of water throughout the day",
            "progress_tracking": ["weight", "energy_levels", "meal_compliance", "hunger_satisfaction"],
            "notes": "Enhanced mock diet plan with realistic nutritional calculations and meal structure"
        }
    
    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response into structured diet plan"""
        try:
            # Try to extract JSON from response
            if "```json" in ai_response:
                json_start = ai_response.find("```json") + 7
                json_end = ai_response.find("```", json_start)
                json_str = ai_response[json_start:json_end].strip()
            else:
                # Try to find JSON in the response
                json_str = ai_response
            
            diet_plan = json.loads(json_str)
            
            # Validate that daily_meals exists and is not empty
            if not diet_plan.get("daily_meals"):
                logger.warning("AI response missing daily_meals, will use fallback")
                diet_plan["daily_meals"] = []
            
            return diet_plan
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, create a structured response
            logger.warning(f"Failed to parse AI response as JSON: {str(e)}")
            logger.warning(f"AI Response preview: {ai_response[:200]}...")
            
            # Try to extract any useful information from the text response
            extracted_info = self._extract_info_from_text_response(ai_response)
            
            # Create a basic daily meal structure since the LLM response parsing failed
            basic_daily_meals = self._create_basic_daily_meals_from_text(ai_response)
            
            return {
                "plan_name": "AI Generated Diet Plan",
                "duration_days": 30,
                "daily_meals": basic_daily_meals,
                "nutritional_summary": extracted_info.get("nutritional_summary", {}),
                "shopping_list": extracted_info.get("shopping_list", []),
                "notes": ai_response,
                "extraction_notes": "Response parsed from text due to JSON parsing failure"
            }
    
    def _extract_info_from_text_response(self, text_response: str) -> Dict[str, Any]:
        """Extract structured information from text-based AI response"""
        extracted_info = {
            "daily_meals": [],
            "nutritional_summary": {},
            "shopping_list": []
        }
        
        # Look for meal-related information in the text
        if "breakfast" in text_response.lower():
            extracted_info["daily_meals"].append({
                "type": "Breakfast",
                "timing": "08:00",
                "name": "AI Generated Breakfast",
                "calories": 400,
                "protein": 20.0,
                "carbs": 45.0,
                "fat": 15.0,
                "fiber": 8.0,
                "instructions": "Prepare breakfast based on AI recommendations",
                "difficulty": "beginner",
                "prep_time": 10,
                "cooking_time": 15,
                "cost_category": "budget"
            })
        
        if "lunch" in text_response.lower():
            extracted_info["daily_meals"].append({
                "type": "Lunch",
                "timing": "13:00",
                "name": "AI Generated Lunch",
                "calories": 600,
                "protein": 30.0,
                "carbs": 60.0,
                "fat": 20.0,
                "fiber": 12.0,
                "instructions": "Prepare lunch based on AI recommendations",
                "difficulty": "beginner",
                "prep_time": 15,
                "cooking_time": 20,
                "cost_category": "budget"
            })
        
        if "dinner" in text_response.lower():
            extracted_info["daily_meals"].append({
                "type": "Dinner",
                "timing": "19:00",
                "name": "AI Generated Dinner",
                "calories": 500,
                "protein": 25.0,
                "carbs": 50.0,
                "fat": 18.0,
                "fiber": 10.0,
                "instructions": "Prepare dinner based on AI recommendations",
                "difficulty": "beginner",
                "prep_time": 12,
                "cooking_time": 18,
                "cost_category": "budget"
            })
        
        return extracted_info
    
    def _create_basic_daily_meals_from_text(self, ai_response: str) -> List[Dict[str, Any]]:
        """Create basic daily meal structure from text-based AI response"""
        logger.info("Creating basic daily meals from text response")
        
        # Create a simple 7-day plan based on the text response
        daily_meals = []
        start_date = datetime.utcnow().date()
        
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            
            daily_plan = {
                "date": current_date.isoformat(),
                "total_calories": 2000,  # Default calories
                "total_protein": 150,
                "total_carbs": 200,
                "total_fat": 67,
                "water_intake_target": 2.5,
                "notes": f"Day {day + 1} - Basic meal plan from AI text",
                "meals": [
                    {
                        "type": "Breakfast",
                        "timing": "08:00",
                        "name": "AI Recommended Breakfast",
                        "calories": 500,
                        "protein": 25.0,
                        "carbs": 50.0,
                        "fat": 20.0,
                        "fiber": 8.0,
                        "instructions": "Prepare breakfast based on AI recommendations in the text",
                        "difficulty": "beginner",
                        "prep_time": 10,
                        "cooking_time": 15,
                        "cost_category": "budget",
                        "ingredients": [
                            {"item": "oats", "quantity": 60.0, "unit": "g", "calories": 228, "protein": 8.0, "carbs": 40.0, "fat": 4.0, "fiber": 6.0},
                            {"item": "milk", "quantity": 240.0, "unit": "ml", "calories": 120, "protein": 8.0, "carbs": 12.0, "fat": 5.0, "fiber": 0.0},
                            {"item": "berries", "quantity": 50.0, "unit": "g", "calories": 25, "protein": 0.5, "carbs": 6.0, "fat": 0.0, "fiber": 2.5}
                        ]
                    },
                    {
                        "type": "Lunch",
                        "timing": "13:00",
                        "name": "AI Recommended Lunch",
                        "calories": 700,
                        "protein": 35.0,
                        "carbs": 70.0,
                        "fat": 25.0,
                        "fiber": 12.0,
                        "instructions": "Prepare lunch based on AI recommendations in the text",
                        "difficulty": "beginner",
                        "prep_time": 15,
                        "cooking_time": 20,
                        "cost_category": "budget",
                        "ingredients": [
                            {"item": "chicken breast", "quantity": 120.0, "unit": "g", "calories": 198, "protein": 37.2, "carbs": 0.0, "fat": 4.3, "fiber": 0.0},
                            {"item": "brown rice", "quantity": 100.0, "unit": "g", "calories": 111, "protein": 2.6, "carbs": 23.0, "fat": 0.9, "fiber": 1.8},
                            {"item": "vegetables", "quantity": 150.0, "unit": "g", "calories": 75, "protein": 4.5, "carbs": 15.0, "fat": 0.0, "fiber": 6.0}
                        ]
                    },
                    {
                        "type": "Dinner",
                        "timing": "19:00",
                        "name": "AI Recommended Dinner",
                        "calories": 600,
                        "protein": 30.0,
                        "carbs": 60.0,
                        "fat": 22.0,
                        "fiber": 10.0,
                        "instructions": "Prepare dinner based on AI recommendations in the text",
                        "difficulty": "beginner",
                        "prep_time": 12,
                        "cooking_time": 18,
                        "cost_category": "budget",
                        "ingredients": [
                            {"item": "salmon", "quantity": 100.0, "unit": "g", "calories": 200, "protein": 20.0, "carbs": 0.0, "fat": 12.0, "fiber": 0.0},
                            {"item": "quinoa", "quantity": 80.0, "unit": "g", "calories": 120, "protein": 4.0, "carbs": 22.0, "fat": 2.0, "fiber": 2.0},
                            {"item": "broccoli", "quantity": 100.0, "unit": "g", "calories": 25, "protein": 2.8, "carbs": 7.0, "fat": 0.4, "fiber": 2.6}
                        ]
                    }
                ]
            }
            
            daily_meals.append(daily_plan)
        
        logger.info(f"Created basic daily meals: {len(daily_meals)} days with {sum(len(day.get('meals', [])) for day in daily_meals)} total meals")
        return daily_meals
    
    def _create_minimal_fallback_plan(self, profile_data: Dict[str, Any], health_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a minimal fallback plan when comprehensive plan fails"""
        logger.info("Creating minimal fallback plan")
        
        daily_plans = []
        start_date = datetime.utcnow().date()
        target_calories = health_metrics.get("target_calories", 2000)
        
        for day in range(7):  # Create 7 days instead of 30 for fallback
            current_date = start_date + timedelta(days=day)
            
            daily_plan = {
                "date": current_date.isoformat(),
                "total_calories": target_calories,
                "total_protein": health_metrics.get("macronutrients", {}).get("protein_g", 150),
                "total_carbs": health_metrics.get("macronutrients", {}).get("carb_g", 200),
                "total_fat": health_metrics.get("macronutrients", {}).get("fat_g", 67),
                "water_intake_target": 2.5,
                "notes": f"Day {day + 1} - Fallback meal plan",
                "meals": [
                    {
                        "type": "Breakfast",
                        "timing": "08:00",
                        "name": "Simple Breakfast",
                        "calories": int(target_calories * 0.25),
                        "protein": int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * 0.25),
                        "carbs": int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * 0.25),
                        "fat": int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * 0.25),
                        "fiber": 5.0,
                        "instructions": "Prepare a simple breakfast with protein and fiber",
                        "difficulty": "beginner",
                        "prep_time": 10,
                        "cooking_time": 15,
                        "cost_category": "budget",
                        "ingredients": [
                            {"item": "oats", "quantity": 50.0, "unit": "g", "calories": 190, "protein": 6.5, "carbs": 34.0, "fat": 3.0, "fiber": 5.0},
                            {"item": "milk", "quantity": 200.0, "unit": "ml", "calories": 100, "protein": 6.6, "carbs": 10.0, "fat": 4.0, "fiber": 0.0}
                        ]
                    },
                    {
                        "type": "Lunch",
                        "timing": "13:00",
                        "name": "Simple Lunch",
                        "calories": int(target_calories * 0.35),
                        "protein": int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * 0.35),
                        "carbs": int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * 0.35),
                        "fat": int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * 0.35),
                        "fiber": 8.0,
                        "instructions": "Prepare a balanced lunch with protein and vegetables",
                        "difficulty": "beginner",
                        "prep_time": 15,
                        "cooking_time": 20,
                        "cost_category": "budget",
                        "ingredients": [
                            {"item": "chicken breast", "quantity": 100.0, "unit": "g", "calories": 165, "protein": 31.0, "carbs": 0.0, "fat": 3.6, "fiber": 0.0},
                            {"item": "rice", "quantity": 80.0, "unit": "g", "calories": 296, "protein": 6.0, "carbs": 64.0, "fat": 0.8, "fiber": 2.4}
                        ]
                    },
                    {
                        "type": "Dinner",
                        "timing": "19:00",
                        "name": "Simple Dinner",
                        "calories": int(target_calories * 0.40),
                        "protein": int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * 0.40),
                        "carbs": int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * 0.40),
                        "fat": int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * 0.40),
                        "fiber": 10.0,
                        "instructions": "Prepare a light dinner with protein and vegetables",
                        "difficulty": "beginner",
                        "prep_time": 12,
                        "cooking_time": 18,
                        "cost_category": "budget",
                        "ingredients": [
                            {"item": "fish", "quantity": 120.0, "unit": "g", "calories": 200, "protein": 24.0, "carbs": 0.0, "fat": 12.0, "fiber": 0.0},
                            {"item": "vegetables", "quantity": 150.0, "unit": "g", "calories": 75, "protein": 4.5, "carbs": 15.0, "fat": 0.0, "fiber": 6.0}
                        ]
                    }
                ]
            }
            
            daily_plans.append(daily_plan)
        
        logger.info(f"Created minimal fallback plan with {len(daily_plans)} days")
        return daily_plans
    
    async def _enhance_comprehensive_diet_plan(self, diet_plan: Dict[str, Any], profile_data: Dict[str, Any], health_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance comprehensive diet plan with additional information"""
        try:
            # Add metadata and health insights
            enhanced_plan = {
                "plan_name": diet_plan.get("plan_name", "Personalized 30-Day Diet Plan"),
                "created_at": datetime.utcnow().isoformat(),
                "user_profile_summary": {
                    "name": profile_data.get("full_name"),
                    "age": profile_data.get("age"),
                    "gender": profile_data.get("gender"),
                    "bmi": health_metrics.get("bmi"),
                    "bmi_category": health_metrics.get("bmi_category"),
                    "target_calories": health_metrics.get("target_calories")
                },
                "health_metrics": health_metrics,
                "daily_meals": diet_plan.get("daily_meals", []),
                "nutritional_summary": diet_plan.get("nutritional_summary", {}),
                "shopping_list": diet_plan.get("shopping_list", []),
                "meal_prep_instructions": diet_plan.get("meal_prep_instructions", ""),
                "hydration_schedule": diet_plan.get("hydration_schedule", ""),
                "progress_tracking": diet_plan.get("progress_tracking", []),
                "notes": diet_plan.get("notes", ""),
                "compliance_tips": self._generate_comprehensive_compliance_tips(profile_data, health_metrics),
                "adaptation_tips": self._generate_adaptation_tips(profile_data, health_metrics)
            }
            
            return enhanced_plan
            
        except Exception as e:
            logger.error(f"Failed to enhance comprehensive diet plan: {str(e)}")
            return diet_plan
    
    def _generate_comprehensive_compliance_tips(self, profile_data: Dict[str, Any], health_metrics: Dict[str, Any]) -> List[str]:
        """Generate comprehensive tips for diet plan compliance"""
        tips = [
            "Track your meals daily using a food diary or app",
            "Prepare meals in advance on Sundays for the week ahead",
            "Keep healthy snacks readily available at home and work",
            "Stay hydrated by carrying a water bottle with you",
            "Listen to your body's hunger and fullness cues",
            "Plan for social events by checking menus in advance",
            "Use smaller plates to help with portion control",
            "Eat slowly and mindfully to improve satisfaction"
        ]
        
        # Add personalized tips based on user profile
        if profile_data.get("cooking_skill_level") == "beginner":
            tips.append("Start with simple recipes and gradually increase complexity")
        
        if profile_data.get("budget_flexibility") == "limited":
            tips.append("Buy seasonal produce and bulk items to save money")
        
        if profile_data.get("motivation_level", 5) < 7:
            tips.append("Set small, achievable goals and celebrate progress")
        
        if profile_data.get("support_system") == "weak":
            tips.append("Join online communities for motivation and accountability")
        
        return tips
    
    def _generate_adaptation_tips(self, profile_data: Dict[str, Any], health_metrics: Dict[str, Any]) -> List[str]:
        """Generate tips for adapting the diet plan to different scenarios"""
        tips = [
            "Travel: Pack healthy snacks and research restaurant options",
            "Work stress: Have backup meal options for busy days",
            "Social events: Eat a healthy snack before going out",
            "Illness: Focus on hydration and easily digestible foods",
            "Exercise changes: Adjust portion sizes based on activity level"
        ]
        
        # Add specific adaptations based on medical conditions
        medical_conditions = profile_data.get("medical_conditions", [])
        if "diabetes" in medical_conditions:
            tips.append("Monitor blood sugar and adjust meal timing accordingly")
        
        if "hypertension" in medical_conditions:
            tips.append("Limit sodium intake and focus on potassium-rich foods")
        
        return tips

    async def _save_diet_plan_to_database(self, user_id: str, diet_plan: Dict[str, Any], health_metrics: Dict[str, Any], profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save the generated diet plan to the database
        
        Args:
            user_id: User's unique identifier
            diet_plan: Generated diet plan data
            health_metrics: Calculated health metrics
            
        Returns:
            Database save result
        """
        try:
            from app.core.supabase import SupabaseManager
            supabase_manager = SupabaseManager()
            
            # Clean up existing diet plans before creating new ones
            logger.info(f"🧹 Cleaning up existing diet plans for user: {user_id}")
            
            # Use the nuclear option to ensure ALL data is completely cleared
            logger.info("💥 Force clearing ALL existing diet data to ensure completely clean slate...")
            force_clear_result = await supabase_manager.force_clear_all_user_data(user_id)
            
            if force_clear_result["success"]:
                deleted_plans = force_clear_result.get("deleted_plans", 0)
                deleted_daily_plans = force_clear_result.get("deleted_daily_plans", 0)
                deleted_meals = force_clear_result.get("deleted_meals", 0)
                deleted_food_items = force_clear_result.get("deleted_food_items", 0)
                
                if deleted_plans > 0:
                    logger.info(f"✅ Force cleared {deleted_plans} diet plans, {deleted_daily_plans} daily plans, {deleted_meals} meals, {deleted_food_items} food items")
                else:
                    logger.info("✅ No existing diet data to clear")
            else:
                logger.warning(f"⚠️ Failed to force clear existing diet data: {force_clear_result.get('error')}")
                # Try regular deletion as fallback
                logger.info("🔄 Attempting regular deletion as fallback...")
                delete_result = await supabase_manager.delete_all_user_diet_plans(user_id)
                
                if delete_result["success"]:
                    deleted_count = delete_result.get("deleted_count", 0)
                    if deleted_count > 0:
                        logger.info(f"✅ Deleted {deleted_count} existing diet plans as fallback")
                    else:
                        logger.info("✅ No existing diet plans to delete")
                else:
                    logger.warning(f"⚠️ Failed to delete existing diet plans: {delete_result.get('error')}")
                    # Continue with plan creation even if cleanup fails
            
            # Calculate plan dates (7 days from today)
            start_date = datetime.utcnow().date()
            end_date = start_date + timedelta(days=6)
            
            # 1. Create diet plan
            plan_data = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "calorie_target": health_metrics.get("target_calories", 2000),
                "protein_target": health_metrics.get("macronutrients", {}).get("protein_g", 150),
                "carb_target": health_metrics.get("macronutrients", {}).get("carb_g", 200),
                "fat_target": health_metrics.get("macronutrients", {}).get("fat_g", 67),
                "plan_name": diet_plan.get("plan_name", "Personalized 7-Day Diet Plan"),
                "status": "active"  # Explicitly set status
            }
            
            plan_result = await supabase_manager.create_diet_plan(user_id, plan_data)
            if not plan_result["success"]:
                logger.error(f"Failed to create diet plan: {plan_result.get('error')}")
                return {"success": False, "error": "Failed to save diet plan"}
            
            plan_id = plan_result["plan_id"]
            logger.info(f"✅ Diet plan created with ID: {plan_id}")
            
            # 2. Create daily plans and meals
            daily_meals = diet_plan.get("daily_meals", [])
            logger.info(f"🔍 Initial daily_meals from diet_plan: {len(daily_meals)} items")
            logger.info(f"🔍 diet_plan keys: {list(diet_plan.keys())}")
            
            if not daily_meals:
                logger.info("🚨 No daily meals in LLM response, creating comprehensive 7-day plan")
                # If no daily meals, create a comprehensive 7-day plan
                try:
                    logger.info("🔄 Calling _create_comprehensive_7_day_plan...")
                    daily_meals = self._create_comprehensive_7_day_plan(profile_data, health_metrics)
                    logger.info(f"✅ Created {len(daily_meals)} daily plans with {sum(len(day.get('meals', [])) for day in daily_meals)} total meals")
                    
                    # Debug: Check the structure of the first day if it exists
                    if daily_meals and len(daily_meals) > 0:
                        first_day = daily_meals[0]
                        logger.info(f"🔍 First day structure: {list(first_day.keys())}")
                        if 'meals' in first_day:
                            logger.info(f"🔍 First day meals: {len(first_day['meals'])} meals")
                        else:
                            logger.warning("⚠️ First day missing 'meals' key")
                    else:
                        logger.warning("⚠️ daily_meals is empty after _create_comprehensive_7_day_plan")
                        
                except Exception as e:
                    logger.error(f"❌ Error creating comprehensive 30-day plan: {str(e)}")
                    logger.error(f"❌ Exception type: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    # Create a minimal fallback
                    logger.info("🔄 Creating minimal fallback plan...")
                    daily_meals = self._create_minimal_fallback_plan(profile_data, health_metrics)
                    logger.info(f"✅ Created minimal fallback plan with {len(daily_meals)} days")
            else:
                logger.info(f"✅ Using LLM-generated daily meals: {len(daily_meals)} days")
            
            # Process each day
            for day_index, day_data in enumerate(daily_meals):
                current_date = start_date + timedelta(days=day_index)
                
                # Create daily plan
                daily_data = {
                    "date": current_date.isoformat(),
                    "total_calories": health_metrics.get("target_calories", 2000),
                    "total_protein": health_metrics.get("macronutrients", {}).get("protein_g", 150),
                    "total_carbs": health_metrics.get("macronutrients", {}).get("carb_g", 200),
                    "total_fat": health_metrics.get("macronutrients", {}).get("fat_g", 67),
                    "water_intake_target": 2.5,  # Default 2.5L per day
                    "notes": day_data.get("notes", "")
                }
                
                daily_result = await supabase_manager.create_daily_plan(plan_id, daily_data)
                if not daily_result["success"]:
                    logger.error(f"Failed to create daily plan for {current_date}: {daily_result.get('error')}")
                    continue
                
                daily_plan_id = daily_result["daily_plan_id"]
                
                # Create meals for this day
                meals = day_data.get("meals", [])
                if not meals:
                    # Create default meal structure
                    meals = self._create_default_meals(health_metrics)
                
                for meal_data in meals:
                    # Create meal
                    meal_info = {
                        "meal_type": meal_data.get("type", "Breakfast"),
                        "meal_time": meal_data.get("timing", "08:00"),
                        "meal_name": meal_data.get("name", "Healthy Meal"),
                        "calories": meal_data.get("calories", 0),
                        "protein": meal_data.get("protein", 0),
                        "carbs": meal_data.get("carbs", 0),
                        "fat": meal_data.get("fat", 0),
                        "fiber": meal_data.get("fiber", 0),
                        "instructions": meal_data.get("instructions", ""),
                        "difficulty_level": meal_data.get("difficulty", "beginner"),
                        "prep_time_minutes": meal_data.get("prep_time", 10),
                        "cooking_time_minutes": meal_data.get("cooking_time", 15),
                        "cost_category": meal_data.get("cost_category", "budget")
                    }
                    
                    meal_result = await supabase_manager.create_meal(daily_plan_id, meal_info)
                    if not meal_result["success"]:
                        logger.error(f"Failed to create meal: {meal_result.get('error')}")
                        continue
                    
                    meal_id = meal_result["meal_id"]
                    
                    # Create food items for this meal
                    ingredients = meal_data.get("ingredients", [])
                    if ingredients:
                        for ingredient in ingredients:
                            if isinstance(ingredient, dict):
                                food_data = {
                                    "food_name": ingredient.get("item", "Food item"),
                                    "quantity": ingredient.get("quantity", 100),
                                    "unit": ingredient.get("unit", "g"),
                                    "calories": ingredient.get("calories", 0),
                                    "protein": ingredient.get("protein", 0),
                                    "carbs": ingredient.get("carbs", 0),
                                    "fat": ingredient.get("fat", 0),
                                    "fiber": ingredient.get("fiber", 0)
                                }
                            else:
                                # Handle simple string ingredients
                                food_data = {
                                    "food_name": str(ingredient),
                                    "quantity": 100,
                                    "unit": "g",
                                    "calories": 0,
                                    "protein": 0,
                                    "carbs": 0,
                                    "fat": 0,
                                    "fiber": 0
                                }
                            
                            await supabase_manager.create_food_item(meal_id, food_data)
            
            # 4. Create initial progress tracking entry for the user
            progress_data = {
                "date": start_date.isoformat(),
                "weight_kg": profile_data.get("current_weight_kg", profile_data.get("weight_kg")),
                "waist_cm": profile_data.get("waist_cm"),
                "energy_level": 7,  # Default starting energy level
                "compliance_percentage": 100.0,  # Starting compliance
                "notes": f"Diet plan started. Target: {health_metrics.get('target_calories', 2000)} calories/day"
            }
            
            progress_result = await supabase_manager.create_progress_tracking(user_id, progress_data)
            if progress_result["success"]:
                logger.info(f"✅ Progress tracking created for user: {user_id}")
            else:
                logger.warning(f"⚠️ Failed to create progress tracking: {progress_result.get('error')}")
            
            logger.info(f"✅ Diet plan saved to database successfully: {plan_id}")
            return {
                "success": True,
                "plan_id": plan_id,
                "message": "Diet plan saved to database",
                "total_days": len(daily_meals),
                "progress_tracking_created": progress_result.get("success", False)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to save diet plan to database: {str(e)}")
            return {
                "success": False,
                "error": f"Database save failed: {str(e)}"
            }
    
    def _create_sample_daily_structure(self, health_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create a sample daily meal structure when AI doesn't provide detailed meals"""
        target_calories = health_metrics.get("target_calories", 2000)
        
        return {
            "date": datetime.utcnow().date().isoformat(),
            "total_calories": target_calories,
            "total_protein": health_metrics.get("macronutrients", {}).get("protein_g", 150),
            "total_carbs": health_metrics.get("macronutrients", {}).get("carb_g", 200),
            "total_fat": health_metrics.get("macronutrients", {}).get("fat_g", 67),
            "water_intake_target": 2.5,
            "notes": "Sample daily structure with balanced nutrition",
            "meals": [
                {
                    "type": "Breakfast",
                    "timing": "08:00",
                    "name": "Protein Oatmeal Bowl",
                    "calories": int(target_calories * 0.25),
                    "protein": int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * 0.25),
                    "carbs": int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * 0.25),
                    "fat": int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * 0.25),
                    "fiber": 8.0,
                    "instructions": "Cook oats with milk, add protein powder, top with nuts and berries",
                    "difficulty": "beginner",
                    "prep_time": 5,
                    "cooking_time": 10,
                    "cost_category": "budget",
                    "ingredients": [
                        {"item": "rolled oats", "quantity": 60.0, "unit": "g", "calories": 228, "protein": 8.0, "carbs": 40.0, "fat": 4.0, "fiber": 6.0},
                        {"item": "protein powder", "quantity": 30.0, "unit": "g", "calories": 120, "protein": 24.0, "carbs": 3.0, "fat": 1.0, "fiber": 0.0},
                        {"item": "almonds", "quantity": 15.0, "unit": "g", "calories": 87, "protein": 3.0, "carbs": 3.0, "fat": 8.0, "fiber": 2.0}
                    ]
                },
                {
                    "type": "Lunch",
                    "timing": "13:00",
                    "name": "Grilled Chicken Salad",
                    "calories": int(target_calories * 0.35),
                    "protein": int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * 0.35),
                    "carbs": int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * 0.35),
                    "fat": int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * 0.35),
                    "fiber": 12.0,
                    "instructions": "Grill chicken breast, serve with mixed greens and olive oil dressing",
                    "difficulty": "beginner",
                    "prep_time": 10,
                    "cooking_time": 15,
                    "cost_category": "moderate",
                    "ingredients": [
                        {"item": "chicken breast", "quantity": 150.0, "unit": "g", "calories": 165, "protein": 31.0, "carbs": 0.0, "fat": 3.6, "fiber": 0.0},
                        {"item": "mixed greens", "quantity": 100.0, "unit": "g", "calories": 25, "protein": 2.0, "carbs": 4.0, "fat": 0.0, "fiber": 2.0},
                        {"item": "olive oil", "quantity": 15.0, "unit": "ml", "calories": 135, "protein": 0.0, "carbs": 0.0, "fat": 15.0, "fiber": 0.0}
                    ]
                },
                {
                    "type": "Dinner",
                    "timing": "19:00",
                    "name": "Salmon with Vegetables",
                    "calories": int(target_calories * 0.30),
                    "protein": int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * 0.30),
                    "carbs": int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * 0.30),
                    "fat": int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * 0.30),
                    "fiber": 8.0,
                    "instructions": "Bake salmon fillet with steamed vegetables",
                    "difficulty": "beginner",
                    "prep_time": 10,
                    "cooking_time": 20,
                    "cost_category": "premium",
                    "ingredients": [
                        {"item": "salmon fillet", "quantity": 120.0, "unit": "g", "calories": 240, "protein": 25.0, "carbs": 0.0, "fat": 14.0, "fiber": 0.0},
                        {"item": "broccoli", "quantity": 100.0, "unit": "g", "calories": 25, "protein": 2.8, "carbs": 7.0, "fat": 0.4, "fiber": 2.6},
                        {"item": "quinoa", "quantity": 80.0, "unit": "g", "calories": 120, "protein": 4.0, "carbs": 22.0, "fat": 2.0, "fiber": 2.0}
                    ]
                }
            ]
        }
    
    def _create_default_meals(self, health_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create default meal structure when no meals are provided"""
        target_calories = health_metrics.get("target_calories", 2000)
        
        return [
            {
                "type": "Breakfast",
                "timing": "08:00",
                "name": "Balanced Breakfast",
                "calories": int(target_calories * 0.25),
                "protein": int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * 0.25),
                "carbs": int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * 0.25),
                "fat": int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * 0.25),
                "fiber": 8.0,
                "instructions": "Follow your personalized meal plan",
                "difficulty": "beginner",
                "prep_time": 10,
                "cooking_time": 15,
                "cost_category": "budget"
            },
            {
                "type": "Lunch",
                "timing": "13:00",
                "name": "Nutritious Lunch",
                "calories": int(target_calories * 0.35),
                "protein": int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * 0.35),
                "carbs": int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * 0.35),
                "fat": int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * 0.35),
                "fiber": 12.0,
                "instructions": "Follow your personalized meal plan",
                "difficulty": "beginner",
                "prep_time": 15,
                "cooking_time": 20,
                "cost_category": "moderate"
            },
            {
                "type": "Dinner",
                "timing": "19:00",
                "name": "Light Dinner",
                "calories": int(target_calories * 0.30),
                "protein": int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * 0.30),
                "carbs": int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * 0.30),
                "fat": int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * 0.30),
                "fiber": 8.0,
                "instructions": "Follow your personalized meal plan",
                "difficulty": "beginner",
                "prep_time": 10,
                "cooking_time": 15,
                "cost_category": "budget"
            }
        ]
    
    def _create_comprehensive_7_day_plan(self, profile_data: Dict[str, Any], health_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a comprehensive 7-day diet plan with realistic data for all days"""
        daily_plans = []
        start_date = datetime.utcnow().date()
        
        # Meal variations for variety
        breakfast_options = [
            {"name": "Protein Oatmeal Bowl", "base_calories": 0.25, "fiber": 8.0, "difficulty": "beginner", "cost": "budget"},
            {"name": "Greek Yogurt Parfait", "base_calories": 0.25, "fiber": 6.0, "difficulty": "beginner", "cost": "moderate"},
            {"name": "Egg and Toast", "base_calories": 0.25, "fiber": 4.0, "difficulty": "beginner", "cost": "budget"},
            {"name": "Smoothie Bowl", "base_calories": 0.25, "fiber": 7.0, "difficulty": "beginner", "cost": "moderate"}
        ]
        
        lunch_options = [
            {"name": "Grilled Chicken Salad", "base_calories": 0.35, "fiber": 12.0, "difficulty": "beginner", "cost": "moderate"},
            {"name": "Quinoa Buddha Bowl", "base_calories": 0.35, "fiber": 15.0, "difficulty": "intermediate", "cost": "budget"},
            {"name": "Turkey Wrap", "base_calories": 0.35, "fiber": 8.0, "difficulty": "beginner", "cost": "budget"},
            {"name": "Lentil Soup", "base_calories": 0.35, "fiber": 18.0, "difficulty": "beginner", "cost": "budget"}
        ]
        
        dinner_options = [
            {"name": "Salmon with Vegetables", "base_calories": 0.30, "fiber": 8.0, "difficulty": "intermediate", "cost": "premium"},
            {"name": "Stir-Fried Tofu", "base_calories": 0.30, "fiber": 10.0, "difficulty": "beginner", "cost": "budget"},
            {"name": "Lean Beef Steak", "base_calories": 0.30, "fiber": 6.0, "difficulty": "intermediate", "cost": "premium"},
            {"name": "Chickpea Curry", "base_calories": 0.30, "fiber": 12.0, "difficulty": "beginner", "cost": "budget"}
        ]
        
        # Generate 7 days of meal plans (Monday through Sunday)
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            
            # Select meal variations for variety
            breakfast = breakfast_options[day % len(breakfast_options)]
            lunch = lunch_options[day % len(lunch_options)]
            dinner = dinner_options[day % len(dinner_options)]
            
            target_calories = health_metrics.get("target_calories", 2000)
            
            daily_plan = {
                "date": current_date.isoformat(),
                "total_calories": target_calories,
                "total_protein": health_metrics.get("macronutrients", {}).get("protein_g", 150),
                "total_carbs": health_metrics.get("macronutrients", {}).get("carb_g", 200),
                "total_fat": health_metrics.get("macronutrients", {}).get("fat_g", 67),
                "water_intake_target": 2.5 + (day % 3) * 0.2,  # Vary water intake slightly
                "notes": f"{day_names[day]} - {day_names[day].lower()} meal plan with balanced nutrition",
                "meals": [
                    {
                        "type": "Breakfast",
                        "timing": "08:00",
                        "name": breakfast["name"],
                        "calories": int(target_calories * breakfast["base_calories"]),
                        "protein": int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * breakfast["base_calories"]),
                        "carbs": int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * breakfast["base_calories"]),
                        "fat": int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * breakfast["base_calories"]),
                        "fiber": breakfast["fiber"],
                        "instructions": f"Prepare {breakfast['name'].lower()} following your meal plan guidelines",
                        "difficulty": breakfast["difficulty"],
                        "prep_time": 5 + (day % 3) * 2,
                        "cooking_time": 10 + (day % 3) * 3,
                        "cost_category": breakfast["cost"],
                        "ingredients": self._create_realistic_food_items(
                            "Breakfast",
                            int(target_calories * breakfast["base_calories"]),
                            int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * breakfast["base_calories"]),
                            int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * breakfast["base_calories"]),
                            int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * breakfast["base_calories"]),
                            breakfast["fiber"]
                        )
                    },
                    {
                        "type": "Snack",
                        "timing": "10:30",
                        "name": "Greek Yogurt with Nuts",
                        "calories": int(target_calories * 0.15),
                        "protein": int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * 0.15),
                        "carbs": int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * 0.15),
                        "fat": int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * 0.15),
                        "fiber": 3.0,
                        "instructions": "Mix Greek yogurt with a handful of mixed nuts for a protein-rich snack",
                        "difficulty": "beginner",
                        "prep_time": 2,
                        "cooking_time": 0,
                        "cost_category": "moderate",
                        "ingredients": self._create_realistic_food_items(
                            "Snack",
                            int(target_calories * 0.15),
                            int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * 0.15),
                            int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * 0.15),
                            int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * 0.15),
                            3.0
                        )
                    },
                    {
                        "type": "Lunch",
                        "timing": "13:00",
                        "name": lunch["name"],
                        "calories": int(target_calories * lunch["base_calories"]),
                        "protein": int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * lunch["base_calories"]),
                        "carbs": int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * lunch["base_calories"]),
                        "fat": int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * lunch["base_calories"]),
                        "fiber": lunch["fiber"],
                        "instructions": f"Prepare {lunch['name'].lower()} following your meal plan guidelines",
                        "difficulty": lunch["difficulty"],
                        "prep_time": 10 + (day % 3) * 2,
                        "cooking_time": 15 + (day % 3) * 3,
                        "cost_category": lunch["cost"],
                        "ingredients": self._create_realistic_food_items(
                            "Lunch",
                            int(target_calories * lunch["base_calories"]),
                            int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * lunch["base_calories"]),
                            int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * lunch["base_calories"]),
                            int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * lunch["base_calories"]),
                            lunch["fiber"]
                        )
                    },
                    {
                        "type": "Snack",
                        "timing": "16:00",
                        "name": "Apple with Peanut Butter",
                        "calories": int(target_calories * 0.10),
                        "protein": int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * 0.10),
                        "carbs": int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * 0.10),
                        "fat": int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * 0.10),
                        "fiber": 4.0,
                        "instructions": "Slice apple and serve with natural peanut butter for a healthy afternoon snack",
                        "difficulty": "beginner",
                        "prep_time": 3,
                        "cooking_time": 0,
                        "cost_category": "budget",
                        "ingredients": self._create_realistic_food_items(
                            "Snack",
                            int(target_calories * 0.10),
                            int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * 0.10),
                            int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * 0.10),
                            int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * 0.10),
                            4.0
                        )
                    },
                    {
                        "type": "Dinner",
                        "timing": "19:00",
                        "name": dinner["name"],
                        "calories": int(target_calories * dinner["base_calories"]),
                        "protein": int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * dinner["base_calories"]),
                        "carbs": int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * dinner["base_calories"]),
                        "fat": int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * dinner["base_calories"]),
                        "fiber": dinner["fiber"],
                        "instructions": f"Prepare {dinner['name'].lower()} following your meal plan guidelines",
                        "difficulty": dinner["difficulty"],
                        "prep_time": 10 + (day % 3) * 2,
                        "cooking_time": 20 + (day % 3) * 3,
                        "cost_category": dinner["cost"],
                        "ingredients": self._create_realistic_food_items(
                            "Dinner",
                            int(target_calories * dinner["base_calories"]),
                            int(health_metrics.get("macronutrients", {}).get("protein_g", 150) * dinner["base_calories"]),
                            int(health_metrics.get("macronutrients", {}).get("carb_g", 200) * dinner["base_calories"]),
                            int(health_metrics.get("macronutrients", {}).get("fat_g", 67) * dinner["base_calories"]),
                            dinner["fiber"]
                        )
                    }
                ]
            }
            
            daily_plans.append(daily_plan)
        
        return daily_plans
    
    def _create_realistic_food_items(self, meal_type: str, meal_calories: int, meal_protein: float, meal_carbs: float, meal_fat: float, meal_fiber: float) -> List[Dict[str, Any]]:
        """Create realistic food items for a meal with proper nutritional breakdown"""
        
        # Food database with nutritional information per 100g
        food_database = {
            "Breakfast": {
                "rolled oats": {"calories": 380, "protein": 13.0, "carbs": 68.0, "fat": 6.0, "fiber": 10.0},
                "protein powder": {"calories": 400, "protein": 80.0, "carbs": 10.0, "fat": 3.0, "fiber": 0.0},
                "almonds": {"calories": 579, "protein": 21.0, "carbs": 22.0, "fat": 50.0, "fiber": 12.0},
                "berries": {"calories": 50, "protein": 1.0, "carbs": 12.0, "fat": 0.0, "fiber": 5.0},
                "milk": {"calories": 50, "protein": 3.3, "carbs": 5.0, "fat": 2.0, "fiber": 0.0},
                "eggs": {"calories": 155, "protein": 13.0, "carbs": 1.1, "fat": 11.0, "fiber": 0.0},
                "bread": {"calories": 265, "protein": 9.0, "carbs": 49.0, "fat": 3.0, "fiber": 4.0},
                "greek yogurt": {"calories": 60, "protein": 10.0, "carbs": 4.0, "fat": 0.0, "fiber": 0.0},
                "banana": {"calories": 89, "protein": 1.1, "carbs": 23.0, "fat": 0.3, "fiber": 2.6}
            },
            "Lunch": {
                "chicken breast": {"calories": 110, "protein": 20.0, "carbs": 0.0, "fat": 2.4, "fiber": 0.0},
                "mixed greens": {"calories": 25, "protein": 2.0, "carbs": 4.0, "fat": 0.0, "fiber": 2.0},
                "olive oil": {"calories": 900, "protein": 0.0, "carbs": 0.0, "fat": 100.0, "fiber": 0.0},
                "tomatoes": {"calories": 18, "protein": 0.9, "carbs": 4.0, "fat": 0.0, "fiber": 1.2},
                "cucumber": {"calories": 16, "protein": 0.7, "carbs": 3.6, "fat": 0.1, "fiber": 0.5},
                "quinoa": {"calories": 120, "protein": 4.0, "carbs": 22.0, "fat": 2.0, "fiber": 2.0},
                "lentils": {"calories": 116, "protein": 9.0, "carbs": 20.0, "fat": 0.4, "fiber": 8.0},
                "turkey": {"calories": 135, "protein": 25.0, "carbs": 0.0, "fat": 3.0, "fiber": 0.0}
            },
            "Dinner": {
                "salmon": {"calories": 200, "protein": 20.0, "carbs": 0.0, "fat": 12.0, "fiber": 0.0},
                "broccoli": {"calories": 25, "protein": 2.8, "carbs": 7.0, "fat": 0.4, "fiber": 2.6},
                "carrots": {"calories": 41, "protein": 0.9, "carbs": 10.0, "fat": 0.0, "fiber": 2.8},
                "tofu": {"calories": 76, "protein": 8.0, "carbs": 1.9, "fat": 4.8, "fiber": 0.3},
                "beef steak": {"calories": 250, "protein": 26.0, "carbs": 0.0, "fat": 15.0, "fiber": 0.0},
                "chickpeas": {"calories": 164, "protein": 9.0, "carbs": 27.0, "fat": 2.6, "fiber": 8.0},
                "brown rice": {"calories": 111, "protein": 2.6, "carbs": 23.0, "fat": 0.9, "fiber": 1.8}
            },
            "Snack": {
                "apple": {"calories": 52, "protein": 0.3, "carbs": 14.0, "fat": 0.2, "fiber": 2.4},
                "peanut butter": {"calories": 588, "protein": 25.0, "carbs": 20.0, "fat": 50.0, "fiber": 6.0},
                "nuts": {"calories": 607, "protein": 20.0, "carbs": 23.0, "fat": 54.0, "fiber": 7.0},
                "hummus": {"calories": 166, "protein": 8.0, "carbs": 14.0, "fat": 10.0, "fiber": 6.0}
            }
        }
        
        # Get available foods for this meal type
        available_foods = food_database.get(meal_type, food_database["Breakfast"])
        
        # Calculate target quantities to meet nutritional goals
        food_items = []
        remaining_calories = meal_calories
        remaining_protein = meal_protein
        remaining_carbs = meal_carbs
        remaining_fat = meal_fat
        remaining_fiber = meal_fiber
        
        # Select 2-4 food items for variety
        num_items = min(4, len(available_foods))
        selected_foods = list(available_foods.keys())[:num_items]
        
        for i, food_name in enumerate(selected_foods):
            food_info = available_foods[food_name]
            
            # Calculate quantity based on remaining nutritional needs
            if i == num_items - 1:  # Last item - use remaining needs
                # Calculate quantity to meet remaining calories
                if food_info["calories"] > 0:
                    quantity = (remaining_calories / food_info["calories"]) * 100
                else:
                    quantity = 100
            else:
                # Use proportional quantities
                proportion = 0.3 + (i * 0.2)  # 30%, 50%, 70% distribution
                quantity = (meal_calories * proportion / food_info["calories"]) * 100
            
            # Ensure reasonable quantities (10g - 200g)
            quantity = max(10, min(200, quantity))
            
            # Calculate actual nutritional values for this quantity
            actual_calories = (quantity / 100) * food_info["calories"]
            actual_protein = (quantity / 100) * food_info["protein"]
            actual_carbs = (quantity / 100) * food_info["carbs"]
            actual_fat = (quantity / 100) * food_info["fat"]
            actual_fiber = (quantity / 100) * food_info["fiber"]
            
            # Determine appropriate unit
            if quantity >= 100:
                unit = "g"
            elif quantity >= 50:
                unit = "g"
            elif food_name in ["apple", "banana"]:
                unit = "medium"
                quantity = 1
            elif food_name in ["eggs"]:
                unit = "pieces"
                quantity = int(quantity / 50)  # Approximate egg weight
            else:
                unit = "g"
            
            food_items.append({
                "item": food_name,
                "quantity": round(quantity, 1),
                "unit": unit,
                "calories": round(actual_calories),
                "protein": round(actual_protein, 1),
                "carbs": round(actual_carbs, 1),
                "fat": round(actual_fat, 1),
                "fiber": round(actual_fiber, 1)
            })
            
            # Update remaining nutritional needs
            remaining_calories -= actual_calories
            remaining_protein -= actual_protein
            remaining_carbs -= actual_carbs
            remaining_fat -= actual_fat
            remaining_fiber -= actual_fiber
        
        return food_items

    def _get_personalized_breakfast_name(self, food_preference: str, primary_goals: List[str]) -> str:
        """Get personalized breakfast name based on food preference and goals"""
        if "weight_loss" in primary_goals:
            if food_preference == "vegetarian":
                return "High-Protein Vegetarian Breakfast Bowl"
            elif food_preference == "vegan":
                return "Protein-Rich Vegan Smoothie Bowl"
            elif food_preference == "non_vegetarian":
                return "Lean Protein Breakfast Plate"
            else:
                return "Weight Loss Breakfast Bowl"
        elif "muscle_gain" in primary_goals:
            if food_preference == "vegetarian":
                return "Muscle Building Vegetarian Breakfast"
            elif food_preference == "vegan":
                return "Plant-Based Protein Power Bowl"
            elif food_preference == "non_vegetarian":
                return "High-Protein Breakfast Platter"
            else:
                return "Muscle Building Breakfast"
        else:
            if food_preference == "vegetarian":
                return "Balanced Vegetarian Breakfast Bowl"
            elif food_preference == "vegan":
                return "Nutritious Vegan Breakfast"
            elif food_preference == "non_vegetarian":
                return "Balanced Breakfast Plate"
            else:
                return "Healthy Breakfast Bowl"

    def _get_personalized_breakfast_ingredients(self, food_preference: str, target_calories: int) -> List[Dict[str, Any]]:
        """Get personalized breakfast ingredients based on food preference"""
        if food_preference == "vegetarian":
            return [
                {"item": "rolled oats", "quantity": 60.0, "unit": "g", "calories": 228, "protein": 8.0, "carbs": 40.0, "fat": 4.0, "fiber": 6.0},
                {"item": "protein powder", "quantity": 30.0, "unit": "g", "calories": 120, "protein": 24.0, "carbs": 3.0, "fat": 1.0, "fiber": 0.0},
                {"item": "almonds", "quantity": 15.0, "unit": "g", "calories": 87, "protein": 3.0, "carbs": 3.0, "fat": 8.0, "fiber": 2.0},
                {"item": "berries", "quantity": 50.0, "unit": "g", "calories": 25, "protein": 0.5, "carbs": 6.0, "fat": 0.0, "fiber": 2.5},
                {"item": "milk", "quantity": 240.0, "unit": "ml", "calories": 120, "protein": 8.0, "carbs": 12.0, "fat": 5.0, "fiber": 0.0}
            ]
        elif food_preference == "vegan":
            return [
                {"item": "quinoa", "quantity": 80.0, "unit": "g", "calories": 120, "protein": 4.0, "carbs": 22.0, "fat": 2.0, "fiber": 2.0},
                {"item": "plant protein powder", "quantity": 30.0, "unit": "g", "calories": 120, "protein": 24.0, "carbs": 3.0, "fat": 1.0, "fiber": 0.0},
                {"item": "chia seeds", "quantity": 20.0, "unit": "g", "calories": 97, "protein": 3.4, "carbs": 8.6, "fat": 8.6, "fiber": 6.8},
                {"item": "banana", "quantity": 1.0, "unit": "medium", "calories": 105, "protein": 1.3, "carbs": 27.0, "fat": 0.4, "fiber": 3.1},
                {"item": "almond milk", "quantity": 240.0, "unit": "ml", "calories": 60, "protein": 2.0, "carbs": 8.0, "fat": 2.5, "fiber": 0.0}
            ]
        elif food_preference == "non_vegetarian":
            return [
                {"item": "eggs", "quantity": 2.0, "unit": "pieces", "calories": 140, "protein": 12.0, "carbs": 0.0, "fat": 10.0, "fiber": 0.0},
                {"item": "whole grain bread", "quantity": 60.0, "unit": "g", "calories": 160, "protein": 6.0, "carbs": 30.0, "fat": 2.0, "fiber": 4.0},
                {"item": "avocado", "quantity": 50.0, "unit": "g", "calories": 80, "protein": 1.0, "carbs": 4.0, "fat": 7.0, "fiber": 3.0},
                {"item": "spinach", "quantity": 30.0, "unit": "g", "calories": 7, "protein": 0.9, "carbs": 1.1, "fat": 0.1, "fiber": 0.7},
                {"item": "olive oil", "quantity": 5.0, "unit": "ml", "calories": 45, "protein": 0.0, "carbs": 0.0, "fat": 5.0, "fiber": 0.0}
            ]
        else:  # eggetarian
            return [
                {"item": "eggs", "quantity": 2.0, "unit": "pieces", "calories": 140, "protein": 12.0, "carbs": 0.0, "fat": 10.0, "fiber": 0.0},
                {"item": "rolled oats", "quantity": 60.0, "unit": "g", "calories": 228, "protein": 8.0, "carbs": 40.0, "fat": 4.0, "fiber": 6.0},
                {"item": "milk", "quantity": 240.0, "unit": "ml", "calories": 120, "protein": 8.0, "carbs": 12.0, "fat": 5.0, "fiber": 0.0},
                {"item": "honey", "quantity": 10.0, "unit": "g", "calories": 30, "protein": 0.0, "carbs": 8.0, "fat": 0.0, "fiber": 0.0},
                {"item": "nuts", "quantity": 20.0, "unit": "g", "calories": 120, "protein": 4.0, "carbs": 4.0, "fat": 10.0, "fiber": 2.0}
            ]

    def _get_personalized_breakfast_instructions(self, food_preference: str, who_cooks: str) -> str:
        """Get personalized breakfast instructions based on food preference and cooking skill"""
        if who_cooks == "cook_helper":
            return "Ask your cook to prepare this nutritious breakfast according to the recipe"
        elif who_cooks == "family_member":
            return "Ask a family member to help prepare this healthy breakfast"
        else:
            if food_preference == "vegetarian":
                return "Cook oats with milk for 10 minutes, stir in protein powder, top with almonds and berries"
            elif food_preference == "vegan":
                return "Cook quinoa with almond milk, stir in plant protein powder, add chia seeds and top with banana"
            elif food_preference == "non_vegetarian":
                return "Scramble eggs with spinach, toast bread, and serve with sliced avocado and olive oil"
            else:  # eggetarian
                return "Boil eggs, cook oats with milk, and serve with honey and nuts"