"""
Profile Memory Module.

Gerencia persistência de dados do perfil do sistema e usuário.
"""

import json
import os
from typing import Dict, Any
from memory.base import BaseMemory
from infra.logger import logger

class ProfileMemory(BaseMemory):
    """
    Memória de Perfil (User & System).
    """

    def __init__(self, filepath: str = "memory/profile.json", default_system: str = "ORION", default_user: str = "User") -> None:
        self.filepath = filepath
        self.data: Dict[str, Any] = {
            "system_name": default_system,
            "user_name": default_user,
            "preferences": {}
        }
        self.load()

    def load(self) -> None:
        """Carrega perfil do JSON."""
        if not os.path.exists(self.filepath):
            logger.info("[ProfileMemory] No profile found, using defaults.")
            self.save() # Persist defaults
            return

        try:
            with open(self.filepath, 'r') as f:
                self.data = json.load(f)
            logger.info("[ProfileMemory] Profile loaded.")
        except Exception as e:
            logger.error(f"[ProfileMemory] Load failed: {e}")

    def save(self) -> None:
        """Salva perfil no JSON."""
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w') as f:
                json.dump(self.data, f, indent=4)
            logger.debug("[ProfileMemory] Profile saved.")
        except Exception as e:
            logger.error(f"[ProfileMemory] Save failed: {e}")

    def get_system_name(self) -> str:
        return self.data.get("system_name", "ORION")

    def get_user_name(self) -> str:
        return self.data.get("user_name", "User")
