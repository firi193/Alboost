"""
Agent orchestration logic using Google's Agent Development Kit (ADK) for content marketing workflow.
"""
from typing import Dict, List, Optional
from workflows.core.agent_base import AgentBase
from workflows.core.planner_agent import PlannerAgent
from workflows.core.researcher_agent import ResearcherAgent
from workflows.core.strategist_agent import StrategistAgent
from workflows.core.writer_agent import WriterAgent
from workflows.core.feedback_agent import FeedbackAgent
import networkx as nx
import logging
from datetime import datetime


logger = logging.getLogger(__name__)

class ContentMarketingWorkflow:
    def __init__(self):
        """
        Initialize the workflow with all agents and their connections.
        """
        self.agents = {
            'planner': PlannerAgent(name='planner_agent', initial_state={}),
            'researcher': ResearcherAgent(name='researcher_agent', initial_state={}),
            'strategist': StrategistAgent(name='strategist_agent', initial_state={}),
            'writer': WriterAgent(name='writer_agent', initial_state={}),
            'feedback': FeedbackAgent(name='feedback_agent', initial_state={})
        }

        # Set up router callback
        for agent in self.agents.values():
            agent.router = self._route_message

        self.graph = self._build_workflow_graph()
        
    def _build_workflow_graph(self) -> nx.DiGraph:
        """
        Build the directed graph representing the workflow.
        
        Returns:
            nx.DiGraph: Workflow graph
        """
        graph = nx.DiGraph()
        
        # Add nodes
        for agent_name in self.agents:
            graph.add_node(agent_name, agent=self.agents[agent_name])
        
        # Add edges representing message flow
        edges = [
            ('planner', 'researcher'),
            ('researcher', 'strategist'),
            ('strategist', 'writer'),
            ('writer', 'feedback'),
            ('feedback', 'planner')
        ]
        
        graph.add_edges_from(edges)
        return graph

    def start_workflow(self, campaign_goal: str) -> Dict:
        """
        Start the workflow with a campaign goal.
        
        Args:
            campaign_goal (str): The marketing campaign goal
            
        Returns:
            Dict: Initial workflow state
        """
        logger.info(f"Starting workflow for goal: {campaign_goal}")
        
        # Initialize planner with campaign goal
        planner = self.agents['planner']
        initial_task = {
            'type': 'goal',
            'content': campaign_goal
        }
        
        # Send to planner
        planner.receive_message('user', {'type': 'task', 'content': initial_task})
        self.process_message('planner', {'type': 'task', 'content': initial_task})
        
        strategist = self.agents['strategist']
        strategy = getattr(strategist, 'latest_result')
        tweets = getattr(self.agents.get('writer'), 'latest_tweets', [])
        if not tweets:
            tweets = ["No tweets generated yet."]
        return {
        'status': 'success',
        'strategy': strategy or "No strategy generated yet.",
        'tweets': tweets
    }

    def get_workflow_state(self) -> Dict:
        """
        Get the current state of the workflow.
        
        Returns:
            Dict: Current workflow state
        """
        state = {}
        for agent_name, agent in self.agents.items():
            state[agent_name] = {
                'status': agent.get_state(),
                'event_log': agent.event_log[-5:]  # Last 5 events
            }
        return state

    def handle_feedback(self, feedback: Dict) -> None:
        """
        Handle feedback from user and adjust workflow.
        
        Args:
            feedback (Dict): User feedback data
        """
        feedback_agent = self.agents['feedback']
        feedback_agent.receive_message('user', {
            'type': 'feedback',
            'content': feedback
        })

    def _route_message(self, sender: str, recipient: str, message: Dict) -> None:
        """
        Route a message from one agent to another explicitly.
        
        Args:
            sender (str): Name of the sending agent
            recipient (str): Name of the receiving agent
            message (Dict): Message to deliver
        """
        if recipient not in self.graph.nodes:
            logger.error(f"Unknown recipient: {recipient}")
            return

        target_agent = self.graph.nodes[recipient]['agent']
        logger.info(f"[ROUTING] {sender} -> {recipient} with: {message}")
        target_agent.receive_message(sender, message)


    def process_message(self, sender: str, message: Dict) -> None:
        """
        Process and route a message through the workflow.
        
        Args:
            sender (str): Name of sending agent
            message (Dict): Message to process
        """
        logger.info(f"Processing message from {sender}")
        self._log_message(sender, message)
        # Determine recipient based on your workflow graph
        # For example, get the first neighbor of sender
        neighbors = list(self.graph.successors(sender))
        if not neighbors:
            logger.error(f"No recipient found for sender: {sender}")
            return
        recipient = neighbors[0]
        self._route_message(sender, recipient, message)

    def _log_message(self, sender: str, message: Dict) -> None:
        """
        Log a message for debugging purposes.
        
        Args:
            sender (str): Name of sending agent
            message (Dict): Message to log
        """
        logger.debug({
            'timestamp': datetime.now().isoformat(),
            'sender': sender,
            'message_type': message.get('type'),
            'content_summary': str(message.get('content', ''))[:100]
        })

    def get_strategy_result(self) -> Dict:
        strategist = self.agents.get("strategist")
        return strategist.latest_result or {}


if __name__ == "__main__":
    # Example usage
    workflow = ContentMarketingWorkflow()
    result = workflow.start_workflow("Launch Twitter campaign for new product")
    print(f"Workflow started: {result}")
    print(f"Current state: {workflow.get_workflow_state()}")
    