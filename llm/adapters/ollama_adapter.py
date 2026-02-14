"""
Ollama LLM Adapter.

Implementação do contrato BaseLLMAdapter para Ollama local.
"""

import requests
from llm.base import BaseLLMAdapter
from core.config import settings
from core.logger import logger
from core.contracts import LLMResult

class OllamaAdapter(BaseLLMAdapter):
    """Adaptador para Ollama (Local)."""

    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.api_url = f"{self.base_url}/api/generate"

    def generate(self, prompt: str) -> LLMResult:
        """
        Gera completion usando Ollama local.
        
        Returns:
            LLMResult com texto, provedor, status degraded e modelo usado.
            degraded=True pois Ollama é o fallback secundário.
        """
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(self.api_url, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            text = result["response"]
            
            return LLMResult(
                text=text,
                provider="ollama",
                degraded=True,  # Fallback, modo degradado
                model=self.model
            )
            
        except Exception as e:
            logger.error(f"[OllamaAdapter] Failed: {e}")
            raise e
