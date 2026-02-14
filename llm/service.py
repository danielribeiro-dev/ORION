"""
LLM Service (Fallback Logic).

Gerencia a tentativa de uso do provedor principal (Groq)
e fallback para o secundário (Ollama).
"""

from llm.base import BaseLLMAdapter
from llm.adapters.groq_adapter import GroqAdapter
from llm.adapters.ollama_adapter import OllamaAdapter
from core.logger import logger
from core.contracts import LLMResult

class LLMService(BaseLLMAdapter):
    """
    Serviço composto que gerencia múltiplos adapters com fallback.
    """

    def __init__(self) -> None:
        self.primary = GroqAdapter()
        self.secondary = OllamaAdapter()

    def generate(self, prompt: str) -> LLMResult:
        """
        Tenta gerar com o primário. Se falhar, tenta o secundário.
        
        Returns:
            LLMResult estruturado com informação de provedor e status degraded.
        """
        try:
            result = self.primary.generate(prompt)
            logger.info(f"[LLMService] Using primary provider: {result.provider}")
            return result
        except Exception as primary_error:
            logger.warning(f"[LLMService] Primary provider failed: {primary_error}")
            logger.info("[LLMService] Switching to fallback (Ollama)...")
            try:
                result = self.secondary.generate(prompt)
                logger.warning(f"[LLMService] Using fallback provider: {result.provider} (degraded mode)")
                return result
            except Exception as secondary_error:
                logger.critical("[LLMService] All providers failed.")
                logger.error(f"Primary error: {primary_error}")
                logger.error(f"Secondary error: {secondary_error}")
                raise secondary_error
