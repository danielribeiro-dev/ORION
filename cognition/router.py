"""
Router Module.

Responsabilidade:
    - Analisar a entrada do usuário.
    - Determinar a intenção (Intent) via LLM + heurísticas.
    - Retornar RouterResult (contrato formal).

Movido de pipeline/router.py → cognition/router.py (v0.4.0 reestruturação).
"""

import json
import re
from typing import Any, Dict, List, Optional
from core.interfaces import BaseRouter
from core.contracts import RouterResult
from cognition.reasoning.prompts import INTENT_CLASSIFICATION_SYSTEM_PROMPT   # atualizado
from cognition.reasoning.keywords import classify_by_keywords, get_best_intent # atualizado
from core.logger import logger


class Router(BaseRouter):
    """
    Componente responsável por rotear a intenção do usuário para o executor correto.
    """

    def __init__(self) -> None:
        pass

    def route(self, input_data: str, context: Optional[List[Dict]] = None, memory_context: str = "") -> RouterResult:
        """
        Analisa a entrada e retorna RouterResult com a intenção classificada.
        """
        from core.container import Container
        container = Container.get_instance()
        llm = container.llm_service

        # Heurística estrutural para intents institucionais (evita LLM)
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

        full_prompt = self._build_prompt_with_context(input_data, context, memory_context)

        try:
            llm_result = llm.generate(full_prompt)
            intent_data = self._extract_json(llm_result.text)

            confidence = intent_data.get("confidence", 0.0)

            if confidence < 0.5:
                logger.warning(f"[Router] Confiança LLM baixa ({confidence:.2f}), usando keywords.")
                
                # Expandindo fallback heurístico para chamadas diretas de memory
                memory_keywords = ["lembra", "lembrar", "você sabe", "já te disse", "me disse", "sabe que", "minha preferência", "o que você sabe sobre mim"]
                if any(kw in lower_input for kw in memory_keywords):
                    intent_data["intent"] = "MEMORY_RECALL"
                    intent_data["confidence"] = 0.95
                    intent_data["reason"] = "Keyword explícito contornando LLM para resgate de longo prazo."
                    intent_data["metadata"] = {"query": input_data}
                else:    
                    keyword_scores = classify_by_keywords(input_data)
                    keyword_intent, keyword_conf = get_best_intent(keyword_scores)
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

    def _build_prompt_with_context(self, input_data: str, context: Optional[List[Dict]], memory_context: str = "") -> str:
        prompt = INTENT_CLASSIFICATION_SYSTEM_PROMPT
        if context and len(context) > 0:
            prompt += "\n\n--- CONVERSATION HISTORY ---\n"
            for entry in context[-3:]:
                prompt += f"User: {entry.get('user_input', '')} [Intent: {entry.get('intent', '')}]\n"
            prompt += "--- END HISTORY ---\n"
        if memory_context:
            prompt += f"\n\nContexto relevante da memória do usuário:\n{memory_context}"
        
        prompt += f"\n\nUSER INPUT: {input_data}"
        return prompt

    def _extract_json(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        cleaned = text.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        match = re.search(r'\{[^{}]*"intent"[^{}]*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        raise json.JSONDecodeError("Nenhum JSON válido encontrado", text, 0)

    def _fallback_to_keywords(
        self, input_data: str, context: Optional[List[Dict]], reason: str
    ) -> RouterResult:
        logger.warning(f"[Router] Fallback para keywords: {reason}")
        keyword_scores = classify_by_keywords(input_data)
        intent, confidence = get_best_intent(keyword_scores)
        return RouterResult(
            intent=intent,
            confidence=confidence,
            reason=f"Keyword-based (LLM falhou: {reason})",
            user_input=input_data,
            metadata={"context": context or []}
        )
