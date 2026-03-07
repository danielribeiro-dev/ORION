"""
Planner Module.

Responsabilidade:
    - Transformar uma intenção (RouterResult) em um plano de execução detalhado.
    - Definir a ordem de chamadas de ferramentas/plugins.

v0.4.0: Aceita RouterResult (contrato formal) além de Dict (duck typing).
        A extração de action/value para intent MEMORY já vem do LLM via metadata
        do RouterResult — garantido pelo prompt em prompts.py.

Proibições:
    - Não executa as ações planejadas.
    - Não interage com o usuário.
"""

from typing import Any, Dict, List, Union
from core.interfaces import BasePlanner
from core.contracts import RouterResult


class Planner(BasePlanner):
    """
    Gera planos de execução baseados em intenções roteadas.
    """

    def __init__(self) -> None:
        pass

    def plan(self, intent: Union[RouterResult, Dict[str, Any]]) -> List[Any]:
        """
        Cria uma lista de passos (Action Plan) a partir do RouterResult ou Dict.

        v0.4.0: Suporta RouterResult diretamente, com acesso via atributos.
        """
        # Suporte a RouterResult (v0.4.0) e Dict (retrocompatibilidade)
        if isinstance(intent, RouterResult):
            intent_type = intent.intent
            user_input = intent.user_input
            context = intent.metadata.get("context", [])
            metadata = intent.metadata
        else:
            # Fallback para Dict (caso algum caminho ainda use dict)
            intent_type = intent.get("intent")
            user_input = intent.get("user_input", "")
            context = intent.get("metadata", {}).get("context", [])
            metadata = intent.get("metadata", {})

        # --- Mapeamento de Intent → Plano ---

        if intent_type in ("CHAT", "HELP"):
            return [("chat", {"user_input": user_input, "context": context})]

        if intent_type == "SYSTEM":
            return [("system", {"user_input": user_input, "intent": intent_type, "metadata": metadata})]

        if intent_type == "WEB":
            return [("web", {"user_input": user_input})]

        if intent_type == "FILESYSTEM":
            return [("fs", {"user_input": user_input})]

        if intent_type == "MEMORY":
            # action e value já vêm extraídos do LLM via metadata (ver prompts.py)
            action = metadata.get("action")
            value = metadata.get("value")

            if action in ("set_system_name", "set_user_name", "set_system_language"):
                return [("memory", {
                    "user_input": user_input,
                    "action": action,
                    "value": value
                })]

            # MEMORY sem action clara → responder via chat
            return [("chat", {"user_input": user_input, "context": context})]

        # Intent desconhecido → CHAT por segurança
        return [("chat", {"user_input": user_input, "context": context})]
