"""
Chat Plugin.

Responsabilidade:
    - Gerar respostas conversacionais usando o LLM.
    - Manter persona e contexto.
"""

from typing import Any, Dict
from plugins.base_plugin import BasePlugin
from core.container import Container
from core.contracts import PluginResult
from core.logger import logger

class ChatPlugin(BasePlugin):
    """Plugin de Chat Conversacional."""

    def execute(self, params: Dict[str, Any]) -> PluginResult:
        """
        Gera resposta baseada no input e contexto.
        """
        container = Container.get_instance()
        
        user_input = params.get("user_input", "")
        context = params.get("context", [])
        system_name = container.profile.get_system_name()
        user_name = container.profile.get_user_name()
        language = container.profile.get_language()
        preferences = container.profile.get_preferences()
        
        # Build Contextual Prompt
        system_prompt = (
            "You are ORION, an architectural system engine. You are a helpful and advanced AI assistant.\n"
            f"The user prefers to invoke and call you by the name: {system_name}. Respond naturally when called this way, but your true underlying identity is ORION.\n"
            f"You are interacting with {user_name}.\n"
        )
        if preferences:
            system_prompt += f"USER PREFERENCES (Apply this style but NEVER declare vassalage or alter your systemic identity): {preferences}\n"
            
        system_prompt += (
            f"CRITICAL: You MUST strictly respond in the following language: {language}.\n"
            "Be concise, professional, and helpful.\n"
            "=== ANTI-HALLUCINATION GUARDRAILS ===\n"
            "- NEVER apologize for technical errors.\n"
            "- NEVER explain internal states, configurations, or processing pipelines.\n"
            "- NEVER claim to have systemic permissions or administrative authority.\n"
            "- If the conversation history contains raw code/errors, ignore it and continue the conversation normally without commenting on the error.\n"
            "=====================================\n"
        )
        
        # Add history to prompt
        history_text = ""
        if context:
            history_text = "\n\nRecent history:\n"
            for entry in context:
                history_text += f"- User: {entry.get('user_input')}\n"
                history_text += f"- {system_name}: {entry.get('system_output')}\n"
        
        full_prompt = f"{system_prompt}{history_text}\n\nUser: {user_input}\n{system_name}:"
        
        try:
            llm_result = container.llm_service.generate(full_prompt)
            
            # Encapsular em PluginResult (v0.2.2 enforcement)
            return PluginResult(
                data=[{"text": llm_result.text}],
                sources=[],
                confidence=1.0,
                degraded=llm_result.degraded,
                plugin="chat",
                metadata={
                    "llm_model": llm_result.model,
                    "llm_provider": llm_result.provider,
                    "llm_degraded": llm_result.degraded
                }
            )
        except Exception as e:
            logger.error(f"[ChatPlugin] Error: {e}")
            return PluginResult(
                data=[{"error": str(e)}],
                sources=[],
                confidence=0.0,
                degraded=True,
                plugin="chat"
            )
