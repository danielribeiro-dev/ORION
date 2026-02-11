"""
Base Plugin Interface.

Define o contrato para todos os plugins do sistema.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

class BasePlugin(ABC):
    """Contrato abstrato para Plugins."""

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any:
        """
        Executa a funcionalidade do plugin.
        """
        pass
