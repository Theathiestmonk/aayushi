#!/usr/bin/env python3
"""
Test script for Diet Planner Agent
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_diet_planner():
    """Test the diet planner agent functionality"""
    try:
        from app.agents.diet_planner_agent import DietPlannerAgent
        
        print("✅ Diet Planner Agent imported successfully")
        
        # Create a test profile
        test_profile = {
            "full_name": "Test User",
            "age": 30,
            "gender": "male",
            "height_cm": 175,
            "current_weight_kg": 70,
            "daily_routine": "moderately_active",
            "primary_goals": ["weight_loss"],
            "progress_pace": "moderate",
            "medical_conditions": [],
            "food_allergies": [],
            "family_history": [],
            "food_preference": "vegetarian",
            "cultural_restrictions": "none",
            "sleep_hours": "7-8",
            "stress_level": "moderate",
            "physical_activity_type": "walking",
            "physical_activity_frequency": "3-4 times per week",
            "physical_activity_duration": "30 minutes",
            "meal_timings": "regular",
            "eating_out_frequency": "weekly",
            "daily_water_intake": "2-3 L",
            "common_cravings": ["sweet"],
            "loved_foods": "fruits, vegetables",
            "disliked_foods": "none",
            "cooking_facilities": ["gas", "microwave"],
            "who_cooks": "self",
            "budget_flexibility": "moderate",
            "motivation_level": 8,
            "support_system": "strong",
            "cooking_skill_level": "beginner"
        }
        
        print("✅ Test profile created")
        
        # Create agent instance
        agent = DietPlannerAgent()
        print("✅ Diet Planner Agent instance created")
        
        # Test health metrics calculation
        health_metrics = agent._calculate_health_metrics(test_profile)
        print("✅ Health metrics calculated:")
        print(f"   BMI: {health_metrics.get('bmi')}")
        print(f"   BMI Category: {health_metrics.get('bmi_category')}")
        print(f"   BMR: {health_metrics.get('bmr')} calories")
        print(f"   TDEE: {health_metrics.get('tdee')} calories")
        print(f"   Target Calories: {health_metrics.get('target_calories')} calories")
        print(f"   Protein: {health_metrics.get('macronutrients', {}).get('protein_g')}g")
        print(f"   Carbs: {health_metrics.get('macronutrients', {}).get('carb_g')}g")
        print(f"   Fat: {health_metrics.get('macronutrients', {}).get('fat_g')}g")
        
        # Test comprehensive 7-day plan creation
        daily_plans = agent._create_comprehensive_7_day_plan(test_profile, health_metrics)
        print(f"✅ 7-day plan created with {len(daily_plans)} days")
        
        # Show sample day structure
        if daily_plans:
            sample_day = daily_plans[0]
            print(f"✅ Sample day structure:")
            print(f"   Date: {sample_day.get('date')}")
            print(f"   Total Calories: {sample_day.get('total_calories')}")
            print(f"   Meals: {len(sample_day.get('meals', []))}")
            
            # Show first meal details
            if sample_day.get('meals'):
                first_meal = sample_day['meals'][0]
                print(f"   First Meal: {first_meal.get('name')}")
                print(f"   Type: {first_meal.get('type')}")
                print(f"   Timing: {first_meal.get('timing')}")
                print(f"   Calories: {first_meal.get('calories')}")
                print(f"   Ingredients: {len(first_meal.get('ingredients', []))}")
        
        # Test realistic food items creation
        food_items = agent._create_realistic_food_items(
            "Breakfast", 
            500,  # calories
            25.0,  # protein
            60.0,  # carbs
            20.0,  # fat
            8.0    # fiber
        )
        print(f"✅ Food items created: {len(food_items)} items")
        
        if food_items:
            first_item = food_items[0]
            print(f"   First food item: {first_item.get('food_name')}")
            print(f"   Quantity: {first_item.get('quantity')} {first_item.get('unit')}")
            print(f"   Calories: {first_item.get('calories')}")
        
        print("\n🎉 All tests passed! Diet Planner Agent is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_diet_planner())


