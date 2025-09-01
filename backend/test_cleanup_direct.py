#!/usr/bin/env python3
"""
Direct test script for diet plan cleanup functionality
This script tests the cleanup methods directly without going through the agent system
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_cleanup_directly():
    """Test cleanup methods directly"""
    
    print("🧪 Testing Diet Plan Cleanup Directly")
    print("=" * 50)
    
    try:
        # Import the Supabase manager
        from app.core.supabase import SupabaseManager
        
        # Initialize Supabase manager
        print("🔧 Initializing Supabase manager...")
        supabase_manager = SupabaseManager()
        print("✅ Supabase manager initialized")
        
        # Test user ID (change this to a real user ID from your database)
        test_user_id = input("Enter a real user ID to test with (or press Enter to use 'test-user-123'): ").strip()
        if not test_user_id:
            test_user_id = "test-user-123"
        
        print(f"📋 Testing with user ID: {test_user_id}")
        
        # Test 1: Check existing data
        print("\n1️⃣ Checking existing data...")
        try:
            check_result = await supabase_manager.has_existing_diet_plans(test_user_id)
            print(f"   Has existing plans: {check_result}")
            
            count_result = await supabase_manager.get_diet_plan_count(test_user_id)
            print(f"   Plan count: {count_result}")
            
            plans_result = await supabase_manager.get_user_diet_plans(test_user_id)
            print(f"   All plans: {plans_result}")
            
        except Exception as e:
            print(f"   ❌ Error checking data: {str(e)}")
        
        # Test 2: Force clear all data
        print("\n2️⃣ Force clearing all data...")
        try:
            force_clear_result = await supabase_manager.force_clear_all_user_data(test_user_id)
            print(f"   Force clear result: {force_clear_result}")
            
            if force_clear_result["success"]:
                deleted_plans = force_clear_result.get("deleted_plans", 0)
                deleted_daily_plans = force_clear_result.get("deleted_daily_plans", 0)
                deleted_meals = force_clear_result.get("deleted_meals", 0)
                deleted_food_items = force_clear_result.get("deleted_food_items", 0)
                print(f"   ✅ Deleted: {deleted_plans} plans, {deleted_daily_plans} daily plans, {deleted_meals} meals, {deleted_food_items} food items")
            else:
                print(f"   ❌ Force clear failed: {force_clear_result.get('error')}")
                
        except Exception as e:
            print(f"   ❌ Error during force clear: {str(e)}")
        
        # Test 3: Verify data was cleared
        print("\n3️⃣ Verifying data was cleared...")
        try:
            verify_result = await supabase_manager.verify_user_data_cleared(test_user_id)
            print(f"   Verification result: {verify_result}")
            
            if verify_result["success"]:
                is_cleared = verify_result.get("is_cleared", False)
                remaining_plans = verify_result.get("remaining_plans", 0)
                remaining_daily_plans = verify_result.get("remaining_daily_plans", 0)
                remaining_meals = verify_result.get("remaining_meals", 0)
                remaining_food_items = verify_result.get("remaining_food_items", 0)
                
                if is_cleared:
                    print(f"   ✅ SUCCESS: All data cleared! No remaining records")
                else:
                    print(f"   ⚠️ PARTIAL: Some data remains - {remaining_plans} plans, {remaining_daily_plans} daily plans, {remaining_meals} meals, {remaining_food_items} food items")
            else:
                print(f"   ❌ Verification failed: {verify_result.get('error')}")
                
        except Exception as e:
            print(f"   ❌ Error during verification: {str(e)}")
        
        # Test 4: Check data again
        print("\n4️⃣ Final check of remaining data...")
        try:
            final_check = await supabase_manager.has_existing_diet_plans(test_user_id)
            final_count = await supabase_manager.get_diet_plan_count(test_user_id)
            
            print(f"   Final check - Has plans: {final_check}")
            print(f"   Final count: {final_count}")
            
        except Exception as e:
            print(f"   ❌ Error during final check: {str(e)}")
        
        print("\n✅ Direct cleanup test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Direct Cleanup Test")
    print("Make sure you have the required environment variables set:")
    print("- SUPABASE_URL")
    print("- SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY)")
    print()
    
    # Run the test
    asyncio.run(test_cleanup_directly())
    
    print("\n🎯 Test Summary:")
    print("- Direct cleanup test completed")
    print("- Check the results above for any errors")
    print("- If cleanup fails, check the error messages")
    print("- Make sure you're using a real user ID from your database")



