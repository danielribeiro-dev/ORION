"""
Formal Data Structures for ORION v0.2.0.

This module defines the contracts between system layers.
All structured data exchanged between components must use these types.

Responsabilidade:
    - Definir contratos formais entre camadas
    - Garantir type safety
    - Facilitar rastreabilidade

Proibições:
    - Não contém lógica de negócio
    - Não decide fluxo
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PluginResult:
    """
    Resultado estruturado retornado por plugins.
    
    Usado para garantir que plugins retornem dados padronizados
    que podem ser processados pelo Answer Pipeline.
    """
    data: List[Any]
    sources: List[Dict[str, Any]]  # [{"title": ..., "url": ..., "score": ...}]
    confidence: float  # 0.0 - 1.0
    degraded: bool
    plugin: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Valida os dados após inicialização."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")


@dataclass
class LLMResult:
    """
    Resultado estruturado retornado pelo LLM Service.
    
    Permite rastreabilidade de qual provedor foi usado e se houve fallback.
    """
    text: str
    provider: str  # "groq" | "ollama" | outros
    degraded: bool  # True se usou fallback
    model: str  # Nome do modelo usado
    
    @property
    def is_primary(self) -> bool:
        """Retorna True se usou o provedor primário."""
        return not self.degraded


@dataclass
class RouterResult:
    """
    Resultado estruturado retornado pelo Router.
    
    Contém a intenção classificada e metadados de decisão.
    """
    intent: str  # CHAT | WEB | FILESYSTEM | MEMORY | HELP
    confidence: float  # 0.0 - 1.0
    reason: str  # Justificativa técnica da classificação
    user_input: str  # Input original do usuário
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Valida os dados após inicialização."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        valid_intents = ["CHAT", "WEB", "FILESYSTEM", "MEMORY", "HELP", "UNKNOWN"]
        if self.intent not in valid_intents:
            raise ValueError(f"Intent must be one of {valid_intents}, got {self.intent}")


@dataclass
class ConfidenceScore:
    """
    Sistema formal de confiança composto.
    
    Agrega múltiplas fontes de confiança para calcular score final.
    """
    router_confidence: float  # 0.0 - 1.0
    plugin_confidence: float = 1.0  # 0.0 - 1.0 (default 1.0 se não aplicável)
    llm_confidence: float = 1.0  # 0.0 - 1.0 (opcional)
    
    @property
    def final_confidence(self) -> float:
        """
        Calcula confiança final como média ponderada.
        
        Pesos:
        - Router: 30% (decisão de caminho)
        - Plugin: 50% (qualidade dos dados)
        - LLM: 20% (qualidade da síntese)
        """
        return (
            self.router_confidence * 0.3 +
            self.plugin_confidence * 0.5 +
            self.llm_confidence * 0.2
        )
    
    def __post_init__(self):
        """Valida os dados após inicialização."""
        for name, value in [
            ("router_confidence", self.router_confidence),
            ("plugin_confidence", self.plugin_confidence),
            ("llm_confidence", self.llm_confidence)
        ]:
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0, got {value}")
