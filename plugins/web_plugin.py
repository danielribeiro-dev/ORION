"""
Web Plugin.

Responsabilidade:
    - Realizar buscas na web.
    - Filtrar resultados irrelevantes.
"""

import requests
from typing import Any, Dict, List
from plugins.base_plugin import BasePlugin
from infra.logger import logger

class WebPlugin(BasePlugin):
    """Plugin de Busca Web."""

    def execute(self, params: Dict[str, Any]) -> str:
        """
        Executa busca web (Simulada/DuckDuckGo se possivel).
        """
        query = params.get("user_input", "")
        logger.info(f"[WebPlugin] Searching for: {query}")
        
        # TODO: Integrate real DuckDuckGo or Google Search API
        # For now, we simulate a search result to enable the flow
        # as requested in the plan (Mock if no API key).
        
        results = [
            f"Result 1 for '{query}': Official Documentation",
            f"Result 2 for '{query}': Wikipedia Article",
            f"Result 3 for '{query}': Latest News"
        ]
        
        # Check if we can reach outside (Simple ping)
        try:
            # Just a connectivity check/placeholder for real implementation
            # In a real scenario, use duckduckgo-search package
            pass 
        except Exception as e:
            logger.warning(f"[WebPlugin] Search failed: {e}")
            return "Unable to perform search due to network error."

        formatted_results = "\n".join(results)
        return f"Search Results for '{query}':\n{formatted_results}\n(Note: This is a simulated result for activation phase)"
