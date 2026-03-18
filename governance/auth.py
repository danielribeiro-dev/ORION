"""
Authentication Module.

Responsabilidade:
    - Gerenciar usuários e roles.
    - Autenticação local segura (bcrypt).
    - Persistência de credenciais em users.json.

Movido de core/auth.py → governance/auth.py (v0.4.0 reestruturação).
"""

import json
import bcrypt
import os
from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass, asdict
from core.logger import logger


class Role(Enum):
    ADMIN = "admin"           # Todas as permissões
    POWER_USER = "power_user" # Pode executar L2 com supervisão
    USER = "user"             # Pode executar L1, L2 requer aprovação
    GUEST = "guest"           # Limitado a L0/L1


@dataclass
class User:
    username: str
    password_hash: str
    role: str
    active: bool = True


class AuthService:
    """Serviço de Autenticação e Gestão de Usuários."""

    FILE_PATH = "users.json"

    def __init__(self):
        self._users: Dict[str, User] = {}
        self._load_users()

    def _load_users(self):
        """Carrega usuários do arquivo JSON."""
        if not os.path.exists(self.FILE_PATH):
            self._create_default_admin()
            return

        try:
            with open(self.FILE_PATH, 'r') as f:
                data = json.load(f)
                for uname, udata in data.items():
                    self._users[uname] = User(**udata)
        except Exception as e:
            logger.error(f"[Auth] Falha ao carregar usuários: {e}")
            self._create_default_admin()

    def _save_users(self):
        """Salva usuários no arquivo JSON."""
        try:
            data = {uname: asdict(user) for uname, user in self._users.items()}
            with open(self.FILE_PATH, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"[Auth] Falha ao salvar usuários: {e}")

    def _create_default_admin(self):
        """Cria usuário admin padrão se não existir."""
        logger.info("[Auth] Criando usuário admin padrão.")
        hashed = bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin = User(
            username="admin",
            password_hash=hashed,
            role=Role.ADMIN.value,
            active=True
        )
        self._users["admin"] = admin
        self._save_users()

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Autentica um usuário."""
        user = self._users.get(username)
        if not user or not user.active:
            return None

        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return user
        return None

    def get_user(self, username: str) -> Optional[User]:
        return self._users.get(username)

    def create_user(self, username: str, password: str, role: Role) -> bool:
        """Cria um novo usuário."""
        if username in self._users:
            return False

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(
            username=username,
            password_hash=hashed,
            role=role.value,
            active=True
        )
        self._users[username] = new_user
        self._save_users()
        logger.info(f"[Auth] Usuário '{username}' criado com role '{role.value}'.")
        return True
