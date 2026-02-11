"""
Infrastructure UI Module.

Responsabilidade:
    - Gerenciar a interação visual com o usuário (CLI).
    - Formatar saídas (Cores, Headers).
    - Abstrair print/input.
"""

import sys
import time

class ConsoleUI:
    """
    Interface de Terminal para o ORION.
    """
    
    # ANSI Colors
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GREY = "\033[90m"

    @staticmethod
    def print_header(system_name: str, version: str, llm_status: str) -> None:
        """Imprime o cabeçalho de inicialização."""
        print(f"{ConsoleUI.CYAN}{ConsoleUI.BOLD}")
        print(f"   {system_name} SYSTEM [{version}]")
        print(f"   Status: {llm_status}")
        print(f"{ConsoleUI.RESET}")
        print(f"{ConsoleUI.GREY}{'-'*50}{ConsoleUI.RESET}")

    @staticmethod
    def print_system(message: str) -> None:
        """Imprime mensagem do sistema (Logs limpos/Info)."""
        print(f"{ConsoleUI.GREY}[SYS] {message}{ConsoleUI.RESET}")

    @staticmethod
    def print_assistant(name: str, message: str) -> None:
        """Imprime resposta do assistente."""
        print(f"\n{ConsoleUI.CYAN}{ConsoleUI.BOLD}[{name}]{ConsoleUI.RESET} {message}\n")

    @staticmethod
    def print_error(message: str) -> None:
        """Imprime erros."""
        print(f"{ConsoleUI.RED}[ERROR] {message}{ConsoleUI.RESET}")

    @staticmethod
    def input_user(prompt_name: str) -> str:
        """Captura entrada do usuário."""
        try:
            return input(f"{ConsoleUI.GREEN}{ConsoleUI.BOLD}[{prompt_name}] >_ {ConsoleUI.RESET}").strip()
        except KeyboardInterrupt:
            return "exit"

    @staticmethod
    def typing_effect(text: str, delay: float = 0.01) -> None:
        """Simula efeito de digitação (opcional)."""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()
