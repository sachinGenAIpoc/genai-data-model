from abc import ABC, abstractmethod
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.3
        )
    
    @abstractmethod
    async def process(self, data: Dict[str, Any] = None) -> Dict[str, Any]:
        pass
