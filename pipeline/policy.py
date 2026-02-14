"""
Capability Guard Policy.

Responsabilidade:
    - Interceptar ações antes da execução.
    - Validar se a ação é permitida pelas políticas de segurança.
    - Bloquear ações não autorizadas.

Proibições:
    - Não executa a ação.
    - Não altera a ação (apenas aprova ou reprova).
"""

from core.interfaces import BasePolicy

class CapabilityGuard(BasePolicy):
    """
    Guarda de segurança para validação de capacidades e ações.
    """

    def __init__(self) -> None:
        """Inicializa o CapabilityGuard."""
        pass

    def validate(self, action: str) -> bool:
        """
        Verifica se uma ação (intent) é permitida.
        
        Policy:
        - CHAT, HELP, MEMORY: Always Allow.
        - WEB: Allow (Future: check connect).
        - FILESYSTEM: Block (High Privilege).
        """
        allowed = ["CHAT", "HELP", "WEB", "MEMORY", "FILESYSTEM"]
        blocked = []
        
        if action in allowed:
            return True
            
        if action in blocked:
            return False
            
        # Default to Block for unknown intents
        return False
