"""
Filesystem Plugin.

Responsabilidade:
    - Ler arquivos e diretórios.
    - Limitar acesso apenas ao diretório do projeto (Sandbox simulada).
"""

import os
from typing import Any, Dict
from plugins.base_plugin import BasePlugin
from core.logger import logger
from core.contracts import PluginResult

class FilesystemPlugin(BasePlugin):
    """Plugin de Sistema de Arquivos (Leitura)."""

    def execute(self, params: Dict[str, Any]) -> PluginResult:
        """
        Executa operações de arquivo.
        Returns:
            PluginResult com dados estruturados.
        """
        cwd = os.getcwd()
        try:
            items = os.listdir(cwd)
            files = [f for f in items if os.path.isfile(f)]
            dirs = [d for d in items if os.path.isdir(d)]
            
            data = {
                "cwd": cwd,
                "directories": dirs,
                "files": files
            }
            
            return PluginResult(
                data=[data],
                sources=[],
                confidence=1.0,
                degraded=False,
                plugin="filesystem",
                metadata={"path": cwd}
            )
        except Exception as e:
            logger.error(f"[FSPlugin] Error: {e}")
            return PluginResult(
                data=[{"error": str(e)}],
                sources=[],
                confidence=0.0,
                degraded=True,
                plugin="filesystem"
            )
