"""
Dependency Injection Container.

Responsabilidade:
    - Centralizar a criação e injeção de dependências.
    - Gerenciar singletons.
    - Prover acesso aos componentes principais.
    - Expor current_user carregado do perfil persistente (v0.4.0).

v0.4.0:
    - Adicionada propriedade current_user (sessão persistente sem login).
    - AuthService instanciado aqui como singleton (removido do Executor).
"""

from typing import Optional

from core.config import settings, Settings
from core.logger import logger
from core.runtime import Runtime
from core.auth import AuthService, User
from pipeline.router import Router
from pipeline.planner import Planner
from pipeline.executor import Executor
from pipeline.answer import AnswerPipeline
from pipeline.policy import GovernanceEngine
from llm.service import LLMService
from memory.profile import ProfileMemory
from memory.history import HistoryMemory


class Container:
    """
    Container de injeção de dependências.
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

        # Auth (singleton aqui, não instanciado por quem consome)
        self.auth_service = AuthService()

        # Core Services
        self.capability_guard = GovernanceEngine()
        self.llm_service = LLMService()

        # Plugins
        from plugins.chat_plugin import ChatPlugin
        from plugins.web_plugin import WebPlugin
        from plugins.fs_plugin import FilesystemPlugin
        from plugins.memory_plugin import MemoryPlugin

        self.plugins = {
            "chat": ChatPlugin(),
            "web": WebPlugin(),
            "fs": FilesystemPlugin(),
            "memory": MemoryPlugin()
        }

        # Pipeline Components
        self.router = Router()
        self.planner = Planner()
        self.executor = Executor()
        self.answer_pipeline = AnswerPipeline()
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
        Se não existir no AuthService (ex: usuário customizado), cria
        um objeto User temporário a partir dos dados do perfil.
        """
        session_data = self.profile.get_current_user()
        username = session_data.get("username", "admin")

        # Tentar buscar do AuthService (usuário real cadastrado)
        user = self.auth_service.get_user(username)

        if user:
            return user

        # Fallback: criar objeto User com dados do perfil (sem hash de senha)
        # Permite que nomes customizados (ex: "daniel") funcionem mesmo sem
        # estar cadastrados formalmente no users.json
        from core.auth import User as UserModel
        return UserModel(
            username=username,
            password_hash="",       # Sessão persistida, sem necessidade de senha
            role=session_data.get("role", "admin"),
            active=True
        )
