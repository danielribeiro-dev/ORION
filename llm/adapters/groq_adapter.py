"""
Groq LLM Adapter.

Implementação do contrato BaseLLMAdapter para a API da Groq.
"""

import os
import requests
from typing import Optional
from llm.base import BaseLLMAdapter
from infra.config import settings
from infra.logger import logger
from infra.contracts import LLMResult

class GroqAdapter(BaseLLMAdapter):
    """Adaptador para a API Groq."""

    def __init__(self) -> None:
        self.api_key = settings.groq_api_key
        self.model = settings.groq_model
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def generate(self, prompt: str) -> LLMResult:
        """
        Gera completion usando Groq API.
        Lança exceção em caso de erro para permitir fallback.
        
        Returns:
            LLMResult com texto, provedor, status degraded e modelo usado.
        """
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            text = result["choices"][0]["message"]["content"]
            
            return LLMResult(
                text=text,
                provider="groq",
                degraded=False,  # Primário, não degradado
                model=self.model
            )
            
        except Exception as e:
            logger.warning(f"[GroqAdapter] Failed: {e}")
            raise e
