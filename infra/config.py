"""
Infrastructure Configuration Module.

Responsabilidade:
    - Centralizar configurações do sistema.
    - Ler variáveis de ambiente.
    - Prover acesso tipado a configurações (Singleton pattern via module-level instance ou class).

Regras:
    - Não conter lógica de negócio.
    - Suportar ambientes (DEV/PROD).
"""

import os
from enum import Enum
from typing import Optional
from pathlib import Path

# Carregar variáveis do .env
try:
    from dotenv import load_dotenv
    # Procurar .env no diretório raiz do projeto
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # Se python-dotenv não estiver instalado, continuar sem ele
    # (variáveis de ambiente do sistema ainda funcionarão)
    pass

class Environment(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"

class Settings:
    """
    Centraliza as configurações da aplicação.
    Padrão Singleton implícito (instanciado uma vez no container).
    """

    def __init__(self) -> None:
        self.env: Environment = self._get_env()
        self.app_name: str = "ORION-Core"
        self.version: str = "0.1.0"
        self.log_level: str = os.getenv("ORION_LOG_LEVEL", "INFO").upper()

        # LLM Configuration
        self.groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
        self.groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        self.ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3:latest")

        # UX Configuration
        self.system_name: str = os.getenv("ORION_SYSTEM_NAME", "ORION")
        self.user_name: str = os.getenv("ORION_USER_NAME", "User")

    def _get_env(self) -> Environment:
        env_str = os.getenv("ORION_ENV", "development").lower()
        if env_str in ("prod", "production"):
            return Environment.PRODUCTION
        return Environment.DEVELOPMENT

    @property
    def is_dev(self) -> bool:
        return self.env == Environment.DEVELOPMENT

    @property
    def is_prod(self) -> bool:
        return self.env == Environment.PRODUCTION

# Global instance mainly for simple access if needed, though Container preferred.
settings = Settings()
