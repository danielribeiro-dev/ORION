"""
Base Router Interface.

Define o contrato para implementações de Router.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseRouter(ABC):
    """Contrato abstrato para o Router."""

    @abstractmethod
    def route(self, input_data: str) -> Dict[str, Any]:
        """
        Define a rota de execução baseada na entrada.
        """
        pass
