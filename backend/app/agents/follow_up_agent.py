"""
Follow-Up Agent - Monitors diet and workout adherence and requests updates
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class FollowUpAgent(BaseAgent):
    """
    Follow-Up Agent responsible for:
    - Monitoring diet and workout adherence
    - Requesting updates from users
    - Coordinating with Tracker Agent
    - Managing follow-up schedules
    """
    
    def __init__(self):
        super().__init__("FollowUpAgent")
        self.follow_up_schedules = {}  # user_id -> schedule
        self.update_requests = {}      # user_id -> pending requests
        self.adherence_thresholds = {
            "diet": 0.8,  # 80% adherence threshold
            "workout": 0.7  # 70% adherence threshold
        }
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for follow-up operations
        
        Args:
            state: Current workflow state containing user data, plans, and tracking info
            
        Returns:
            Updated state with follow-up actions and recommendations
        """
        try:
            await self.update_status("processing")
            
            # Extract user data and plans
            user_data = state.get("user_data", {})
            user_id = user_data.get("user_id")
            diet_plan = state.get("diet_plan")
            workout_plan = state.get("workout_plan")
            
            if not user_id:
                raise ValueError("User ID is required for follow-up processing")
            
            # Initialize MCP client if available
            if user_id:
                self.initialize_mcp_client(user_id)
            
            # Initialize follow-up schedule for new users
            if user_id not in self.follow_up_schedules:
                await self._initialize_follow_up_schedule(user_id, diet_plan, workout_plan)
            
            # Check if it's time for follow-up
            if await self._should_request_update(user_id):
                # Request updates from user
                update_request = await self._request_user_update(user_id, diet_plan, workout_plan)
                state["follow_up_request"] = update_request
                
                # Share information with Tracker Agent
                tracking_data = await self._prepare_tracking_data(user_id, diet_plan, workout_plan)
                state["tracking_data"] = tracking_data
                
                # Update follow-up schedule
                await self._update_follow_up_schedule(user_id)
            
            # Check adherence and trigger interventions if needed
            adherence_status = await self._check_adherence(user_id, state)
            if adherence_status.get("needs_intervention"):
                intervention = await self._create_intervention(user_id, adherence_status)
                state["intervention"] = intervention
            
            # Update state with follow-up information
            state["follow_up_status"] = {
                "last_follow_up": self.follow_up_schedules.get(user_id, {}).get("last_follow_up"),
                "next_follow_up": self.follow_up_schedules.get(user_id, {}).get("next_follow_up"),
                "pending_requests": len(self.update_requests.get(user_id, [])),
                "adherence_score": adherence_status.get("overall_score", 0)
            }
            
            await self.increment_success()
            return state
            
        except Exception as e:
            error_response = await self.handle_error(e, "Follow-up processing")
            state["follow_up_error"] = error_response
            return state
    
    async def _initialize_follow_up_schedule(self, user_id: str, diet_plan: Dict, workout_plan: Dict):
        """Initialize follow-up schedule for a new user"""
        try:
            # Determine follow-up frequency based on plan complexity
            diet_complexity = self._assess_plan_complexity(diet_plan)
            workout_complexity = self._assess_plan_complexity(workout_plan)
            
            # Set initial follow-up schedule
            follow_up_frequency = self._calculate_follow_up_frequency(diet_complexity, workout_complexity)
            
            self.follow_up_schedules[user_id] = {
                "created_at": datetime.utcnow(),
                "last_follow_up": None,
                "next_follow_up": datetime.utcnow() + timedelta(hours=follow_up_frequency),
                "frequency_hours": follow_up_frequency,
                "diet_complexity": diet_complexity,
                "workout_complexity": workout_complexity,
                "total_follow_ups": 0
            }
            
            logger.info(f"Initialized follow-up schedule for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize follow-up schedule for user {user_id}: {str(e)}")
    
    async def _should_request_update(self, user_id: str) -> bool:
        """Check if it's time to request an update from the user"""
        try:
            schedule = self.follow_up_schedules.get(user_id)
            if not schedule:
                return False
            
            # Check if next follow-up time has passed
            if schedule["next_follow_up"] and datetime.utcnow() >= schedule["next_follow_up"]:
                return True
            
            # Check if there are pending urgent requests
            pending_requests = self.update_requests.get(user_id, [])
            urgent_requests = [req for req in pending_requests if req.get("priority") == "high"]
            
            return len(urgent_requests) > 0
            
        except Exception as e:
            logger.error(f"Error checking update requirement for user {user_id}: {str(e)}")
            return False
    
    async def _request_user_update(self, user_id: str, diet_plan: Dict, workout_plan: Dict) -> Dict[str, Any]:
        """Request updates from the user"""
        try:
            # Create update request
            update_request = {
                "request_id": f"update_{user_id}_{datetime.utcnow().timestamp()}",
                "timestamp": datetime.utcnow().isoformat(),
                "type": "follow_up",
                "priority": "medium",
                "diet_questions": self._generate_diet_questions(diet_plan),
                "workout_questions": self._generate_workout_questions(workout_plan),
                "status": "pending"
            }
            
            # Store the request
            if user_id not in self.update_requests:
                self.update_requests[user_id] = []
            self.update_requests[user_id].append(update_request)
            
            # Use MCP tools if available for enhanced follow-up
            if self.mcp_client:
                try:
                    # Get health insights for personalized questions
                    health_insights = await self.get_health_insights(user_data={"user_id": user_id})
                    if health_insights.get("success"):
                        update_request["health_context"] = health_insights.get("result", {})
                except Exception as e:
                    logger.warning(f"Could not get health insights for follow-up: {str(e)}")
            
            logger.info(f"Created update request for user {user_id}: {update_request['request_id']}")
            return update_request
            
        except Exception as e:
            logger.error(f"Failed to create update request for user {user_id}: {str(e)}")
            return {}
    
    async def _prepare_tracking_data(self, user_id: str, diet_plan: Dict, workout_plan: Dict) -> Dict[str, Any]:
        """Prepare data to share with Tracker Agent"""
        try:
            tracking_data = {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "diet_plan": {
                    "plan_id": diet_plan.get("plan_id"),
                    "meals": diet_plan.get("meals", []),
                    "nutritional_goals": diet_plan.get("nutritional_goals", {}),
                    "dietary_restrictions": diet_plan.get("dietary_restrictions", [])
                },
                "workout_plan": {
                    "plan_id": workout_plan.get("plan_id"),
                    "exercises": workout_plan.get("exercises", []),
                    "frequency": workout_plan.get("frequency", {}),
                    "intensity": workout_plan.get("intensity", "moderate")
                },
                "follow_up_context": {
                    "last_follow_up": self.follow_up_schedules.get(user_id, {}).get("last_follow_up"),
                    "total_follow_ups": self.follow_up_schedules.get(user_id, {}).get("total_follow_ups", 0)
                }
            }
            
            return tracking_data
            
        except Exception as e:
            logger.error(f"Failed to prepare tracking data for user {user_id}: {str(e)}")
            return {}
    
    async def _check_adherence(self, user_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Check user adherence to diet and workout plans"""
        try:
            # Get tracking data from state
            tracking_data = state.get("tracking_data", {})
            user_updates = state.get("user_updates", {})
            
            # Calculate adherence scores
            diet_adherence = self._calculate_diet_adherence(tracking_data, user_updates)
            workout_adherence = self._calculate_workout_adherence(tracking_data, user_updates)
            
            overall_score = (diet_adherence + workout_adherence) / 2
            
            adherence_status = {
                "diet_score": diet_adherence,
                "workout_score": workout_adherence,
                "overall_score": overall_score,
                "needs_intervention": overall_score < 0.6,  # Below 60%
                "diet_threshold_met": diet_adherence >= self.adherence_thresholds["diet"],
                "workout_threshold_met": workout_adherence >= self.adherence_thresholds["workout"]
            }
            
            return adherence_status
            
        except Exception as e:
            logger.error(f"Failed to check adherence for user {user_id}: {str(e)}")
            return {"overall_score": 0, "needs_intervention": False}
    
    async def _create_intervention(self, user_id: str, adherence_status: Dict[str, Any]) -> Dict[str, Any]:
        """Create intervention plan for users with low adherence"""
        try:
            intervention = {
                "intervention_id": f"intervention_{user_id}_{datetime.utcnow().timestamp()}",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "adherence_intervention",
                "priority": "high" if adherence_status["overall_score"] < 0.4 else "medium",
                "recommendations": []
            }
            
            # Generate specific recommendations based on adherence scores
            if adherence_status["diet_score"] < self.adherence_thresholds["diet"]:
                intervention["recommendations"].append({
                    "category": "diet",
                    "action": "schedule_diet_consultation",
                    "description": "Schedule a consultation to review and adjust diet plan",
                    "urgency": "medium"
                })
            
            if adherence_status["workout_score"] < self.adherence_thresholds["workout"]:
                intervention["recommendations"].append({
                    "category": "workout",
                    "action": "adjust_workout_intensity",
                    "description": "Consider reducing workout intensity or frequency",
                    "urgency": "medium"
                })
            
            # Use MCP tools for enhanced recommendations if available
            if self.mcp_client:
                try:
                    # Get wellness recommendations
                    wellness_recs = await self.get_health_insights(
                        user_data={"user_id": user_id},
                        context="adherence_intervention"
                    )
                    if wellness_recs.get("success"):
                        intervention["wellness_recommendations"] = wellness_recs.get("result", {})
                except Exception as e:
                    logger.warning(f"Could not get wellness recommendations: {str(e)}")
            
            return intervention
            
        except Exception as e:
            logger.error(f"Failed to create intervention for user {user_id}: {str(e)}")
            return {}
    
    async def _update_follow_up_schedule(self, user_id: str):
        """Update follow-up schedule after requesting updates"""
        try:
            if user_id in self.follow_up_schedules:
                schedule = self.follow_up_schedules[user_id]
                schedule["last_follow_up"] = datetime.utcnow()
                schedule["total_follow_ups"] += 1
                
                # Adjust frequency based on adherence and user response
                # More frequent follow-ups for users with low adherence
                adherence_score = getattr(self, '_last_adherence_score', 0.7)
                if adherence_score < 0.5:
                    schedule["frequency_hours"] = max(6, schedule["frequency_hours"] * 0.8)  # More frequent
                elif adherence_score > 0.8:
                    schedule["frequency_hours"] = min(72, schedule["frequency_hours"] * 1.2)  # Less frequent
                
                schedule["next_follow_up"] = datetime.utcnow() + timedelta(hours=schedule["frequency_hours"])
                
                logger.info(f"Updated follow-up schedule for user {user_id}")
                
        except Exception as e:
            logger.error(f"Failed to update follow-up schedule for user {user_id}: {str(e)}")
    
    def _assess_plan_complexity(self, plan: Dict) -> str:
        """Assess the complexity of a diet or workout plan"""
        if not plan:
            return "simple"
        
        # Diet plan complexity
        if "diet" in str(plan).lower():
            meals = plan.get("meals", [])
            restrictions = plan.get("dietary_restrictions", [])
            complexity_score = len(meals) + len(restrictions) * 2
            
            if complexity_score <= 3:
                return "simple"
            elif complexity_score <= 6:
                return "moderate"
            else:
                return "complex"
        
        # Workout plan complexity
        elif "workout" in str(plan).lower():
            exercises = plan.get("exercises", [])
            frequency = plan.get("frequency", {})
            complexity_score = len(exercises) + len(frequency) * 2
            
            if complexity_score <= 4:
                return "simple"
            elif complexity_score <= 8:
                return "moderate"
            else:
                return "complex"
        
        return "simple"
    
    def _calculate_follow_up_frequency(self, diet_complexity: str, workout_complexity: str) -> int:
        """Calculate follow-up frequency based on plan complexity"""
        complexity_scores = {"simple": 1, "moderate": 1.5, "complex": 2}
        
        diet_score = complexity_scores.get(diet_complexity, 1)
        workout_score = complexity_scores.get(workout_complexity, 1)
        
        # Base frequency: 24 hours
        base_frequency = 24
        
        # Adjust based on complexity
        adjusted_frequency = base_frequency * (diet_score + workout_score) / 2
        
        # Ensure reasonable bounds (6-72 hours)
        return max(6, min(72, int(adjusted_frequency)))
    
    def _generate_diet_questions(self, diet_plan: Dict) -> List[str]:
        """Generate personalized diet follow-up questions"""
        questions = [
            "How well are you following your meal schedule?",
            "Are you experiencing any cravings or hunger between meals?",
            "How do you feel after eating the recommended foods?"
        ]
        
        if diet_plan and diet_plan.get("dietary_restrictions"):
            questions.append("Are you finding it easy to avoid restricted foods?")
        
        if diet_plan and diet_plan.get("supplements"):
            questions.append("Are you taking your supplements as recommended?")
        
        return questions
    
    def _generate_workout_questions(self, workout_plan: Dict) -> List[str]:
        """Generate personalized workout follow-up questions"""
        questions = [
            "How are you feeling during your workouts?",
            "Are you able to complete all planned exercises?",
            "How is your energy level after workouts?"
        ]
        
        if workout_plan and workout_plan.get("intensity") == "high":
            questions.append("Are you experiencing any muscle soreness or fatigue?")
        
        if workout_plan and workout_plan.get("frequency", {}).get("days_per_week", 0) > 4:
            questions.append("Are you getting enough rest between workout days?")
        
        return questions
    
    def _calculate_diet_adherence(self, tracking_data: Dict, user_updates: Dict) -> float:
        """Calculate diet adherence score (0.0 to 1.0)"""
        try:
            # This would typically use real tracking data
            # For now, return a mock score
            return 0.75  # 75% adherence
        except Exception as e:
            logger.error(f"Error calculating diet adherence: {str(e)}")
            return 0.5
    
    def _calculate_workout_adherence(self, tracking_data: Dict, user_updates: Dict) -> float:
        """Calculate workout adherence score (0.0 to 1.0)"""
        try:
            # This would typically use real tracking data
            # For now, return a mock score
            return 0.65  # 65% adherence
        except Exception as e:
            logger.error(f"Error calculating workout adherence: {str(e)}")
            return 0.5
    
    async def get_follow_up_status(self, user_id: str) -> Dict[str, Any]:
        """Get current follow-up status for a user"""
        try:
            schedule = self.follow_up_schedules.get(user_id, {})
            requests = self.update_requests.get(user_id, [])
            
            return {
                "user_id": user_id,
                "schedule": schedule,
                "pending_requests": len(requests),
                "last_update": schedule.get("last_follow_up"),
                "next_update": schedule.get("next_follow_up")
            }
        except Exception as e:
            logger.error(f"Failed to get follow-up status for user {user_id}: {str(e)}")
            return {}
    
    async def mark_update_completed(self, user_id: str, request_id: str):
        """Mark an update request as completed"""
        try:
            if user_id in self.update_requests:
                for request in self.update_requests[user_id]:
                    if request.get("request_id") == request_id:
                        request["status"] = "completed"
                        request["completed_at"] = datetime.utcnow().isoformat()
                        break
                
                logger.info(f"Marked update request {request_id} as completed for user {user_id}")
                
        except Exception as e:
            logger.error(f"Failed to mark update completed for user {user_id}: {str(e)}")

