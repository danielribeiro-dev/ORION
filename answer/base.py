"""
Base Answer Pipeline Interface.

Define o contrato para implementações de Answer Pipeline.
"""

from abc import ABC, abstractmethod
from typing import Any

class BaseAnswerPipeline(ABC):
    """Contrato abstrato para o Answer Pipeline."""

    @abstractmethod
    def process(self, result: Any) -> str:
        """
        Processa o resultado e gera a resposta final.
        """
        pass
