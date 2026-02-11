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

from typing import Any, List
from execution.base import BaseExecutor

class Executor(BaseExecutor):
    """
    Motor de execução que processa o plano de ações.
    """

    def execute(self, plan: List[Any]) -> Any:
        """
        Executa sequencialmente os passos do plano.
        Format: [(plugin_name, params), ...]
        """
        from infra.container import Container
        container = Container.get_instance()
        
        results = []
        
        for step in plan:
            plugin_name, params = step
            plugin = container.plugins.get(plugin_name)
            
            if plugin:
                try:
                    res = plugin.execute(params)
                    results.append(str(res))
                except Exception as e:
                    results.append(f"Error executing {plugin_name}: {e}")
            else:
                results.append(f"Plugin '{plugin_name}' not found.")
                
        return "\n".join(results)
