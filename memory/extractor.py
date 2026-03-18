import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class MemoryExtractor:
    """Extrae automaticamente fatos e padrões durante uma conversa para armanzenamento semântico de longo prazo."""
    
    def __init__(self):
        # Prompt enraizado conforme as diretrizes para ignorar dados transientes
        self.system_prompt = (
            "Você é um extrator de memória para um assistente de IA chamado ORION.\n"
            "Analise o trecho de conversa abaixo e extraia APENAS informações duráveis e relevantes sobre o usuário.\n"
            "Ignore informações temporárias, perguntas pontuais ou contexto sem valor futuro.\n\n"
            "Responda SOMENTE com um JSON válido no formato:\n"
            "{\n"
            "  \"facts\": [\n"
            "    {\"text\": \"...\", \"category\": \"preference|identity|context|skill|relationship\"}\n"
            "  ],\n"
            "  \"procedures\": [\n"
            "    {\"trigger\": \"...\", \"sequence\": [\"passo1\", \"passo2\"]}\n"
            "  ]\n"
            "}\n\n"
            "Se não houver nada relevante para extrair, responda: {\"facts\": [], \"procedures\": []}\n"
            "Não inclua nenhum texto fora do JSON."
        )

    def extract_and_store(self, user_input: str, assistant_response: str, semantic_memory, llm_service) -> None:
        """Disparável fire-and-forget: Extrai entidades relevantes das frases gerando fatos ou procedimentos."""
        if not semantic_memory or not semantic_memory.is_available():
            return
            
        full_prompt = (
            f"{self.system_prompt}\n\n"
            "USER:\n"
            "Conversa:\n"
            f"Usuário: {user_input}\n"
            f"Assistente: {assistant_response}"
        )
        
        try:
            llm_res = llm_service.generate(full_prompt)
            raw_text = llm_res.text.strip()
            
            # Limpa blockticks se surgirem
            cleaned = raw_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            
            facts = data.get("facts", [])
            procedures = data.get("procedures", [])
            
            if not facts and not procedures:
                return
                
            for fact_entry in facts:
                if "text" in fact_entry and "category" in fact_entry:
                     semantic_memory.store_fact(
                         fact=fact_entry["text"],
                         category=fact_entry["category"]
                     )
                     
            for proc_entry in procedures:
                 if "trigger" in proc_entry and "sequence" in proc_entry:
                     semantic_memory.store_procedure(
                         trigger=proc_entry["trigger"],
                         sequence=proc_entry["sequence"]
                     )
                     
        except json.JSONDecodeError as e:
            logger.debug(f"[MemoryExtractor] Conversão de Payload JSON falhou. Extração Skipada: {e}")
        except Exception as e:
            logger.debug(f"[MemoryExtractor] Processo abortado assíncrono: {e}")
