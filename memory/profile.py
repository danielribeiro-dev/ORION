"""
Profile Memory Module.

Gerencia persistência de dados do perfil do sistema, usuário e sessão ativa.

v0.4.0: Adicionado suporte a usuário de sessão persistente.
        O usuário não precisa logar a cada inicialização — a sessão é salva
        diretamente em profile.json com username, role e dev_mode.
"""

import json
import os
from typing import Any, Dict, Optional
from memory.base import BaseMemory
from core.logger import logger


class ProfileMemory(BaseMemory):
    """
    Memória de Perfil (User & System & Sessão).
    """

    # Dados padrão quando o perfil não existe
    _DEFAULTS: Dict[str, Any] = {
        "system_name": "ORION",
        "user_name": "User",
        "language": "pt-BR",
        "preferences": {},
        # Sessão persistente — sem necessidade de login a cada startup
        "current_user": {
            "username": "admin",
            "role": "admin",
            "dev_mode": False
        }
    }

    def __init__(
        self,
        filepath: str = "memory/profile.json",
        default_system: str = "ORION",
        default_user: str = "User",
        default_language: str = "pt-BR"
    ) -> None:
        self.filepath = filepath
        self.data: Dict[str, Any] = {
            **self._DEFAULTS,
            "system_name": default_system,
            "user_name": default_user,
            "language": default_language,
        }
        self.load()

    def load(self) -> None:
        """Carrega perfil do JSON, com retrocompatibilidade."""
        if not os.path.exists(self.filepath):
            logger.info("[ProfileMemory] Nenhum perfil encontrado, usando padrões.")
            self.save()
            return

        try:
            with open(self.filepath, 'r') as f:
                loaded = json.load(f)

            # Retrocompatibilidade: garante que novos campos existam
            for key, default_value in self._DEFAULTS.items():
                if key not in loaded:
                    loaded[key] = default_value

            self.data = loaded
            logger.info("[ProfileMemory] Perfil carregado.")
        except Exception as e:
            logger.error(f"[ProfileMemory] Falha ao carregar: {e}")

    def save(self) -> None:
        """Salva perfil no JSON."""
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
            logger.debug("[ProfileMemory] Perfil salvo.")
        except Exception as e:
            logger.error(f"[ProfileMemory] Falha ao salvar: {e}")

    # =========================================================
    # Getters / Setters — Sistema
    # =========================================================

    def get_system_name(self) -> str:
        return self.data.get("system_name", "ORION")

    def set_system_name(self, name: str) -> None:
        self.data["system_name"] = name
        self.save()
        logger.info(f"[ProfileMemory] Nome do sistema alterado para: {name}")

    def get_user_name(self) -> str:
        return self.data.get("user_name", "User")

    def set_user_name(self, name: str) -> None:
        self.data["user_name"] = name
        self.save()
        logger.info(f"[ProfileMemory] Nome do usuário alterado para: {name}")

    def get_language(self) -> str:
        return self.data.get("language", "pt-BR")

    def set_language(self, language: str) -> None:
        self.data["language"] = language
        self.save()
        logger.info(f"[ProfileMemory] Idioma alterado para: {language}")

    def get_preferences(self) -> str:
        """Retorna as preferências do usuário como string."""
        prefs = self.data.get("preferences", "")
        if isinstance(prefs, dict):
            if not prefs:
                return ""
            return json.dumps(prefs, ensure_ascii=False)
        return str(prefs)

    # =========================================================
    # Sessão de Usuário Persistente (v0.4.0)
    # =========================================================

    def get_current_user(self) -> Dict[str, Any]:
        """
        Retorna os dados do usuário de sessão atual.

        Returns:
            Dict com 'username', 'role', 'dev_mode'.
            Nunca retorna None — usa admin como fallback seguro.
        """
        session = self.data.get("current_user", {})
        # Garante campos obrigatórios mesmo em perfis antigos
        return {
            "username": session.get("username", "admin"),
            "role": session.get("role", "admin"),
            "dev_mode": session.get("dev_mode", False)
        }

    def set_current_user(self, username: str, role: str, dev_mode: bool = False) -> None:
        """
        Persiste o usuário de sessão em profile.json.

        Não exige login a cada startup — o usuário configurado aqui
        será restaurado automaticamente na próxima inicialização.

        Args:
            username: Nome do usuário (ex: 'daniel')
            role: Papel do usuário (ex: 'admin', 'power_user', 'user', 'guest')
            dev_mode: Se True, ativa funcionalidades de desenvolvimento
        """
        self.data["current_user"] = {
            "username": username,
            "role": role,
            "dev_mode": dev_mode
        }
        self.save()
        logger.info(f"[ProfileMemory] Sessão persistida: {username} ({role}), dev_mode={dev_mode}")

    def get_current_role(self) -> str:
        """Atalho para obter a role do usuário atual."""
        return self.get_current_user().get("role", "admin")

    def is_dev_mode(self) -> bool:
        """Atalho para verificar se dev_mode está ativo."""
        return self.get_current_user().get("dev_mode", False)
