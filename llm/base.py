"""
LLM Base Adapter Interface.

v0.4.0: Unificado base.py + base_adapter.py em um único módulo (M-09).
        Assinatura de generate() corrigida para retornar LLMResult (não str).
"""

from abc import ABC, abstractmethod
from core.contracts import LLMResult


class BaseLLMAdapter(ABC):
    """
    Contrato abstrato para Adaptadores de LLM.

    Todos os adapters (Groq, Ollama, etc.) devem herdar desta classe
    e implementar generate() retornando um LLMResult estruturado.
    """

    @abstractmethod
    def generate(self, prompt: str) -> LLMResult:
        """
        Gera texto a partir de um prompt.

        Args:
            prompt: Texto de entrada para o modelo.

        Returns:
            LLMResult com texto gerado, provedor, modelo e status degraded.

        Raises:
            Exception: Se a geração falhar (permite fallback no LLMService).
        """
        pass
