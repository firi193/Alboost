"""
StrategistAgent class that generates marketing strategies based on goals and research.
"""
from typing import Dict, List
from .agent_base import AgentBase
from .performance_analyzer import analyze_performance
from .kpi_normalizer import normalize_post
import json
from datetime import datetime, timedelta

class StrategistAgent(AgentBase):
    def __init__(self, name: str, initial_state: dict, context: dict = None):
        super().__init__(name, initial_state, context)
        self.strategy_templates = {
            'social_media': {
                'platforms': ['Twitter', 'Instagram', 'LinkedIn'],
                'content_types': ['videos', 'images', 'text posts'],
                'frequency': '2-3 posts per day'
            },
            'blog': {
                'length': '1000-1500 words',
                'structure': ['Introduction', 'Main Content', 'Call to Action'],
                'seo_keywords': []
            }
        }
        self.latest_result = None  # Store the latest generated strategy

    def generate_strategy(self, goal: str, research_data: Dict) -> Dict:
        """
        Generate a marketing strategy based on goal and research.
        
        Args:
            goal (str): Marketing goal
            research_data (Dict): Research findings
            
        Returns:
            Dict: Generated strategy
        """
        strategy = {
            'goal': goal,
            'research_summary': research_data.get('summary', ''),
            'key_findings': research_data.get('key_points', []),
            'recommended_actions': [],
            'timeline': {}
        }

        # Add platform-specific recommendations
        if 'social_media' in goal.lower():
            strategy.update(self.strategy_templates['social_media'])
        
        return strategy

    def act(self, task: dict) -> dict:
        """
        Process incoming tasks and generate strategies.
        
        Args:
            task (dict): Task to process
            
        Returns:
            dict: Generated strategy
        """
        if task.get('type') == 'strategy_request':
            research_data = task.get('research_data', {})
            strategy = self.generate_strategy(task['goal'], research_data)
            
            # Send strategy back to planner
            self.send_message('planner', {
                'type': 'task_result',
                'content': strategy
            })

            self.latest_result = strategy
            
            return {'status': 'success', 'message': 'Strategy generated'}
        
        return {'status': 'error', 'message': 'Invalid task type'}

    def receive_message(self, sender: str, message: dict) -> None:
        """
        Handle incoming messages and update state.
        
        Args:
            sender (str): Name of the sending agent
            message (dict): Received message
        """
        if message.get('type') == 'task':
            self.act(message['content'])
            self.log_event('strategy_generated', {
                'goal': message['content'].get('goal', ''),
                'sender': sender
            })
