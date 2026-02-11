"""
Base Planner Interface.

Define o contrato para implementações de Planner.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BasePlanner(ABC):
    """Contrato abstrato para o Planner."""

    @abstractmethod
    def plan(self, intent: Dict[str, Any]) -> List[Any]:
        """
        Gera um plano de execução a partir de uma intenção.
        """
        pass
