"""
Base Memory Interface.

Contrato para módulos de memória.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseMemory(ABC):
    """Contrato abstrato para Memória."""

    @abstractmethod
    def load(self) -> None:
        """Carrega dados da persistência."""
        pass

    @abstractmethod
    def save(self) -> None:
        """Salva dados na persistência."""
        pass
