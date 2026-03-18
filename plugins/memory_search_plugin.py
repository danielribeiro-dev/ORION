from plugins.base_plugin import BasePlugin
from core.contracts import PluginResult


class MemorySearchPlugin(BasePlugin):
    """
    Busca rápida na nova arquitetura vetorial contendo memóricas duradouras ou operacionais relacionadas.
    """
    
    name = "memory_search"
    description = "Busca informações na memória de longo prazo do ORION"
    
    def __init__(self, semantic_memory):
        self.semantic_memory = semantic_memory

    def execute(self, params: dict) -> PluginResult:
        if not self.semantic_memory or not self.semantic_memory.is_available():
            return PluginResult(
                plugin="memory_search",
                success=False,
                data=[],
                degraded=True,
                metadata={"error": "Subsistema de memória indisponível no momento."}
            )
            
        query = params.get("query", "")
        # coleções limitadoras para buscar caso desejado em "params"
        collections = params.get("collections", None)
        
        if not query:
             return PluginResult(
                 plugin="memory_search",
                 success=False,
                 data=[],
                 degraded=True,
                 metadata={"error": "Parâmetro 'query' ausente."}
             )
        
        try:
             matches = self.semantic_memory.search(query, collections, top_k=6)
             
             if not matches:
                 return PluginResult(
                     plugin="memory_search",
                     success=True,
                     data=[{"content": "Não encontrei nada relevante na memória sobre isso."}],
                     degraded=False
                 )
                 
             formatted_data = []
             for res in matches:
                 if res.collection == "orion_episodic":
                     ts = res.metadata.get("timestamp", "...")
                     formatted_data.append({
                         "type": "episodic",
                         "date": ts,
                         "content": res.text
                     })
                 elif res.collection == "orion_semantic":
                     cat = res.metadata.get("category", "")
                     formatted_data.append({
                         "type": "semantic",
                         "category": cat,
                         "content": res.text
                     })
                 elif res.collection == "orion_procedural":
                     seq = res.metadata.get("sequence", "[]") # Json repassado nativo
                     formatted_data.append({
                         "type": "procedural",
                         "trigger": res.text,
                         "sequence": seq
                     })
             
             return PluginResult(
                 plugin="memory_search",
                 success=True,
                 data=formatted_data,
                 degraded=False
             )
             
        except Exception as e:
             return PluginResult(
                 plugin="memory_search",
                 success=False,
                 data=[],
                 degraded=True,
                 metadata={"error": str(e)}
             )
