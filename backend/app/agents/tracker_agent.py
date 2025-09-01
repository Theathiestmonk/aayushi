"""
Tracker Agent - Monitors user progress and identifies shortcomings
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class TrackerAgent(BaseAgent):
    """
    Tracker Agent responsible for:
    - Tracking diet and workout progress
    - Identifying shortcomings and deviations
    - Providing progress affirmations
    - Coordinating with Recommender Agent
    - Managing progress metrics
    """
    
    def __init__(self):
        super().__init__("TrackerAgent")
        self.user_progress = {}  # user_id -> progress data
        self.progress_metrics = {}  # user_id -> metrics
        self.shortcomings = {}  # user_id -> identified shortcomings
        self.progress_thresholds = {
            "diet_completion": 0.8,  # 80% completion threshold
            "workout_completion": 0.7,  # 70% completion threshold
            "goal_progress": 0.6,  # 60% progress threshold
            "consistency": 0.75  # 75% consistency threshold
        }
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for tracking operations
        
        Args:
            state: Current workflow state containing tracking data and user updates
            
        Returns:
            Updated state with tracking results and identified shortcomings
        """
        try:
            await self.update_status("processing")
            
            # Extract tracking data from state
            tracking_data = state.get("tracking_data", {})
            user_data = state.get("user_data", {})
            user_id = user_data.get("user_id")
            
            if not user_id:
                raise ValueError("User ID is required for tracking processing")
            
            # Initialize MCP client if available
            if user_id:
                self.initialize_mcp_client(user_id)
            
            # Process tracking data from Follow-Up Agent
            if tracking_data:
                progress_result = await self._process_tracking_data(user_id, tracking_data)
                state["progress_analysis"] = progress_result
                
                # Check for shortcomings
                if progress_result.get("has_shortcomings"):
                    shortcomings = await self._identify_shortcomings(user_id, progress_result)
                    state["shortcomings"] = shortcomings
                    
                    # Prepare data for Recommender Agent
                    state["recommendation_data"] = {
                        "user_id": user_id,
                        "shortcomings": shortcomings,
                        "progress_context": progress_result,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                
                # Provide progress affirmation if appropriate
                if progress_result.get("overall_score", 0) >= 0.8:
                    affirmation = await self._generate_progress_affirmation(user_id, progress_result)
                    state["progress_affirmation"] = affirmation
            
            # Process user updates if available
            user_updates = state.get("user_updates", {})
            if user_updates:
                update_analysis = await self._analyze_user_updates(user_id, user_updates)
                state["update_analysis"] = update_analysis
                
                # Check for deviations from plans
                if update_analysis.get("has_deviations"):
                    deviations = await self._identify_deviations(user_id, update_analysis)
                    state["deviations"] = deviations
                    
                    # Add to recommendation data
                    if "recommendation_data" in state:
                        state["recommendation_data"]["deviations"] = deviations
                    else:
                        state["recommendation_data"] = {
                            "user_id": user_id,
                            "deviations": deviations,
                            "update_context": update_analysis,
                            "timestamp": datetime.utcnow().isoformat()
                        }
            
            # Update progress metrics
            await self._update_progress_metrics(user_id, state)
            
            # Generate tracking summary
            tracking_summary = await self._generate_tracking_summary(user_id)
            state["tracking_summary"] = tracking_summary
            
            await self.increment_success()
            return state
            
        except Exception as e:
            error_response = await self.handle_error(e, "Tracking processing")
            state["tracking_error"] = error_response
            return state
    
    async def _process_tracking_data(self, user_id: str, tracking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process tracking data from Follow-Up Agent"""
        try:
            # Extract plan information
            diet_plan = tracking_data.get("diet_plan", {})
            workout_plan = tracking_data.get("workout_plan", {})
            follow_up_context = tracking_data.get("follow_up_context", {})
            
            # Analyze diet plan adherence
            diet_analysis = await self._analyze_diet_progress(user_id, diet_plan)
            
            # Analyze workout plan adherence
            workout_analysis = await self._analyze_workout_progress(user_id, workout_plan)
            
            # Calculate overall progress score
            overall_score = self._calculate_overall_progress(diet_analysis, workout_analysis)
            
            # Determine if there are shortcomings
            has_shortcomings = (
                diet_analysis.get("completion_rate", 0) < self.progress_thresholds["diet_completion"] or
                workout_analysis.get("completion_rate", 0) < self.progress_thresholds["workout_completion"] or
                overall_score < self.progress_thresholds["goal_progress"]
            )
            
            progress_result = {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "diet_analysis": diet_analysis,
                "workout_analysis": workout_analysis,
                "overall_score": overall_score,
                "has_shortcomings": has_shortcomings,
                "follow_up_context": follow_up_context,
                "progress_trend": await self._calculate_progress_trend(user_id)
            }
            
            # Store progress data
            if user_id not in self.user_progress:
                self.user_progress[user_id] = []
            self.user_progress[user_id].append(progress_result)
            
            logger.info(f"Processed tracking data for user {user_id}, overall score: {overall_score:.2f}")
            return progress_result
            
        except Exception as e:
            logger.error(f"Failed to process tracking data for user {user_id}: {str(e)}")
            return {"has_shortcomings": False, "overall_score": 0}
    
    async def _analyze_diet_progress(self, user_id: str, diet_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze diet plan progress and adherence"""
        try:
            # This would typically analyze real tracking data
            # For now, simulate analysis based on plan complexity
            
            meals = diet_plan.get("meals", [])
            restrictions = diet_plan.get("dietary_restrictions", [])
            
            # Simulate completion rates
            total_meals = len(meals) * 7  # Weekly meal count
            completed_meals = int(total_meals * 0.75)  # 75% completion
            
            # Calculate adherence metrics
            completion_rate = completed_meals / total_meals if total_meals > 0 else 0
            restriction_adherence = 0.9 if restrictions else 1.0  # 90% adherence to restrictions
            
            # Use MCP tools for enhanced nutrition analysis if available
            nutrition_insights = {}
            if self.mcp_client:
                try:
                    # Get nutrition analysis
                    nutrition_data = await self.analyze_data("nutrition", user_id=user_id)
                    if nutrition_data.get("success"):
                        nutrition_insights = nutrition_data.get("result", {})
                except Exception as e:
                    logger.warning(f"Could not get nutrition insights: {str(e)}")
            
            return {
                "plan_id": diet_plan.get("plan_id"),
                "total_meals": total_meals,
                "completed_meals": completed_meals,
                "completion_rate": completion_rate,
                "restriction_adherence": restriction_adherence,
                "nutritional_goals_met": 0.8,  # 80% of nutritional goals met
                "nutrition_insights": nutrition_insights,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze diet progress for user {user_id}: {str(e)}")
            return {"completion_rate": 0, "restriction_adherence": 0}
    
    async def _analyze_workout_progress(self, user_id: str, workout_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze workout plan progress and adherence"""
        try:
            # This would typically analyze real tracking data
            # For now, simulate analysis based on plan complexity
            
            exercises = workout_plan.get("exercises", [])
            frequency = workout_plan.get("frequency", {})
            intensity = workout_plan.get("intensity", "moderate")
            
            # Simulate completion rates
            target_workouts = frequency.get("days_per_week", 3) * 4  # Monthly workout count
            completed_workouts = int(target_workouts * 0.65)  # 65% completion
            
            # Calculate adherence metrics
            completion_rate = completed_workouts / target_workouts if target_workouts > 0 else 0
            intensity_maintenance = 0.8 if intensity == "high" else 0.9  # Intensity adherence
            
            # Use MCP tools for enhanced workout analysis if available
            workout_insights = {}
            if self.mcp_client:
                try:
                    # Get workout analysis
                    workout_data = await self.analyze_data("workout", user_id=user_id)
                    if workout_data.get("success"):
                        workout_insights = workout_data.get("result", {})
                except Exception as e:
                    logger.warning(f"Could not get workout insights: {str(e)}")
            
            return {
                "plan_id": workout_plan.get("plan_id"),
                "target_workouts": target_workouts,
                "completed_workouts": completed_workouts,
                "completion_rate": completion_rate,
                "intensity_maintenance": intensity_maintenance,
                "recovery_adequacy": 0.75,  # 75% adequate recovery
                "workout_insights": workout_insights,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze workout progress for user {user_id}: {str(e)}")
            return {"completion_rate": 0, "intensity_maintenance": 0}
    
    async def _identify_shortcomings(self, user_id: str, progress_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific shortcomings based on progress analysis"""
        try:
            shortcomings = []
            
            diet_analysis = progress_result.get("diet_analysis", {})
            workout_analysis = progress_result.get("workout_analysis", {})
            
            # Check diet shortcomings
            if diet_analysis.get("completion_rate", 0) < self.progress_thresholds["diet_completion"]:
                shortcomings.append({
                    "category": "diet",
                    "type": "low_completion",
                    "severity": "medium",
                    "description": f"Diet plan completion rate is {diet_analysis.get('completion_rate', 0):.1%}, below the {self.progress_thresholds['diet_completion']:.1%} threshold",
                    "metric": "completion_rate",
                    "current_value": diet_analysis.get("completion_rate", 0),
                    "target_value": self.progress_thresholds["diet_completion"],
                    "recommendation": "Consider simplifying meal plans or adjusting portion sizes"
                })
            
            if diet_analysis.get("restriction_adherence", 0) < 0.9:
                shortcomings.append({
                    "category": "diet",
                    "type": "restriction_violation",
                    "severity": "high",
                    "description": "Dietary restrictions are not being followed consistently",
                    "metric": "restriction_adherence",
                    "current_value": diet_analysis.get("restriction_adherence", 0),
                    "target_value": 0.9,
                    "recommendation": "Review dietary restrictions and provide alternative food options"
                })
            
            # Check workout shortcomings
            if workout_analysis.get("completion_rate", 0) < self.progress_thresholds["workout_completion"]:
                shortcomings.append({
                    "category": "workout",
                    "type": "low_completion",
                    "severity": "medium",
                    "description": f"Workout plan completion rate is {workout_analysis.get('completion_rate', 0):.1%}, below the {self.progress_thresholds['workout_completion']:.1%} threshold",
                    "metric": "completion_rate",
                    "current_value": workout_analysis.get("completion_rate", 0),
                    "target_value": self.progress_thresholds["workout_completion"],
                    "recommendation": "Consider reducing workout frequency or duration"
                })
            
            if workout_analysis.get("recovery_adequacy", 0) < 0.7:
                shortcomings.append({
                    "category": "workout",
                    "type": "inadequate_recovery",
                    "severity": "medium",
                    "description": "Recovery time between workouts may be insufficient",
                    "metric": "recovery_adequacy",
                    "current_value": workout_analysis.get("recovery_adequacy", 0),
                    "target_value": 0.7,
                    "recommendation": "Increase rest days or reduce workout intensity"
                })
            
            # Store shortcomings
            if user_id not in self.shortcomings:
                self.shortcomings[user_id] = []
            self.shortcomings[user_id].extend(shortcomings)
            
            logger.info(f"Identified {len(shortcomings)} shortcomings for user {user_id}")
            return shortcomings
            
        except Exception as e:
            logger.error(f"Failed to identify shortcomings for user {user_id}: {str(e)}")
            return []
    
    async def _analyze_user_updates(self, user_id: str, user_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user-provided updates and identify patterns"""
        try:
            # This would typically analyze real user update data
            # For now, simulate analysis
            
            update_text = user_updates.get("text", "")
            update_photos = user_updates.get("photos", [])
            update_timestamp = user_updates.get("timestamp")
            
            # Analyze update sentiment and content
            sentiment_score = self._analyze_sentiment(update_text)
            content_analysis = self._analyze_content(update_text)
            
            # Check for deviations from plans
            has_deviations = self._check_for_deviations(content_analysis)
            
            return {
                "user_id": user_id,
                "timestamp": update_timestamp,
                "sentiment_score": sentiment_score,
                "content_analysis": content_analysis,
                "has_deviations": has_deviations,
                "photo_count": len(update_photos),
                "update_quality": "high" if len(update_text) > 50 else "medium"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze user updates for user {user_id}: {str(e)}")
            return {"has_deviations": False, "sentiment_score": 0}
    
    async def _identify_deviations(self, user_id: str, update_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify deviations from planned diet and workout routines"""
        try:
            deviations = []
            content_analysis = update_analysis.get("content_analysis", {})
            
            # Check for diet deviations
            if content_analysis.get("skipped_meals"):
                deviations.append({
                    "category": "diet",
                    "type": "meal_skipping",
                    "severity": "medium",
                    "description": "User reported skipping planned meals",
                    "context": content_analysis.get("skipped_meals_context", ""),
                    "recommendation": "Provide quick meal alternatives or adjust meal timing"
                })
            
            if content_analysis.get("unplanned_snacks"):
                deviations.append({
                    "category": "diet",
                    "type": "unplanned_consumption",
                    "severity": "low",
                    "description": "User consumed unplanned snacks or foods",
                    "context": content_analysis.get("snack_context", ""),
                    "recommendation": "Incorporate healthy snacks into meal plans"
                })
            
            # Check for workout deviations
            if content_analysis.get("missed_workouts"):
                deviations.append({
                    "category": "workout",
                    "type": "workout_missed",
                    "severity": "medium",
                    "description": "User missed planned workout sessions",
                    "context": content_analysis.get("missed_workout_context", ""),
                    "recommendation": "Provide alternative workout options or adjust schedule"
                })
            
            if content_analysis.get("modified_exercises"):
                deviations.append({
                    "category": "workout",
                    "type": "exercise_modification",
                    "severity": "low",
                    "description": "User modified planned exercises",
                    "context": content_analysis.get("modification_context", ""),
                    "recommendation": "Review exercise modifications and adjust plans if needed"
                })
            
            return deviations
            
        except Exception as e:
            logger.error(f"Failed to identify deviations for user {user_id}: {str(e)}")
            return []
    
    async def _generate_progress_affirmation(self, user_id: str, progress_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate positive affirmation for good progress"""
        try:
            overall_score = progress_result.get("overall_score", 0)
            
            if overall_score >= 0.9:
                message = "Excellent progress! You're exceeding your goals and maintaining great consistency."
                tone = "celebratory"
            elif overall_score >= 0.8:
                message = "Great job! You're consistently meeting your goals and showing strong commitment."
                tone = "encouraging"
            else:
                message = "Good progress! You're making steady improvements toward your goals."
                tone = "supportive"
            
            affirmation = {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": message,
                "tone": tone,
                "overall_score": overall_score,
                "highlighted_achievements": self._identify_achievements(progress_result),
                "motivation_tip": self._generate_motivation_tip(overall_score)
            }
            
            return affirmation
            
        except Exception as e:
            logger.error(f"Failed to generate progress affirmation for user {user_id}: {str(e)}")
            return {}
    
    def _calculate_overall_progress(self, diet_analysis: Dict, workout_analysis: Dict) -> float:
        """Calculate overall progress score from diet and workout analysis"""
        try:
            diet_score = diet_analysis.get("completion_rate", 0) * 0.6  # 60% weight
            workout_score = workout_analysis.get("completion_rate", 0) * 0.4  # 40% weight
            
            return diet_score + workout_score
            
        except Exception as e:
            logger.error(f"Error calculating overall progress: {str(e)}")
            return 0.0
    
    async def _calculate_progress_trend(self, user_id: str) -> str:
        """Calculate progress trend over time"""
        try:
            user_progress = self.user_progress.get(user_id, [])
            
            if len(user_progress) < 2:
                return "insufficient_data"
            
            # Get last 3 progress entries
            recent_progress = user_progress[-3:]
            scores = [entry.get("overall_score", 0) for entry in recent_progress]
            
            if len(scores) < 2:
                return "insufficient_data"
            
            # Calculate trend
            if scores[-1] > scores[0]:
                return "improving"
            elif scores[-1] < scores[0]:
                return "declining"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculating progress trend for user {user_id}: {str(e)}")
            return "unknown"
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of user update text (0.0 to 1.0)"""
        try:
            # Simple keyword-based sentiment analysis
            # In production, this would use NLP libraries or AI services
            
            positive_words = ["good", "great", "excellent", "feeling", "better", "improved", "happy", "satisfied"]
            negative_words = ["bad", "difficult", "hard", "struggling", "tired", "frustrated", "challenging"]
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count == 0 and negative_count == 0:
                return 0.5  # Neutral
            
            return positive_count / (positive_count + negative_count)
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return 0.5
    
    def _analyze_content(self, text: str) -> Dict[str, Any]:
        """Analyze content of user update text for patterns"""
        try:
            text_lower = text.lower()
            
            content_analysis = {
                "skipped_meals": any(word in text_lower for word in ["skip", "missed", "didn't eat", "forgot"]),
                "unplanned_snacks": any(word in text_lower for word in ["snack", "extra", "unplanned", "impulse"]),
                "missed_workouts": any(word in text_lower for word in ["missed", "skipped", "didn't work out", "too tired"]),
                "modified_exercises": any(word in text_lower for word in ["modified", "changed", "adjusted", "instead of"]),
                "energy_levels": any(word in text_lower for word in ["energy", "tired", "energized", "fatigue"]),
                "mood": any(word in text_lower for word in ["mood", "feeling", "happy", "frustrated", "motivated"])
            }
            
            # Add context for deviations
            if content_analysis["skipped_meals"]:
                content_analysis["skipped_meals_context"] = self._extract_context(text, ["skip", "missed", "didn't eat"])
            
            if content_analysis["unplanned_snacks"]:
                content_analysis["snack_context"] = self._extract_context(text, ["snack", "extra", "unplanned"])
            
            if content_analysis["missed_workouts"]:
                content_analysis["missed_workout_context"] = self._extract_context(text, ["missed", "skipped", "didn't work out"])
            
            if content_analysis["modified_exercises"]:
                content_analysis["modification_context"] = self._extract_context(text, ["modified", "changed", "adjusted"])
            
            return content_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            return {}
    
    def _extract_context(self, text: str, keywords: List[str]) -> str:
        """Extract context around keywords in text"""
        try:
            # Simple context extraction
            # In production, this would use more sophisticated NLP
            for keyword in keywords:
                if keyword in text.lower():
                    start = max(0, text.lower().find(keyword) - 20)
                    end = min(len(text), text.lower().find(keyword) + len(keyword) + 20)
                    return text[start:end].strip()
            return ""
        except Exception as e:
            logger.error(f"Error extracting context: {str(e)}")
            return ""
    
    def _check_for_deviations(self, content_analysis: Dict[str, Any]) -> bool:
        """Check if content analysis indicates deviations from plans"""
        return any([
            content_analysis.get("skipped_meals", False),
            content_analysis.get("unplanned_snacks", False),
            content_analysis.get("missed_workouts", False),
            content_analysis.get("modified_exercises", False)
        ])
    
    def _identify_achievements(self, progress_result: Dict[str, Any]) -> List[str]:
        """Identify specific achievements to highlight"""
        achievements = []
        
        diet_analysis = progress_result.get("diet_analysis", {})
        workout_analysis = progress_result.get("workout_analysis", {})
        
        if diet_analysis.get("completion_rate", 0) >= 0.9:
            achievements.append("Excellent diet plan adherence")
        
        if workout_analysis.get("completion_rate", 0) >= 0.8:
            achievements.append("Strong workout consistency")
        
        if diet_analysis.get("restriction_adherence", 0) >= 0.95:
            achievements.append("Perfect dietary restriction compliance")
        
        if workout_analysis.get("recovery_adequacy", 0) >= 0.8:
            achievements.append("Good recovery management")
        
        return achievements
    
    def _generate_motivation_tip(self, overall_score: float) -> str:
        """Generate motivational tip based on progress score"""
        if overall_score >= 0.9:
            return "Keep up the amazing work! You're setting a great example for consistency."
        elif overall_score >= 0.8:
            return "You're doing great! Small improvements each day lead to big results over time."
        elif overall_score >= 0.6:
            return "Good progress! Remember that consistency is more important than perfection."
        else:
            return "Every step forward counts! Focus on building sustainable habits."
    
    async def _update_progress_metrics(self, user_id: str, state: Dict[str, Any]):
        """Update progress metrics for the user"""
        try:
            if user_id not in self.progress_metrics:
                self.progress_metrics[user_id] = {
                    "created_at": datetime.utcnow(),
                    "total_tracking_sessions": 0,
                    "average_score": 0.0,
                    "best_score": 0.0,
                    "improvement_trend": "stable"
                }
            
            metrics = self.progress_metrics[user_id]
            metrics["total_tracking_sessions"] += 1
            
            # Update average score
            current_score = state.get("progress_analysis", {}).get("overall_score", 0)
            if current_score > 0:
                total_score = metrics["average_score"] * (metrics["total_tracking_sessions"] - 1) + current_score
                metrics["average_score"] = total_score / metrics["total_tracking_sessions"]
                
                if current_score > metrics["best_score"]:
                    metrics["best_score"] = current_score
            
            # Update improvement trend
            if metrics["total_tracking_sessions"] >= 3:
                metrics["improvement_trend"] = await self._calculate_progress_trend(user_id)
            
        except Exception as e:
            logger.error(f"Failed to update progress metrics for user {user_id}: {str(e)}")
    
    async def _generate_tracking_summary(self, user_id: str) -> Dict[str, Any]:
        """Generate comprehensive tracking summary for the user"""
        try:
            user_progress = self.user_progress.get(user_id, [])
            metrics = self.progress_metrics.get(user_id, {})
            user_shortcomings = self.shortcomings.get(user_id, [])
            
            # Calculate recent performance
            recent_progress = user_progress[-7:] if len(user_progress) >= 7 else user_progress
            recent_scores = [entry.get("overall_score", 0) for entry in recent_progress]
            recent_average = sum(recent_scores) / len(recent_scores) if recent_scores else 0
            
            summary = {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "overall_performance": {
                    "current_score": user_progress[-1].get("overall_score", 0) if user_progress else 0,
                    "recent_average": recent_average,
                    "best_score": metrics.get("best_score", 0),
                    "total_sessions": metrics.get("total_tracking_sessions", 0)
                },
                "progress_trend": metrics.get("improvement_trend", "unknown"),
                "shortcomings_count": len(user_shortcomings),
                "recent_shortcomings": user_shortcomings[-3:] if user_shortcomings else [],
                "recommendations": self._generate_tracking_recommendations(user_id, recent_average)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate tracking summary for user {user_id}: {str(e)}")
            return {}
    
    def _generate_tracking_recommendations(self, user_id: str, recent_average: float) -> List[str]:
        """Generate recommendations based on tracking performance"""
        recommendations = []
        
        if recent_average < 0.5:
            recommendations.append("Consider reducing plan complexity to improve adherence")
            recommendations.append("Schedule a consultation to review and adjust goals")
        elif recent_average < 0.7:
            recommendations.append("Focus on building consistent daily habits")
            recommendations.append("Identify and address specific barriers to adherence")
        elif recent_average < 0.85:
            recommendations.append("Great progress! Consider adding new challenges")
            recommendations.append("Review and optimize your current routine")
        else:
            recommendations.append("Excellent performance! Consider setting new goals")
            recommendations.append("Share your success strategies with others")
        
        return recommendations
    
    async def get_tracking_summary(self, user_id: str) -> Dict[str, Any]:
        """Get current tracking summary for a user"""
        try:
            return await self._generate_tracking_summary(user_id)
        except Exception as e:
            logger.error(f"Failed to get tracking summary for user {user_id}: {str(e)}")
            return {}
    
    async def get_shortcomings(self, user_id: str) -> List[Dict[str, Any]]:
        """Get identified shortcomings for a user"""
        try:
            return self.shortcomings.get(user_id, [])
        except Exception as e:
            logger.error(f"Failed to get shortcomings for user {user_id}: {str(e)}")
            return []




