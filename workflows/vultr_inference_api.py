"""
Client for interacting with Vultr-hosted LLM inference endpoints.
"""

import requests
import logging
import time
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class VultrLLMClient:
    def __init__(self, api_url: str, api_key: str):
        """
        Initialize the Vultr LLM client.
        
        Args:
            api_url (str): Base URL of the Vultr inference endpoint
            api_key (str): API key for authentication
        """
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def query_model(self, prompt: str, model: str = 'mixtral-8x7b', **kwargs) -> Dict:
        """
        Send a prompt to the Vultr-hosted LLM model.
        
        Args:
            prompt (str): The prompt to send to the model
            model (str): Model name to use (default: mixtral-8x7b)
            **kwargs: Additional parameters for the model
            
        Returns:
            Dict: Model response
        
        Raises:
            requests.RequestException: If the request fails
        """
        try:
            payload = {
                'model': model,
                'prompt': prompt,
                'max_tokens': kwargs.get('max_tokens', 2048),
                'temperature': kwargs.get('temperature', 0.7),
                'top_p': kwargs.get('top_p', 0.95),
                **kwargs
            }
            
            response = requests.post(
                f"{self.api_url}/v1/inference",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error querying model: {str(e)}")
            raise
            
    def generate_content(self, prompt: str, context: Dict = None) -> str:
        """
        Generate content using the model with optional context.
        
        Args:
            prompt (str): The prompt to generate content from
            context (Dict): Additional context for the generation
            
        Returns:
            str: Generated content
        """
        if context:
            prompt = self._format_prompt_with_context(prompt, context)
            
        response = self.query_model(prompt)
        return response.get('content', '')
        
    def _format_prompt_with_context(self, prompt: str, context: Dict) -> str:
        """
        Format a prompt with additional context.
        
        Args:
            prompt (str): Base prompt
            context (Dict): Context data
            
        Returns:
            str: Formatted prompt
        """
        context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
        return f"Context:\n{context_str}\n\nPrompt:\n{prompt}"

if __name__ == "__main__":
    # Example usage
    client = VultrLLMClient(
        api_url="https://your-vultr-api-endpoint.com",
        api_key="your-api-key"
    )
    
    prompt = "Write a tweet about AI marketing benefits"
    try:
        response = client.generate_content(prompt)
        print(f"Generated content: {response}")
    except Exception as e:
        print(f"Error: {str(e)}")