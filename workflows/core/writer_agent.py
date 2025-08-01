"""
WriterAgent class that generates written content based on strategy and instructions.
"""
from typing import Dict
from .agent_base import AgentBase

class WriterAgent(AgentBase):
    def __init__(self, name: str, initial_state: dict, context: dict = None):
        super().__init__(name, initial_state, context)
        self.content_types = {
            'tweet': {
                'max_length': 280,
                'format': 'text',
                'required_fields': ['text', 'hashtags']
            },
            'blog_post': {
                'min_length': 1000,
                'format': 'markdown',
                'required_fields': ['title', 'content', 'meta_description']
            }
        }

    def generate_content(self, strategy: Dict, content_type: str) -> Dict:
        """
        Generate content based on strategy and type.
        
        Args:
            strategy (Dict): Strategy to follow
            content_type (str): Type of content to generate
            
        Returns:
            Dict: Generated content
        """
        content_spec = self.content_types.get(content_type, {})
        
        # Placeholder for actual content generation
        generated_content = {
            'type': content_type,
            'content': "[Generated content based on strategy will go here]",
            'strategy_used': strategy,
            'status': 'draft'
        }
        
        return generated_content

    def act(self, task: dict) -> dict:
        """
        Process incoming tasks and generate content.
        
        Args:
            task (dict): Task to process
            
        Returns:
            dict: Generated content
        """
        if task.get('type') == 'content_request':
            strategy = task.get('strategy', {})
            content_type = task.get('content_type', 'tweet')
            
            content = self.generate_content(strategy, content_type)
            
            # Send content back to planner
            self.send_message('planner', {
                'type': 'task_result',
                'content': content
            })
            
            return {'status': 'success', 'message': 'Content generated'}
        
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
            self.log_event('content_generated', {
                'type': message['content'].get('content_type', ''),
                'sender': sender
            })
