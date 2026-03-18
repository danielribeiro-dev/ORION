"""
Keyword Heuristics for Intent Classification.

Usado como fallback quando a classificação LLM tem baixa confiança.

v0.4.0: Removidas palavras genéricas do mapeamento WEB que causavam
        falsos positivos (BUG-07): "quando", "onde", "quem", "qual", "quais".
        Mantidas apenas palavras que indicam busca explícita ou informação temporal.
"""

from typing import Dict, List

# Mapeamento de keywords para intents
INTENT_KEYWORDS: Dict[str, List[str]] = {
    "WEB": [
        # Busca explícita — palavras de ação
        "pesquise", "procure", "busque", "encontre", "descubra", "search",
        "pesquisa", "busca",
        # Informação temporal/atual — requer dados externos atualizados
        "hoje", "agora", "atual", "atualmente", "recente", "recentemente",
        "últimas notícias", "últimos", "novidades",
        # Dados financeiros/preços — requer consulta externa
        "cotação", "preço", "valor", "quanto custa", "câmbio",
        # Ações de consulta online claras
        "na internet", "online", "na web", "no google",
    ],
    "FILESYSTEM": [
        "edite", "mova", "delete", "remova", "escreva", "crie arquivo",
        "liste pasta", "liste arquivos", "diretório", "pasta",
        "salve em", "abra arquivo", "feche arquivo", "renomeie", "copie",
    ],
    "MEMORY": [
        "lembre", "salve isso", "apague da memória", "esqueça",
        "memorize", "guarde", "anote", "registre",
        "meu nome é", "me chamo", "prefiro ser chamado",
        "mude meu nome", "altere meu nome",
        "mude o idioma", "fale em", "responda em", "language",
        "mude o nome do sistema", "seu nome agora é", "se chame",
    ],
    "HELP": [
        "ajuda", "help", "o que você faz", "como funciona",
        "comandos", "capacidades", "funcionalidades", "o que pode fazer",
    ],
    "SYSTEM": [
        "meu cargo", "minha permissão", "minhas permissões", "versão do sistema",
        "quem é você", "identidade do sistema", "user role", "permissions",
        "system version", "qual a sua versão", "qual versão",
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
    scores["CHAT"] = 0.0  # Default intent

    # Contar matches por intent
    for intent, keywords in INTENT_KEYWORDS.items():
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        if matches > 0:
            # Score baseado em número de matches (normalizado)
            scores[intent] = min(matches / 3.0, 1.0)  # Max 3 keywords = 1.0

    # Se nenhum match, é CHAT com alta confiança
    if all(score == 0.0 for score in scores.values()):
        scores["CHAT"] = 0.8

    return scores


def get_best_intent(scores: Dict[str, float]) -> tuple[str, float]:
    """
    Retorna o intent com maior score.

    Returns:
        (intent, confidence)
    """
    best_intent = max(scores.items(), key=lambda x: x[1])
    return best_intent
