"""
PROJECT NOVA - Base LLM Adapter (Model Socket)
==============================================
This module defines the abstract interface for language models in NOVA.

IMPORTANT FOR YOUR FUTURE CUSTOM LLM:
-------------------------------------
When you train your own proprietary PyTorch / transformer LLM later:
1. You DO NOT change any code in the router, search, or verification engine.
2. You simply create a new adapter (e.g. `models/proprietary_adapter.py`)
   that inherits from `BaseLLMAdapter` and implements these methods.
3. Plug it into NOVA, and your custom model immediately drives the entire system.
"""

from abc import ABC, abstractmethod
from typing import Generator, List, Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseLLMAdapter(ABC):
    """
    Abstract interface for LLM inference in Project NOVA.
    Both Ollama and your future custom model must implement this interface.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        """
        Generate a complete text response for a given prompt.
        """
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
    ) -> T:
        """
        Generate a strictly structured response validated against a Pydantic schema.
        Critical for routing decisions and fact verification.
        """
        pass

    @abstractmethod
    def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> Generator[str, None, None]:
        """
        Stream response tokens chunk-by-chunk for live UI rendering.
        """
        pass

    @abstractmethod
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate dense vector embeddings for semantic document search.
        """
        pass

