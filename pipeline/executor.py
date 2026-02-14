"""
Executor Module.

Responsabilidade:
    - Executar o plano de ações gerado pelo Planner.
    - Invocar plugins e ferramentas.
    - Coletar resultados brutos.

Proibições:
    - OBRIGATÓRIO retornar sempre PluginResult (v0.2.2).
    - Não decide o que fazer.
"""

from typing import Any, List
from core.interfaces import BaseExecutor
from core.contracts import PluginResult
from core.logger import logger

class Executor(BaseExecutor):
    """
    Motor de execução que processa o plano de ações.
    """

    def execute(self, plan: List[Any]) -> PluginResult:
        """
        Executa sequencialmente os passos do plano.
        Format: [(plugin_name, params), ...]
        
        Returns:
            PluginResult estruturado (Mandatório na v0.2.2).
        """
        from core.container import Container
        container = Container.get_instance()
        
        # v0.2.2: Na fase atual de plano sequencial de um passo,
        # retornamos o resultado do último plugin executado.
        # Para planos multi-step futuros, será necessária agregação.
        
        last_result = None
        
        for step in plan:
            plugin_name, params = step
            plugin = container.plugins.get(plugin_name)
            
            if plugin:
                try:
                    logger.info(f"[Executor] Executing plugin: {plugin_name}")
                    res = plugin.execute(params)
                    
                    if isinstance(res, PluginResult):
                        last_result = res
                    else:
                        logger.error(f"[Executor] Plugin {plugin_name} did not return PluginResult!")
                        # Fallback for safety during migration
                        last_result = self._wrap_legacy(plugin_name, res)
                        
                except Exception as e:
                    logger.error(f"[Executor] Error executing {plugin_name}: {e}")
                    last_result = self._create_error_result(plugin_name, str(e))
            else:
                logger.error(f"[Executor] Plugin '{plugin_name}' not found.")
                last_result = self._create_error_result(plugin_name, "Plugin not found")
        
        if not last_result:
            return self._create_error_result("executor", "Empty plan or no results")
            
        return last_result

    def _wrap_legacy(self, plugin: str, legacy_res: Any) -> PluginResult:
        """Encapsula resultado legado em PluginResult."""
        return PluginResult(
            data=[{"legacy_output": str(legacy_res)}],
            sources=[],
            confidence=0.5,
            degraded=True,
            plugin=plugin,
            metadata={"warning": "legacy_output_wrap"}
        )

    def _create_error_result(self, plugin: str, error_msg: str) -> PluginResult:
        """Cria um resultado de erro estruturado."""
        return PluginResult(
            data=[{"error": error_msg}],
            sources=[],
            confidence=0.0,
            degraded=True,
            plugin=plugin
        )
