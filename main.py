"""
ORION Main Entrypoint.

Responsabilidade:
    - Ponto único de entrada do sistema.
    - Inicializa o Runtime.
    - Instancia os componentes principais via Container.
    - Mantém o Loop de Execução (REPL).

v0.4.0:
    - Removida validação duplicada de governança (BUG-02).
      A governança agora ocorre SOMENTE dentro do Executor (PEP centralizado).
    - Adaptado para receber RouterResult do Router.
    - Dashboard exibe usuário da sessão persistente.

Regras:
    - Não contém lógica de negócio.
    - Apenas orquestra o início e o loop.
"""

import sys
import threading
from datetime import datetime
from uuid import uuid4
from core.container import Container
from core.ui import ConsoleUI


def main() -> None:
    # 1. Inicializar Container (inclui todos os componentes e memória)
    container = Container.get_instance()
    settings = container.settings
    logger = container.logger
    
    session_id = str(uuid4())

    # 2. Iniciar Runtime
    container.runtime.start()

    # 3. Dashboard de Inicialização
    current_user = container.current_user
    llm_status = f"ONLINE ({settings.groq_model})" if settings.groq_api_key else "OFFLINE (Local/Null)"
    dev_flag = " | DEV MODE" if container.profile.is_dev_mode() else ""

    ConsoleUI.print_header(settings.system_name, settings.version, llm_status)
    ConsoleUI.print_system(f"Sistema inicializado. Sessão: {current_user.username} ({current_user.role}){dev_flag}")
    ConsoleUI.print_system("Aguardando entrada do usuário...")

    # 4. Main Loop (REPL)
    try:
        while True:
            try:
                user_input = ConsoleUI.input_user(settings.user_name)

                if not user_input:
                    continue

                if user_input.lower() in ("exit", "sair", "quit"):
                    ConsoleUI.print_system("Encerrando sistema...")
                    break

                # ─── Fluxo de Execução ───────────────────────────────

                # A. Classificar Intent (retorna RouterResult em v0.4.0)
                recent_history = container.history.get_recent(n=5)
                memory_context = container.semantic_memory.get_context_for_prompt(user_input)
                router_result = container.router.route(user_input, context=recent_history, memory_context=memory_context)

                # B. Planejar (RouterResult → [(plugin, params), ...])
                plan = container.planner.plan(router_result)

                # C. Executar (a governança e PEP ocorrem aqui, centralizado)
                #    v0.4.0: validação de policy REMOVIDA daqui (BUG-02).
                #    O GovernanceEngine é validado dentro do Executor.
                raw_result = container.executor.execute(plan)

                # D. Formatar Resposta
                final_response = container.answer_pipeline.process(raw_result)

                # E. Persistir Histórico
                container.history.add_interaction(
                    user_input,
                    final_response,
                    router_result.intent  # Acessa atributo tipado do RouterResult
                )

                # F. Exibir ao Usuário
                system_name = container.profile.get_system_name()
                ConsoleUI.print_assistant(system_name, final_response or "(Nenhuma resposta gerada)")
                
                # G. Extração Assíncrona e Salvamento Episódico na Memória Semântica longa
                threading.Thread(
                    target=container.memory_extractor.extract_and_store,
                    args=(user_input, final_response, container.semantic_memory, container.llm_service),
                    daemon=True
                ).start()
                
                container.semantic_memory.store_episode(
                    text=f"Usuário: {user_input}\nAssistente: {final_response}",
                    metadata={
                        "timestamp": datetime.utcnow().isoformat(),
                        "session_id": session_id,
                        "source": "conversation"
                    }
                )

            except KeyboardInterrupt:
                print()
                ConsoleUI.print_system("Encerrando sistema...")
                break
            except Exception as e:
                ConsoleUI.print_error(f"Erro Crítico: {e}")
                logger.exception("Erro no Main Loop")

    finally:
        # SEMPRE executa — garante flush mesmo em crash ou Ctrl+C
        logger.info("[Main] Fazendo flush da memória antes de encerrar...")
        container.history.save()
        container.runtime.shutdown()
        logger.info("[Main] Shutdown completo.")


if __name__ == "__main__":
    main()
