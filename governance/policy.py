"""
Governance Engine (Policy Enforcement).

Responsabilidade:
    - Validar se a ação é permitida baseada na Role do usuário e Nível de Risco.
    - Aplicar Regra Mestra: Nível 2 exige confirmação ou permissão explícita.

Movido de pipeline/policy.py → governance/policy.py (v0.4.0 reestruturação).
"""

from typing import Optional
from core.interfaces import BasePolicy
from core.contracts import ActionLevel
from governance.auth import User, Role      # atualizado: core.auth → governance.auth
from governance.audit import AuditLogger   # atualizado: core.audit → governance.audit


class GovernanceEngine(BasePolicy):
    """
    Motor de Governança e Segurança.
    """

    def validate(
        self,
        action: str,
        user: Optional[User] = None,
        level: ActionLevel = ActionLevel.LEVEL_0
    ) -> bool:
        """
        Valida se uma ação é permitida.

        Args:
            action: Nome da Intent ou Ação.
            user: Usuário solicitante (Obrigatório para L1/L2).
            level: Nível de Risco da Ação.

        Returns:
            bool: True se permitido, False se bloqueado.
        """
        reason = "Permitido por política padrão"
        allowed = True

        # 1. Nível 0 (Conversacional) — Sempre Permitido
        if level == ActionLevel.LEVEL_0:
            allowed = True
            reason = "Ação L0 sempre permitida"

        # 2. Nível 1 (Consulta) — Requer Autenticação
        elif level == ActionLevel.LEVEL_1:
            if not user:
                allowed = False
                reason = "Autenticação necessária para L1"
            else:
                allowed = True
                reason = "L1 permitido para usuário autenticado"

        # 3. Nível 2 (Modificação) — Requer Privilégio
        elif level == ActionLevel.LEVEL_2:
            if not user:
                allowed = False
                reason = "Autenticação necessária para L2"
            elif user.role == Role.GUEST.value:
                allowed = False
                reason = "Guest não pode executar ações L2"
            elif user.role in [Role.ADMIN.value, Role.POWER_USER.value]:
                allowed = True
                reason = f"{user.role} autorizado para L2"
            elif user.role == Role.USER.value:
                # USER pode executar L2 com supervisão (confirmação no Executor)
                allowed = True
                reason = "Usuário autorizado para L2 (confirmação obrigatória)"
            else:
                allowed = False
                reason = "Role não autorizada para L2"

        # Auditoria
        if user:
            AuditLogger.log_action(user, action, level, allowed, reason)

        return allowed
