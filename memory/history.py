"""
History Memory Module.

Gerencia o histórico de conversação (Memória Episódica Simplificada).
"""

import json
import os
import time
from typing import List, Dict, Any
from memory.base import BaseMemory
from infra.logger import logger

class HistoryMemory(BaseMemory):
    """
    Memória de Histórico (Append-only log).
    """

    def __init__(self, filepath: str = "memory/history.jsonl") -> None:
        self.filepath = filepath
        self.session_buffer: List[Dict[str, Any]] = []

    def load(self) -> None:
        """
        Carrega histórico completo (CUIDADO: pode ser grande).
        Para implementação real, usar paginação ou leitura reversa.
        """
        pass # Por enquanto, append-only.

    def save(self) -> None:
        """Força flush do buffer para disco."""
        if not self.session_buffer:
            return

        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'a') as f:
                for entry in self.session_buffer:
                    f.write(json.dumps(entry) + "\n")
            
            self.session_buffer = [] # Clear buffer after flush
            logger.debug("[HistoryMemory] Flushed to disk.")
        except Exception as e:
            logger.error(f"[HistoryMemory] Flush failed: {e}")

    def add_interaction(self, user_input: str, system_output: str, intent: str) -> None:
        """Registra uma interação."""
        entry = {
            "timestamp": time.time(),
            "user_input": user_input,
            "system_output": system_output,
            "intent": intent
        }
        self.session_buffer.append(entry)
        self.save() # Auto-flush for safety
