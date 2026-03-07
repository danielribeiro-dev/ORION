"""
Router Module.

Responsabilidade:
    - Analisar a entrada do usuário.
    - Determinar a intenção (Intent).
    - Decidir o caminho de execução (Plugin, LLM, etc.).
    - Usar contexto de histórico para continuidade conversacional.

v0.4.0: Retorna RouterResult (contrato formal) em vez de Dict puro (M-02 / C-01).

Proibições:
    - Não executa ações.
    - Não gera respostas finais ao usuário.
"""

import json
import re
from typing import Any, Dict, List, Optional
from core.interfaces import BaseRouter
from core.contracts import RouterResult
from pipeline.prompts import INTENT_CLASSIFICATION_SYSTEM_PROMPT
from pipeline.keywords import classify_by_keywords, get_best_intent
from core.logger import logger


class Router(BaseRouter):
    """
    Componente responsável por rotear a intenção do usuário para o executor correto.
    Usa LLM para classificar a intenção, com fallback para keywords.
    """

    def __init__(self) -> None:
        pass

    def route(self, input_data: str, context: Optional[List[Dict]] = None) -> RouterResult:
        """
        Analisa a entrada e define o plano de execução via LLM.

        Args:
            input_data: Input do usuário
            context: Histórico recente de interações (opcional)

        Returns:
            RouterResult com intent, confidence, reason e metadata.
        """
        from core.container import Container
        container = Container.get_instance()
        llm = container.llm_service

        # 0. Heurística Estrutural para intents institucionais (SYSTEM)
        # Ignora o LLM completamente para evitar alucinações sobre identidade do sistema
        system_keywords = [
            "versão", "cargo", "permissão", "permissões", "quem é você",
            "identidade do sistema", "user role", "permissions", "system version",
            "qual a sua versão", "qual versão"
        ]
        lower_input = input_data.lower()
        if any(kw in lower_input for kw in system_keywords):
            logger.info("[Router] Pre-check heurístico: intent SYSTEM interceptado.")
            return RouterResult(
                intent="SYSTEM",
                confidence=1.0,
                reason="Heurística estrutural pré-LLM",
                user_input=input_data,
                metadata={"context": context or []}
            )

        # Construir prompt com contexto de histórico
        full_prompt = self._build_prompt_with_context(input_data, context)

        try:
            llm_result = llm.generate(full_prompt)
            response_text = llm_result.text

            # Parsing robusto do JSON retornado pelo LLM
            intent_data = self._extract_json(response_text)

            confidence = intent_data.get("confidence", 0.0)

            # Fallback para keywords se a confiança do LLM for baixa
            if confidence < 0.5:
                logger.warning(f"[Router] Confiança baixa do LLM ({confidence:.2f}), usando keywords como fallback.")
                keyword_scores = classify_by_keywords(input_data)
                keyword_intent, keyword_conf = get_best_intent(keyword_scores)

                # Média ponderada: 50% LLM + 50% keywords
                combined_conf = (confidence + keyword_conf) / 2

                if keyword_conf > confidence:
                    intent_data["intent"] = keyword_intent
                    intent_data["confidence"] = combined_conf
                    intent_data["reason"] = f"Keyword fallback (LLM: {confidence:.2f}, KW: {keyword_conf:.2f})"

            final_intent = intent_data.get("intent", "CHAT")
            final_conf = float(intent_data.get("confidence", 0.5))
            final_reason = intent_data.get("reason", "LLM classification")
            metadata = intent_data.get("metadata", {})
            metadata["context"] = context or []

            logger.info(f"[Router] Intent: {final_intent} (Conf: {final_conf:.2f})")

            return RouterResult(
                intent=final_intent,
                confidence=final_conf,
                reason=final_reason,
                user_input=input_data,
                metadata=metadata
            )

        except json.JSONDecodeError as e:
            logger.error(f"[Router] Falha no parsing JSON: {e}")
            return self._fallback_to_keywords(input_data, context, "JSON Parsing Failed")
        except Exception as e:
            logger.error(f"[Router] Erro: {e}")
            return self._fallback_to_keywords(input_data, context, f"LLM Error: {e}")

    def _build_prompt_with_context(self, input_data: str, context: Optional[List[Dict]]) -> str:
        """Constrói prompt incluindo contexto de histórico se disponível."""
        prompt = INTENT_CLASSIFICATION_SYSTEM_PROMPT

        if context and len(context) > 0:
            prompt += "\n\n--- CONVERSATION HISTORY (para contexto) ---\n"
            for entry in context[-3:]:  # Últimas 3 interações
                user_input = entry.get("user_input", "")
                intent = entry.get("intent", "")
                prompt += f"User: {user_input} [Intent: {intent}]\n"
            prompt += "--- END HISTORY ---\n"

        prompt += f"\n\nUSER INPUT: {input_data}"
        return prompt

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extrai JSON de forma robusta usando múltiplas estratégias."""
        # Tentativa 1: parsing direto
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        # Tentativa 2: remover markdown code blocks
        cleaned = text.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Tentativa 3: regex para encontrar objeto JSON
        match = re.search(r'\{[^{}]*"intent"[^{}]*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        raise json.JSONDecodeError("Nenhum JSON válido encontrado", text, 0)

    def _fallback_to_keywords(
        self,
        input_data: str,
        context: Optional[List[Dict]],
        reason: str
    ) -> RouterResult:
        """Fallback completo para keywords quando o LLM falha."""
        logger.warning(f"[Router] Usando fallback de keywords: {reason}")
        keyword_scores = classify_by_keywords(input_data)
        intent, confidence = get_best_intent(keyword_scores)

        return RouterResult(
            intent=intent,
            confidence=confidence,
            reason=f"Keyword-based (LLM falhou: {reason})",
            user_input=input_data,
            metadata={"context": context or []}
        )
