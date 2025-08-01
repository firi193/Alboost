"""
FeedbackAgent class that collects user feedback and adjusts agent behavior.
"""
from typing import Dict
from .agent_base import AgentBase
import json

class FeedbackAgent(AgentBase):
    def __init__(self, name: str, initial_state: dict, context: dict = None):
        super().__init__(name, initial_state, context)
        self.feedback_config = {
            'sensitivity': 0.5,
            'learning_rate': 0.1,
            'current_behavior': {},
            'desired_behavior': {}
        }

    def process_feedback(self, feedback: Dict) -> Dict:
        """
        Process user feedback and adjust behavior.
        
        Args:
            feedback (Dict): User feedback data
            
        Returns:
            Dict: Updated behavior configuration
        """
        # Update behavior based on feedback
        if feedback.get('type') == 'positive':
            self.feedback_config['sensitivity'] = min(1.0, self.feedback_config['sensitivity'] + self.feedback_config['learning_rate'])
        elif feedback.get('type') == 'negative':
            self.feedback_config['sensitivity'] = max(0.0, self.feedback_config['sensitivity'] - self.feedback_config['learning_rate'])
            
        return self.feedback_config

    def act(self, task: dict) -> dict:
        """
        Process incoming feedback tasks.
        
        Args:
            task (dict): Task to process
            
        Returns:
            dict: Updated configuration
        """
        if task.get('type') == 'feedback':
            feedback = task.get('content', {})
            updated_config = self.process_feedback(feedback)
            
            # Broadcast updated configuration
            self.send_message('all_agents', {
                'type': 'config_update',
                'content': updated_config
            })
            
            return {'status': 'success', 'message': 'Feedback processed'}
        
        return {'status': 'error', 'message': 'Invalid task type'}

    def receive_message(self, sender: str, message: dict) -> None:
        """
        Handle incoming messages and update state.
        
        Args:
            sender (str): Name of the sending agent
            message (dict): Received message
        """
        if message.get('type') == 'feedback':
            self.act(message['content'])
            self.log_event('feedback_processed', {
                'feedback_type': message['content'].get('type', ''),
                'sender': sender
            })
        elif message.get('type') == 'config_update':
            self.feedback_config.update(message['content'])
            self.log_event('config_updated', {
                'new_config': message['content'],
                'sender': sender
            })
