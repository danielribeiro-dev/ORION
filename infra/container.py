"""
Dependency Injection Container.

Responsabilidade:
    - Centralizar a criação e injeção de dependências.
    - Gerenciar singletons.
    - Prover acesso aos componentes principais.

Regras:
    - O main.py deve usar este container para inicializar o sistema.
"""

from typing import Optional

from infra.config import settings, Settings
from infra.logger import logger
from runtime.lifecycle import Runtime
from routing.router import Router
from planning.planner import Planner
from execution.executor import Executor
from answer.answer_pipeline import AnswerPipeline
from policies.capability_guard import CapabilityGuard
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

        # Core Services
        self.capability_guard = CapabilityGuard()
        self.llm_service = LLMService()
        
        # Plugins
        from plugins.chat_plugin import ChatPlugin
        from plugins.web_plugin import WebPlugin
        from plugins.fs_plugin import FilesystemPlugin
        
        self.plugins = {
            "chat": ChatPlugin(),
            "web": WebPlugin(),
            "fs": FilesystemPlugin()
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
