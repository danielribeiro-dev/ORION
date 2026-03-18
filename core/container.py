"""
Dependency Injection Container.

Responsabilidade:
    - Centralizar a criação e injeção de dependências.
    - Gerenciar singletons.
    - Prover acesso aos componentes principais.
    - Expor current_user carregado do perfil persistente.

v0.4.0 — Reestruturação:
    - pipeline.* → cognition.*
    - core.auth / core.audit → governance.*
    - plugins.*_plugin → plugins.<sub>.*
"""

from typing import Optional

from core.config import settings, Settings
from core.logger import logger
from core.runtime import Runtime

# Governance (movidos de core/ e pipeline/)
from governance.auth import AuthService, User
from governance.policy import GovernanceEngine

# Cognition (movidos de pipeline/)
from cognition.router import Router
from cognition.planner import Planner
from cognition.executor import Executor
from cognition.answer import AnswerPipeline

# LLM
from llm.service import LLMService

# Memory
from memory.profile import ProfileMemory     # via memory/profile/__init__.py
from memory.history import HistoryMemory     # via memory/history/__init__.py
from memory.semantic import SemanticMemory
from memory.extractor import MemoryExtractor


class Container:
    """
    Container de injeção de dependências — Singleton.
    """

    _instance: Optional['Container'] = None

    def __init__(self) -> None:
        self.settings: Settings = settings
        self.logger = logger

        # Memory
        self.profile = ProfileMemory(
            default_system=settings.system_name,
            default_user=settings.user_name
        )
        self.history = HistoryMemory()

        # Auth (singleton — não instanciar fora do Container)
        self.auth_service = AuthService()

        # Governance
        self.capability_guard = GovernanceEngine()

        # LLM
        self.llm_service = LLMService()

        # Semantic Long-Term Memory
        self.semantic_memory = SemanticMemory()
        self.memory_extractor = MemoryExtractor()

        # Plugins (carregados dos subpacotes)
        from plugins.chat import ChatPlugin
        from plugins.web import WebPlugin
        from plugins.filesystem import FilesystemPlugin
        from plugins.memory import MemoryPlugin
        from plugins.memory_search_plugin import MemorySearchPlugin

        self.plugins = {
            "chat": ChatPlugin(),
            "web": WebPlugin(),
            "fs": FilesystemPlugin(),
            "memory": MemoryPlugin(),
            "memory_search": MemorySearchPlugin(self.semantic_memory)
        }

        # Cognition Pipeline
        self.router = Router()
        self.planner = Planner()
        self.executor = Executor()
        self.answer_pipeline = AnswerPipeline()

        # Runtime
        self.runtime = Runtime()

    @classmethod
    def get_instance(cls) -> 'Container':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def current_user(self) -> Optional[User]:
        """
        Retorna o usuário da sessão atual, carregado do profile.json.
        Não requer login: o usuário é persistido entre sessões.
        """
        session_data = self.profile.get_current_user()
        username = session_data.get("username", "admin")

        # Tentar buscar usuário cadastrado no AuthService
        user = self.auth_service.get_user(username)

        if user:
            return user

        # Fallback: criar User temporário a partir dos dados do perfil
        return User(
            username=username,
            password_hash="",
            role=session_data.get("role", "admin"),
            active=True
        )
