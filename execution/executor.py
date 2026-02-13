"""
Executor Module.

Responsabilidade:
    - Executar o plano de ações gerado pelo Planner.
    - Invocar plugins e ferramentas.
    - Coletar resultados brutos.

Proibições:
    - Não decide o que fazer (apenas executa o que foi planejado).
    - Não inventa dados.
"""

from typing import Any, List, Union
from execution.base import BaseExecutor
from infra.contracts import PluginResult

class Executor(BaseExecutor):
    """
    Motor de execução que processa o plano de ações.
    """

    def execute(self, plan: List[Any]) -> Union[str, PluginResult]:
        """
        Executa sequencialmente os passos do plano.
        Format: [(plugin_name, params), ...]
        
        Returns:
            PluginResult se algum plugin retornar PluginResult,
            senão retorna string (compatibilidade retroativa).
        """
        from infra.container import Container
        container = Container.get_instance()
        
        results = []
        plugin_result = None  # Armazena o primeiro PluginResult encontrado
        
        for step in plan:
            plugin_name, params = step
            plugin = container.plugins.get(plugin_name)
            
            if plugin:
                try:
                    res = plugin.execute(params)
                    
                    # Se retornou PluginResult, armazenar
                    if isinstance(res, PluginResult):
                        plugin_result = res
                        results.append(f"[{plugin_name}] Retrieved {len(res.data)} results")
                    else:
                        # String ou outro tipo (legado)
                        results.append(str(res))
                        
                except Exception as e:
                    results.append(f"Error executing {plugin_name}: {e}")
            else:
                results.append(f"Plugin '{plugin_name}' not found.")
        
        # Se algum plugin retornou PluginResult, retornar ele
        # (Answer Pipeline processará os dados estruturados)
        if plugin_result:
            return plugin_result
        
        # Caso contrário, retornar string concatenada (legado)
        return "\n".join(results)
