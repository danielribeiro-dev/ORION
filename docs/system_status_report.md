# ORION System Status & Roadmap

## 1. O que o sistema FAZ HOJE (Capacidades Reais)

O ORION é uma fundação estrutural sólida com capacidade de comunicação externa (LLM) já implementada, mas ainda não "ativada" no fluxo de decisão.

*   **Infraestrutura Hardened**:
    *   **Container de Injeção de Dependência**: Gerencia todo o ciclo de vida dos objetos.
    *   **Configuração Centralizada**: `infra/config.py` gerencia chaves (Groq/Ollama) e ambiente.
    *   **Logging Estruturado**: Logs padronizados em todo o sistema.

*   **Camada de Inteligência (LLM Layer)**:
    *   **Adaptadores Prontos**: Conecta-se à API Groq (Llama-3) e Ollama (Local).
    *   **Sistema de Fallback**: Se a Groq falhar ou estiver sem internet, tenta automaticamente usar o Ollama local.
    *   *Nota*: A capacidade existe (`llm/service.py`), mas o `Router` ainda não a chama para tomar decisões.

*   **Arquitetura Base**:
    *   Todos os componentes (Router, Planner, Executor) existem e seguem contratos estritos (`Base...`).
    *   O fluxo `main.py` roda de ponta a ponta sem erros.

*   **Governança e Segurança (v0.3.0 Consolidado)**:
    *   **Fonte Única de Verdade**: As declarações de identidade (versão, permissões, roles) são resolvidas via intent estrutural `SYSTEM` e validadas puramente no `Executor`.
    *   **Contrato de Governança**:
        - Validação de Permissões: Ocorre em `GovernanceEngine.validate()` via injeção no `Executor`.
        - Confirmação de Nível 2 (High-Risk): Exigida interativamente em `Executor.execute()` através de `ConsoleUI.confirm_action()`.
        - Resolução de Intents Institucionais: Executadas estruturalmente sem inferência do LLM e retornam respostas definitivas.

---

## 2. Sugestões de Melhorias (Roadmap Prioritário)

Com base nos princípios do `ARCHITECTURE.md` e nas necessidades do usuário, definem-se as próximas etapas críticas:

### 2.1 Melhoria de UX e Interface (Console)
*   **Limpeza Visual**: Remover timestamps e logs de debug da saída principal do usuário (manter apenas em arquivo `.log`).
*   **Dashboard de Inicialização**:
    *   Exibir ASCII Art ou Header minimalista: `ORION SYSTEM [v0.3.0]`.
    *   Indicador de Estado do LLM: `[ONLINE: Groq]` ou `[OFFLINE: Local Only]` ou `[NO LLM]`.
*   **Prompt Dinâmico**:
    *   Exibir nome do sistema personalizado: `[JARVIS] >_` em vez de texto genérico.
*   **Feedback Visual**: Cores sutis para diferenciar:
    *   *System Info* (Cinza)
    *   *User Input* (Branco)
    *   *AI Response* (Ciano/Verde)
    *   *Action Execution* (Amarelo)

### 2.2 Sistema de Memória (Persistente e Contextual)
Para permitir que o sistema "lembre", devemos implementar o módulo `memory/` com duas sub-camadas:

1.  **Perfil & Preferências (Profile Memory)**:
    *   Arquivo: `memory/profile.json` ou SQLite leve.
    *   Dados:
        *   `system_name`: Nome do assistente (ex: "Jarvis").
        *   `user_name`: Nome do usuário (ex: "Senhor Dan").
        *   `user_preferences`: Regras de tratamento, concisão, etc.
    *   *Uso*: Carregado no Boot e injetado no Contexto do Prompt do LLM.

2.  **Memória Episódica (Conversation History)**:
    *   Arquivo: `memory/history.db` (SQLite) ou `logs/chat_history.jsonl`.
    *   Estrutura: Salvar cada turno `(timestamp, user_input, intent, action_result, final_response)`.
    *   *Funcionalidade*:
        *   **Contexto Imediato**: Manter as últimas N mensagens em memória RAM para manter o fio da meada.
        *   **Recall (Busca)**: Permitir consultas como "O que fizemos dia 11?". O `Planner` poderá consultar o módulo `Memory` para responder a intents do tipo `MEMORY_RECALL`.

---

## 3. Próximos Passos Recomendados

1.  **Refinar Interface (UX)**: Alterar `main.py` e `infra/logger.py` para limpar a saída.
2.  **Ativar o Cérebro**: Fazer o `Router` usar o `LLMService` com o prompt de classificação já criado.
3.  **Implementar Memória Básica**: Criar estutura para salvar/ler o nome do usuário e sistema.
