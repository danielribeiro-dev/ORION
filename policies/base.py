"""
Base Policy Interface.

Define o contrato para implementações de Policy Enforcement.
"""

from abc import ABC, abstractmethod

class BasePolicy(ABC):
    """Contrato abstrato para Políticas."""

    @abstractmethod
    def validate(self, action: str) -> bool:
        """
        Valida se uma ação é permitida.
        """
        pass
