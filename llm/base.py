"""
Base LLM Adapter Interface.

Define o contrato para adaptadores de LLM.
"""

from abc import ABC, abstractmethod

class BaseLLMAdapter(ABC):
    """Contrato abstrato para Adaptadores de LLM."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Gera texto a partir de um prompt.
        """
        pass
