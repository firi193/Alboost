"""
PlannerAgent class that extends AgentBase to manage and coordinate tasks.
"""
from typing import List, Dict
from .agent_base import AgentBase
import json

class PlannerAgent(AgentBase):
    def __init__(self, name: str, initial_state: dict, context: dict = None):
        super().__init__(name, initial_state, context)
        self.task_queue = []
        self.completed_tasks = []

    def breakdown_goal(self, goal: str) -> List[Dict]:
        """
        Break down a goal into subtasks.
        
        Args:
            goal (str): Main goal to break down
            
        Returns:
            List[Dict]: List of subtasks
        """
        subtasks = [
            {
                'type': 'research',
                'description': f'Research best practices for {goal}',
                'priority': 1
            },
            {
                'type': 'strategy',
                'description': f'Develop strategy for {goal}',
                'priority': 2
            },
            {
                'type': 'content_creation',
                'description': f'Create content for {goal}',
                'priority': 3
            }
        ]
        return subtasks

    def dispatch_task(self, task: Dict, agent_name: str) -> None:
        """
        Send a task to the appropriate agent.
        
        Args:
            task (Dict): Task to dispatch
            agent_name (str): Name of the target agent
        """
        message = {
            'type': 'task',
            'content': task,
            'sender': self.name
        }
        self.send_message(agent_name, message)

    def act(self, task: dict) -> dict:
        """
        Handle incoming tasks and coordinate workflow.
        
        Args:
            task (dict): Task to process
            
        Returns:
            dict: Result of the action
        """
        if task.get('type') == 'goal':
            # Break down goal into subtasks
            subtasks = self.breakdown_goal(task['content'])
            self.task_queue.extend(subtasks)
            
            # Dispatch first task
            if self.task_queue:
                first_task = self.task_queue.pop(0)
                agent_name = self._get_appropriate_agent(first_task['type'])
                self.dispatch_task(first_task, agent_name)
                
            return {'status': 'success', 'message': 'Goal breakdown initiated'}
        
        return {'status': 'error', 'message': 'Unknown task type'}

    def receive_message(self, sender: str, message: dict) -> None:
        """
        Handle incoming messages and update state.
        
        Args:
            sender (str): Name of the sending agent
            message (dict): Received message
        """
        if message.get('type') == 'task_result':
            self.completed_tasks.append(message['content'])
            
            # Check if there are more tasks to dispatch
            if self.task_queue:
                next_task = self.task_queue.pop(0)
                agent_name = self._get_appropriate_agent(next_task['type'])
                self.dispatch_task(next_task, agent_name)
            
            self.log_event('task_completed', {
                'task': message['content'],
                'sender': sender
            })

    def _get_appropriate_agent(self, task_type: str) -> str:
        """
        Get the appropriate agent for a given task type.
        
        Args:
            task_type (str): Type of task
            
        Returns:
            str: Name of appropriate agent
        """
        agent_map = {
            'research': 'researcher_agent',
            'strategy': 'strategist_agent',
            'content_creation': 'writer_agent'
        }
        return agent_map.get(task_type, 'default_agent')
