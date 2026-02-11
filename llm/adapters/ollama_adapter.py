"""
Ollama LLM Adapter.

Implementação do contrato BaseLLMAdapter para Ollama local.
"""

import requests
from llm.base import BaseLLMAdapter
from infra.config import settings
from infra.logger import logger

class OllamaAdapter(BaseLLMAdapter):
    """Adaptador para Ollama (Local)."""

    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.api_url = f"{self.base_url}/api/generate"

    def generate(self, prompt: str) -> str:
        """
        Gera completion usando Ollama local.
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
            return result["response"]
            
        except Exception as e:
            logger.error(f"[OllamaAdapter] Failed: {e}")
            raise e
