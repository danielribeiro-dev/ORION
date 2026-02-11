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
    logger = container.logger # Keeps logger for file logs if needed, or structured ops
    
    # 2. Start Runtime
    # Runtime start might log to file, but we keep UI clean
    container.runtime.start()

    # 3. Dashboard
    # Determine LLM Status (Naive check: check config present)
    llm_status = f"ONLINE ({settings.groq_model})" if settings.groq_api_key else "OFFLINE (Local/Null)"
    
    ConsoleUI.print_header(settings.system_name, settings.version, llm_status)
    ConsoleUI.print_system("System initialized. Waiting for input...")

    # 4. Main Loop
    while True:
        try:
            user_input = ConsoleUI.input_user(settings.user_name)
            
            if not user_input:
                continue
                
            if user_input.lower() in ("exit", "sair", "quit"):
                ConsoleUI.print_system("Shutting down...")
                break

            # --- Execution Flow ---
            
            # A. Intent
            # TODO: Phase 2 will plug LLM here real-time
            intent = container.router.route(user_input)
            
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
            # Save interaction
            container.history.add_interaction(user_input, final_response, intent.get("intent", "UNKNOWN"))
            
            # Output
            system_name = container.profile.get_system_name()
            ConsoleUI.print_assistant(system_name, final_response or "(No response generated yet)")

        except KeyboardInterrupt:
            print()
            ConsoleUI.print_system("Shutting down...")
            container.history.save() # Ensure flush
            sys.exit(0)
        except Exception as e:
            ConsoleUI.print_error(f"Critical Error: {e}")
            logger.exception("Main Loop Error")

if __name__ == "__main__":
    main()
