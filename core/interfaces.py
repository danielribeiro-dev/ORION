"""
Core Interfaces Module.

Consolida todos os contratos abstratos (ABCs) do sistema.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseRouter(ABC):
    """Contrato abstrato para o Router."""

    @abstractmethod
    def route(self, input_data: str, context: List[Dict] = None) -> Dict[str, Any]:
        """
        Define a rota de execução baseada na entrada.
        """
        pass

class BasePlanner(ABC):
    """Contrato abstrato para o Planner."""

    @abstractmethod
    def plan(self, intent: Dict[str, Any]) -> List[Any]:
        """
        Gera um plano de execução a partir de uma intenção.
        """
        pass

class BaseExecutor(ABC):
    """Contrato abstrato para o Executor."""

    @abstractmethod
    def execute(self, plan: List[Any]) -> Any:
        """
        Executa um plano de ações.
        """
        pass

class BaseAnswerPipeline(ABC):
    """Contrato abstrato para o Answer Pipeline."""

    @abstractmethod
    def process(self, result: Any) -> str:
        """
        Processa o resultado e gera a resposta final.
        """
        pass

class BasePolicy(ABC):
    """Contrato abstrato para Políticas."""

    @abstractmethod
    def validate(self, action: str) -> bool:
        """
        Valida se uma ação é permitida.
        """
        pass
