"""
Governance Engine (Policy Enforcement).

Responsabilidade:
    - Validar se a ação é permitida baseada na Role do usuário e Nível de Risco.
    - Aplicar Regra Mestra: Nível 2 exige confirmação ou permissão explícita.
"""

from typing import Optional
from core.interfaces import BasePolicy
from core.contracts import ActionLevel
from core.auth import User, Role
from core.audit import AuditLogger

class GovernanceEngine(BasePolicy):
    """
    Motor de Governança e Segurança.
    Substitui o antigo CapabilityGuard.
    """

    def validate(self, action: str, user: Optional[User] = None, level: ActionLevel = ActionLevel.LEVEL_0) -> bool:
        """
        Valida se uma ação é permitida.
        
        Args:
            action: Nome da Intent ou Ação.
            user: Usuário solicitante (Obrigatório para L1/L2).
            level: Nível de Risco da Ação.
            
        Returns:
            bool: True se permitido, False se bloqueado.
        """
        reason = "Allowed by default policy"
        allowed = True
        
        # 1. Regra de Nível 0 (Conversacional) - Sempre Permitido
        if level == ActionLevel.LEVEL_0:
            allowed = True
            reason = "L0 action always allowed"
            
        # 2. Regra de Nível 1 (Consulta) - Requer Autenticação (Guest limit)
        elif level == ActionLevel.LEVEL_1:
            if not user:
                allowed = False
                reason = "Authentication required for L1"
            else:
                allowed = True
                reason = "L1 allowed for authenticated user"

        # 3. Regra de Nível 2 (Modificação) - Requer Privilégio
        elif level == ActionLevel.LEVEL_2:
            if not user:
                allowed = False
                reason = "Authentication required for L2"
            elif user.role == Role.GUEST.value:
                allowed = False
                reason = "Guest cannot perform L2 actions"
            elif user.role in [Role.ADMIN.value, Role.POWER_USER.value]:
                allowed = True
                reason = f"{user.role} authorized for L2"
            elif user.role == Role.USER.value:
                # Users precisam de aprovação explícita (tratado no Executor)
                # Aqui dizemos que é "Permitido sob supervisão"
                allowed = True 
                reason = "User authorized for L2 (Supervisor Check required)"
            else:
                allowed = False
                reason = "Role not authorized for L2"

        # Auditoria (Se user existir)
        if user:
            AuditLogger.log_action(user, action, level, allowed, reason)
            
        return allowed
