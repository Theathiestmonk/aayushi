"""
Recommender Agent - Provides personalized recommendations based on tracking data and deviations
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class RecommenderAgent(BaseAgent):
    """
    Recommender Agent responsible for:
    - Analyzing shortcomings and deviations
    - Generating personalized recommendations
    - Coordinating with Follow-Up Agent
    - Providing actionable improvement strategies
    - Managing recommendation history
    """
    
    def __init__(self):
        super().__init__("RecommenderAgent")
        self.recommendation_history = {}  # user_id -> recommendation history
        self.recommendation_templates = {}  # category -> templates
        self.improvement_strategies = {}  # user_id -> strategies
        self.recommendation_weights = {
            "shortcomings": 0.4,
            "deviations": 0.3,
            "progress_trend": 0.2,
            "user_preferences": 0.1
        }
        
        # Initialize recommendation templates
        self._initialize_recommendation_templates()
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for recommendation generation
        
        Args:
            state: Current workflow state containing recommendation data and context
            
        Returns:
            Updated state with personalized recommendations and strategies
        """
        try:
            await self.update_status("processing")
            
            # Extract recommendation data from state
            recommendation_data = state.get("recommendation_data", {})
            user_data = state.get("user_data", {})
            user_id = user_data.get("user_id")
            
            if not user_id:
                raise ValueError("User ID is required for recommendation processing")
            
            # Initialize MCP client if available
            if user_id:
                self.initialize_mcp_client(user_id)
            
            # Generate recommendations if data is available
            if recommendation_data:
                recommendations = await self._generate_recommendations(user_id, recommendation_data)
                state["recommendations"] = recommendations
                
                # Generate improvement strategies
                strategies = await self._generate_improvement_strategies(user_id, recommendations)
                state["improvement_strategies"] = strategies
                
                # Update Follow-Up Agent with recommendations
                follow_up_update = await self._prepare_follow_up_update(user_id, recommendations)
                state["follow_up_update"] = follow_up_update
                
                # Generate user communication
                user_communication = await self._generate_user_communication(user_id, recommendations)
                state["user_communication"] = user_communication
            
            # Update recommendation history
            await self._update_recommendation_history(user_id, state)
            
            # Generate recommendation summary
            recommendation_summary = await self._generate_recommendation_summary(user_id)
            state["recommendation_summary"] = recommendation_summary
            
            await self.increment_success()
            return state
            
        except Exception as e:
            error_response = await self.handle_error(e, "Recommendation processing")
            state["recommendation_error"] = error_response
            return state
    
    def _initialize_recommendation_templates(self):
        """Initialize recommendation templates for different categories"""
        try:
            self.recommendation_templates = {
                "diet": {
                    "low_completion": {
                        "title": "Improve Diet Plan Adherence",
                        "description": "Your diet plan completion rate is below target. Here are strategies to improve:",
                        "strategies": [
                            "Simplify meal preparation with batch cooking",
                            "Set meal reminders and alarms",
                            "Prepare healthy snacks in advance",
                            "Adjust portion sizes to match your appetite"
                        ]
                    },
                    "restriction_violation": {
                        "title": "Better Dietary Restriction Management",
                        "description": "You're having difficulty following dietary restrictions. Consider these approaches:",
                        "strategies": [
                            "Find alternative ingredients for restricted foods",
                            "Plan meals that naturally avoid restrictions",
                            "Use food substitution guides",
                            "Consult with a nutritionist for alternatives"
                        ]
                    },
                    "meal_skipping": {
                        "title": "Address Meal Skipping",
                        "description": "Skipping meals can affect your energy and metabolism. Try these solutions:",
                        "strategies": [
                            "Prepare quick meal options for busy days",
                            "Set consistent meal times",
                            "Keep healthy snacks readily available",
                            "Consider meal timing adjustments"
                        ]
                    }
                },
                "workout": {
                    "low_completion": {
                        "title": "Enhance Workout Consistency",
                        "description": "Your workout completion rate needs improvement. Here are effective strategies:",
                        "strategies": [
                            "Start with shorter, more manageable sessions",
                            "Schedule workouts at your most energetic times",
                            "Find workout buddies for accountability",
                            "Mix different types of exercises to stay engaged"
                        ]
                    },
                    "inadequate_recovery": {
                        "title": "Optimize Recovery Between Workouts",
                        "description": "Proper recovery is essential for progress. Improve with these strategies:",
                        "strategies": [
                            "Increase rest days between intense sessions",
                            "Incorporate active recovery activities",
                            "Focus on sleep quality and duration",
                            "Consider reducing workout intensity"
                        ]
                    },
                    "workout_missed": {
                        "title": "Handle Missed Workouts",
                        "description": "Missing workouts occasionally is normal. Here's how to stay on track:",
                        "strategies": [
                            "Have backup workout plans for busy days",
                            "Make up missed sessions when possible",
                            "Focus on consistency over perfection",
                            "Adjust your weekly workout schedule"
                        ]
                    }
                },
                "general": {
                    "motivation": {
                        "title": "Boost Your Motivation",
                        "description": "Maintaining motivation is key to long-term success. Try these approaches:",
                        "strategies": [
                            "Set smaller, achievable short-term goals",
                            "Track your progress visually",
                            "Reward yourself for milestones",
                            "Connect with others on similar journeys"
                        ]
                    },
                    "consistency": {
                        "title": "Build Consistent Habits",
                        "description": "Consistency is more important than perfection. Develop these habits:",
                        "strategies": [
                            "Start with one habit at a time",
                            "Use habit stacking techniques",
                            "Create visual reminders",
                            "Build routines around existing habits"
                        ]
                    }
                }
            }
            
            logger.info("Recommendation templates initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize recommendation templates: {str(e)}")
    
    async def _generate_recommendations(self, user_id: str, recommendation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations based on data analysis"""
        try:
            recommendations = []
            
            # Process shortcomings
            shortcomings = recommendation_data.get("shortcomings", [])
            for shortcoming in shortcomings:
                recommendation = await self._create_shortcoming_recommendation(user_id, shortcoming)
                if recommendation:
                    recommendations.append(recommendation)
            
            # Process deviations
            deviations = recommendation_data.get("deviations", [])
            for deviation in deviations:
                recommendation = await self._create_deviation_recommendation(user_id, deviation)
                if recommendation:
                    recommendations.append(recommendation)
            
            # Generate general improvement recommendations
            general_recommendations = await self._generate_general_recommendations(user_id, recommendation_data)
            recommendations.extend(general_recommendations)
            
            # Prioritize recommendations
            prioritized_recommendations = self._prioritize_recommendations(recommendations)
            
            # Use MCP tools for enhanced recommendations if available
            if self.mcp_client:
                enhanced_recommendations = await self._enhance_recommendations_with_mcp(user_id, prioritized_recommendations)
                return enhanced_recommendations
            
            return prioritized_recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations for user {user_id}: {str(e)}")
            return []
    
    async def _create_shortcoming_recommendation(self, user_id: str, shortcoming: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create recommendation for a specific shortcoming"""
        try:
            category = shortcoming.get("category")
            shortcoming_type = shortcoming.get("type")
            
            # Get template for this shortcoming
            template = self.recommendation_templates.get(category, {}).get(shortcoming_type)
            if not template:
                # Use general template if specific one not found
                template = self.recommendation_templates.get("general", {}).get("consistency", {})
            
            recommendation = {
                "recommendation_id": f"rec_{user_id}_{datetime.utcnow().timestamp()}",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "category": category,
                "type": "shortcoming_based",
                "priority": shortcoming.get("severity", "medium"),
                "title": template.get("title", "Improvement Recommendation"),
                "description": template.get("description", "Here are strategies to improve your progress:"),
                "strategies": template.get("strategies", []),
                "context": {
                    "shortcoming_id": shortcoming.get("shortcoming_id", ""),
                    "metric": shortcoming.get("metric", ""),
                    "current_value": shortcoming.get("current_value", 0),
                    "target_value": shortcoming.get("target_value", 0)
                },
                "estimated_impact": self._estimate_recommendation_impact(shortcoming),
                "implementation_difficulty": self._assess_implementation_difficulty(shortcoming),
                "time_to_see_results": self._estimate_time_to_results(shortcoming)
            }
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Failed to create shortcoming recommendation: {str(e)}")
            return None
    
    async def _create_deviation_recommendation(self, user_id: str, deviation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create recommendation for a specific deviation"""
        try:
            category = deviation.get("category")
            deviation_type = deviation.get("type")
            
            # Get template for this deviation
            template = self.recommendation_templates.get(category, {}).get(deviation_type)
            if not template:
                # Use general template if specific one not found
                template = self.recommendation_templates.get("general", {}).get("consistency", {})
            
            recommendation = {
                "recommendation_id": f"rec_{user_id}_{datetime.utcnow().timestamp()}",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "category": category,
                "type": "deviation_based",
                "priority": deviation.get("severity", "medium"),
                "title": template.get("title", "Deviation Management"),
                "description": template.get("description", "Here are strategies to handle this deviation:"),
                "strategies": template.get("strategies", []),
                "context": {
                    "deviation_type": deviation_type,
                    "description": deviation.get("description", ""),
                    "context": deviation.get("context", "")
                },
                "estimated_impact": "medium",
                "implementation_difficulty": "low",
                "time_to_see_results": "immediate"
            }
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Failed to create deviation recommendation: {str(e)}")
            return None
    
    async def _generate_general_recommendations(self, user_id: str, recommendation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate general improvement recommendations"""
        try:
            general_recommendations = []
            
            # Get progress context
            progress_context = recommendation_data.get("progress_context", {})
            overall_score = progress_context.get("overall_score", 0)
            
            # Generate motivation recommendations for low scores
            if overall_score < 0.6:
                motivation_rec = {
                    "recommendation_id": f"rec_{user_id}_{datetime.utcnow().timestamp()}",
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "category": "general",
                    "type": "motivation",
                    "priority": "high",
                    "title": "Boost Your Motivation",
                    "description": "Your progress score indicates you might need motivation. Here are strategies to stay motivated:",
                    "strategies": self.recommendation_templates.get("general", {}).get("motivation", {}).get("strategies", []),
                    "context": {"overall_score": overall_score},
                    "estimated_impact": "high",
                    "implementation_difficulty": "low",
                    "time_to_see_results": "1-2 weeks"
                }
                general_recommendations.append(motivation_rec)
            
            # Generate consistency recommendations
            consistency_rec = {
                "recommendation_id": f"rec_{user_id}_{datetime.utcnow().timestamp()}",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "category": "general",
                "type": "consistency",
                "priority": "medium",
                "title": "Build Consistent Habits",
                "description": "Consistency is key to long-term success. Here are strategies to build lasting habits:",
                "strategies": self.recommendation_templates.get("general", {}).get("consistency", {}).get("strategies", []),
                "context": {"overall_score": overall_score},
                "estimated_impact": "high",
                "implementation_difficulty": "medium",
                "time_to_see_results": "2-4 weeks"
            }
            general_recommendations.append(consistency_rec)
            
            return general_recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate general recommendations: {str(e)}")
            return []
    
    def _prioritize_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize recommendations based on impact and difficulty"""
        try:
            # Calculate priority score for each recommendation
            for rec in recommendations:
                priority_score = 0
                
                # Impact score (high=3, medium=2, low=1)
                impact_scores = {"high": 3, "medium": 2, "low": 1}
                priority_score += impact_scores.get(rec.get("estimated_impact", "medium"), 2)
                
                # Difficulty score (low=3, medium=2, high=1) - easier is better
                difficulty_scores = {"low": 3, "medium": 2, "high": 1}
                priority_score += difficulty_scores.get(rec.get("implementation_difficulty", "medium"), 2)
                
                # Priority from original data
                priority_scores = {"high": 3, "medium": 2, "low": 1}
                priority_score += priority_scores.get(rec.get("priority", "medium"), 2)
                
                rec["priority_score"] = priority_score
            
            # Sort by priority score (descending)
            sorted_recommendations = sorted(recommendations, key=lambda x: x.get("priority_score", 0), reverse=True)
            
            # Add rank
            for i, rec in enumerate(sorted_recommendations):
                rec["rank"] = i + 1
            
            return sorted_recommendations
            
        except Exception as e:
            logger.error(f"Failed to prioritize recommendations: {str(e)}")
            return recommendations
    
    async def _enhance_recommendations_with_mcp(self, user_id: str, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance recommendations using MCP tools"""
        try:
            enhanced_recommendations = []
            
            for rec in recommendations:
                enhanced_rec = rec.copy()
                
                # Use MCP tools to enhance specific recommendation types
                if rec.get("category") == "diet":
                    try:
                        # Get nutrition insights
                        nutrition_data = await self.get_health_insights(
                            user_data={"user_id": user_id},
                            context="diet_recommendation"
                        )
                        if nutrition_data.get("success"):
                            enhanced_rec["nutrition_insights"] = nutrition_data.get("result", {})
                    except Exception as e:
                        logger.warning(f"Could not get nutrition insights: {str(e)}")
                
                elif rec.get("category") == "workout":
                    try:
                        # Get workout insights
                        workout_data = await self.analyze_data("workout", user_id=user_id)
                        if workout_data.get("success"):
                            enhanced_rec["workout_insights"] = workout_data.get("result", {})
                    except Exception as e:
                        logger.warning(f"Could not get workout insights: {str(e)}")
                
                enhanced_recommendations.append(enhanced_rec)
            
            return enhanced_recommendations
            
        except Exception as e:
            logger.error(f"Failed to enhance recommendations with MCP: {str(e)}")
            return recommendations
    
    async def _generate_improvement_strategies(self, user_id: str, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive improvement strategies"""
        try:
            strategies = {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "overview": "Comprehensive improvement plan based on your current progress",
                "strategies": [],
                "timeline": "4-8 weeks",
                "expected_outcomes": []
            }
            
            # Group strategies by category
            diet_strategies = [rec for rec in recommendations if rec.get("category") == "diet"]
            workout_strategies = [rec for rec in recommendations if rec.get("category") == "workout"]
            general_strategies = [rec for rec in recommendations if rec.get("category") == "general"]
            
            # Create category-specific strategy plans
            if diet_strategies:
                diet_plan = {
                    "category": "diet",
                    "focus_areas": [rec.get("title") for rec in diet_strategies[:3]],
                    "key_strategies": diet_strategies[0].get("strategies", [])[:3],
                    "timeline": "2-4 weeks",
                    "success_metrics": ["meal completion rate", "restriction adherence", "energy levels"]
                }
                strategies["strategies"].append(diet_plan)
            
            if workout_strategies:
                workout_plan = {
                    "category": "workout",
                    "focus_areas": [rec.get("title") for rec in workout_strategies[:3]],
                    "key_strategies": workout_strategies[0].get("strategies", [])[:3],
                    "timeline": "3-6 weeks",
                    "success_metrics": ["workout completion rate", "recovery quality", "strength gains"]
                }
                strategies["strategies"].append(workout_plan)
            
            if general_strategies:
                general_plan = {
                    "category": "general",
                    "focus_areas": [rec.get("title") for rec in general_strategies[:2]],
                    "key_strategies": general_strategies[0].get("strategies", [])[:3],
                    "timeline": "4-8 weeks",
                    "success_metrics": ["overall consistency", "motivation levels", "habit formation"]
                }
                strategies["strategies"].append(general_plan)
            
            # Generate expected outcomes
            strategies["expected_outcomes"] = [
                "Improved adherence to diet and workout plans",
                "Better consistency in daily routines",
                "Enhanced motivation and engagement",
                "Measurable progress toward goals"
            ]
            
            # Store strategies
            self.improvement_strategies[user_id] = strategies
            
            return strategies
            
        except Exception as e:
            logger.error(f"Failed to generate improvement strategies: {str(e)}")
            return {}
    
    async def _prepare_follow_up_update(self, user_id: str, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare update for Follow-Up Agent with new recommendations"""
        try:
            follow_up_update = {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "recommendations_update",
                "recommendations_count": len(recommendations),
                "priority_recommendations": [rec for rec in recommendations if rec.get("rank", 0) <= 3],
                "next_follow_up_adjustment": self._calculate_follow_up_adjustment(recommendations),
                "intervention_needed": any(rec.get("priority") == "high" for rec in recommendations)
            }
            
            return follow_up_update
            
        except Exception as e:
            logger.error(f"Failed to prepare follow-up update: {str(e)}")
            return {}
    
    async def _generate_user_communication(self, user_id: str, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate user communication with recommendations"""
        try:
            # Get top 3 recommendations
            top_recommendations = [rec for rec in recommendations if rec.get("rank", 0) <= 3]
            
            # Generate personalized message
            message = self._generate_personalized_message(user_id, top_recommendations)
            
            # Create action items
            action_items = []
            for rec in top_recommendations:
                action_items.append({
                    "title": rec.get("title", ""),
                    "description": rec.get("description", ""),
                    "priority": rec.get("priority", "medium"),
                    "strategies": rec.get("strategies", [])[:2]  # Top 2 strategies
                })
            
            communication = {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "recommendations_update",
                "message": message,
                "action_items": action_items,
                "total_recommendations": len(recommendations),
                "next_review_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
            
            return communication
            
        except Exception as e:
            logger.error(f"Failed to generate user communication: {str(e)}")
            return {}
    
    def _generate_personalized_message(self, user_id: str, top_recommendations: List[Dict[str, Any]]) -> str:
        """Generate personalized message for user"""
        try:
            if not top_recommendations:
                return "Great job on your progress! Keep up the excellent work."
            
            # Count recommendations by category
            diet_count = len([rec for rec in top_recommendations if rec.get("category") == "diet"])
            workout_count = len([rec for rec in top_recommendations if rec.get("category") == "workout"])
            general_count = len([rec for rec in top_recommendations if rec.get("category") == "general"])
            
            message_parts = []
            
            if diet_count > 0:
                message_parts.append(f"Based on your progress, I have {diet_count} diet-related recommendations")
            
            if workout_count > 0:
                message_parts.append(f"{workout_count} workout improvement suggestions")
            
            if general_count > 0:
                message_parts.append(f"{general_count} general wellness tips")
            
            message = f"I've analyzed your progress and created personalized recommendations for you. {', '.join(message_parts)}. "
            message += "These are designed to help you overcome current challenges and continue making progress toward your goals."
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to generate personalized message: {str(e)}")
            return "I have some personalized recommendations to help you continue making progress."
    
    def _calculate_follow_up_adjustment(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate adjustments needed for follow-up schedule"""
        try:
            high_priority_count = len([rec for rec in recommendations if rec.get("priority") == "high"])
            
            if high_priority_count >= 2:
                return {
                    "frequency_increase": True,
                    "reason": "Multiple high-priority recommendations require closer monitoring",
                    "suggested_interval": "12-24 hours"
                }
            elif high_priority_count == 1:
                return {
                    "frequency_increase": True,
                    "reason": "High-priority recommendation requires closer monitoring",
                    "suggested_interval": "24-48 hours"
                }
            else:
                return {
                    "frequency_increase": False,
                    "reason": "Standard follow-up schedule is appropriate",
                    "suggested_interval": "48-72 hours"
                }
                
        except Exception as e:
            logger.error(f"Failed to calculate follow-up adjustment: {str(e)}")
            return {"frequency_increase": False, "reason": "Unable to determine", "suggested_interval": "48-72 hours"}
    
    def _estimate_recommendation_impact(self, shortcoming: Dict[str, Any]) -> str:
        """Estimate the impact of implementing a recommendation"""
        try:
            severity = shortcoming.get("severity", "medium")
            metric = shortcoming.get("metric", "")
            
            if severity == "high":
                return "high"
            elif severity == "medium":
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            logger.error(f"Failed to estimate recommendation impact: {str(e)}")
            return "medium"
    
    def _assess_implementation_difficulty(self, shortcoming: Dict[str, Any]) -> str:
        """Assess the difficulty of implementing a recommendation"""
        try:
            category = shortcoming.get("category", "")
            shortcoming_type = shortcoming.get("type", "")
            
            # Diet-related recommendations are generally easier to implement
            if category == "diet":
                if "restriction" in shortcoming_type:
                    return "medium"  # Changing eating habits can be challenging
                else:
                    return "low"  # Meal planning and preparation are manageable
            
            # Workout-related recommendations vary in difficulty
            elif category == "workout":
                if "recovery" in shortcoming_type:
                    return "low"  # Rest and recovery are easy to implement
                elif "completion" in shortcoming_type:
                    return "medium"  # Changing workout habits requires effort
                else:
                    return "medium"
            
            else:
                return "medium"
                
        except Exception as e:
            logger.error(f"Failed to assess implementation difficulty: {str(e)}")
            return "medium"
    
    def _estimate_time_to_results(self, shortcoming: Dict[str, Any]) -> str:
        """Estimate time to see results from implementing a recommendation"""
        try:
            category = shortcoming.get("category", "")
            shortcoming_type = shortcoming.get("type", "")
            
            if category == "diet":
                if "restriction" in shortcoming_type:
                    return "1-2 weeks"  # Dietary changes show results quickly
                else:
                    return "2-4 weeks"  # Meal planning habits take time to develop
            
            elif category == "workout":
                if "recovery" in shortcoming_type:
                    return "1-2 weeks"  # Recovery improvements are noticeable quickly
                elif "completion" in shortcoming_type:
                    return "3-6 weeks"  # Building workout consistency takes time
                else:
                    return "2-4 weeks"
            
            else:
                return "2-4 weeks"
                
        except Exception as e:
            logger.error(f"Failed to estimate time to results: {str(e)}")
            return "2-4 weeks"
    
    async def _update_recommendation_history(self, user_id: str, state: Dict[str, Any]):
        """Update recommendation history for the user"""
        try:
            if user_id not in self.recommendation_history:
                self.recommendation_history[user_id] = []
            
            # Add current recommendations to history
            recommendations = state.get("recommendations", [])
            if recommendations:
                history_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "recommendations_count": len(recommendations),
                    "top_recommendations": [rec.get("title") for rec in recommendations[:3]],
                    "overall_priority": "high" if any(rec.get("priority") == "high" for rec in recommendations) else "medium"
                }
                
                self.recommendation_history[user_id].append(history_entry)
                
                # Keep only last 10 entries
                if len(self.recommendation_history[user_id]) > 10:
                    self.recommendation_history[user_id] = self.recommendation_history[user_id][-10:]
            
        except Exception as e:
            logger.error(f"Failed to update recommendation history for user {user_id}: {str(e)}")
    
    async def _generate_recommendation_summary(self, user_id: str) -> Dict[str, Any]:
        """Generate summary of recommendation activity"""
        try:
            history = self.recommendation_history.get(user_id, [])
            current_strategies = self.improvement_strategies.get(user_id, {})
            
            summary = {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "total_recommendations_generated": len(history),
                "current_active_strategies": len(current_strategies.get("strategies", [])),
                "recommendation_trend": self._calculate_recommendation_trend(history),
                "most_common_categories": self._identify_common_categories(history),
                "last_recommendations": history[-3:] if history else []
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate recommendation summary for user {user_id}: {str(e)}")
            return {}
    
    def _calculate_recommendation_trend(self, history: List[Dict[str, Any]]) -> str:
        """Calculate trend in recommendation generation"""
        try:
            if len(history) < 2:
                return "insufficient_data"
            
            # Analyze recent vs. older recommendations
            recent = history[-3:] if len(history) >= 3 else history
            older = history[:-3] if len(history) >= 3 else []
            
            if not older:
                return "insufficient_data"
            
            recent_avg = sum(entry.get("recommendations_count", 0) for entry in recent) / len(recent)
            older_avg = sum(entry.get("recommendations_count", 0) for entry in older) / len(older)
            
            if recent_avg > older_avg * 1.2:
                return "increasing"
            elif recent_avg < older_avg * 0.8:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Failed to calculate recommendation trend: {str(e)}")
            return "unknown"
    
    def _identify_common_categories(self, history: List[Dict[str, Any]]) -> List[str]:
        """Identify most common recommendation categories"""
        try:
            category_counts = {}
            
            for entry in history:
                for rec_title in entry.get("top_recommendations", []):
                    if "diet" in rec_title.lower():
                        category_counts["diet"] = category_counts.get("diet", 0) + 1
                    elif "workout" in rec_title.lower():
                        category_counts["workout"] = category_counts.get("workout", 0) + 1
                    elif "motivation" in rec_title.lower() or "consistency" in rec_title.lower():
                        category_counts["general"] = category_counts.get("general", 0) + 1
            
            # Sort by count and return top 3
            sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
            return [cat for cat, count in sorted_categories[:3]]
            
        except Exception as e:
            logger.error(f"Failed to identify common categories: {str(e)}")
            return []
    
    async def get_recommendation_summary(self, user_id: str) -> Dict[str, Any]:
        """Get current recommendation summary for a user"""
        try:
            return await self._generate_recommendation_summary(user_id)
        except Exception as e:
            logger.error(f"Failed to get recommendation summary for user {user_id}: {str(e)}")
            return {}
    
    async def get_improvement_strategies(self, user_id: str) -> Dict[str, Any]:
        """Get improvement strategies for a user"""
        try:
            return self.improvement_strategies.get(user_id, {})
        except Exception as e:
            logger.error(f"Failed to get improvement strategies for user {user_id}: {str(e)}")
            return {}




