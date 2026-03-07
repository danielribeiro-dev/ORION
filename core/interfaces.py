"""
Core Interfaces Module.

Consolida todos os contratos abstratos (ABCs) do sistema.

v0.4.0: Corrigida assinatura de BasePolicy.validate() para refletir
        a implementação real do GovernanceEngine (BUG-03 / LSP fix).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from core.contracts import ActionLevel


class BaseRouter(ABC):
    """Contrato abstrato para o Router."""

    @abstractmethod
    def route(self, input_data: str, context: List[Dict] = None) -> Any:
        """
        Define a rota de execução baseada na entrada.
        Retorna RouterResult.
        """
        pass


class BasePlanner(ABC):
    """Contrato abstrato para o Planner."""

    @abstractmethod
    def plan(self, intent: Any) -> List[Any]:
        """
        Gera um plano de execução a partir de uma intenção (RouterResult ou Dict).
        """
        pass


class BaseExecutor(ABC):
    """Contrato abstrato para o Executor."""

    @abstractmethod
    def execute(self, plan: List[Any]) -> Any:
        """
        Executa um plano de ações. Retorna PluginResult.
        """
        pass


class BaseAnswerPipeline(ABC):
    """Contrato abstrato para o Answer Pipeline."""

    @abstractmethod
    def process(self, result: Any) -> str:
        """
        Processa o resultado e gera a resposta final ao usuário.
        """
        pass


class BasePolicy(ABC):
    """
    Contrato abstrato para Políticas de Governança.

    v0.4.0: Assinatura corrigida para incluir 'user' e 'level',
    refletindo o que GovernanceEngine realmente implementa.
    Isso resolve a violação de LSP (BUG-03).
    """

    @abstractmethod
    def validate(
        self,
        action: str,
        user: Optional[Any] = None,
        level: ActionLevel = ActionLevel.LEVEL_0
    ) -> bool:
        """
        Valida se uma ação é permitida.

        Args:
            action: Nome da intent ou ação.
            user: Usuário solicitante (User dataclass ou None para guest).
            level: Nível de risco da ação (ActionLevel enum).

        Returns:
            True se permitido, False se bloqueado.
        """
        pass
