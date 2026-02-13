"""
ORION Main Entrypoint.

Responsabilidade:
    - Ponto único de entrada do sistema.
    - Inicializa o Runtime.
    - Instancia os componentes principais via Container.
    - Mantém o Loop de Execução (REPL).

Regras:
    - Não contém lógica de negócio.
    - Apenas orquestra o início e o loop.
"""

import sys
from infra.container import Container
from infra.ui import ConsoleUI

def main() -> None:
    # 1. Initialize Container
    container = Container.get_instance()
    settings = container.settings
    logger = container.logger
    
    # 2. Start Runtime
    container.runtime.start()

    # 3. Dashboard
    llm_status = f"ONLINE ({settings.groq_model})" if settings.groq_api_key else "OFFLINE (Local/Null)"
    
    ConsoleUI.print_header(settings.system_name, settings.version, llm_status)
    ConsoleUI.print_system("System initialized. Waiting for input...")

    # 4. Main Loop com flush seguro
    try:
        while True:
            try:
                user_input = ConsoleUI.input_user(settings.user_name)
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ("exit", "sair", "quit"):
                    ConsoleUI.print_system("Shutting down...")
                    break

                # --- Execution Flow ---
                
                # A. Intent (com contexto de histórico)
                recent_history = container.history.get_recent(n=5)
                intent = container.router.route(user_input, context=recent_history)
                
                # B. Policy
                intent_name = intent.get("intent", "UNKNOWN")
                allowed = container.capability_guard.validate(intent_name)
                
                if not allowed:
                    ConsoleUI.print_error(f"Action '{intent_name}' blocked by security policy.")
                    continue

                # C. Plan
                plan = container.planner.plan(intent)

                # D. Execute
                raw_result = container.executor.execute(plan)

                # E. Answer
                final_response = container.answer_pipeline.process(raw_result)
                
                # F. Memory
                container.history.add_interaction(user_input, final_response, intent.get("intent", "UNKNOWN"))
                
                # Output
                system_name = container.profile.get_system_name()
                ConsoleUI.print_assistant(system_name, final_response or "(No response generated yet)")

            except KeyboardInterrupt:
                print()
                ConsoleUI.print_system("Shutting down...")
                break
            except Exception as e:
                ConsoleUI.print_error(f"Critical Error: {e}")
                logger.exception("Main Loop Error")
    
    finally:
        # SEMPRE executa, mesmo em crash ou Ctrl+C
        logger.info("[Main] Flushing memory before exit...")
        container.history.save()
        container.runtime.shutdown()
        logger.info("[Main] Shutdown complete.")

if __name__ == "__main__":
    main()
