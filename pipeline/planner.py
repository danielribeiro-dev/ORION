"""
Planner Module.

Responsabilidade:
    - Transformar uma intenção (Intent) em um plano de execução detalhado.
    - Definir a ordem de chamadas de ferramentas/plugins.

Proibições:
    - Não executa as ações planejadas.
    - Não interage com o usuário.
"""

from typing import Any, Dict, List
from core.interfaces import BasePlanner

class Planner(BasePlanner):
    """
    Gera planos de execução baseados em intenções roteadas.
    """

    def __init__(self) -> None:
        """Inicializa o Planner."""
        pass

    def plan(self, intent: Dict[str, Any]) -> List[Any]:
        """
        Cria uma lista de passos (Action Plan) a partir da intenção.
        """
        intent_type = intent.get("intent")
        user_input = intent.get("user_input", "") # Router must pass this!
        
        # Simple Mapping Strategy (Phase 3)
        context = intent.get("metadata", {}).get("context", [])
        
        if intent_type in ("CHAT", "HELP"):
            return [("chat", {"user_input": user_input, "context": context})]
            
        if intent_type == "WEB":
            return [("web", {"user_input": user_input})]
            
        if intent_type == "FILESYSTEM":
             return [("fs", {"user_input": user_input})]
             
        if intent_type == "MEMORY":
            metadata = intent.get("metadata", {})
            action = metadata.get("action")
            value = metadata.get("value")
            
            if action in ("set_system_name", "set_user_name"):
                return [("memory", {"user_input": user_input, "action": action, "value": value})]
            
            # Default to chat for memory retrieval/queries
            return [("chat", {"user_input": user_input, "context": context})]

        return []
