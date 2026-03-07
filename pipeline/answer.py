"""
Answer Pipeline Module.

Responsabilidade:
    - Processar o resultado bruto da execução.
    - Formatar a resposta final para o usuário.
    - Gerar síntese inteligente usando LLM para resultados de busca.
    - Exibir origem, fontes e confiança.

v0.4.0:
    - Adicionada formatação para plugin 'fs' (BUG-08).
    - Síntese web agora injeta o idioma do perfil do usuário (M-06).
    - ConfidenceScore agora usa router_confidence do metadata quando disponível (C-05 parcial).
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
        pass

    def process(self, result: PluginResult) -> str:
        """
        Formata o resultado da execução em uma resposta legível.
        Sempre espera PluginResult.
        """
        if not result:
            return ""

        if not isinstance(result, PluginResult):
            logger.warning(f"[AnswerPipeline] Esperado PluginResult, recebido {type(result)}")
            return str(result)

        return self._format_plugin_result(result)

    def _format_plugin_result(self, result: PluginResult) -> str:
        """
        Formata PluginResult com fontes, confiança e metadados.
        Diferencia o comportamento por plugin.
        """
        # Erro explícito
        if result.degraded and result.data and "error" in result.data[0]:
            error_msg = result.data[0].get("error", "Erro desconhecido")
            return f"⚠️ Erro no plugin {result.plugin.upper()}: {error_msg}"

        # Sem dados
        if not result.data:
            return f"Nenhum resultado encontrado no plugin {result.plugin.upper()}."

        # Despacho por plugin
        if result.plugin == "web":
            return self._format_web_result(result)
        elif result.plugin == "chat":
            return self._format_chat_result(result)
        elif result.plugin == "memory":
            return self._format_memory_result(result)
        elif result.plugin == "system":
            return self._format_system_result(result)
        elif result.plugin == "fs":
            return self._format_filesystem_result(result)

        # Fallback genérico
        return f"[{result.plugin.upper()}] Resultado: {result.data}"

    def _format_chat_result(self, result: PluginResult) -> str:
        """Formata resultado do plugin de chat."""
        text = result.data[0].get("text", "")
        footer = self._build_footer(result)
        return f"{text}\n\n{footer}"

    def _format_system_result(self, result: PluginResult) -> str:
        """Formata resposta institucional do sistema (SYSTEM intent)."""
        text = result.data[0].get("text", "")
        # Respostas institucionais dispensam o footer do LLM
        return f"🛡️ **[RESPOSTA INSTITUCIONAL]**\n\n{text}"

    def _format_memory_result(self, result: PluginResult) -> str:
        """Formata resultado do plugin de memória."""
        msg = result.data[0].get("message", "Ação de memória concluída.")
        footer = self._build_footer(result)
        return f"✅ {msg}\n\n{footer}"

    def _format_filesystem_result(self, result: PluginResult) -> str:
        """
        Formata resultado do FilesystemPlugin de forma legível.
        v0.4.0: Adicionado para corrigir BUG-08.
        """
        data = result.data[0] if result.data else {}
        cwd = data.get("cwd", "?")
        directories = data.get("directories", [])
        files = data.get("files", [])

        lines = [f"📁 **Diretório Atual:** `{cwd}`\n"]

        if directories:
            lines.append("**Pastas:**")
            for d in sorted(directories):
                lines.append(f"  📂 {d}/")
            lines.append("")

        if files:
            lines.append("**Arquivos:**")
            for f in sorted(files):
                lines.append(f"  📄 {f}")
            lines.append("")

        if not directories and not files:
            lines.append("*(Diretório vazio ou todos os itens estão protegidos)*")

        footer = self._build_footer(result)
        lines.append(footer)
        return "\n".join(lines)

    def _format_web_result(self, result: PluginResult) -> str:
        """
        Formata resultado de busca web com síntese inteligente.
        v0.4.0: Síntese usa o idioma do perfil do usuário (M-06).
        """
        lines = []

        query = result.metadata.get("query", "Busca")
        lines.append(f"🔍 **Resultados para:** {query}\n")

        # Síntese inteligente via LLM (com idioma injetado)
        synthesis = self._generate_synthesis(result)
        if synthesis:
            lines.append("### 📝 Resumo Inteligente")
            lines.append(synthesis)
            lines.append("")

        # Lista de fontes principais
        lines.append("### 📚 Fontes Principais")
        for idx, item in enumerate(result.data[:5], 1):
            title = item.get("title", "Sem título")
            body = item.get("body", "")
            url = item.get("url", "")

            lines.append(f"{idx}. **{title}**")
            if body:
                body_preview = body[:150] + "..." if len(body) > 150 else body
                lines.append(f"   {body_preview}")
            if url:
                lines.append(f"   🔗 {url}")
            lines.append("")

        lines.append(self._build_footer(result))
        return "\n".join(lines)

    def _generate_synthesis(self, result: PluginResult) -> str:
        """
        Gera síntese dos resultados de busca usando o LLM.
        v0.4.0: Injeta o idioma do perfil do usuário no prompt (M-06).
        """
        from core.container import Container
        container = Container.get_instance()

        # Obter idioma do perfil do usuário
        user_language = container.profile.get_language()

        data_context = ""
        for idx, item in enumerate(result.data[:7], 1):
            data_context += f"Fonte {idx}: {item.get('title')}\nConteúdo: {item.get('body')}\n\n"

        prompt = (
            f"You are a Synthesis Module. Summarize the following search results "
            f"into a cohesive, helpful answer.\n\n"
            f"CRITICAL: Your response MUST be written in: {user_language}.\n\n"
            "STRICT RULES:\n"
            "1. Use ONLY the provided source information.\n"
            "2. Do NOT hallucinate or add external knowledge.\n"
            "3. If sources conflict, mention it.\n"
            "4. Do NOT invent links not present in the sources.\n\n"
            "SEARCH RESULTS:\n"
            f"{data_context}\n"
            "Synthesis:"
        )

        try:
            llm_res = container.llm_service.generate(prompt)
            return llm_res.text
        except Exception as e:
            logger.error(f"[AnswerPipeline] Síntese falhou: {e}")
            return "Não foi possível gerar o resumo inteligente no momento."

    def _build_footer(self, result: PluginResult) -> str:
        """Constrói o rodapé de transparência e metadados."""
        footer_lines = ["---"]
        footer_lines.append(f"📊 **Fonte:** Plugin {result.plugin.upper()}")

        # Usar router_confidence do metadata se disponível, senão 0.8 como estimativa neutra
        router_conf = result.metadata.get("router_confidence", 0.8) if result.metadata else 0.8

        conf = ConfidenceScore(
            router_confidence=router_conf,
            plugin_confidence=result.confidence,
            source_count=len(result.data) if result.plugin == "web" else 0,
            is_degraded=result.degraded
        )

        final_score = conf.final_confidence
        footer_lines.append(f"📈 **Confiança:** {final_score:.2f}")

        if result.metadata:
            llm_model = result.metadata.get("llm_model")
            llm_provider = result.metadata.get("llm_provider")
            llm_degraded = result.metadata.get("llm_degraded")

            if llm_model and llm_provider:
                icon = "⚡" if not llm_degraded else "🔄"
                footer_lines.append(f"{icon} **LLM:** {llm_provider}/{llm_model}")

        return "\n".join(footer_lines)
