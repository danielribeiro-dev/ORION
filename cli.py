#!/usr/bin/env python3
"""
ORION CLI Entrypoint.

Responsabilidade:
    - Prover o comando 'orion' no terminal.
    - Chamar a função main() do sistema principal.
    - (Opcional) Processar argumentos de linha de comando no futuro.
"""

import sys
from main import main as start_repl

def main():
    """Função de entrada para o console script definido no pyproject.toml."""
    try:
        # No futuro, podemos adicionar suporte a flags aqui (ex: --version, --status)
        if len(sys.argv) > 1:
            arg = sys.argv[1].lower()
            if arg in ("--version", "-v"):
                from core.config import settings
                print(f"ORION Version: {settings.version}")
                return
            elif arg in ("--help", "-h"):
                print("Uso: orion [OPÇÕES]")
                print("\nOpções:")
                print("  -v, --version    Mostra a versão do sistema")
                print("  -h, --help       Mostra esta mensagem de ajuda")
                print("\nSem argumentos, inicia o REPL do ORION.")
                return

        # Inicia o REPL principal
        start_repl()
    except KeyboardInterrupt:
        print("\nInterrompido via CLI. Saindo...")
        sys.exit(0)
    except Exception as e:
        print(f"Erro fatal ao iniciar ORION via CLI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
