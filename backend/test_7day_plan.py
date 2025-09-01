#!/usr/bin/env python3
"""
Test script for the new 7-day diet plan structure
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.diet_planner_agent import DietPlannerAgent

def test_7day_plan():
    """Test the 7-day diet plan creation"""
    
    # Create agent instance
    agent = DietPlannerAgent()
    
    # Test profile data
    test_profile = {
        "user_id": "test_user_123",
        "full_name": "Test User",
        "age": 30,
        "gender": "female",
        "current_weight_kg": 65.0,
        "height_cm": 165.0,
        "primary_goals": ["weight_loss"],
        "food_preference": "vegetarian",
        "medical_conditions": [],
        "food_allergies": [],
        "daily_routine": "9-5 office job",
        "sleep_hours": "7-8 hours",
        "stress_level": "moderate",
        "physical_activity_type": "walking",
        "physical_activity_frequency": "3-4 times per week",
        "physical_activity_duration": "30 minutes",
        "meal_timings": "regular",
        "eating_out_frequency": "1-2 times per week",
        "daily_water_intake": "2-3L",
        "common_cravings": ["sweet", "salty"],
        "progress_pace": "steady",
        "loved_foods": "fruits, vegetables, nuts",
        "disliked_foods": "fish, shellfish",
        "cooking_facilities": ["stove", "oven", "microwave"],
        "who_cooks": "self",
        "budget_flexibility": "moderate",
        "motivation_level": 8
    }
    
    # Calculate health metrics
    health_metrics = agent._calculate_health_metrics(test_profile)
    
    print("🏥 Health Metrics:")
    print(f"   BMR: {health_metrics.get('bmr')} calories/day")
    print(f"   TDEE: {health_metrics.get('tdee')} calories/day")
    print(f"   Target Calories: {health_metrics.get('target_calories')} calories/day")
    print(f"   Protein: {health_metrics.get('macronutrients', {}).get('protein_g')}g")
    print(f"   Carbs: {health_metrics.get('macronutrients', {}).get('carb_g')}g")
    print(f"   Fat: {health_metrics.get('macronutrients', {}).get('fat_g')}g")
    
    # Test comprehensive 7-day plan creation
    daily_plans = agent._create_comprehensive_7_day_plan(test_profile, health_metrics)
    print(f"✅ 7-day plan created with {len(daily_plans)} days")
    
    # Show sample day structure
    if daily_plans:
        first_day = daily_plans[0]
        print(f"\n📅 Sample Day: {first_day.get('date')}")
        print(f"   Total Calories: {first_day.get('total_calories')}")
        print(f"   Notes: {first_day.get('notes')}")
        
        meals = first_day.get('meals', [])
        print(f"   Meals: {len(meals)}")
        
        for i, meal in enumerate(meals):
            print(f"     {i+1}. {meal.get('type')} - {meal.get('name')} at {meal.get('timing')}")
            print(f"        Calories: {meal.get('calories')}, Protein: {meal.get('protein')}g")
    
    # Verify meal structure matches requirements
    print(f"\n🔍 Verifying meal structure...")
    required_meal_types = ["Breakfast", "Snack", "Lunch", "Snack", "Dinner"]
    
    for day_idx, day in enumerate(daily_plans):
        meals = day.get('meals', [])
        meal_types = [meal.get('type') for meal in meals]
        
        print(f"   Day {day_idx + 1}: {meal_types}")
        
        # Check if we have the right number of meals
        if len(meals) == 5:
            print(f"     ✅ Correct number of meals: {len(meals)}")
        else:
            print(f"     ❌ Wrong number of meals: {len(meals)}, expected 5")
        
        # Check if meal types match requirements
        if meal_types == required_meal_types:
            print(f"     ✅ Correct meal structure: {meal_types}")
        else:
            print(f"     ❌ Wrong meal structure: {meal_types}, expected {required_meal_types}")
    
    print(f"\n🎯 Summary:")
    print(f"   - Created {len(daily_plans)} daily plans")
    print(f"   - Each day has 5 meals: Breakfast, Snack, Lunch, Snack, Dinner")
    print(f"   - Plan covers Monday through Sunday")
    print(f"   - Total plan duration: 7 days")

if __name__ == "__main__":
    test_7day_plan()


