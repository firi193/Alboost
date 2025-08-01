# core/agent_base.py

from abc import ABC, abstractmethod
from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv() 

class AgentBase(ABC):
    def __init__(self, name: str, initial_state: dict, context: dict = None):
        self.name = name
        self.state = initial_state
        self.context = context or {}
        self.event_log = []

        # 🧠 Set up OpenAI client (ensure OPENAI_API_KEY is set in your env)
        self.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY_"))

    def log_event(self, event: str, details: dict = None):
        self.event_log.append({
            "event": event,
            "details": details or {}
        })

    @abstractmethod
    def receive_message(self, sender: str, message: dict):
        pass

    def send_message(self, recipient: str, message: dict):
        if self.router:
            self.router(self.name, recipient, message)
        else:
            print(f"[{self.name}] No router defined for sending message to {recipient}")

    def get_state(self):
        return self.state
