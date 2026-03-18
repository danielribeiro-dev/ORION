"""
Audit System Module.

Responsabilidade:
    - Registrar todas as ações críticas do sistema.
    - Log estruturado e imutável (append-only).
    - Rastrear Quem, O Quê, Quando e Resultado.

Movido de core/audit.py → governance/audit.py (v0.4.0 reestruturação).
"""

import json
import time
from typing import Any, Dict
from datetime import datetime
from governance.auth import User       # atualizado: core.auth → governance.auth
from core.contracts import ActionLevel


class AuditLogger:
    """Sistema de Auditoria Estruturada."""

    LOG_FILE = "audit.log"

    @staticmethod
    def log_action(
        user: User,
        intent: str,
        action_level: ActionLevel,
        allowed: bool,
        reason: str,
        metadata: Dict[str, Any] = None
    ):
        """Registra uma ação no log de auditoria."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user.username,
            "role": user.role,
            "intent": intent,
            "level": action_level.name,
            "allowed": allowed,
            "reason": reason,
            "metadata": metadata or {}
        }

        try:
            with open(AuditLogger.LOG_FILE, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"[CRITICAL AUDIT FAILURE] {entry} - Erro: {e}")

    @staticmethod
    def read_logs(limit: int = 50) -> list:
        """Lê os últimos N logs de auditoria."""
        logs = []
        try:
            with open(AuditLogger.LOG_FILE, "r") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    logs.append(json.loads(line))
        except FileNotFoundError:
            pass
        return logs
