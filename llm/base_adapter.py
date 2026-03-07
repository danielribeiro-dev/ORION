"""
LLM Base Adapter (compatibilidade).

v0.4.0: Mantido como alias para não quebrar imports existentes.
        O contrato real está em llm/base.py (BaseLLMAdapter).
"""

from llm.base import BaseLLMAdapter

# Alias de compatibilidade — BaseAdapter == BaseLLMAdapter
BaseAdapter = BaseLLMAdapter
