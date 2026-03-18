"""
Filesystem Plugin.

Responsabilidade:
    - Ler arquivos e diretórios.
    - Limitar acesso apenas ao diretório do projeto (Sandbox simulada).
    - Bloquear acesso a diretórios sensíveis (core, pipeline, auth).
    - Executar operações de read, write, edit (via LLM), delete e move.
"""

import os
import shutil
from typing import Any, Dict
from plugins.base_plugin import BasePlugin
from core.logger import logger
from core.contracts import PluginResult
from core.container import Container
from core.ui import ConsoleUI

class FilesystemPlugin(BasePlugin):
    """Plugin de Sistema de Arquivos (Leitura/Escrita Segura)."""

    PROTECTED_PATHS = ["core", "pipeline", ".env", "users.json", ".git", ".venv", "audit.log"]

    def execute(self, params: Dict[str, Any]) -> PluginResult:
        """
        Executa operações de arquivo com filtro de segurança.
        Ações suportadas: list (default), read, write, edit, delete, move
        """
        cwd = os.getcwd()
        action = params.get("action", "list")
        
        try:
            if action == "list":
                return self._action_list(cwd)
            elif action == "read":
                return self._action_read(cwd, params)
            elif action == "write":
                return self._action_write(cwd, params)
            elif action == "edit":
                return self._action_edit(cwd, params)
            elif action == "delete":
                return self._action_delete(cwd, params)
            elif action == "move":
                return self._action_move(cwd, params)
            else:
                raise ValueError(f"Ação não suportada: {action}")
        except Exception as e:
            logger.error(f"[FSPlugin] Error: {e}")
            return PluginResult(
                data=[{"error": str(e)}],
                sources=[],
                confidence=0.0,
                degraded=True,
                plugin="filesystem"
            )

    def _is_safe_path(self, target_path: str, cwd: str) -> bool:
        """Garante que o caminho não acessa paths protegidos do sistema central do ORION."""
        try:
            expanded_path = os.path.expanduser(target_path)
            abs_path = os.path.abspath(expanded_path)
            
            # Se o arquivo alvo estiver dentro do cwd do ORION, validamos se não tenta tocar no núcleo (core, .env, etc).
            # Caminhos fora (ex: /home/user/Downloads) são permitidos, confiaremos no Governance (LEVEL 2).
            if abs_path.startswith(os.path.abspath(cwd)):
                rel_path = os.path.relpath(abs_path, cwd)
                parts = rel_path.split(os.sep)
                if any(p in self.PROTECTED_PATHS for p in parts):
                    return False
                
            return True
        except Exception:
            return False

    def _resolve_fuzzy_path(self, filename: str, cwd: str) -> str:
        """Resolve o caminho de um arquivo lidando com ~ e efetuando busca fuzzy se não encontrar diretamente."""
        expanded = os.path.expanduser(filename)
        
        # Testar existência direta
        if os.path.isabs(expanded):
            if os.path.exists(expanded):
                return expanded
        else:
            full_path = os.path.join(cwd, expanded)
            if os.path.exists(full_path):
                return full_path
                
        # Busca fuzzy em profundidade (DFS)
        base_name = os.path.basename(expanded).lower()
        search_dir = os.path.expanduser("~") if filename.startswith("~") else cwd
        
        matches = []
        for root, dirs, files in os.walk(search_dir):
            if len(matches) > 10: # Limita travamentos
                break
            # Ignorar dirs protegidos ou ocultos pra poupar CPU (pulamos apenas no top level de root ou genericamente)
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in self.PROTECTED_PATHS]
            
            for f in files:
                f_lower = f.lower()
                if f_lower == base_name or f_lower.startswith(base_name + "."):
                    matches.append(os.path.join(root, f))
                    
        if not matches:
             raise FileNotFoundError(f"Arquivo não encontrado (nem em busca aproximada): {filename}")
             
        if len(matches) == 1:
             return matches[0]
             
        # Desempate com UI
        ui = ConsoleUI()
        print(f"\n[FSPlugin] Foram encontrados vários arquivos parecidos com '{filename}'.")
        for idx, m in enumerate(matches, 1):
            print(f"  [{idx}] {m}")
            
        while True:
            choice = ui.input_user("\n> Digite o número correspondente (ou '0' para cancelar): ")
            if choice.strip() == "0":
                 raise FileNotFoundError("Busca de arquivo múltiplo cancelada pelo usuário.")
            try:
                idx = int(choice.strip())
                if 1 <= idx <= len(matches):
                     return matches[idx - 1]
            except ValueError:
                pass
            print("Opção inválida.")

    def _action_list(self, cwd: str) -> PluginResult:
        items = os.listdir(cwd)
        files = []
        dirs = []
        
        for item in items:
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
            plugin="fs",
            metadata={"path": cwd, "filtered": True}
        )

    def _action_read(self, cwd: str, params: Dict[str, Any]) -> PluginResult:
        filename = params.get("filename")
        if not filename:
             raise ValueError("filename é obrigatório para leitura.")
             
        full_path = self._resolve_fuzzy_path(filename, cwd)
        
        if not self._is_safe_path(full_path, cwd):
            raise PermissionError("Acesso negado: Tentativa de acessar caminho protegido.")
            
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return PluginResult(
            data=[{"filename": filename, "content": content}],
            sources=[],
            confidence=1.0,
            degraded=False,
            plugin="fs",
            metadata={"action": "read", "file": filename}
        )

    def _action_write(self, cwd: str, params: Dict[str, Any]) -> PluginResult:
        filename = params.get("filename")
        content = params.get("content")
        llm_instruction = params.get("llm_instruction")
        
        if not filename or content is None:
             raise ValueError("filename e content são obrigatórios para escrita.")
             
        # Pergunta no CLI sobre confirmação do Path onde quer salvar
        ui = ConsoleUI()
        nova_pasta = ui.input_user(f"Onde voce deseja salvar o arquivo '{filename}'? (Deixe em branco para salvar em {cwd}/): ")
        
        target_dir = cwd
        if nova_pasta.strip():
            # Tratar caminho relativo vs absoluto
            if os.path.isabs(nova_pasta):
                target_dir = nova_pasta
            else:
                target_dir = os.path.join(cwd, nova_pasta)

        full_path = os.path.join(target_dir, filename)
            
        if not self._is_safe_path(full_path, cwd):
             raise PermissionError(f"Acesso negado: Tentativa de acessar caminho protegido '{full_path}'.")

        # cria dirtório se não existir
        os.makedirs(os.path.dirname(full_path) or '.', exist_ok=True)
        
        # Inteligência extra: Se o Planner passou llm_instruction, o fs passa pelo LLM
        degraded = False
        if llm_instruction:
            logger.info("[FSPlugin] Processando conteúdo com LLM antes da gravação...")
            container = Container.get_instance()
            prompt = (
                 f"Siga estritamente esta instrução: {llm_instruction}\n\n"
                 f"BASE DE DADOS CRUA DE CONTEÚDO:\n"
                 f"```text\n{content}\n```\n\n"
                 "Retorne APENAS o texto final lapidado a ser salvo no arquivo, não de explicações de como você gerou. Se for relatório/resumo, use excelente formatação Markdown."
            )
            try:
                llm_res = container.llm_service.generate(prompt)
                content = llm_res.text.strip()
                degraded = llm_res.degraded
                
                # Strip raw markdown wrap if returned
                if content.startswith("```"):
                    lines = content.splitlines()
                    if len(lines) > 0 and lines[0].startswith("```"):
                        lines = lines[1:]
                    if len(lines) > 0 and lines[-1].strip() == "```":
                         lines = lines[:-1]
                    content = "\n".join(lines).strip()
            except Exception as e:
                logger.error(f"[FSPlugin] Falha ao sumariar write via LLM: {e}")

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return PluginResult(
            data=[{"filename": filename, "status": "created_or_updated"}],
            sources=[],
            confidence=1.0,
            degraded=degraded,
            plugin="fs",
            metadata={"action": "write", "path": full_path}
        )

    def _action_edit(self, cwd: str, params: Dict[str, Any]) -> PluginResult:
        filename = params.get("filename")
        instruction = params.get("instruction")
        
        if not filename or not instruction:
            raise ValueError("filename e instruction são obrigatórios para edição.")
            
        full_path = self._resolve_fuzzy_path(filename, cwd)
        
        if not self._is_safe_path(full_path, cwd):
            raise PermissionError("Acesso negado: Tentativa de acessar caminho protegido.")
             
        with open(full_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
            
        container = Container.get_instance()
        prompt = (
            f"O usuário pediu para editar o arquivo '{filename}' com a seguinte instrução:\n"
            f"{instruction}\n\n"
            f"Conteúdo Atual:\n"
            f"```text\n{current_content}\n```\n\n"
            "Retorne APENAS o NOVO CONTEÚDO final, de modo que ele não tenha explicações."
        )
        
        llm_res = container.llm_service.generate(prompt)
        new_content = llm_res.text.strip()
        
        # Strip markdown format if present
        if new_content.startswith("```"):
            lines = new_content.splitlines()
            if len(lines) > 0 and lines[0].startswith("```"):
                lines = lines[1:]
            if len(lines) > 0 and lines[-1].strip() == "```":
                 lines = lines[:-1]
            new_content = "\n".join(lines).strip()
            
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        return PluginResult(
            data=[{"filename": filename, "status": "edited"}],
            sources=[],
            confidence=1.0,
            degraded=llm_res.degraded,
            plugin="fs",
            metadata={"action": "edit"}
        )

    def _action_delete(self, cwd: str, params: Dict[str, Any]) -> PluginResult:
        filenames = params.get("filenames", [])
        if "filename" in params and params["filename"] not in filenames:
            filenames.append(params["filename"])
            
        if not filenames:
             raise ValueError("Nenhum arquivo especificado para deletar.")
             
        container = Container.get_instance()
        user = container.current_user
        
        if user and user.role != "admin" and len(filenames) > 3:
             raise PermissionError(f"Limite excedido: Usuários normais só podem deletar até 3 arquivos por vez. Solicitado: {len(filenames)}.")
             
        deleted = []
        for f in filenames:
            try:
                full_path = self._resolve_fuzzy_path(f, cwd)
            except FileNotFoundError:
                continue
                
            if not self._is_safe_path(full_path, cwd):
                 continue
                 
            if os.path.isfile(full_path):
                 os.remove(full_path)
            else:
                 shutil.rmtree(full_path)
            deleted.append(f)
                 
        return PluginResult(
            data=[{"deleted": deleted}],
            sources=[],
            confidence=1.0,
            degraded=False,
            plugin="fs",
            metadata={"action": "delete"}
        )

    def _action_move(self, cwd: str, params: Dict[str, Any]) -> PluginResult:
        source = params.get("source")
        filenames = params.get("filenames", [])
        destination = params.get("destination")
        
        if source and source not in filenames:
             filenames.append(source)
             
        if not filenames:
             raise ValueError("Nenhum arquivo especificado para mover (forneça source ou filenames).")
             
        # Questionar interativamente para onde mover
        ui = ConsoleUI()
        sugerido = destination if destination else f"{cwd}/"
        label_src = filenames[0] if len(filenames) == 1 else f"{len(filenames)} arquivos"
        nova_pasta = ui.input_user(f"Mover '{label_src}' para qual diretório? (Deixe em branco para usar {sugerido}): ")
        
        if nova_pasta.strip():
             destination = nova_pasta.strip()
        elif not destination:
             destination = cwd
             
        # Expandir ~ caso exista
        destination = os.path.expanduser(destination)
        
        # Tratar o destination como absoluto ou relativo
        if os.path.isabs(destination):
            full_dest = destination
        else:
            full_dest = os.path.join(cwd, destination)
            
        if not self._is_safe_path(full_dest, cwd):
             raise PermissionError(f"Acesso negado a destino protegido: {full_dest}")
             
        # Garante a existência do diretório alvo principal para onde moveremos os itens
        if not os.path.exists(full_dest):
             os.makedirs(full_dest, exist_ok=True)
             
        moved = []
        for src in filenames:
            try:
                full_source = self._resolve_fuzzy_path(src, cwd)
            except FileNotFoundError as e:
                logger.warning(f"[FSPlugin] Falha de resolução: {e}")
                continue
            
            if not self._is_safe_path(full_source, cwd):
                 logger.warning(f"[FSPlugin] Ignorando arquivo protegido ou inseguro: {full_source}")
                 continue
                 
            shutil.move(full_source, full_dest)
            moved.append(src)
        
        return PluginResult(
            data=[{"moved": moved, "destination": destination}],
            sources=[],
            confidence=1.0,
            degraded=False,
            plugin="fs",
            metadata={"action": "move"}
        )
