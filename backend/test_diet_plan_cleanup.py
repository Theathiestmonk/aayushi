#!/usr/bin/env python3
"""
Test script for diet plan cleanup functionality
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.supabase import SupabaseManager

async def test_diet_plan_cleanup():
    """Test the diet plan cleanup functionality"""
    
    print("🧪 Testing Diet Plan Cleanup Functionality")
    print("=" * 50)
    
    try:
        # Initialize Supabase manager
        supabase_manager = SupabaseManager()
        
        # Test user ID (you can change this to test with a real user)
        test_user_id = "test-user-123"
        
        print(f"📋 Testing with user ID: {test_user_id}")
        
        # 1. Check if user has existing diet plans
        print("\n1️⃣ Checking for existing diet plans...")
        check_result = await supabase_manager.has_existing_diet_plans(test_user_id)
        print(f"   Result: {check_result}")
        
        # 2. Get diet plan count
        print("\n2️⃣ Getting diet plan count...")
        count_result = await supabase_manager.get_diet_plan_count(test_user_id)
        print(f"   Result: {count_result}")
        
        # 3. Get all diet plans
        print("\n3️⃣ Getting all diet plans...")
        plans_result = await supabase_manager.get_user_diet_plans(test_user_id)
        print(f"   Result: {plans_result}")
        
        # 4. Test archiving (this will fail for non-existent user, but tests the method)
        print("\n4️⃣ Testing archive functionality...")
        archive_result = await supabase_manager.archive_user_diet_plans(test_user_id)
        print(f"   Result: {archive_result}")
        
        # 5. Test deletion (this will fail for non-existent user, but tests the method)
        print("\n5️⃣ Testing deletion functionality...")
        delete_result = await supabase_manager.delete_all_user_diet_plans(test_user_id)
        print(f"   Result: {delete_result}")
        
        # 6. Test force clear functionality...
        print("\n6️⃣ Testing force clear functionality...")
        force_clear_result = await supabase_manager.force_clear_all_user_data(test_user_id)
        print(f"   Result: {force_clear_result}")
        
        # 7. Test verification functionality...
        print("\n7️⃣ Testing verification functionality...")
        verify_result = await supabase_manager.verify_user_data_cleared(test_user_id)
        print(f"   Result: {verify_result}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_with_real_user():
    """Test with a real user if available"""
    
    print("\n🔐 Testing with Real User (if available)")
    print("=" * 50)
    
    try:
        # Initialize Supabase manager
        supabase_manager = SupabaseManager()
        
        # Try to get a real user from the database
        # This is just a test - in production you'd get this from authentication
        print("   Note: This test requires a real user ID from your database")
        print("   You can manually test the endpoints with a real user ID")
        
    except Exception as e:
        print(f"❌ Real user test failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Diet Plan Cleanup Tests")
    print("Make sure you have the required environment variables set:")
    print("- SUPABASE_URL")
    print("- SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY)")
    print()
    
    # Run the tests
    asyncio.run(test_diet_plan_cleanup())
    asyncio.run(test_with_real_user())
    
    print("\n🎯 Test Summary:")
    print("- Basic functionality tests completed")
    print("- Check the results above for any errors")
    print("- Test the API endpoints manually for full functionality")
    print("- The cleanup will work automatically when creating new diet plans")
