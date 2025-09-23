"""
Supabase client configuration and authentication utilities
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
import logging

logger = logging.getLogger(__name__)

class SupabaseManager:
    """Manages Supabase client and authentication operations"""
    
    def __init__(self):
        self._client: Optional[Client] = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Ensure the Supabase client is initialized"""
        if not self._initialized:
            self.supabase_url = os.getenv("SUPABASE_URL")
            # Use service role key for backend operations to bypass RLS
            self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
            
            if not self.supabase_url or not self.supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY) must be set in environment variables")
            
            # Initialize Supabase client
            self._client = create_client(
                self.supabase_url, 
                self.supabase_key,
                options=ClientOptions(
                    schema="public",
                    headers={
                        "X-Client-Info": "ai-dietitian-backend"
                    }
                )
            )
            
            self._initialized = True
            logger.info("✅ Supabase client initialized successfully")
            if os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
                logger.info("🔑 Using service role key (bypasses RLS)")
            else:
                logger.warning("⚠️ Using anon key (RLS policies will apply)")
    
    @property
    def client(self) -> Client:
        """Get the Supabase client, initializing if necessary"""
        self._ensure_initialized()
        return self._client
    
    async def sign_up(self, email: str, password: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new user
        
        Args:
            email: User's email address
            password: User's password
            user_data: Additional user profile data
            
        Returns:
            Registration result with user info and session
        """
        try:
            logger.info(f"🔍 Attempting to register user: {email}")
            
            # Sign up the user
            auth_response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_data
                }
            })
            
            logger.info(f"📧 Supabase auth response: {auth_response}")
            logger.info(f"👤 User object: {auth_response.user}")
            logger.info(f"🔑 Session object: {auth_response.session}")
            
            if auth_response.user:
                # Create user profile in profiles table
                profile_data = {
                    "id": auth_response.user.id,
                    "email": email,
                    "full_name": user_data.get("full_name", ""),
                    "created_at": auth_response.user.created_at,
                    "updated_at": auth_response.user.created_at
                }
                
                logger.info(f"📝 Profile data to insert: {profile_data}")
                
                try:
                    # Insert profile data
                    profile_response = self.client.table("user_profiles").insert(profile_data).execute()
                    logger.info(f"✅ User profile created successfully: {email}")
                    logger.info(f"📊 Profile response: {profile_response}")
                except Exception as profile_error:
                    logger.warning(f"⚠️ Profile creation failed, but user registered: {str(profile_error)}")
                    # Continue even if profile creation fails
                
                logger.info(f"✅ User registered successfully: {email}")
                
                return {
                    "success": True,
                    "user": auth_response.user,
                    "session": auth_response.session,
                    "profile": profile_data,
                    "message": "Registration successful"
                }
            else:
                logger.error("❌ No user object returned from Supabase")
                return {
                    "success": False,
                    "error": "Registration failed - no user data returned"
                }
                
        except Exception as e:
            logger.error(f"❌ User registration failed: {str(e)}")
            logger.error(f"❌ Exception type: {type(e)}")
            logger.error(f"❌ Exception details: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Sign in an existing user
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Sign in result with user info and session
        """
        try:
            # Sign in the user
            auth_response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user and auth_response.session:
                # Get user profile from user_profiles table (handle case where profile might not exist)
                try:
                    profile_response = self.client.table("user_profiles").select("*").eq("id", auth_response.user.id).execute()
                    profile_data = profile_response.data[0] if profile_response.data else {}
                except Exception as profile_error:
                    logger.warning(f"⚠️ Could not fetch profile for user {auth_response.user.id}: {str(profile_error)}")
                    profile_data = {}
                
                logger.info(f"✅ User signed in successfully: {email}")
                
                return {
                    "success": True,
                    "user": auth_response.user,
                    "session": auth_response.session,
                    "profile": profile_data,
                    "message": "Sign in successful"
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid credentials"
                }
                
        except Exception as e:
            logger.error(f"❌ User sign in failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sign_out(self, access_token: str) -> Dict[str, Any]:
        """
        Sign out a user
        
        Args:
            access_token: User's access token
            
        Returns:
            Sign out result
        """
        try:
            # Set the session for the client
            self.client.auth.set_session(access_token, "")
            
            # Sign out
            self.client.auth.sign_out()
            
            logger.info("✅ User signed out successfully")
            
            return {
                "success": True,
                "message": "Sign out successful"
            }
            
        except Exception as e:
            logger.error(f"❌ User sign out failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get user profile data
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            User profile data
        """
        try:
            profile_response = self.client.table("user_profiles").select("*").eq("id", user_id).execute()
            
            if profile_response.data:
                return {
                    "success": True,
                    "profile": profile_response.data[0]
                }
            else:
                return {
                    "success": False,
                    "error": "Profile not found"
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get user profile: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user profile data
        
        Args:
            user_id: User's unique identifier
            profile_data: Profile data to update
            
        Returns:
            Update result
        """
        try:
            # Add updated_at timestamp
            profile_data["updated_at"] = "now()"
            
            profile_response = self.client.table("user_profiles").update(profile_data).eq("id", user_id).execute()
            
            if profile_response.data:
                logger.info(f"✅ User profile updated successfully: {user_id}")
                
                return {
                    "success": True,
                    "profile": profile_response.data[0],
                    "message": "Profile updated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Profile update failed"
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to update user profile: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def reset_password(self, email: str) -> Dict[str, Any]:
        """
        Send password reset email
        
        Args:
            email: User's email address
            
        Returns:
            Password reset result
        """
        try:
            # Include redirect URL so the recovery flow knows where to return
            redirect_base = os.getenv("FRONTEND_URL") or "http://localhost:3000"
            redirect_url = f"{redirect_base.rstrip('/')}/reset-password"
            
            try:
                self.client.auth.reset_password_email(email, {"redirect_to": redirect_url})
            except TypeError:
                # Some SDK versions accept keyword options
                self.client.auth.reset_password_email(email, options={"redirect_to": redirect_url})
            
            logger.info(f"✅ Password reset email sent: {email}")
            
            return {
                "success": True,
                "message": "Password reset email sent",
                "redirect_to": redirect_url
            }
            
        except Exception as e:
            logger.error(f"❌ Password reset failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_user_session(self, access_token: str) -> Dict[str, Any]:
        """
        Verify if a user session is valid
        
        Args:
            access_token: User's access token
            
        Returns:
            Session verification result
        """
        try:
            # Set the session for the client
            self.client.auth.set_session(access_token, "")
            
            # Get current user
            user = self.client.auth.get_user()
            
            if user:
                return {
                    "success": True,
                    "user": user,
                    "valid": True
                }
            else:
                return {
                    "success": False,
                    "valid": False,
                    "error": "Invalid session"
                }
                
        except Exception as e:
            logger.error(f"❌ Session verification failed: {str(e)}")
            return {
                "success": False,
                "valid": False,
                "error": str(e)
            }

    async def create_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user profile
        
        Args:
            user_id: User's unique identifier
            profile_data: Complete profile data
            
        Returns:
            Profile creation result
        """
        try:
            # Use service role client to bypass RLS for profile creation
            # This is safe because we're validating the user_id in the backend
            profile_response = self.client.table("user_profiles").insert(profile_data).execute()
            
            if profile_response.data:
                logger.info(f"✅ User profile created successfully: {user_id}")
                
                return {
                    "success": True,
                    "profile": profile_response.data[0],
                    "message": "Profile created successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Profile creation failed"
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to create user profile: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def upsert_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update user profile data (upsert)
        
        Args:
            user_id: User's unique identifier
            profile_data: Profile data to create or update
            
        Returns:
            Upsert result
        """
        try:
            # Check if profile exists
            existing_profile = await self.get_user_profile(user_id)
            
            if existing_profile["success"]:
                # Profile exists, update it
                logger.info(f"🔄 Profile exists, updating: {user_id}")
                return await self.update_user_profile(user_id, profile_data)
            else:
                # Profile doesn't exist, create it
                logger.info(f"🆕 Profile doesn't exist, creating: {user_id}")
                return await self.create_user_profile(user_id, profile_data)
                
        except Exception as e:
            logger.error(f"❌ Failed to upsert user profile: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    # Diet Plan Management Methods
    
    async def create_diet_plan(self, user_id: str, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new diet plan
        
        Args:
            user_id: User's unique identifier
            plan_data: Diet plan data including start_date, end_date, targets, etc.
            
        Returns:
            Creation result with plan_id
        """
        try:
            # Add user_id to plan data
            plan_data["user_id"] = user_id
            
            # Insert diet plan
            plan_response = self.client.table("diet_plans").insert(plan_data).execute()
            
            if plan_response.data:
                plan_id = plan_response.data[0]["plan_id"]
                logger.info(f"✅ Diet plan created successfully: {plan_id}")
                
                return {
                    "success": True,
                    "plan_id": plan_id,
                    "plan": plan_response.data[0],
                    "message": "Diet plan created successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create diet plan"
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to create diet plan: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_daily_plan(self, plan_id: str, daily_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a daily plan entry
        
        Args:
            plan_id: Diet plan ID
            daily_data: Daily plan data including date, nutrition targets, etc.
            
        Returns:
            Creation result with daily_plan_id
        """
        try:
            # Validate that the date is within the plan's date range
            plan_response = self.client.table("diet_plans").select("start_date, end_date").eq("plan_id", plan_id).execute()
            
            if not plan_response.data:
                return {
                    "success": False,
                    "error": "Diet plan not found"
                }
            
            plan = plan_response.data[0]
            plan_start = plan["start_date"]
            plan_end = plan["end_date"]
            daily_date = daily_data.get("date")
            
            if daily_date:
                # Convert string dates to date objects if needed
                if isinstance(daily_date, str):
                    daily_date = datetime.fromisoformat(daily_date.replace('Z', '+00:00')).date()
                if isinstance(plan_start, str):
                    plan_start = datetime.fromisoformat(plan_start.replace('Z', '+00:00')).date()
                if isinstance(plan_end, str):
                    plan_end = datetime.fromisoformat(plan_end.replace('Z', '+00:00')).date()
                
                # Check if daily date is within plan range
                if daily_date < plan_start or daily_date > plan_end:
                    return {
                        "success": False,
                        "error": f"Date {daily_date} is outside the plan range ({plan_start} to {plan_end})"
                    }
            
            # Add plan_id to daily data
            daily_data["plan_id"] = plan_id
            
            # Insert daily plan
            daily_response = self.client.table("daily_plans").insert(daily_data).execute()
            
            if daily_response.data:
                daily_plan_id = daily_response.data[0]["daily_plan_id"]
                logger.info(f"✅ Daily plan created successfully: {daily_plan_id}")
                
                return {
                    "success": True,
                    "daily_plan_id": daily_plan_id,
                    "daily_plan": daily_response.data[0],
                    "message": "Daily plan created successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create daily plan"
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to create daily plan: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_meal(self, daily_plan_id: str, meal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a meal entry
        
        Args:
            daily_plan_id: Daily plan ID
            meal_data: Meal data including type, timing, nutrition, etc.
            
        Returns:
            Creation result with meal_id
        """
        try:
            # Add daily_plan_id to meal data
            meal_data["daily_plan_id"] = daily_plan_id
            
            # Insert meal
            meal_response = self.client.table("meals").insert(meal_data).execute()
            
            if meal_response.data:
                meal_id = meal_response.data[0]["meal_id"]
                logger.info(f"✅ Meal created successfully: {meal_id}")
                
                return {
                    "success": True,
                    "meal_id": meal_id,
                    "meal": meal_response.data[0],
                    "message": "Meal created successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create meal"
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to create meal: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_food_item(self, meal_id: str, food_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a food item entry
        
        Args:
            meal_id: Meal ID
            food_data: Food item data including name, quantity, nutrition, etc.
            
        Returns:
            Creation result with food_id
        """
        try:
            # Add meal_id to food data
            food_data["meal_id"] = meal_id
            
            # Insert food item
            food_response = self.client.table("food_items").insert(food_data).execute()
            
            if food_response.data:
                food_id = food_response.data[0]["food_id"]
                logger.info(f"✅ Food item created successfully: {food_id}")
                
                return {
                    "success": True,
                    "food_id": food_id,
                    "food_item": food_response.data[0],
                    "message": "Food item created successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create food item"
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to create food item: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_diet_plans(self, user_id: str) -> Dict[str, Any]:
        """
        Get all diet plans for a user
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            List of diet plans
        """
        try:
            plans_response = self.client.table("diet_plans").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            
            if plans_response.data:
                return {
                    "success": True,
                    "plans": plans_response.data
                }
            else:
                return {
                    "success": True,
                    "plans": []
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get user diet plans: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_all_user_diet_plans(self, user_id: str) -> Dict[str, Any]:
        """
        Delete all existing diet plans for a user to avoid duplicates
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            Deletion result with count of deleted plans
        """
        try:
            logger.info(f"🧹 Cleaning up existing diet plans for user: {user_id}")
            
            # Get all diet plans for the user
            plans_response = self.client.table("diet_plans").select("plan_id").eq("user_id", user_id).execute()
            
            if not plans_response.data:
                logger.info(f"✅ No existing diet plans found for user: {user_id}")
                return {
                    "success": True,
                    "deleted_count": 0,
                    "message": "No existing diet plans to delete"
                }
            
            deleted_count = 0
            
            # Delete each diet plan (cascade will handle daily_plans, meals, and food_items)
            for plan in plans_response.data:
                plan_id = plan["plan_id"]
                try:
                    # Delete the diet plan (cascade will delete related records)
                    delete_response = self.client.table("diet_plans").delete().eq("plan_id", plan_id).execute()
                    
                    if delete_response.data:
                        deleted_count += 1
                        logger.info(f"✅ Deleted diet plan: {plan_id}")
                    else:
                        logger.warning(f"⚠️ No data returned when deleting diet plan: {plan_id}")
                        
                except Exception as e:
                    logger.error(f"❌ Failed to delete diet plan {plan_id}: {str(e)}")
                    # Continue with other plans even if one fails
            
            logger.info(f"✅ Successfully deleted {deleted_count} diet plans for user: {user_id}")
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "message": f"Successfully deleted {deleted_count} existing diet plans"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to delete user diet plans: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def force_clear_all_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Force clear ALL diet-related data for a user (nuclear option)
        This method directly deletes all related records to ensure complete cleanup
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            Clear result with counts of deleted records
        """
        try:
            logger.info(f"💥 Force clearing ALL diet data for user: {user_id}")
            
            # Get all diet plans for the user
            plans_response = self.client.table("diet_plans").select("plan_id").eq("user_id", user_id).execute()
            
            if not plans_response.data:
                logger.info(f"✅ No existing diet plans found for user: {user_id}")
                return {
                    "success": True,
                    "deleted_plans": 0,
                    "deleted_daily_plans": 0,
                    "deleted_meals": 0,
                    "deleted_food_items": 0,
                    "message": "No existing diet data to clear"
                }
            
            total_deleted_plans = 0
            total_deleted_daily_plans = 0
            total_deleted_meals = 0
            total_deleted_food_items = 0
            
            # Force delete each diet plan and all related data
            for plan in plans_response.data:
                plan_id = plan["plan_id"]
                logger.info(f"🗑️ Force deleting diet plan: {plan_id}")
                
                try:
                    # Get all daily plans for this diet plan
                    daily_response = self.client.table("daily_plans").select("daily_plan_id").eq("plan_id", plan_id).execute()
                    daily_plans = daily_response.data if daily_response.data else []
                    logger.info(f"   📋 Found {len(daily_plans)} daily plans for diet plan: {plan_id}")
                    
                    # Get all meals and food items for each daily plan
                    for daily_plan in daily_plans:
                        daily_plan_id = daily_plan["daily_plan_id"]
                        logger.info(f"   🗑️ Processing daily plan: {daily_plan_id}")
                        
                        # Get meals for this daily plan
                        meals_response = self.client.table("meals").select("meal_id").eq("daily_plan_id", daily_plan_id).execute()
                        meals = meals_response.data if meals_response.data else []
                        logger.info(f"   📋 Found {len(meals)} meals for daily plan: {daily_plan_id}")
                        
                        # Delete food items for each meal
                        for meal in meals:
                            meal_id = meal["meal_id"]
                            try:
                                logger.info(f"      🗑️ Deleting food items for meal: {meal_id}")
                                food_delete = self.client.table("food_items").delete().eq("meal_id", meal_id).execute()
                                if food_delete.data:
                                    total_deleted_food_items += len(food_delete.data)
                                    logger.info(f"      ✅ Deleted {len(food_delete.data)} food items for meal: {meal_id}")
                                else:
                                    logger.warning(f"      ⚠️ No food items found for meal: {meal_id}")
                            except Exception as e:
                                logger.warning(f"      ⚠️ Failed to delete food items for meal {meal_id}: {str(e)}")
                        
                        # Delete meals for this daily plan
                        try:
                            logger.info(f"   🗑️ Deleting meals for daily plan: {daily_plan_id}")
                            meals_delete = self.client.table("meals").delete().eq("daily_plan_id", daily_plan_id).execute()
                            if meals_delete.data:
                                total_deleted_meals += len(meals_delete.data)
                                logger.info(f"   ✅ Deleted {len(meals_delete.data)} meals for daily plan: {daily_plan_id}")
                            else:
                                logger.warning(f"   ⚠️ No meals found for daily plan: {daily_plan_id}")
                        except Exception as e:
                            logger.warning(f"   ⚠️ Failed to delete meals for daily plan {daily_plan_id}: {str(e)}")
                        
                        # Delete daily plan
                        try:
                            logger.info(f"   🗑️ Deleting daily plan: {daily_plan_id}")
                            daily_delete = self.client.table("daily_plans").delete().eq("daily_plan_id", daily_plan_id).execute()
                            if daily_delete.data:
                                total_deleted_daily_plans += len(daily_delete.data)
                                logger.info(f"   ✅ Deleted daily plan: {daily_plan_id}")
                            else:
                                logger.warning(f"   ⚠️ No daily plan found: {daily_plan_id}")
                        except Exception as e:
                            logger.warning(f"   ⚠️ Failed to delete daily plan {daily_plan_id}: {str(e)}")
                    
                    # Finally delete the diet plan itself
                    logger.info(f"🗑️ Deleting diet plan: {plan_id}")
                    plan_delete = self.client.table("diet_plans").delete().eq("plan_id", plan_id).execute()
                    if plan_delete.data:
                        total_deleted_plans += 1
                        logger.info(f"✅ Successfully deleted diet plan: {plan_id}")
                    else:
                        logger.warning(f"⚠️ No data returned when deleting diet plan: {plan_id}")
                        
                except Exception as e:
                    logger.error(f"❌ Failed to delete diet plan {plan_id}: {str(e)}")
                    # Continue with other plans even if one fails
            
            logger.info(f"💥 Force clear completed for user: {user_id}")
            logger.info(f"   - Deleted {total_deleted_plans} diet plans")
            logger.info(f"   - Deleted {total_deleted_daily_plans} daily plans")
            logger.info(f"   - Deleted {total_deleted_meals} meals")
            logger.info(f"   - Deleted {total_deleted_food_items} food items")
            
            return {
                "success": True,
                "deleted_plans": total_deleted_plans,
                "deleted_daily_plans": total_deleted_daily_plans,
                "deleted_meals": total_deleted_meals,
                "deleted_food_items": total_deleted_food_items,
                "message": f"Force cleared all diet data: {total_deleted_plans} plans, {total_deleted_daily_plans} daily plans, {total_deleted_meals} meals, {total_deleted_food_items} food items"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to force clear user diet data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_user_data_cleared(self, user_id: str) -> Dict[str, Any]:
        """
        Verify that all diet-related data has been cleared for a user
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            Verification result with counts of remaining records
        """
        try:
            logger.info(f"🔍 Verifying data clearance for user: {user_id}")
            
            # Check diet plans
            plans_response = self.client.table("diet_plans").select("plan_id").eq("user_id", user_id).execute()
            remaining_plans = len(plans_response.data) if plans_response.data else 0
            
            # Check daily plans (through diet plans)
            daily_response = self.client.table("daily_plans").select("daily_plan_id, plan_id").execute()
            remaining_daily_plans = 0
            if daily_response.data:
                # Filter daily plans that belong to this user's diet plans
                user_plan_ids = [plan["plan_id"] for plan in plans_response.data] if plans_response.data else []
                remaining_daily_plans = len([dp for dp in daily_response.data if dp["plan_id"] in user_plan_ids])
            
            # Check meals (through daily plans)
            remaining_meals = 0
            remaining_food_items = 0
            
            if remaining_daily_plans > 0:
                for daily_plan in daily_response.data:
                    daily_plan_id = daily_plan["daily_plan_id"]
                    meals_response = self.client.table("meals").select("meal_id").eq("daily_plan_id", daily_plan_id).execute()
                    meals = meals_response.data if meals_response.data else []
                    remaining_meals += len(meals)
                    
                    for meal in meals:
                        meal_id = meal["meal_id"]
                        food_response = self.client.table("food_items").select("food_id").eq("meal_id", meal_id).execute()
                        food_items = food_response.data if food_response.data else []
                        remaining_food_items += len(food_items)
            
            is_cleared = remaining_plans == 0 and remaining_daily_plans == 0 and remaining_meals == 0 and remaining_food_items == 0
            
            logger.info(f"🔍 Data verification for user {user_id}:")
            logger.info(f"   - Remaining diet plans: {remaining_plans}")
            logger.info(f"   - Remaining daily plans: {remaining_daily_plans}")
            logger.info(f"   - Remaining meals: {remaining_meals}")
            logger.info(f"   - Remaining food items: {remaining_food_items}")
            logger.info(f"   - Data completely cleared: {is_cleared}")
            
            return {
                "success": True,
                "is_cleared": is_cleared,
                "remaining_plans": remaining_plans,
                "remaining_daily_plans": remaining_daily_plans,
                "remaining_meals": remaining_meals,
                "remaining_food_items": remaining_food_items,
                "message": f"Data verification complete. Cleared: {is_cleared}"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to verify data clearance: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def archive_user_diet_plans(self, user_id: str) -> Dict[str, Any]:
        """
        Archive all existing diet plans for a user by changing status to 'completed'
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            Archive result with count of archived plans
        """
        try:
            logger.info(f"📦 Archiving existing diet plans for user: {user_id}")
            
            # Update all diet plans to 'completed' status instead of deleting
            update_response = self.client.table("diet_plans").update({"status": "completed"}).eq("user_id", user_id).eq("status", "active").execute()
            
            if update_response.data:
                archived_count = len(update_response.data)
                logger.info(f"✅ Successfully archived {archived_count} diet plans for user: {user_id}")
                
                return {
                    "success": True,
                    "archived_count": archived_count,
                    "message": f"Successfully archived {archived_count} existing diet plans"
                }
            else:
                logger.info(f"✅ No active diet plans found to archive for user: {user_id}")
                return {
                    "success": True,
                    "archived_count": 0,
                    "message": "No active diet plans to archive"
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to archive user diet plans: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_diet_plan_count(self, user_id: str) -> Dict[str, Any]:
        """
        Get the count of existing diet plans for a user
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            Count of existing diet plans
        """
        try:
            plans_response = self.client.table("diet_plans").select("plan_id", count="exact").eq("user_id", user_id).execute()
            
            count = plans_response.count if hasattr(plans_response, 'count') else len(plans_response.data) if plans_response.data else 0
            
            return {
                "success": True,
                "count": count,
                "message": f"User has {count} existing diet plans"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get diet plan count: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def has_existing_diet_plans(self, user_id: str) -> Dict[str, Any]:
        """
        Check if a user has existing diet plans
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            Boolean indicating if user has existing plans
        """
        try:
            plans_response = self.client.table("diet_plans").select("plan_id").eq("user_id", user_id).limit(1).execute()
            
            has_plans = len(plans_response.data) > 0 if plans_response.data else False
            
            return {
                "success": True,
                "has_existing_plans": has_plans,
                "message": "Successfully checked for existing diet plans"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to check for existing diet plans: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_diet_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Delete a specific diet plan by ID
        
        Args:
            plan_id: Diet plan ID to delete
            
        Returns:
            Deletion result
        """
        try:
            logger.info(f"🗑️ Deleting diet plan: {plan_id}")
            
            # Delete the diet plan (cascade will handle daily_plans, meals, and food_items)
            delete_response = self.client.table("diet_plans").delete().eq("plan_id", plan_id).execute()
            
            if delete_response.data:
                logger.info(f"✅ Successfully deleted diet plan: {plan_id}")
                return {
                    "success": True,
                    "message": "Diet plan deleted successfully"
                }
            else:
                logger.warning(f"⚠️ No data returned when deleting diet plan: {plan_id}")
                return {
                    "success": False,
                    "error": "No data returned from deletion operation"
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to delete diet plan {plan_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_diet_plan_details(self, plan_id: str) -> Dict[str, Any]:
        """
        Get detailed diet plan with daily plans and meals
        
        Args:
            plan_id: Diet plan ID
            
        Returns:
            Complete diet plan details
        """
        try:
            # Get diet plan
            plan_response = self.client.table("diet_plans").select("*").eq("plan_id", plan_id).execute()
            
            if not plan_response.data:
                return {
                    "success": False,
                    "error": "Diet plan not found"
                }
            
            plan = plan_response.data[0]
            
            # Get daily plans
            daily_response = self.client.table("daily_plans").select("*").eq("plan_id", plan_id).order("date").execute()
            daily_plans = daily_response.data if daily_response.data else []
            
            # Get meals for each daily plan
            for daily_plan in daily_plans:
                meals_response = self.client.table("meals").select("*").eq("daily_plan_id", daily_plan["daily_plan_id"]).order("meal_time").execute()
                daily_plan["meals"] = meals_response.data if meals_response.data else []
                
                # Get food items for each meal
                for meal in daily_plan["meals"]:
                    food_response = self.client.table("food_items").select("*").eq("meal_id", meal["meal_id"]).execute()
                    meal["food_items"] = food_response.data if food_response.data else []
            
            return {
                "success": True,
                "plan": plan,
                "daily_plans": daily_plans
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get diet plan details: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def create_progress_tracking(self, user_id: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create progress tracking entry
        
        Args:
            user_id: User's unique identifier
            progress_data: Progress data including weight, energy, compliance, etc.
            
        Returns:
            Creation result with progress_id
        """
        try:
            # Add user_id to progress data
            progress_data["user_id"] = user_id
            
            # Insert progress tracking (use upsert to handle duplicates)
            progress_response = self.client.table("progress_tracking").upsert(progress_data).execute()
            
            if progress_response.data:
                progress_id = progress_response.data[0]["progress_id"]
                logger.info(f"✅ Progress tracking created successfully: {progress_id}")
                
                return {
                    "success": True,
                    "progress_id": progress_id,
                    "progress": progress_response.data[0],
                    "message": "Progress tracked successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create progress tracking"
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to create progress tracking: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def log_profile_access(self, user_id: str, access_type: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
        """
        Log profile access for audit trail
        
        Args:
            user_id: User's unique identifier
            access_type: Type of access (view, update, create, delete)
            ip_address: IP address of the request
            user_agent: User agent string
            
        Returns:
            Logging result
        """
        try:
            # Call the database function to log access
            log_data = {
                "p_profile_id": user_id,
                "p_access_type": access_type,
                "p_ip_address": ip_address,
                "p_user_agent": user_agent
            }
            
            # Execute the function
            result = self.client.rpc("log_profile_access", log_data).execute()
            
            logger.info(f"✅ Profile access logged: {user_id} - {access_type}")
            
            return {
                "success": True,
                "message": "Access logged successfully"
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to log profile access: {str(e)}")
            # Don't fail the main operation if logging fails
            return {
                "success": False,
                "error": str(e)
            }

    async def get_diet_plan_details(self, plan_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a diet plan including daily plans, meals, and food items
        
        Args:
            plan_id: Diet plan ID
            user_id: User ID for verification
            
        Returns:
            Detailed plan information
        """
        try:
            # First verify the plan belongs to the user
            plan_response = self.client.table("diet_plans").select("*").eq("plan_id", plan_id).eq("user_id", user_id).execute()
            
            if not plan_response.data:
                return {
                    "success": False,
                    "error": "Diet plan not found or access denied"
                }
            
            plan = plan_response.data[0]
            
            # Get daily plans for this diet plan
            daily_plans_response = self.client.table("daily_plans").select("*").eq("plan_id", plan_id).order("date").execute()
            daily_plans = daily_plans_response.data or []
            
            # For each daily plan, get meals
            for daily_plan in daily_plans:
                meals_response = self.client.table("meals").select("*").eq("daily_plan_id", daily_plan["daily_plan_id"]).order("meal_time").execute()
                daily_plan["meals"] = meals_response.data or []
                
                # For each meal, get food items
                for meal in daily_plan["meals"]:
                    food_items_response = self.client.table("food_items").select("*").eq("meal_id", meal["meal_id"]).execute()
                    meal["food_items"] = food_items_response.data or []
            
            # Get progress tracking for this plan
            progress_response = self.client.table("progress_tracking").select("*").eq("user_id", user_id).gte("date", plan["start_date"]).lte("date", plan["end_date"]).order("date").execute()
            progress_tracking = progress_response.data or []
            
            # Compile all the data
            plan_details = {
                **plan,
                "daily_plans": daily_plans,
                "progress_tracking": progress_tracking
            }
            
            logger.info(f"✅ Diet plan details retrieved successfully: {plan_id}")
            
            return {
                "success": True,
                "plan_details": plan_details
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get diet plan details: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }



# Global Supabase manager instance
supabase_manager = SupabaseManager()
