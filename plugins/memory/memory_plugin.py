"""
Memory Plugin.

Responsabilidade:
    - Gerenciar alterações persistentes na memória de perfil (ProfileMemory).
    - Lidar com intents do tipo MEMORY.
"""

from typing import Any, Dict
from plugins.base_plugin import BasePlugin
from core.container import Container
from core.contracts import PluginResult
from core.logger import logger

class MemoryPlugin(BasePlugin):
    """Plugin para gerenciamento de memória persistente (Perfil)."""

    def execute(self, params: Dict[str, Any]) -> PluginResult:
        """
        Executa comandos de memória (alteração de perfil).
        """
        container = Container.get_instance()
        action = params.get("action")
        value = params.get("value")
        query = params.get("user_input", "")

        if action == "set_system_name":
            container.profile.set_system_name(value)
            msg = f"Nome do sistema alterado para: {value}"
        elif action == "set_user_name":
            container.profile.set_user_name(value)
            msg = f"Nome do usuário alterado para: {value}"
        elif action == "set_system_language":
            container.profile.set_language(value)
            msg = f"Idioma do sistema alterado para: {value}"
        else:
            msg = "Comando de memória não reconhecido."
            logger.warning(f"[MemoryPlugin] Unknown action: {action}")

        return PluginResult(
            data=[{"message": msg}],
            sources=[],
            confidence=1.0,
            degraded=False,
            plugin="memory",
            metadata={"query": query, "action": action, "value": value}
        )
