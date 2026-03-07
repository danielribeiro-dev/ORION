"""
Filesystem Plugin.

Responsabilidade:
    - Ler arquivos e diretórios.
    - Limitar acesso apenas ao diretório do projeto (Sandbox simulada).
    - Bloquear acesso a diretórios sensíveis (core, pipeline, auth).
"""

import os
from typing import Any, Dict
from plugins.base_plugin import BasePlugin
from core.logger import logger
from core.contracts import PluginResult

class FilesystemPlugin(BasePlugin):
    """Plugin de Sistema de Arquivos (Leitura Segura)."""

    PROTECTED_PATHS = ["core", "pipeline", ".env", "users.json", ".git", ".venv", "audit.log"]

    def execute(self, params: Dict[str, Any]) -> PluginResult:
        """
        Executa operações de arquivo com filtro de segurança.
        Returns:
            PluginResult com dados estruturados.
        """
        cwd = os.getcwd()
        
        try:
            items = os.listdir(cwd)
            files = []
            dirs = []
            
            for item in items:
                # Security Filter: Hide protected paths from listing
                if item in self.PROTECTED_PATHS:
                    continue
                    
                full_path = os.path.join(cwd, item)
                if os.path.isdir(full_path):
                    dirs.append(item)
                elif os.path.isfile(full_path):
                    files.append(item)
            
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
                plugin="fs",  # v0.4.0: padronizado para bater com a chave no Container (BUG-04)
                metadata={"path": cwd, "filtered": True}
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
