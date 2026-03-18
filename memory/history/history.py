"""
History Memory Module.

Gerencia o histórico de conversação (Memória Episódica).

v0.4.0: Implementado load() de verdade — carrega as últimas N entradas
        do arquivo .jsonl no session_buffer durante a inicialização (BUG-06).
"""

import json
import os
import time
from typing import List, Dict, Any
from memory.base import BaseMemory
from core.logger import logger

# Quantas interações recentes carregar do disco no startup
_PRELOAD_COUNT = 20


class HistoryMemory(BaseMemory):
    """
    Memória de Histórico (Append-only log com pré-carregamento no startup).
    """

    def __init__(self, filepath: str = "memory/history.jsonl") -> None:
        self.filepath = filepath
        self.session_buffer: List[Dict[str, Any]] = []
        # v0.4.0: carrega histórico recente do disco automaticamente
        self.load()

    def load(self) -> None:
        """
        Carrega as últimas _PRELOAD_COUNT entradas do arquivo .jsonl
        para o session_buffer, permitindo continuidade conversacional.

        v0.4.0: Antes era um stub vazio (BUG-06). Agora funciona de verdade.
        """
        if not os.path.exists(self.filepath):
            logger.info("[HistoryMemory] Arquivo de histórico não encontrado. Iniciando do zero.")
            return

        try:
            with open(self.filepath, 'r') as f:
                lines = f.readlines()

            # Pegar apenas as últimas N linhas para não sobrecarregar memória
            recent_lines = lines[-_PRELOAD_COUNT:]
            loaded = []
            for line in recent_lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    loaded.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

            self.session_buffer = loaded
            logger.info(f"[HistoryMemory] {len(loaded)} interações carregadas do histórico.")
        except Exception as e:
            logger.error(f"[HistoryMemory] Falha ao carregar histórico: {e}")

    def save(self) -> None:
        """Força flush do buffer para disco."""
        if not self.session_buffer:
            return

        # Salvar apenas entradas que ainda não estão no arquivo
        # (estratégia simples: apenas entries não-persistidas ficam no buffer)
        to_persist = [e for e in self.session_buffer if not e.get("_persisted")]
        if not to_persist:
            return

        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'a') as f:
                for entry in to_persist:
                    # Remove flag interna antes de persistir
                    clean = {k: v for k, v in entry.items() if k != "_persisted"}
                    f.write(json.dumps(clean) + "\n")

            # Marcar como persistidas no buffer
            for entry in self.session_buffer:
                entry["_persisted"] = True

            logger.debug(f"[HistoryMemory] {len(to_persist)} entradas salvas no disco.")
        except Exception as e:
            logger.error(f"[HistoryMemory] Falha ao salvar histórico: {e}")

    def add_interaction(self, user_input: str, system_output: str, intent: str) -> None:
        """Registra uma interação na sessão atual."""
        entry = {
            "timestamp": time.time(),
            "user_input": user_input,
            "system_output": system_output,
            "intent": intent,
            "_persisted": False  # Flag interna de controle de flush
        }
        self.session_buffer.append(entry)
        self.save()  # Auto-flush para segurança

    def get_recent(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Retorna as últimas N interações da sessão (inclui histórico carregado do disco).
        """
        # Remove a flag interna antes de retornar para os consumidores
        clean_buffer = [
            {k: v for k, v in e.items() if k != "_persisted"}
            for e in self.session_buffer
        ]
        return clean_buffer[-n:]
