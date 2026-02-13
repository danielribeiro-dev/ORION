"""
Keyword Heuristics for Intent Classification.

Usado como fallback quando a classificação LLM tem baixa confiança.
"""

from typing import Dict, List

# Mapeamento de keywords para intents
INTENT_KEYWORDS: Dict[str, List[str]] = {
    "WEB": [
        # Busca explícita
        "pesquise", "procure", "busque", "encontre", "descubra", "search",
        # Informação temporal/atual
        "hoje", "agora", "atual", "atualmente", "recente", "últimas",
        "cotação", "preço", "valor", "quanto custa",
        # Perguntas que requerem dados externos
        "quando", "onde", "quem", "qual", "quais",
    ],
    "FILESYSTEM": [
        "edite", "mova", "delete", "remova", "escreva", "crie arquivo",
        "liste pasta", "diretório", "arquivo", "salve em",
        "abra", "feche", "renomeie", "copie",
    ],
    "MEMORY": [
        "lembre", "salve isso", "apague da memória", "esqueça",
        "memorize", "guarde", "anote", "registre",
        "meu nome é", "me chamo", "prefiro",
    ],
    "HELP": [
        "ajuda", "help", "o que você faz", "como funciona",
        "comandos", "capacidades", "funcionalidades",
    ]
}


def classify_by_keywords(text: str) -> Dict[str, float]:
    """
    Classifica texto usando keywords.
    
    Returns:
        Dict com scores por intent (0.0-1.0)
    """
    text_lower = text.lower()
    scores = {intent: 0.0 for intent in INTENT_KEYWORDS.keys()}
    scores["CHAT"] = 0.0  # Default
    
    # Contar matches por intent
    for intent, keywords in INTENT_KEYWORDS.items():
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        if matches > 0:
            # Score baseado em número de matches (normalizado)
            scores[intent] = min(matches / 3.0, 1.0)  # Max 3 keywords = 1.0
    
    # Se nenhum match, é CHAT
    if all(score == 0.0 for score in scores.values()):
        scores["CHAT"] = 0.8  # Alta confiança em CHAT se não há keywords
    
    return scores


def get_best_intent(scores: Dict[str, float]) -> tuple[str, float]:
    """
    Retorna o intent com maior score.
    
    Returns:
        (intent, confidence)
    """
    best_intent = max(scores.items(), key=lambda x: x[1])
    return best_intent
