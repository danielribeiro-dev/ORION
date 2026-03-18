"""
Web Plugin - Real Implementation.

Responsabilidade:
    - Realizar buscas na web usando API real.
    - Filtrar e rankear resultados por relevância.
    - Retornar dados estruturados (PluginResult).

Proibições:
    - Não decide o que fazer com os dados.
    - Não formata resposta final ao usuário.
    - Não simula resultados.
"""

from typing import Any, Dict, List
from plugins.base_plugin import BasePlugin
from core.logger import logger
from core.contracts import PluginResult
import hashlib
import time
from datetime import datetime, timedelta

class WebPlugin(BasePlugin):
    """Plugin de Busca Web com integração real."""

    def __init__(self):
        """Inicializa o WebPlugin."""
        self.max_results = 10  # Limite padrão de resultados
        self.min_score = 0.3  # Score mínimo base
        self.adaptive_threshold = True  # Threshold dinâmico
        
        # Cache de buscas (v0.2.1)
        self.cache = {}  # {query_hash: (result, timestamp)}
        self.cache_ttl = timedelta(hours=1)  # TTL de 1 hora
        
        # Rate limiting (v0.2.1)
        self.requests = []  # [(timestamp, query), ...]
        self.max_requests_per_minute = 10

    def execute(self, params: Dict[str, Any]) -> PluginResult:
        """
        Executa busca web real com cache e rate limiting.
        
        Args:
            params: Dicionário com 'user_input' contendo a query
            
        Returns:
            PluginResult estruturado com dados, fontes e confiança
        """
        query = params.get("user_input", "")
        logger.info(f"[WebPlugin] Searching for: {query}")
        
        # Verificar rate limit (v0.2.1)
        try:
            self._check_rate_limit(query)
        except Exception as e:
            logger.warning(f"[WebPlugin] Rate limit exceeded: {e}")
            return self._create_error_result(str(e), query)
        
        # Verificar cache (v0.2.1)
        cached_result = self._get_from_cache(query)
        if cached_result:
            logger.info(f"[WebPlugin] Cache hit for: {query}")
            return cached_result
        
        try:
            # Importar duckduckgo_search
            # Importar DDGS (preferencialmente de ddgs ou fallback)
            try:
                from ddgs import DDGS
            except ImportError:
                try:
                    from duckduckgo_search import DDGS
                except ImportError:
                    logger.error("[WebPlugin] ddgs/duckduckgo-search not installed. Install with: pip install ddgs")
                    return self._create_error_result(
                        "Web search unavailable: ddgs package not installed",
                        query
                    )
            
            # Realizar busca
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.max_results))
            
            if not results:
                logger.warning(f"[WebPlugin] No results found for: {query}")
                return PluginResult(
                    data=[],
                    sources=[],
                    confidence=0.0,
                    degraded=False,
                    plugin="web",
                    metadata={"query": query, "result_count": 0}
                )
            
            # Processar e rankear resultados
            processed_results = self._process_results(results)
            
            # Deduplicar por URL
            deduplicated = self._deduplicate(processed_results)
            
            # Calcular threshold dinâmico (v0.2.1)
            threshold = self._calculate_threshold(deduplicated)
            
            # Filtrar por score mínimo
            filtered = [r for r in deduplicated if r["score"] >= threshold]
            
            # Ordenar por score (maior primeiro)
            ranked = sorted(filtered, key=lambda x: x["score"], reverse=True)
            
            # Preparar fontes
            sources = [
                {
                    "title": r["title"],
                    "url": r["url"],
                    "score": r["score"]
                }
                for r in ranked
            ]
            
            # Preparar dados (corpo dos resultados)
            data = [
                {
                    "title": r["title"],
                    "body": r["body"],
                    "url": r["url"]
                }
                for r in ranked
            ]
            
            # Calcular confiança baseada na quantidade e qualidade dos resultados
            confidence = self._calculate_confidence(ranked)
            
            logger.info(f"[WebPlugin] Found {len(ranked)} relevant results (confidence: {confidence:.2f})")
            
            result = PluginResult(
                data=data,
                sources=sources,
                confidence=confidence,
                degraded=False,
                plugin="web",
                metadata={
                    "query": query,
                    "result_count": len(ranked),
                    "total_found": len(results),
                    "deduplicated": len(results) - len(deduplicated),
                    "filtered_by_score": len(deduplicated) - len(filtered),
                    "threshold_used": threshold
                }
            )
            
            # Cachear resultado (v0.2.1)
            self._save_to_cache(query, result)
            
            return result
            
        except Exception as e:
            logger.error(f"[WebPlugin] Search failed: {e}")
            return self._create_error_result(str(e), query)
    
    def _process_results(self, results: List[Dict]) -> List[Dict]:
        """
        Processa resultados brutos e calcula score de relevância.
        
        Score baseado em:
        - Posição no ranking (primeiros resultados têm maior score)
        - Presença de body (resultados com descrição são mais relevantes)
        """
        processed = []
        for idx, result in enumerate(results):
            # Score baseado na posição (1.0 para primeiro, decai linearmente)
            position_score = 1.0 - (idx / len(results)) * 0.5
            
            # Bonus se tem body
            has_body = bool(result.get("body", "").strip())
            body_bonus = 0.2 if has_body else 0.0
            
            score = min(position_score + body_bonus, 1.0)
            
            processed.append({
                "title": result.get("title", "Untitled"),
                "url": result.get("href", result.get("url", "")),
                "body": result.get("body", ""),
                "score": score
            })
        
        return processed
    
    def _deduplicate(self, results: List[Dict]) -> List[Dict]:
        """Remove resultados duplicados baseado na URL."""
        seen_urls = set()
        deduplicated = []
        
        for result in results:
            url = result["url"]
            if url not in seen_urls:
                seen_urls.add(url)
                deduplicated.append(result)
            else:
                logger.debug(f"[WebPlugin] Duplicate URL removed: {url}")
        
        return deduplicated
    
    def _calculate_confidence(self, results: List[Dict]) -> float:
        """
        Calcula confiança geral baseada na quantidade e qualidade dos resultados.
        
        Lógica:
        - 0 resultados: 0.0
        - 1-2 resultados: 0.5
        - 3-5 resultados: 0.7
        - 6+ resultados: 0.85
        - Ajustado pela média dos scores
        """
        if not results:
            return 0.0
        
        count = len(results)
        
        # Base confidence por quantidade
        if count >= 6:
            base = 0.85
        elif count >= 3:
            base = 0.7
        elif count >= 1:
            base = 0.5
        else:
            base = 0.0
        
        # Ajustar pela média dos scores
        avg_score = sum(r["score"] for r in results) / len(results)
        
        # Confiança final é média ponderada (70% base, 30% avg_score)
        confidence = base * 0.7 + avg_score * 0.3
        
        return min(confidence, 1.0)
    
    def _create_error_result(self, error_message: str, query: str) -> PluginResult:
        """Cria PluginResult de erro."""
        return PluginResult(
            data=[],
            sources=[],
            confidence=0.0,
            degraded=True,
            plugin="web",
            metadata={
                "error": error_message,
                "query": query
            }
        )
    
    # ========== v0.2.1: Cache Methods ==========
    
    def _get_query_hash(self, query: str) -> str:
        """Gera hash MD5 da query para usar como chave de cache."""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def _get_from_cache(self, query: str) -> PluginResult | None:
        """
        Recupera resultado do cache se existir e não estiver expirado.
        
        Returns:
            PluginResult se cache hit, None se cache miss
        """
        query_hash = self._get_query_hash(query)
        
        if query_hash not in self.cache:
            return None
        
        result, timestamp = self.cache[query_hash]
        
        # Verificar se cache expirou
        if datetime.now() - timestamp > self.cache_ttl:
            logger.debug(f"[WebPlugin] Cache expired for: {query}")
            del self.cache[query_hash]
            return None
        
        return result
    
    def _save_to_cache(self, query: str, result: PluginResult):
        """Salva resultado no cache."""
        query_hash = self._get_query_hash(query)
        self.cache[query_hash] = (result, datetime.now())
        logger.debug(f"[WebPlugin] Cached result for: {query}")
    
    # ========== v0.2.1: Rate Limiting ==========
    
    def _check_rate_limit(self, query: str):
        """
        Verifica se rate limit foi excedido.
        
        Raises:
            Exception se rate limit excedido
        """
        now = time.time()
        
        # Remover requests antigas (> 1 minuto)
        self.requests = [(t, q) for t, q in self.requests if now - t < 60]
        
        if len(self.requests) >= self.max_requests_per_minute:
            raise Exception(
                f"Rate limit exceeded: max {self.max_requests_per_minute} requests/minute. "
                f"Try again in {60 - (now - self.requests[0][0]):.0f} seconds."
            )
        
        self.requests.append((now, query))
        logger.debug(f"[WebPlugin] Rate limit: {len(self.requests)}/{self.max_requests_per_minute} requests in last minute")
    
    # ========== v0.2.1: Dynamic Threshold ==========
    
    def _calculate_threshold(self, results: List[Dict]) -> float:
        """
        Calcula threshold dinâmico baseado no número de resultados.
        
        Se temos muitos resultados, aumentamos o threshold para filtrar mais.
        Se temos poucos, mantemos threshold baixo para não perder informação.
        
        Args:
            results: Lista de resultados processados
            
        Returns:
            Threshold calculado (0.0 - 1.0)
        """
        if not self.adaptive_threshold:
            return self.min_score
        
        num_results = len(results)
        
        if num_results > 20:
            threshold = 0.5  # Muitos resultados, ser mais seletivo
        elif num_results > 10:
            threshold = 0.4  # Quantidade média, threshold médio
        else:
            threshold = 0.3  # Poucos resultados, threshold baixo
        
        logger.debug(f"[WebPlugin] Adaptive threshold: {threshold} (based on {num_results} results)")
        return threshold
