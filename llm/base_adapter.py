"""
LLM Base Adapter.

Responsabilidade:
    - Abstrair a comunicação com provedores de LLM (Gemini, Groq, etc.).
    - Enviar prompts e receber completions.

Proibições:
    - Não contém regras de negócio.
    - Não decide fluxo.
"""

from llm.base import BaseLLMAdapter

class BaseAdapter(BaseLLMAdapter):
    """
    Interface base para adaptadores de LLM.
    """

    def __init__(self) -> None:
        """Inicializa o adaptador."""
        pass

    def generate(self, prompt: str) -> str:
        """
        Gera uma resposta a partir de um prompt.

        Args:
            prompt: O texto de entrada para o modelo.

        Returns:
            O texto gerado pelo modelo.
        """
        pass
