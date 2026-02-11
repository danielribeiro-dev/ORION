"""
Base Executor Interface.

Define o contrato para implementações de Executor.
"""

from abc import ABC, abstractmethod
from typing import Any, List

class BaseExecutor(ABC):
    """Contrato abstrato para o Executor."""

    @abstractmethod
    def execute(self, plan: List[Any]) -> Any:
        """
        Executa um plano de ações.
        """
        pass
