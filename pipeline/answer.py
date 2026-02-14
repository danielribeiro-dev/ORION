"""
Answer Pipeline Module.

Responsabilidade:
    - Processar o resultado bruto da execução.
    - Formatar a resposta final para o usuário.
    - Gerar síntese inteligente usando LLM para resultados de busca (v0.2.2).
    - Exibir origem, fontes e confiança.
"""

from typing import Any, List, Dict
from core.interfaces import BaseAnswerPipeline
from core.contracts import PluginResult, LLMResult, ConfidenceScore
from core.logger import logger

class AnswerPipeline(BaseAnswerPipeline):
    """
    Pipeline final de montagem da resposta ao usuário.
    """

    def __init__(self) -> None:
        """Inicializa o AnswerPipeline."""
        pass

    def process(self, result: PluginResult) -> str:
        """
        Formata o resultado da execução em uma resposta legível.
        v0.2.2: Sempre espera PluginResult.
        """
        if not result:
            return ""
        
        if not isinstance(result, PluginResult):
            logger.warning(f"[AnswerPipeline] Expected PluginResult, got {type(result)}")
            return str(result)
            
        return self._format_plugin_result(result)
    
    def _format_plugin_result(self, result: PluginResult) -> str:
        """
        Formata PluginResult com fontes, confiança e metadados.
        """
        # Se houve erro
        if result.degraded and (not result.data or "error" in result.data[0]):
            error_msg = result.data[0].get("error", "Unknown error") if result.data else "No data available"
            return f"⚠️ Error in {result.plugin.upper()} plugin: {error_msg}"
        
        # Se não há dados
        if not result.data:
            return f"No results found for your query in {result.plugin.upper()} plugin."
        
        # Diferenciar comportamento por plugin
        if result.plugin == "web":
            return self._format_web_result(result)
        elif result.plugin == "chat":
            return self._format_chat_result(result)
        elif result.plugin == "memory":
            return self._format_memory_result(result)
        
        # Default fallback
        return f"[{result.plugin.upper()}] Result: {result.data}"

    def _format_chat_result(self, result: PluginResult) -> str:
        """Formata resultado do plugin de chat."""
        text = result.data[0].get("text", "")
        
        # Adicionar informações de transparência LLM
        footer = self._build_footer(result)
        return f"{text}\n\n{footer}"

    def _format_memory_result(self, result: PluginResult) -> str:
        """Formata resultado do plugin de memória."""
        msg = result.data[0].get("message", "Ação de memória concluída.")
        footer = self._build_footer(result)
        return f"✅ {msg}\n\n{footer}"

    def _format_web_result(self, result: PluginResult) -> str:
        """
        Formata resultado de busca web com síntese inteligente.
        """
        from core.container import Container
        container = Container.get_instance()
        lines = []
        
        # 1. Título e Metadados Iniciais
        query = result.metadata.get("query", "Search")
        lines.append(f"🔍 **Search Results for:** {query}\n")
        
        # 2. Síntese Inteligente (v0.2.2)
        synthesis = self._generate_synthesis(result)
        if synthesis:
            lines.append("### 📝 Smart Summary")
            lines.append(synthesis)
            lines.append("")
        
        # 3. Lista de Fontes Principais
        lines.append("### 📚 Key Sources")
        for idx, item in enumerate(result.data[:5], 1):
            title = item.get("title", "Untitled")
            body = item.get("body", "")
            url = item.get("url", "")
            
            lines.append(f"{idx}. **{title}**")
            if body:
                body_preview = body[:150] + "..." if len(body) > 150 else body
                lines.append(f"   {body_preview}")
            if url:
                lines.append(f"   🔗 {url}")
            lines.append("")

        # 4. Rodapé de Transparência
        lines.append(self._build_footer(result))
        
        return "\n".join(lines)

    def _generate_synthesis(self, result: PluginResult) -> str:
        """
        Gera uma síntese dos resultados usando o LLM.
        Garante isolamento: LLM recebe apenas os snippets retornados.
        """
        from core.container import Container
        container = Container.get_instance()
        data_context = ""
        for idx, item in enumerate(result.data[:7], 1):
            data_context += f"Source {idx}: {item.get('title')}\nContent: {item.get('body')}\n\n"
        
        prompt = (
            "You are a Synthesis Module. Your task is to summarize the following search results "
            "into a cohesive, helpful, and concise answer for the user.\n\n"
            "STRICT RULES:\n"
            "1. ONLY use the provided Source information below.\n"
            "2. DO NOT add external knowledge or hallucinate information.\n"
            "3. If sources contain conflicting information, mention it.\n"
            "4. DO NOT invent links or references not present in the sources.\n\n"
            "SEARCH RESULTS:\n"
            f"{data_context}\n"
            "Synthesis:"
        )
        
        try:
            llm_res = container.llm_service.generate(prompt)
            return llm_res.text
        except Exception as e:
            logger.error(f"[AnswerPipeline] Synthesis failed: {e}")
            return "Unable to generate smart summary at this time."

    def _build_footer(self, result: PluginResult) -> str:
        """Constrói o rodapé de transparência e metadados."""
        footer_lines = ["---"]
        footer_lines.append(f"📊 **Source:** {result.plugin.upper()} Plugin")
        
        # Cálculo de confiança refinado v0.2.2
        conf = ConfidenceScore(
            router_confidence=0.9, # Placeholder enquanto RouterResult não flui totalmente
            plugin_confidence=result.confidence,
            source_count=len(result.data) if result.plugin == "web" else 0,
            is_degraded=result.degraded
        )
        
        final_score = conf.final_confidence
        footer_lines.append(f"📈 **Confidence:** {final_score:.2f}")
        
        if result.metadata:
            llm_model = result.metadata.get("llm_model")
            llm_provider = result.metadata.get("llm_provider")
            llm_degraded = result.metadata.get("llm_degraded")
            
            if llm_model and llm_provider:
                icon = "⚡" if not llm_degraded else "🔄"
                footer_lines.append(f"{icon} **LLM:** {llm_provider}/{llm_model}")
        
        return "\n".join(footer_lines)
