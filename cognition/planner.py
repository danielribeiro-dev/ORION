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

import json
from typing import Any, Dict, List, Union
from core.interfaces import BasePlanner
from core.contracts import RouterResult
from core.logger import logger


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

        if intent_type in ("AUTOMATION", "FILESYSTEM"):
            return self._plan_automation(user_input, context)

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

        if intent_type == "MEMORY_RECALL":
             # Repassa o resgate extraído pelo RouterResult pra o Plugin Vetorial.
             query_to_search = metadata.get("query") if metadata.get("query") else user_input
             return [("memory_search", {"query": query_to_search})]

        # Intent desconhecido → CHAT por segurança
        return [("chat", {"user_input": user_input, "context": context})]

    def _plan_automation(self, user_input: str, context: List[Dict]) -> List[Any]:
        """Usa o LLM para quebrar o pedido em múltiplos passos de execução."""
        from core.container import Container
        container = Container.get_instance()
        
        prompt = (
            "You are the ORION Planner.\n"
            "The user asked for a multi-step automation. Break it down into a chronological JSON list of steps.\n"
            "Available Plugins: \n"
            " - 'web' (for searching internet. Params: 'user_input' inside params). CRITICAL: Do NOT send the whole user's phrase to the web plugin, extract ONLY the core subject/keywords optimized for DuckDuckGo. E.g. If user asks 'pesquise melhores opções de Notebook no mercado hoje e salve', send ONLY 'melhores opções de Notebook mercado hoje' to 'web'.\n"
            " - 'fs' (for file operations. Params: 'action' [read|write|list|edit|delete|move], 'filename', 'filenames' (array of exact names, if action is delete or move), 'destination' (if action is move), 'content' (if action is write), 'llm_instruction' (if you want the FS module to formulate/summarize 'content' before saving), 'instruction' (if editing)).\n"
            "You can forward the results from a previous step to the next by using the exact string '{{previous_result}}' in the 'content' or 'instruction' fields.\n"
            "If the user asks to save 'a summary' or 'the results' to a file, YOU MUST add 'llm_instruction' to the 'fs' params explaining how it should summarize the 'content' (e.g. 'Crie um resumo claro em português dos dados extraídos da web').\n"
            "Return ONLY a valid JSON array of objects. Example:\n"
            "[\n"
            "  {\"plugin\": \"web\", \"params\": {\"user_input\": \"best notebook options 2026\"}},\n"
            "  {\"plugin\": \"fs\", \"params\": {\"action\": \"write\", \"filename\": \"result.md\", \"content\": \"Context:\\n{{previous_result}}\", \"llm_instruction\": \"Write a summary in portuguese about the context.\"}}\n"
            "]\n\n"
            f"User request: {user_input}\n"
        )
        
        try:
            llm_res = container.llm_service.generate(prompt)
            # Limpa blockticks caso existam
            cleaned = llm_res.text.strip().replace("```json", "").replace("```", "").strip()
            plan_data = json.loads(cleaned)
            
            plan = []
            for step in plan_data:
                plugin = step.get("plugin")
                params = step.get("params", {})
                if plugin:
                    plan.append((plugin, params))
                    
            if not plan:
                return [("chat", {"user_input": "Falha ao gerar o plano de automação (vazio)."})]
                
            return plan
        except Exception as e:
            logger.error(f"[Planner] Erro ao planejar automação: {e}")
            return [("chat", {"user_input": "Erro interno ao processar plano de automação."})]
