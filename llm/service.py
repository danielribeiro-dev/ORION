"""
LLM Service (Fallback Logic).

Gerencia a tentativa de uso do provedor principal (Groq)
e fallback para o secundário (Ollama).
"""

from llm.base import BaseLLMAdapter
from llm.adapters.groq_adapter import GroqAdapter
from llm.adapters.ollama_adapter import OllamaAdapter
from infra.logger import logger

class LLMService(BaseLLMAdapter):
    """
    Serviço composto que gerencia múltiplos adapters com fallback.
    """

    def __init__(self) -> None:
        self.primary = GroqAdapter()
        self.secondary = OllamaAdapter()

    def generate(self, prompt: str) -> str:
        """
        Tenta gerar com o primário. Se falhar, tenta o secundário.
        """
        try:
            return self.primary.generate(prompt)
        except Exception:
            logger.info("[LLMService] Switching to fallback (Ollama)...")
            try:
                return self.secondary.generate(prompt)
            except Exception as e:
                logger.critical("[LLMService] All providers failed.")
                raise e
