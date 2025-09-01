"""
Data Analyzer Agent - Processes user updates and generates insights
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class DataAnalyzerAgent(BaseAgent):
    """
    Data Analyzer Agent responsible for:
    - Processing user updates (text and photos)
    - Generating insights and patterns
    - Providing data-driven recommendations
    - Coordinating with other agents
    """
    
    def __init__(self):
        super().__init__("DataAnalyzerAgent")
        self.analysis_types = ["nutrition", "progress", "behavior", "trends", "correlations"]
        self.insight_categories = ["diet", "workout", "lifestyle", "goals", "challenges"]
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for data analysis
        
        Args:
            state: Current workflow state containing user updates and data
            
        Returns:
            Updated state with analysis results and insights
        """
        try:
            await self.update_status("processing")
            
            # Extract user updates and data
            user_updates = state.get("user_updates", {})
            user_data = state.get("user_data", {})
            user_id = user_data.get("user_id")
            
            if not user_id:
                raise ValueError("User ID is required for data analysis")
            
            # Initialize MCP client if available
            if user_id:
                self.initialize_mcp_client(user_id)
            
            # Analyze user updates
            if user_updates:
                analysis_result = await self._analyze_user_updates(user_id, user_updates, state)
                state["data_analysis"] = analysis_result
                
                # Generate insights
                insights = await self._generate_insights(user_id, analysis_result, state)
                state["data_insights"] = insights
            
            # Analyze overall progress patterns
            progress_analysis = await self._analyze_progress_patterns(user_id, state)
            state["progress_analysis"] = progress_analysis
            
            await self.increment_success()
            return state
            
        except Exception as e:
            error_response = await self.handle_error(e, "Data analysis")
            state["data_analysis_error"] = error_response
            return state
    
    async def _analyze_user_updates(self, user_id: str, user_updates: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user-provided updates"""
        try:
            update_text = user_updates.get("text", "")
            update_photos = user_updates.get("photos", [])
            update_timestamp = user_updates.get("timestamp")
            
            # Text analysis
            text_analysis = self._analyze_text_content(update_text)
            
            # Sentiment analysis
            sentiment_analysis = self._analyze_sentiment(update_text)
            
            # Pattern recognition
            pattern_analysis = self._recognize_patterns(update_text)
            
            analysis_result = {
                "user_id": user_id,
                "timestamp": update_timestamp,
                "text_analysis": text_analysis,
                "photo_count": len(update_photos),
                "sentiment_analysis": sentiment_analysis,
                "pattern_analysis": pattern_analysis,
                "overall_mood": self._determine_overall_mood(sentiment_analysis, pattern_analysis),
                "key_topics": self._extract_key_topics(update_text),
                "action_items": self._identify_action_items(update_text)
            }
            
            logger.info(f"Analyzed user updates for user {user_id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Failed to analyze user updates for user {user_id}: {str(e)}")
            return {}
    
    def _analyze_text_content(self, text: str) -> Dict[str, Any]:
        """Analyze text content for patterns and insights"""
        try:
            text_lower = text.lower()
            
            # Analyze nutrition-related content
            nutrition_analysis = self._analyze_nutrition_content(text_lower)
            
            # Analyze workout-related content
            workout_analysis = self._analyze_workout_content(text_lower)
            
            # Extract key metrics
            key_metrics = self._extract_key_metrics(text)
            
            return {
                "nutrition_analysis": nutrition_analysis,
                "workout_analysis": workout_analysis,
                "key_metrics": key_metrics,
                "text_length": len(text),
                "complexity_score": self._calculate_text_complexity(text)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze text content: {str(e)}")
            return {}
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the text"""
        try:
            text_lower = text.lower()
            
            # Positive and negative word analysis
            positive_words = ["good", "great", "excellent", "amazing", "happy", "satisfied", "progress", "improved"]
            negative_words = ["bad", "difficult", "hard", "struggling", "frustrated", "tired", "challenging", "disappointed"]
            
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            # Calculate sentiment score
            total_words = positive_count + negative_count
            if total_words == 0:
                sentiment_score = 0.5  # Neutral
            else:
                sentiment_score = positive_count / total_words
            
            # Determine sentiment category
            if sentiment_score >= 0.7:
                sentiment_category = "positive"
            elif sentiment_score <= 0.3:
                sentiment_category = "negative"
            else:
                sentiment_category = "neutral"
            
            return {
                "sentiment_score": sentiment_score,
                "sentiment_category": sentiment_category,
                "positive_words_found": positive_count,
                "negative_words_found": negative_count
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {str(e)}")
            return {"sentiment_score": 0.5, "sentiment_category": "neutral"}
    
    def _recognize_patterns(self, text: str) -> Dict[str, Any]:
        """Recognize patterns in the text"""
        try:
            text_lower = text.lower()
            patterns = {}
            
            # Check for meal timing patterns
            meal_timing = []
            if "breakfast" in text_lower:
                meal_timing.append("breakfast")
            if "lunch" in text_lower:
                meal_timing.append("lunch")
            if "dinner" in text_lower:
                meal_timing.append("dinner")
            if "snack" in text_lower:
                meal_timing.append("snack")
            
            patterns["meal_timing"] = meal_timing
            
            # Check for exercise patterns
            exercise_patterns = []
            if any(word in text_lower for word in ["cardio", "running", "walking"]):
                exercise_patterns.append("cardio")
            if any(word in text_lower for word in ["strength", "lifting", "weights"]):
                exercise_patterns.append("strength")
            if any(word in text_lower for word in ["yoga", "stretching", "flexibility"]):
                exercise_patterns.append("flexibility")
            
            patterns["exercise_patterns"] = exercise_patterns
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to recognize patterns: {str(e)}")
            return {}
    
    def _determine_overall_mood(self, sentiment_analysis: Dict[str, Any], pattern_analysis: Dict[str, Any]) -> str:
        """Determine overall mood based on analysis"""
        try:
            sentiment_score = sentiment_analysis.get("sentiment_score", 0.5)
            
            if sentiment_score >= 0.7:
                return "excellent"
            elif sentiment_score >= 0.6:
                return "good"
            elif sentiment_score <= 0.4:
                return "challenging"
            else:
                return "neutral"
                
        except Exception as e:
            logger.error(f"Failed to determine overall mood: {str(e)}")
            return "neutral"
    
    def _extract_key_topics(self, text: str) -> List[str]:
        """Extract key topics from the text"""
        try:
            text_lower = text.lower()
            topics = []
            
            # Define topic keywords
            topic_keywords = {
                "nutrition": ["food", "meal", "diet", "nutrition", "calories", "protein", "carbs"],
                "workout": ["exercise", "workout", "training", "fitness", "gym", "cardio", "strength"],
                "sleep": ["sleep", "rest", "bedtime", "wake", "tired", "energy"],
                "stress": ["stress", "anxiety", "relax", "meditation", "mindfulness"],
                "goals": ["goal", "target", "achievement", "progress", "milestone"]
            }
            
            # Check for topics
            for topic, keywords in topic_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    topics.append(topic)
            
            return topics
            
        except Exception as e:
            logger.error(f"Failed to extract key topics: {str(e)}")
            return []
    
    def _identify_action_items(self, text: str) -> List[str]:
        """Identify action items from the text"""
        try:
            text_lower = text.lower()
            action_items = []
            
            # Action-oriented phrases
            action_phrases = [
                "need to", "should", "must", "will", "going to", "plan to",
                "want to", "hope to", "aim to", "target", "goal"
            ]
            
            # Check for action phrases
            for phrase in action_phrases:
                if phrase in text_lower:
                    # Extract the action item
                    start_idx = text_lower.find(phrase)
                    end_idx = min(start_idx + 100, len(text))  # Get next 100 characters
                    action_text = text[start_idx:end_idx].strip()
                    action_items.append(action_text)
            
            return action_items
            
        except Exception as e:
            logger.error(f"Failed to identify action items: {str(e)}")
            return []
    
    def _analyze_nutrition_content(self, text_lower: str) -> Dict[str, Any]:
        """Analyze nutrition-related content"""
        try:
            nutrition_analysis = {
                "food_mentions": [],
                "meal_patterns": [],
                "nutritional_goals": [],
                "dietary_restrictions": [],
                "hydration": "adequate"
            }
            
            # Check for food mentions
            food_keywords = ["chicken", "vegetables", "fruits", "grains", "protein", "carbs", "fats"]
            for food in food_keywords:
                if food in text_lower:
                    nutrition_analysis["food_mentions"].append(food)
            
            # Check meal patterns
            if "breakfast" in text_lower:
                nutrition_analysis["meal_patterns"].append("breakfast")
            if "lunch" in text_lower:
                nutrition_analysis["meal_patterns"].append("lunch")
            if "dinner" in text_lower:
                nutrition_analysis["meal_patterns"].append("dinner")
            
            return nutrition_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze nutrition content: {str(e)}")
            return {}
    
    def _analyze_workout_content(self, text_lower: str) -> Dict[str, Any]:
        """Analyze workout-related content"""
        try:
            workout_analysis = {
                "exercise_types": [],
                "intensity_level": "moderate",
                "duration": "standard",
                "recovery_needs": "normal",
                "motivation_level": "good"
            }
            
            # Check exercise types
            exercise_keywords = {
                "cardio": ["running", "walking", "cycling", "swimming", "cardio"],
                "strength": ["lifting", "weights", "strength", "muscle", "gym"],
                "flexibility": ["yoga", "stretching", "flexibility", "pilates"],
                "sports": ["tennis", "basketball", "football", "soccer"]
            }
            
            for category, keywords in exercise_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    workout_analysis["exercise_types"].append(category)
            
            return workout_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze workout content: {str(e)}")
            return {}
    
    def _extract_key_metrics(self, text: str) -> Dict[str, Any]:
        """Extract key metrics from text"""
        try:
            import re
            
            metrics = {
                "weight": None,
                "calories": None,
                "steps": None,
                "workout_duration": None,
                "sleep_hours": None
            }
            
            # Extract weight
            weight_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kgs|pounds|lbs)', text, re.IGNORECASE)
            if weight_match:
                metrics["weight"] = float(weight_match.group(1))
            
            # Extract calories
            calorie_match = re.search(r'(\d+)\s*(?:calories|cal)', text, re.IGNORECASE)
            if calorie_match:
                metrics["calories"] = int(calorie_match.group(1))
            
            # Extract steps
            steps_match = re.search(r'(\d+)\s*(?:steps|step)', text, re.IGNORECASE)
            if steps_match:
                metrics["steps"] = int(steps_match.group(1))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to extract key metrics: {str(e)}")
            return {}
    
    def _calculate_text_complexity(self, text: str) -> float:
        """Calculate text complexity score"""
        try:
            if not text:
                return 0.0
            
            # Simple complexity calculation
            words = text.split()
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            
            # Normalize to 0-1 scale
            complexity_score = min(avg_word_length / 10, 1.0)
            
            return round(complexity_score, 2)
            
        except Exception as e:
            logger.error(f"Failed to calculate text complexity: {str(e)}")
            return 0.0
    
    async def _generate_insights(self, user_id: str, analysis_result: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from analysis results"""
        try:
            insights = {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "key_insights": [],
                "trends": [],
                "recommendations": []
            }
            
            # Generate key insights
            key_insights = self._generate_key_insights(analysis_result)
            insights["key_insights"] = key_insights
            
            # Identify trends
            trends = self._identify_trends(analysis_result, state)
            insights["trends"] = trends
            
            # Generate recommendations
            recommendations = self._generate_insight_recommendations(analysis_result, trends)
            insights["recommendations"] = recommendations
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights for user {user_id}: {str(e)}")
            return {}
    
    def _generate_key_insights(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate key insights from analysis"""
        try:
            insights = []
            
            # Sentiment insights
            sentiment = analysis_result.get("sentiment_analysis", {})
            if sentiment.get("sentiment_category") == "positive":
                insights.append("User is showing positive engagement with their health journey")
            elif sentiment.get("sentiment_category") == "negative":
                insights.append("User may be experiencing challenges that need attention")
            
            # Pattern insights
            patterns = analysis_result.get("pattern_analysis", {})
            if patterns.get("meal_timing"):
                insights.append(f"User is tracking {len(patterns['meal_timing'])} meal types")
            
            if patterns.get("exercise_patterns"):
                insights.append(f"User is engaging in {len(patterns['exercise_patterns'])} types of exercise")
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate key insights: {str(e)}")
            return []
    
    def _identify_trends(self, analysis_result: Dict[str, Any], state: Dict[str, Any]) -> List[str]:
        """Identify trends in user data"""
        try:
            trends = []
            
            # Mood trends
            overall_mood = analysis_result.get("overall_mood", "neutral")
            if overall_mood == "excellent":
                trends.append("Consistently high energy and motivation levels")
            elif overall_mood == "challenging":
                trends.append("Experiencing consistent challenges that may need intervention")
            
            # Progress trends
            if "progress" in analysis_result.get("key_topics", []):
                trends.append("User is actively tracking and reporting progress")
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to identify trends: {str(e)}")
            return []
    
    def _generate_insight_recommendations(self, analysis_result: Dict[str, Any], trends: List[str]) -> List[str]:
        """Generate recommendations based on insights"""
        try:
            recommendations = []
            
            # Sentiment-based recommendations
            sentiment = analysis_result.get("sentiment_analysis", {})
            if sentiment.get("sentiment_category") == "negative":
                recommendations.append("Consider scheduling a check-in to address challenges")
                recommendations.append("Review and potentially adjust current goals")
            
            # Pattern-based recommendations
            patterns = analysis_result.get("pattern_analysis", {})
            if not patterns.get("meal_timing"):
                recommendations.append("Encourage meal tracking for better nutrition insights")
            
            if not patterns.get("exercise_patterns"):
                recommendations.append("Suggest diversifying workout routines")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate insight recommendations: {str(e)}")
            return []
    
    async def _analyze_progress_patterns(self, user_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall progress patterns"""
        try:
            # This would typically analyze historical data
            # For now, return mock analysis
            
            progress_analysis = {
                "user_id": user_id,
                "analysis_period": "last_30_days",
                "consistency_score": 0.75,
                "improvement_areas": ["nutrition_tracking", "workout_consistency"],
                "strength_areas": ["goal_setting", "progress_reporting"],
                "overall_trend": "improving"
            }
            
            return progress_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze progress patterns for user {user_id}: {str(e)}")
            return {}
    
    async def get_data_analysis(self, user_id: str) -> Dict[str, Any]:
        """Get data analysis for a user"""
        try:
            # This would typically retrieve from database
            # For now, return empty dict
            return {}
        except Exception as e:
            logger.error(f"Failed to get data analysis for user {user_id}: {str(e)}")
            return {}
    
    async def get_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights for a user"""
        try:
            # This would typically retrieve from database
            # For now, return empty dict
            return {}
        except Exception as e:
            logger.error(f"Failed to get insights for user {user_id}: {str(e)}")
            return {}
