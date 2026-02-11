"""
Chat Plugin.

Responsabilidade:
    - Gerar respostas conversacionais usando o LLM.
    - Manter persona e contexto.
"""

from typing import Any, Dict
from plugins.base_plugin import BasePlugin
from infra.container import Container

class ChatPlugin(BasePlugin):
    """Plugin de Chat Conversacional."""

    def execute(self, params: Dict[str, Any]) -> str:
        """
        Gera resposta baseada no input.
        """
        from infra.container import Container
        container = Container.get_instance()
        
        user_input = params.get("user_input", "")
        system_name = container.profile.get_system_name()
        user_name = container.profile.get_user_name()
        
        # Build Contextual Prompt
        system_prompt = (
            f"You are {system_name}, a helpful and advanced AI assistant."
            f"You are interacting with {user_name}."
            "Be concise, professional, and helpful."
        )
        
        full_prompt = f"{system_prompt}\n\nUser: {user_input}\n{system_name}:"
        
        try:
            return container.llm_service.generate(full_prompt)
        except Exception as e:
            return f"I apologize, but I encountered an error generating a response: {e}"
