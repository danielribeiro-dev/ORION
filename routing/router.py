"""
Router Module.

Responsabilidade:
    - Analisar a entrada do usuário.
    - Determinar a intenção (Intent).
    - Decidir o caminho de execução (Plugin, LLM, etc.).

Proibições:
    - Não executa ações.
    - Não gera respostas finais ao usuário.
"""

from typing import Any, Dict
from routing.base import BaseRouter

import json
from typing import Any, Dict
from routing.base import BaseRouter
from routing.prompts import INTENT_CLASSIFICATION_SYSTEM_PROMPT
from infra.logger import logger

class Router(BaseRouter):
    """
    Componente responsável por rotear a intenção do usuário para o executor correto.
    Usa LLM para classificar a intenção.
    """

    def __init__(self) -> None:
        """Inicializa o Router."""
        pass

    def route(self, input_data: str) -> Dict[str, Any]:
        """
        Analisa a entrada e define o plano de execução via LLM.
        """
        from infra.container import Container
        container = Container.get_instance()
        llm = container.llm_service
        
        # Construct Prompt
        # We append the user input to the system prompt
        full_prompt = f"{INTENT_CLASSIFICATION_SYSTEM_PROMPT}\n\nUSER INPUT: {input_data}"
        
        try:
            # Generate
            response_text = llm.generate(full_prompt)
            
            # Clean response (remove markdown code blocks if present)
            cleaned_response = response_text.replace("```json", "").replace("```", "").strip()
            
            # Parse JSON
            intent_data = json.loads(cleaned_response)
            
            logger.info(f"[Router] Intent: {intent_data.get('intent')} (Conf: {intent_data.get('confidence')})")
            return intent_data

        except json.JSONDecodeError:
            logger.error(f"[Router] Failed to parse JSON: {response_text}")
            # Fallback intent
            return {"intent": "CHAT", "confidence": 0.0, "reason": "JSON Parsing Failed"}
        except Exception as e:
            logger.error(f"[Router] Error: {e}")
            return {"intent": "CHAT", "confidence": 0.0, "reason": "LLM Error", "user_input": input_data}
            
        # Inject Input for Planner usage
        intent_data = intent_data if isinstance(intent_data, dict) else {}
        intent_data["user_input"] = input_data
        
        return intent_data
