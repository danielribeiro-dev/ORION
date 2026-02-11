"""
Answer Pipeline Module.

Responsabilidade:
    - Processar o resultado bruto da execução.
    - Formatar a resposta final para o usuário.
    - Garantir o tom e estilo adequados.

Proibições:
    - Não executa novas ações de busca.
    - Não altera a verdade dos dados (alucinação).
"""

from typing import Any
from answer.base import BaseAnswerPipeline

class AnswerPipeline(BaseAnswerPipeline):
    """
    Pipeline final de montagem da resposta ao usuário.
    """

    def __init__(self) -> None:
        """Inicializa o AnswerPipeline."""
        pass

    def process(self, result: Any) -> str:
        """
        Formata o resultado da execução em uma resposta legível.
        """
        if not result:
            return ""
            
        return str(result)
