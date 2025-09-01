"""
Agent Manager - Orchestrates the multi-agent system using LangGraph
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.base_agent import BaseAgent
from app.agents.diet_planner_agent import DietPlannerAgent
from app.agents.follow_up_agent import FollowUpAgent
from app.agents.tracker_agent import TrackerAgent
from app.agents.recommender_agent import RecommenderAgent
from app.agents.workout_planner_agent import WorkoutPlannerAgent
from app.agents.recipe_generator_agent import RecipeGeneratorAgent
from app.agents.grocery_list_agent import GroceryListAgent
from app.agents.grocery_ordering_agent import GroceryOrderingAgent
from app.agents.data_analyzer_agent import DataAnalyzerAgent

logger = logging.getLogger(__name__)

class AgentManager:
    """
    Manages the multi-agent system for the AI Dietitian
    Orchestrates workflow between specialized agents
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.workflow_graph = None
        self.memory_saver = MemorySaver()
        
        # Initialize all agents
        self._initialize_agents()
        
        # Build workflow graph
        self._build_workflow()
    
    def _initialize_agents(self):
        """Initialize all specialized agents"""
        try:
            # Core planning agents
            self.agents["diet_planner"] = DietPlannerAgent()
            self.agents["workout_planner"] = WorkoutPlannerAgent()
            
            # Recipe and grocery agents
            self.agents["recipe_generator"] = RecipeGeneratorAgent()
            self.agents["grocery_list"] = GroceryListAgent()
            self.agents["grocery_ordering"] = GroceryOrderingAgent()
            
            # Follow-up and tracking agents
            self.agents["follow_up"] = FollowUpAgent()
            self.agents["tracker"] = TrackerAgent()
            self.agents["recommender"] = RecommenderAgent()
            
            # Analysis agent
            self.agents["data_analyzer"] = DataAnalyzerAgent()
            
            logger.info(f"✅ Initialized {len(self.agents)} specialized agents")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize agents: {str(e)}")
            # Fallback to mock agents
            self._initialize_mock_agents()
    
    def _initialize_mock_agents(self):
        """Initialize mock agents as fallback"""
        try:
            # Create simple mock agents for each type
            agent_types = [
                "diet_planner", "workout_planner", "recipe_generator",
                "grocery_list", "grocery_ordering", "follow_up",
                "tracker", "recommender", "data_analyzer"
            ]
            
            for agent_type in agent_types:
                self.agents[agent_type] = self._create_mock_agent(agent_type)
            
            logger.info(f"✅ Initialized {len(self.agents)} mock agents as fallback")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize mock agents: {str(e)}")
    
    def _create_mock_agent(self, agent_type: str) -> BaseAgent:
        """Create a mock agent for fallback"""
        class MockAgent(BaseAgent):
            async def process(self, state):
                state[f"{agent_type}_result"] = {
                    "status": "mock_processed",
                    "agent": agent_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": f"Mock processing by {agent_type}"
                }
                return state
        
        return MockAgent(agent_type)
    
    def _build_workflow(self):
        """Build the LangGraph workflow"""
        try:
            # Create state graph
            workflow = StateGraph(StateType=Dict[str, Any])
            
            # Add nodes for each agent
            for agent_name, agent in self.agents.items():
                workflow.add_node(agent_name, agent.process)
            
            # Define workflow edges based on the flowchart
            # Initial setup flow
            workflow.add_edge("diet_planner", "recipe_generator")
            workflow.add_edge("diet_planner", "grocery_list")
            workflow.add_edge("workout_planner", "follow_up")
            
            # Recipe and grocery flow
            workflow.add_edge("recipe_generator", "grocery_list")
            workflow.add_edge("grocery_list", "grocery_ordering")
            
            # Follow-up and tracking flow
            workflow.add_edge("follow_up", "tracker")
            workflow.add_edge("tracker", "recommender")
            
            # Data analysis flow
            workflow.add_edge("data_analyzer", "recommender")
            
            # Set entry points
            workflow.set_entry_point("diet_planner")
            workflow.set_entry_point("workout_planner")
            
            # Set end points
            workflow.add_edge("grocery_ordering", END)
            workflow.add_edge("recommender", END)
            
            # Compile workflow
            self.workflow_graph = workflow.compile(checkpointer=self.memory_saver)
            
            logger.info("✅ LangGraph workflow built successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to build workflow: {str(e)}")
            self.workflow_graph = None
    
    async def process_request(self, user_data: Dict[str, Any], request_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Process a user request through the multi-agent system
        
        Args:
            user_data: User profile and request data
            request_type: Type of request (comprehensive, diet_only, workout_only, etc.)
            
        Returns:
            Processed result from the agent system
        """
        try:
            if not self.workflow_graph:
                logger.warning("⚠️ Workflow graph not available, using fallback processing")
                return await self._fallback_processing(user_data, request_type)
            
            # Prepare initial state
            initial_state = self._prepare_initial_state(user_data, request_type)
            
            # Execute workflow
            config = {"configurable": {"thread_id": f"thread_{user_data.get('user_id', 'unknown')}"}}
            result = await self.workflow_graph.ainvoke(initial_state, config)
            
            logger.info(f"✅ Request processed successfully for user {user_data.get('user_id')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to process request: {str(e)}")
            return await self._fallback_processing(user_data, request_type)
    
    def _prepare_initial_state(self, user_data: Dict[str, Any], request_type: str) -> Dict[str, Any]:
        """Prepare initial state for the workflow"""
        try:
            state = {
                "user_data": user_data,
                "request_type": request_type,
                "timestamp": datetime.utcnow().isoformat(),
                "workflow_status": "started",
                "agent_results": {},
                "errors": []
            }
            
            # Add request-specific data
            if request_type == "diet_only":
                state["focus_areas"] = ["diet_planning", "recipe_generation", "grocery_management"]
            elif request_type == "workout_only":
                state["focus_areas"] = ["workout_planning", "progress_tracking"]
            else:  # comprehensive
                state["focus_areas"] = ["diet_planning", "workout_planning", "recipe_generation", 
                                      "grocery_management", "progress_tracking", "follow_up"]
            
            return state
            
        except Exception as e:
            logger.error(f"Failed to prepare initial state: {str(e)}")
            return {"user_data": user_data, "error": str(e)}
    
    async def _fallback_processing(self, user_data: Dict[str, Any], request_type: str) -> Dict[str, Any]:
        """Fallback processing when workflow is unavailable"""
        try:
            logger.info("🔄 Using fallback processing")
            
            state = self._prepare_initial_state(user_data, request_type)
            
            # Process with each agent sequentially
            for agent_name, agent in self.agents.items():
                try:
                    logger.info(f"Processing with {agent_name}")
                    state = await agent.process(state)
                except Exception as e:
                    logger.error(f"Error in {agent_name}: {str(e)}")
                    state["errors"].append(f"{agent_name}: {str(e)}")
            
            state["workflow_status"] = "completed_fallback"
            state["timestamp"] = datetime.utcnow().isoformat()
            
            return state
            
        except Exception as e:
            logger.error(f"Fallback processing failed: {str(e)}")
            return {
                "user_data": user_data,
                "error": f"Processing failed: {str(e)}",
                "workflow_status": "failed",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        try:
            status = {}
            for agent_name, agent in self.agents.items():
                status[agent_name] = {
                    "status": await agent.get_status(),
                    "performance": agent.get_performance_metrics(),
                    "last_activity": agent.last_activity.isoformat()
                }
            
            return {
                "total_agents": len(self.agents),
                "agents": status,
                "workflow_available": self.workflow_graph is not None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get agent status: {str(e)}")
            return {"error": str(e)}
    
    async def get_workflow_status(self) -> Dict[str, Any]:
        """Get workflow status and configuration"""
        try:
            if not self.workflow_graph:
                return {"status": "unavailable", "error": "Workflow not built"}
            
            return {
                "status": "available",
                "total_agents": len(self.agents),
                "agent_names": list(self.agents.keys()),
                "workflow_type": "LangGraph",
                "memory_enabled": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow status: {str(e)}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            for agent_name, agent in self.agents.items():
                await agent.cleanup()
            
            logger.info("✅ Agent manager cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Agent manager cleanup failed: {str(e)}")

# Global agent manager instance
agent_manager = AgentManager()
