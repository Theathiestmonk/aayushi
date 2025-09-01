"""
Workout Planner Agent - Generates personalized workout plans
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class WorkoutPlannerAgent(BaseAgent):
    """
    Workout Planner Agent responsible for:
    - Creating personalized workout plans
    - Adapting plans based on user feedback
    - Coordinating with other agents
    - Managing workout progression
    """
    
    def __init__(self):
        super().__init__("WorkoutPlannerAgent")
        self.workout_templates = {}
        self.exercise_library = {}
        self.progression_rules = {}
        
        # Initialize workout components
        self._initialize_workout_templates()
        self._initialize_exercise_library()
        self._initialize_progression_rules()
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for workout planning
        
        Args:
            state: Current workflow state containing user data and preferences
            
        Returns:
            Updated state with workout plan
        """
        try:
            await self.update_status("processing")
            
            # Extract user data
            user_data = state.get("user_data", {})
            user_id = user_data.get("user_id")
            
            if not user_id:
                raise ValueError("User ID is required for workout planning")
            
            # Initialize MCP client if available
            if user_id:
                self.initialize_mcp_client(user_id)
            
            # Check if workout plan already exists
            existing_plan = state.get("workout_plan")
            if existing_plan:
                # Adapt existing plan based on feedback
                adapted_plan = await self._adapt_workout_plan(user_id, existing_plan, state)
                state["workout_plan"] = adapted_plan
            else:
                # Create new workout plan
                new_plan = await self._create_workout_plan(user_id, user_data, state)
                state["workout_plan"] = new_plan
            
            # Generate workout schedule
            workout_schedule = await self._generate_workout_schedule(state["workout_plan"])
            state["workout_schedule"] = workout_schedule
            
            # Create progression timeline
            progression_timeline = await self._create_progression_timeline(state["workout_plan"])
            state["progression_timeline"] = progression_timeline
            
            await self.increment_success()
            return state
            
        except Exception as e:
            error_response = await self.handle_error(e, "Workout planning")
            state["workout_planning_error"] = error_response
            return state
    
    def _initialize_workout_templates(self):
        """Initialize workout plan templates"""
        try:
            self.workout_templates = {
                "beginner": {
                    "name": "Beginner Fitness Foundation",
                    "description": "Perfect for those new to fitness or returning after a break",
                    "focus": ["form", "consistency", "basic strength"],
                    "intensity": "low",
                    "frequency": {"days_per_week": 3, "rest_days": 4},
                    "session_duration": "30-45 minutes",
                    "progression_rate": "slow"
                },
                "intermediate": {
                    "name": "Intermediate Strength & Conditioning",
                    "description": "For those with consistent fitness experience",
                    "focus": ["strength", "endurance", "muscle building"],
                    "intensity": "moderate",
                    "frequency": {"days_per_week": 4, "rest_days": 3},
                    "session_duration": "45-60 minutes",
                    "progression_rate": "moderate"
                },
                "advanced": {
                    "name": "Advanced Performance Training",
                    "description": "For experienced athletes and fitness enthusiasts",
                    "focus": ["power", "performance", "specialization"],
                    "intensity": "high",
                    "frequency": {"days_per_week": 5, "rest_days": 2},
                    "session_duration": "60-90 minutes",
                    "progression_rate": "fast"
                }
            }
            
            logger.info("Workout templates initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize workout templates: {str(e)}")
    
    def _initialize_exercise_library(self):
        """Initialize exercise library with categorized exercises"""
        try:
            self.exercise_library = {
                "strength": {
                    "upper_body": [
                        {"name": "Push-ups", "difficulty": "beginner", "equipment": "none", "muscles": ["chest", "triceps", "shoulders"]},
                        {"name": "Pull-ups", "difficulty": "intermediate", "equipment": "bar", "muscles": ["back", "biceps"]},
                        {"name": "Dumbbell Rows", "difficulty": "beginner", "equipment": "dumbbells", "muscles": ["back", "biceps"]}
                    ],
                    "lower_body": [
                        {"name": "Squats", "difficulty": "beginner", "equipment": "none", "muscles": ["quads", "glutes", "hamstrings"]},
                        {"name": "Lunges", "difficulty": "beginner", "equipment": "none", "muscles": ["quads", "glutes", "hamstrings"]},
                        {"name": "Deadlifts", "difficulty": "intermediate", "equipment": "barbell", "muscles": ["back", "glutes", "hamstrings"]}
                    ],
                    "core": [
                        {"name": "Planks", "difficulty": "beginner", "equipment": "none", "muscles": ["abs", "core"]},
                        {"name": "Crunches", "difficulty": "beginner", "equipment": "none", "muscles": ["abs"]},
                        {"name": "Russian Twists", "difficulty": "intermediate", "equipment": "none", "muscles": ["obliques", "core"]}
                    ]
                },
                "cardio": {
                    "low_impact": [
                        {"name": "Walking", "difficulty": "beginner", "equipment": "none", "intensity": "low"},
                        {"name": "Cycling", "difficulty": "beginner", "equipment": "bike", "intensity": "low"},
                        {"name": "Swimming", "difficulty": "beginner", "equipment": "pool", "intensity": "low"}
                    ],
                    "high_impact": [
                        {"name": "Running", "difficulty": "intermediate", "equipment": "none", "intensity": "high"},
                        {"name": "Jump Rope", "difficulty": "intermediate", "equipment": "rope", "intensity": "high"},
                        {"name": "Burpees", "difficulty": "advanced", "equipment": "none", "intensity": "high"}
                    ]
                },
                "flexibility": {
                    "static": [
                        {"name": "Hamstring Stretch", "difficulty": "beginner", "equipment": "none", "target": "hamstrings"},
                        {"name": "Chest Stretch", "difficulty": "beginner", "equipment": "none", "target": "chest"},
                        {"name": "Hip Flexor Stretch", "difficulty": "beginner", "equipment": "none", "target": "hip flexors"}
                    ],
                    "dynamic": [
                        {"name": "Arm Circles", "difficulty": "beginner", "equipment": "none", "target": "shoulders"},
                        {"name": "Leg Swings", "difficulty": "beginner", "equipment": "none", "target": "hips"},
                        {"name": "Walking Knee Hugs", "difficulty": "beginner", "equipment": "none", "target": "full body"}
                    ]
                }
            }
            
            logger.info("Exercise library initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize exercise library: {str(e)}")
    
    def _initialize_progression_rules(self):
        """Initialize progression rules for workout advancement"""
        try:
            self.progression_rules = {
                "strength": {
                    "beginner": {"weeks_to_advance": 8, "progression_type": "volume"},
                    "intermediate": {"weeks_to_advance": 6, "progression_type": "intensity"},
                    "advanced": {"weeks_to_advance": 4, "progression_type": "complexity"}
                },
                "cardio": {
                    "beginner": {"weeks_to_advance": 6, "progression_type": "duration"},
                    "intermediate": {"weeks_to_advance": 4, "progression_type": "intensity"},
                    "advanced": {"weeks_to_advance": 3, "progression_type": "volume"}
                },
                "flexibility": {
                    "beginner": {"weeks_to_advance": 4, "progression_type": "duration"},
                    "intermediate": {"weeks_to_advance": 3, "progression_type": "depth"},
                    "advanced": {"weeks_to_advance": 2, "progression_type": "complexity"}
                }
            }
            
            logger.info("Progression rules initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize progression rules: {str(e)}")
    
    async def _create_workout_plan(self, user_id: str, user_data: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new personalized workout plan"""
        try:
            # Determine user fitness level
            fitness_level = self._assess_fitness_level(user_data)
            
            # Get appropriate template
            template = self.workout_templates.get(fitness_level, self.workout_templates["beginner"])
            
            # Create workout plan
            workout_plan = {
                "plan_id": f"workout_{user_id}_{datetime.utcnow().timestamp()}",
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "fitness_level": fitness_level,
                "template": template,
                "goals": self._extract_workout_goals(user_data),
                "restrictions": self._extract_workout_restrictions(user_data),
                "preferences": self._extract_workout_preferences(user_data),
                "exercises": await self._select_exercises(fitness_level, user_data),
                "schedule": self._create_weekly_schedule(template),
                "progression_plan": self._create_progression_plan(fitness_level),
                "estimated_duration": "8-12 weeks",
                "success_metrics": self._define_success_metrics(fitness_level)
            }
            
            # Use MCP tools for enhanced planning if available
            if self.mcp_client:
                try:
                    # Get health insights for workout planning
                    health_insights = await self.get_health_insights(
                        user_data=user_data,
                        context="workout_planning"
                    )
                    if health_insights.get("success"):
                        workout_plan["health_insights"] = health_insights.get("result", {})
                except Exception as e:
                    logger.warning(f"Could not get health insights for workout planning: {str(e)}")
            
            logger.info(f"Created workout plan for user {user_id}, fitness level: {fitness_level}")
            return workout_plan
            
        except Exception as e:
            logger.error(f"Failed to create workout plan for user {user_id}: {str(e)}")
            return {}
    
    async def _adapt_workout_plan(self, user_id: str, existing_plan: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt existing workout plan based on feedback and progress"""
        try:
            adapted_plan = existing_plan.copy()
            
            # Get user feedback and progress data
            user_feedback = state.get("user_feedback", {})
            progress_data = state.get("progress_data", {})
            
            # Adapt based on feedback
            if user_feedback:
                adapted_plan = await self._incorporate_user_feedback(adapted_plan, user_feedback)
            
            # Adapt based on progress
            if progress_data:
                adapted_plan = await self._adapt_based_on_progress(adapted_plan, progress_data)
            
            # Update adaptation timestamp
            adapted_plan["last_adapted"] = datetime.utcnow().isoformat()
            adapted_plan["adaptation_count"] = adapted_plan.get("adaptation_count", 0) + 1
            
            logger.info(f"Adapted workout plan for user {user_id}")
            return adapted_plan
            
        except Exception as e:
            logger.error(f"Failed to adapt workout plan for user {user_id}: {str(e)}")
            return existing_plan
    
    def _assess_fitness_level(self, user_data: Dict[str, Any]) -> str:
        """Assess user's fitness level based on data"""
        try:
            # Extract relevant data
            age = user_data.get("age", 30)
            fitness_experience = user_data.get("fitness_experience", "beginner")
            current_activity_level = user_data.get("activity_level", "sedentary")
            health_conditions = user_data.get("health_conditions", [])
            
            # Simple assessment logic
            if fitness_experience == "advanced" and current_activity_level in ["very_active", "extremely_active"]:
                return "advanced"
            elif fitness_experience == "intermediate" or current_activity_level in ["moderately_active", "very_active"]:
                return "intermediate"
            else:
                return "beginner"
                
        except Exception as e:
            logger.error(f"Failed to assess fitness level: {str(e)}")
            return "beginner"
    
    def _extract_workout_goals(self, user_data: Dict[str, Any]) -> List[str]:
        """Extract workout goals from user data"""
        try:
            goals = []
            
            # Primary goals
            if user_data.get("goal_weight_loss"):
                goals.append("weight_loss")
            if user_data.get("goal_muscle_gain"):
                goals.append("muscle_gain")
            if user_data.get("goal_endurance"):
                goals.append("endurance")
            if user_data.get("goal_strength"):
                goals.append("strength")
            if user_data.get("goal_flexibility"):
                goals.append("flexibility")
            
            # Secondary goals
            if user_data.get("goal_general_fitness"):
                goals.append("general_fitness")
            if user_data.get("goal_sports_performance"):
                goals.append("sports_performance")
            
            return goals if goals else ["general_fitness"]
            
        except Exception as e:
            logger.error(f"Failed to extract workout goals: {str(e)}")
            return ["general_fitness"]
    
    def _extract_workout_restrictions(self, user_data: Dict[str, Any]) -> List[str]:
        """Extract workout restrictions from user data"""
        try:
            restrictions = []
            
            # Physical restrictions
            if user_data.get("injury_history"):
                restrictions.append("injury_considerations")
            if user_data.get("joint_issues"):
                restrictions.append("low_impact_only")
            if user_data.get("back_problems"):
                restrictions.append("no_heavy_lifting")
            
            # Equipment restrictions
            if not user_data.get("access_gym"):
                restrictions.append("home_workouts_only")
            if not user_data.get("access_equipment"):
                restrictions.append("bodyweight_only")
            
            # Time restrictions
            if user_data.get("time_constraint") == "very_limited":
                restrictions.append("short_sessions")
            
            return restrictions
            
        except Exception as e:
            logger.error(f"Failed to extract workout restrictions: {str(e)}")
            return []
    
    def _extract_workout_preferences(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract workout preferences from user data"""
        try:
            preferences = {
                "workout_time": user_data.get("preferred_workout_time", "morning"),
                "workout_duration": user_data.get("preferred_workout_duration", "45_minutes"),
                "workout_style": user_data.get("preferred_workout_style", "traditional"),
                "group_vs_individual": user_data.get("group_workout_preference", "individual"),
                "music": user_data.get("workout_music_preference", True),
                "outdoor_vs_indoor": user_data.get("outdoor_workout_preference", "indoor")
            }
            
            return preferences
            
        except Exception as e:
            logger.error(f"Failed to extract workout preferences: {str(e)}")
            return {}
    
    async def _select_exercises(self, fitness_level: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Select appropriate exercises for the user"""
        try:
            selected_exercises = {
                "strength": {},
                "cardio": {},
                "flexibility": {}
            }
            
            # Select strength exercises
            for body_part, exercises in self.exercise_library["strength"].items():
                selected_exercises["strength"][body_part] = []
                for exercise in exercises:
                    if self._is_exercise_suitable(exercise, fitness_level, user_data):
                        selected_exercises["strength"][body_part].append(exercise)
            
            # Select cardio exercises
            for intensity, exercises in self.exercise_library["cardio"].items():
                selected_exercises["cardio"][intensity] = []
                for exercise in exercises:
                    if self._is_exercise_suitable(exercise, fitness_level, user_data):
                        selected_exercises["cardio"][intensity].append(exercise)
            
            # Select flexibility exercises
            for style, exercises in self.exercise_library["flexibility"].items():
                selected_exercises["flexibility"][style] = []
                for exercise in exercises:
                    if self._is_exercise_suitable(exercise, fitness_level, user_data):
                        selected_exercises["flexibility"][style].append(exercise)
            
            return selected_exercises
            
        except Exception as e:
            logger.error(f"Failed to select exercises: {str(e)}")
            return {}
    
    def _is_exercise_suitable(self, exercise: Dict[str, Any], fitness_level: str, user_data: Dict[str, Any]) -> bool:
        """Check if an exercise is suitable for the user"""
        try:
            # Check fitness level compatibility
            if exercise.get("difficulty") == "advanced" and fitness_level == "beginner":
                return False
            
            # Check equipment availability
            if exercise.get("equipment") != "none" and not user_data.get("access_equipment"):
                return False
            
            # Check injury restrictions
            if "injury_considerations" in user_data.get("workout_restrictions", []):
                if exercise.get("name") in ["Deadlifts", "Squats", "Burpees"]:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check exercise suitability: {str(e)}")
            return False
    
    def _create_weekly_schedule(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Create weekly workout schedule based on template"""
        try:
            days_per_week = template["frequency"]["days_per_week"]
            rest_days = template["frequency"]["rest_days"]
            
            # Simple schedule creation
            schedule = {
                "monday": "strength_upper_body" if days_per_week >= 3 else "rest",
                "tuesday": "cardio" if days_per_week >= 2 else "rest",
                "wednesday": "strength_lower_body" if days_per_week >= 3 else "rest",
                "thursday": "flexibility" if days_per_week >= 4 else "rest",
                "friday": "strength_full_body" if days_per_week >= 3 else "rest",
                "saturday": "cardio" if days_per_week >= 4 else "rest",
                "sunday": "rest"
            }
            
            return schedule
            
        except Exception as e:
            logger.error(f"Failed to create weekly schedule: {str(e)}")
            return {}
    
    def _create_progression_plan(self, fitness_level: str) -> Dict[str, Any]:
        """Create progression plan for workout advancement"""
        try:
            progression_plan = {
                "current_phase": "foundation",
                "total_phases": 3,
                "weeks_per_phase": self.progression_rules["strength"][fitness_level]["weeks_to_advance"],
                "progression_criteria": {
                    "strength": "increase weight or reps",
                    "cardio": "increase duration or intensity",
                    "flexibility": "increase hold time or depth"
                },
                "milestones": [
                    {"week": 4, "milestone": "establish_consistency"},
                    {"week": 8, "milestone": "increase_intensity"},
                    {"week": 12, "milestone": "advanced_variations"}
                ]
            }
            
            return progression_plan
            
        except Exception as e:
            logger.error(f"Failed to create progression plan: {str(e)}")
            return {}
    
    def _define_success_metrics(self, fitness_level: str) -> List[str]:
        """Define success metrics for the workout plan"""
        try:
            base_metrics = ["consistency", "progression", "enjoyment"]
            
            if fitness_level == "beginner":
                base_metrics.extend(["form_improvement", "habit_formation"])
            elif fitness_level == "intermediate":
                base_metrics.extend(["strength_gains", "endurance_improvement"])
            else:
                base_metrics.extend(["performance_metrics", "specialization_goals"])
            
            return base_metrics
            
        except Exception as e:
            logger.error(f"Failed to define success metrics: {str(e)}")
            return ["consistency", "progression"]
    
    async def _generate_workout_schedule(self, workout_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed workout schedule"""
        try:
            schedule = workout_plan.get("schedule", {})
            exercises = workout_plan.get("exercises", {})
            
            detailed_schedule = {}
            
            for day, workout_type in schedule.items():
                if workout_type == "rest":
                    detailed_schedule[day] = {"type": "rest", "description": "Recovery day"}
                else:
                    day_exercises = self._get_exercises_for_workout_type(workout_type, exercises)
                    detailed_schedule[day] = {
                        "type": workout_type,
                        "exercises": day_exercises,
                        "duration": workout_plan["template"]["session_duration"],
                        "intensity": workout_plan["template"]["intensity"]
                    }
            
            return detailed_schedule
            
        except Exception as e:
            logger.error(f"Failed to generate workout schedule: {str(e)}")
            return {}
    
    def _get_exercises_for_workout_type(self, workout_type: str, exercises: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get exercises for a specific workout type"""
        try:
            if workout_type == "strength_upper_body":
                return exercises.get("strength", {}).get("upper_body", [])[:3]
            elif workout_type == "strength_lower_body":
                return exercises.get("strength", {}).get("lower_body", [])[:3]
            elif workout_type == "strength_full_body":
                upper = exercises.get("strength", {}).get("upper_body", [])[:2]
                lower = exercises.get("strength", {}).get("lower_body", [])[:2]
                core = exercises.get("strength", {}).get("core", [])[:1]
                return upper + lower + core
            elif workout_type == "cardio":
                return exercises.get("cardio", {}).get("low_impact", [])[:2]
            elif workout_type == "flexibility":
                return exercises.get("flexibility", {}).get("static", [])[:3]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to get exercises for workout type: {str(e)}")
            return []
    
    async def _create_progression_timeline(self, workout_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create timeline for workout progression"""
        try:
            progression_plan = workout_plan.get("progression_plan", {})
            weeks_per_phase = progression_plan.get("weeks_per_phase", 8)
            
            timeline = {
                "total_weeks": weeks_per_phase * 3,
                "phases": [
                    {
                        "phase": "foundation",
                        "weeks": f"1-{weeks_per_phase}",
                        "focus": "establish_consistency",
                        "intensity": "low_to_moderate"
                    },
                    {
                        "phase": "progression",
                        "weeks": f"{weeks_per_phase + 1}-{weeks_per_phase * 2}",
                        "focus": "increase_intensity",
                        "intensity": "moderate"
                    },
                    {
                        "phase": "advancement",
                        "weeks": f"{weeks_per_phase * 2 + 1}-{weeks_per_phase * 3}",
                        "focus": "advanced_variations",
                        "intensity": "moderate_to_high"
                    }
                ]
            }
            
            return timeline
            
        except Exception as e:
            logger.error(f"Failed to create progression timeline: {str(e)}")
            return {}
    
    async def _incorporate_user_feedback(self, workout_plan: Dict[str, Any], user_feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Incorporate user feedback into workout plan"""
        try:
            adapted_plan = workout_plan.copy()
            
            # Handle difficulty feedback
            if user_feedback.get("too_difficult"):
                adapted_plan = await self._reduce_difficulty(adapted_plan)
            elif user_feedback.get("too_easy"):
                adapted_plan = await self._increase_difficulty(adapted_plan)
            
            # Handle time feedback
            if user_feedback.get("too_long"):
                adapted_plan = await self._reduce_duration(adapted_plan)
            elif user_feedback.get("too_short"):
                adapted_plan = await self._increase_duration(adapted_plan)
            
            # Handle preference feedback
            if user_feedback.get("exercise_preferences"):
                adapted_plan = await self._adjust_exercises(adapted_plan, user_feedback["exercise_preferences"])
            
            return adapted_plan
            
        except Exception as e:
            logger.error(f"Failed to incorporate user feedback: {str(e)}")
            return workout_plan
    
    async def _adapt_based_on_progress(self, workout_plan: Dict[str, Any], progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt workout plan based on progress data"""
        try:
            adapted_plan = workout_plan.copy()
            
            # Check if ready for progression
            if progress_data.get("consistency_score", 0) >= 0.8:
                adapted_plan = await self._progress_workout(adapted_plan)
            
            # Check if need to reduce intensity
            if progress_data.get("fatigue_score", 0) >= 0.7:
                adapted_plan = await self._reduce_intensity(adapted_plan)
            
            return adapted_plan
            
        except Exception as e:
            logger.error(f"Failed to adapt based on progress: {str(e)}")
            return workout_plan
    
    async def _reduce_difficulty(self, workout_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Reduce workout difficulty"""
        try:
            adapted_plan = workout_plan.copy()
            
            # Reduce intensity
            if adapted_plan["template"]["intensity"] == "high":
                adapted_plan["template"]["intensity"] = "moderate"
            elif adapted_plan["template"]["intensity"] == "moderate":
                adapted_plan["template"]["intensity"] = "low"
            
            # Reduce frequency
            current_frequency = adapted_plan["template"]["frequency"]["days_per_week"]
            if current_frequency > 3:
                adapted_plan["template"]["frequency"]["days_per_week"] = current_frequency - 1
            
            return adapted_plan
            
        except Exception as e:
            logger.error(f"Failed to reduce difficulty: {str(e)}")
            return workout_plan
    
    async def _increase_difficulty(self, workout_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Increase workout difficulty"""
        try:
            adapted_plan = workout_plan.copy()
            
            # Increase intensity
            if adapted_plan["template"]["intensity"] == "low":
                adapted_plan["template"]["intensity"] = "moderate"
            elif adapted_plan["template"]["intensity"] == "moderate":
                adapted_plan["template"]["intensity"] = "high"
            
            # Increase frequency
            current_frequency = adapted_plan["template"]["frequency"]["days_per_week"]
            if current_frequency < 6:
                adapted_plan["template"]["frequency"]["days_per_week"] = current_frequency + 1
            
            return adapted_plan
            
        except Exception as e:
            logger.error(f"Failed to increase difficulty: {str(e)}")
            return workout_plan
    
    async def _reduce_duration(self, workout_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Reduce workout duration"""
        try:
            adapted_plan = workout_plan.copy()
            
            # Reduce session duration
            if "60-90 minutes" in adapted_plan["template"]["session_duration"]:
                adapted_plan["template"]["session_duration"] = "45-60 minutes"
            elif "45-60 minutes" in adapted_plan["template"]["session_duration"]:
                adapted_plan["template"]["session_duration"] = "30-45 minutes"
            
            return adapted_plan
            
        except Exception as e:
            logger.error(f"Failed to reduce duration: {str(e)}")
            return workout_plan
    
    async def _increase_duration(self, workout_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Increase workout duration"""
        try:
            adapted_plan = workout_plan.copy()
            
            # Increase session duration
            if "30-45 minutes" in adapted_plan["template"]["session_duration"]:
                adapted_plan["template"]["session_duration"] = "45-60 minutes"
            elif "45-60 minutes" in adapted_plan["template"]["session_duration"]:
                adapted_plan["template"]["session_duration"] = "60-90 minutes"
            
            return adapted_plan
            
        except Exception as e:
            logger.error(f"Failed to increase duration: {str(e)}")
            return workout_plan
    
    async def _adjust_exercises(self, workout_plan: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust exercises based on user preferences"""
        try:
            adapted_plan = workout_plan.copy()
            
            # This would implement exercise substitution logic
            # For now, return the original plan
            return adapted_plan
            
        except Exception as e:
            logger.error(f"Failed to adjust exercises: {str(e)}")
            return workout_plan
    
    async def _progress_workout(self, workout_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Progress workout to next phase"""
        try:
            adapted_plan = workout_plan.copy()
            
            # Update progression phase
            current_phase = adapted_plan["progression_plan"]["current_phase"]
            if current_phase == "foundation":
                adapted_plan["progression_plan"]["current_phase"] = "progression"
            elif current_phase == "progression":
                adapted_plan["progression_plan"]["current_phase"] = "advancement"
            
            return adapted_plan
            
        except Exception as e:
            logger.error(f"Failed to progress workout: {str(e)}")
            return workout_plan
    
    async def _reduce_intensity(self, workout_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Reduce workout intensity"""
        try:
            adapted_plan = workout_plan.copy()
            
            # Reduce intensity
            if adapted_plan["template"]["intensity"] == "high":
                adapted_plan["template"]["intensity"] = "moderate"
            elif adapted_plan["template"]["intensity"] == "moderate":
                adapted_plan["template"]["intensity"] = "low"
            
            return adapted_plan
            
        except Exception as e:
            logger.error(f"Failed to reduce intensity: {str(e)}")
            return workout_plan
    
    async def get_workout_plan(self, user_id: str) -> Dict[str, Any]:
        """Get current workout plan for a user"""
        try:
            # This would typically retrieve from database
            # For now, return empty dict
            return {}
        except Exception as e:
            logger.error(f"Failed to get workout plan for user {user_id}: {str(e)}")
            return {}
    
    async def get_workout_schedule(self, user_id: str) -> Dict[str, Any]:
        """Get workout schedule for a user"""
        try:
            # This would typically retrieve from database
            # For now, return empty dict
            return {}
        except Exception as e:
            logger.error(f"Failed to get workout schedule for user {user_id}: {str(e)}")
            return {}




