"""
Filesystem Plugin.

Responsabilidade:
    - Ler arquivos e diretórios.
    - Limitar acesso apenas ao diretório do projeto (Sandbox simulada).
"""

import os
from typing import Any, Dict
from plugins.base_plugin import BasePlugin
from infra.logger import logger

class FilesystemPlugin(BasePlugin):
    """Plugin de Sistema de Arquivos (Leitura)."""

    def execute(self, params: Dict[str, Any]) -> str:
        """
        Executa operações de arquivo.
        Params:
            - operation: list_dir | read_file
            - path: caminho alvo
        """
        # Default behavior: if no specific op, list current dir or summarize
        # For this phase, we map user input to list_dir of cwd
        
        cwd = os.getcwd()
        try:
            items = os.listdir(cwd)
            files = [f for f in items if os.path.isfile(f)]
            dirs = [d for d in items if os.path.isdir(d)]
            
            output = f"Current Directory ({cwd}):\n"
            output += "Directories:\n" + "\n".join([f"  [DIR] {d}" for d in dirs]) + "\n"
            output += "Files:\n" + "\n".join([f"  {f}" for f in files])
            
            return output
        except Exception as e:
            logger.error(f"[FSPlugin] Error: {e}")
            return f"Error accessing filesystem: {e}"
