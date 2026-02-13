"""
Router Module.

Responsabilidade:
    - Analisar a entrada do usuário.
    - Determinar a intenção (Intent).
    - Decidir o caminho de execução (Plugin, LLM, etc.).
    - Usar contexto de histórico para continuidade conversacional.

Proibições:
    - Não executa ações.
    - Não gera respostas finais ao usuário.
"""

import json
import re
from typing import Any, Dict, List, Optional
from routing.base import BaseRouter
from routing.prompts import INTENT_CLASSIFICATION_SYSTEM_PROMPT
from routing.keywords import classify_by_keywords, get_best_intent
from infra.logger import logger

class Router(BaseRouter):
    """
    Componente responsável por rotear a intenção do usuário para o executor correto.
    Usa LLM para classificar a intenção.
    """

    def __init__(self) -> None:
        """Inicializa o Router."""
        pass

    def route(self, input_data: str, context: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Analisa a entrada e define o plano de execução via LLM.
        
        Args:
            input_data: Input do usuário
            context: Histórico recente de interações (opcional)
        """
        from infra.container import Container
        container = Container.get_instance()
        llm = container.llm_service
        
        # Construct Prompt com contexto
        full_prompt = self._build_prompt_with_context(input_data, context)
        
        try:
            # Generate (agora retorna LLMResult)
            llm_result = llm.generate(full_prompt)
            response_text = llm_result.text
            
            # Parsing robusto de JSON
            intent_data = self._extract_json(response_text)
            
            # Se confiança baixa, usar keywords como fallback
            confidence = intent_data.get("confidence", 0.0)
            if confidence < 0.5:
                logger.warning(f"[Router] Low LLM confidence ({confidence:.2f}), using keyword fallback")
                keyword_scores = classify_by_keywords(input_data)
                keyword_intent, keyword_conf = get_best_intent(keyword_scores)
                
                # Combinar scores (média ponderada: 50% LLM + 50% keywords)
                combined_conf = (confidence + keyword_conf) / 2
                
                # Se keyword tem maior confiança, usar ela
                if keyword_conf > confidence:
                    intent_data["intent"] = keyword_intent
                    intent_data["confidence"] = combined_conf
                    intent_data["reason"] = f"Keyword fallback (LLM: {confidence:.2f}, KW: {keyword_conf:.2f})"
            
            logger.info(f"[Router] Intent: {intent_data.get('intent')} (Conf: {intent_data.get('confidence'):.2f})")
            # Adicionar contexto aos metadados para uso posterior (Planner/Plugins)
            if "metadata" not in intent_data:
                intent_data["metadata"] = {}
            intent_data["metadata"]["context"] = context
            
            # Inject Input for Planner usage
            intent_data["user_input"] = input_data
            return intent_data

        except json.JSONDecodeError as e:
            logger.error(f"[Router] JSON parsing failed: {e}")
            return self._fallback_to_keywords(input_data, "JSON Parsing Failed")
        except Exception as e:
            logger.error(f"[Router] Error: {e}")
            return self._fallback_to_keywords(input_data, f"LLM Error: {e}")
    
    def _build_prompt_with_context(self, input_data: str, context: Optional[List[Dict]]) -> str:
        """
        Constrói prompt incluindo contexto de histórico se disponível.
        """
        prompt = INTENT_CLASSIFICATION_SYSTEM_PROMPT
        
        if context and len(context) > 0:
            prompt += "\n\n--- CONVERSATION HISTORY (for context) ---\n"
            for entry in context[-3:]:  # Últimas 3 interações
                user_input = entry.get("user_input", "")
                intent = entry.get("intent", "")
                prompt += f"User: {user_input} [Intent: {intent}]\n"
            prompt += "--- END HISTORY ---\n"
        
        prompt += f"\n\nUSER INPUT: {input_data}"
        return prompt
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extrai JSON de forma robusta usando regex.
        """
        # Tentar parsing direto primeiro
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        # Remover markdown code blocks
        cleaned = text.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        # Usar regex para encontrar objeto JSON
        match = re.search(r'\{[^{}]*"intent"[^{}]*\}', text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        
        raise json.JSONDecodeError("No valid JSON found", text, 0)
    
    def _fallback_to_keywords(self, input_data: str, reason: str) -> Dict[str, Any]:
        """
        Fallback completo para keywords quando LLM falha.
        """
        logger.warning(f"[Router] Falling back to keywords: {reason}")
        keyword_scores = classify_by_keywords(input_data)
        intent, confidence = get_best_intent(keyword_scores)
        
        return {
            "intent": intent,
            "confidence": confidence,
            "reason": f"Keyword-based (LLM failed: {reason})",
            "user_input": input_data
        }
