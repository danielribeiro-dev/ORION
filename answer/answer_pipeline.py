"""
Answer Pipeline Module.

Responsabilidade:
    - Processar o resultado bruto da execução.
    - Formatar a resposta final para o usuário.
    - Garantir o tom e estilo adequados.
    - Exibir origem, fontes e confiança.

Proibições:
    - Não executa novas ações de busca.
    - Não altera a verdade dos dados (alucinação).
"""

from typing import Any, Union
from answer.base import BaseAnswerPipeline
from infra.contracts import PluginResult, LLMResult, ConfidenceScore

class AnswerPipeline(BaseAnswerPipeline):
    """
    Pipeline final de montagem da resposta ao usuário.
    """

    def __init__(self) -> None:
        """Inicializa o AnswerPipeline."""
        pass

    def process(self, result: Any) -> str:
        """
        Formata o resultado da execução em uma resposta legível.
        
        Processa:
        - PluginResult: Formata com fontes e confiança
        - String: Retorna diretamente (legado)
        """
        if not result:
            return ""
        
        # Se é PluginResult, processar estruturado
        if isinstance(result, PluginResult):
            return self._format_plugin_result(result)
        
        # Caso contrário, retornar como string (legado)
        return str(result)
    
    def _format_plugin_result(self, result: PluginResult) -> str:
        """
        Formata PluginResult com fontes, confiança e metadados.
        """
        # Se houve erro (degraded com data vazia ou erro)
        if result.degraded and (not result.data or "error" in result.data[0]):
            error_msg = result.data[0].get("error", "Unknown error") if result.data else "No data available"
            return f"⚠️ Web search failed: {error_msg}"
        
        # Se não há dados
        if not result.data:
            return "No results found for your query."
        
        # Construir resposta
        lines = []
        
        # 1. Resumo dos resultados
        lines.append(f"Found {len(result.data)} relevant results:\n")
        
        # 2. Listar resultados principais (top 5)
        for idx, item in enumerate(result.data[:5], 1):
            title = item.get("title", "Untitled")
            body = item.get("body", "")
            url = item.get("url", "")
            
            lines.append(f"{idx}. **{title}**")
            if body:
                # Limitar body a 150 caracteres
                body_preview = body[:150] + "..." if len(body) > 150 else body
                lines.append(f"   {body_preview}")
            if url:
                lines.append(f"   🔗 {url}")
            lines.append("")  # Linha em branco
        
        # 3. Metadados (origem, confiança, fontes)
        lines.append("---")
        lines.append(f"📊 **Source:** {result.plugin.upper()} Plugin")
        lines.append(f"📈 **Confidence:** {result.confidence:.2f}")
        
        # v0.2.1: Exibir modelo LLM se disponível
        if result.metadata:
            query = result.metadata.get("query", "")
            if query:
                lines.append(f"🔍 **Query:** {query}")
            
            # Exibir informações do LLM se disponível
            llm_model = result.metadata.get("llm_model")
            llm_provider = result.metadata.get("llm_provider")
            llm_degraded = result.metadata.get("llm_degraded")
            
            if llm_model and llm_provider:
                provider_icon = "⚡" if not llm_degraded else "🔄"
                mode_text = "" if not llm_degraded else " (fallback)"
                lines.append(f"{provider_icon} **LLM:** {llm_provider}/{llm_model}{mode_text}")
        
        # 4. Fontes completas (se houver mais que 5)
        if len(result.sources) > 5:
            lines.append(f"\n📚 **All Sources ({len(result.sources)} total):**")
            for idx, source in enumerate(result.sources, 1):
                title = source.get("title", "Untitled")
                url = source.get("url", "")
                score = source.get("score", 0.0)
                lines.append(f"   {idx}. [{title}]({url}) (score: {score:.2f})")
        
        return "\n".join(lines)
