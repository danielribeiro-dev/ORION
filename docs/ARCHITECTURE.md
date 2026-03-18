# ORION — System Architecture

## 1. Visão Geral

ORION é um **engine arquitetural** para sistemas inteligentes. Ele **não é um chatbot**, **não é um agente autônomo** e **não é um LLM com plugins**.

ORION utiliza modelos de linguagem (LLMs) **como ferramentas**, nunca como núcleo decisório. Todas as decisões, execuções e respostas seguem um fluxo rígido, auditável e governado por políticas explícitas.

O objetivo do ORION é ser:

* previsível
* extensível
* auditável
* seguro
* preparado para evolução (voz, visão, memória, UX)

---

## 2. Princípios Fundamentais (Imutáveis)

1. O LLM nunca é o núcleo do sistema.
2. Toda resposta ao usuário passa obrigatoriamente pelo Answer Pipeline.
3. Nenhuma ação é executada sem passar por Policy Enforcement.
4. Router decide caminhos; Executor executa ações. Nunca o inverso.
5. Plugins são ferramentas puras: não decidem, não conversam, não formatam respostas.
6. Dados temporais ou mutáveis exigem uso obrigatório de Web ou fonte externa válida.
7. Falha de fonte externa resulta em resposta honesta, nunca inferida.
8. Configuração nunca é código.
9. Estado nunca é lógica.
10. Se não está documentado, não é comportamento válido do sistema.

---

## 3. Fluxo Canônico do Sistema

Este fluxo é obrigatório e não pode ser alterado sem breaking change arquitetural.

```
User Input
   ↓
Runtime / EntryPoint
   ↓
Router
   ↓
Intent & Decision
   ↓
Policy Enforcement
   ↓
Action Plan
   ↓
Executor
   ↓
Plugins / Tools
   ↓
Action Result
   ↓
Answer Pipeline
   ↓
User Output
```

Cada etapa possui responsabilidade única e não pode assumir o papel de outra.

---

## 4. Camadas do Sistema

### 4.1 Runtime

Responsável por:

* boot do sistema
* validação de ambiente
* carregamento de configuração

Proibições:

* não decide
* não executa ações
* não chama LLM

---

### 4.2 Routing

Inclui:

* Router
* Intent Resolution
* Decision

Responsável por:

* classificar o pedido do usuário
* definir o caminho de execução

Proibições:

* não executa ações
* não responde usuário

---

### 4.3 Policies

Responsável por:

* validar permissões baseadas no usuário (AuthService)
* forçar uso de ferramentas obrigatórias
* bloquear fluxos inválidos via `ActionLevel` (LEVEL_0, LEVEL_1, LEVEL_2)

Implementação core: `GovernanceEngine`. Policy é lei. Nenhuma camada pode ignorá-la.

---

### 4.4 Planning

Responsável por:

* transformar intenção em plano executável
* definir passos e ordem

Proibições:

* não executa
* não responde

---

### 4.5 Execution

Responsável por:

* executar planos
* chamar plugins
* coletar resultados
* solicitar confirmação de usuário para ações críticas (LEVEL_2)
* resolver contextos `SYSTEM` estruturalmente, ignorando LLM

Executor é determinístico e atua como PEP (Policy Enforcement Point).

---

### 4.6 Plugins

Plugins são ferramentas isoladas.

Regras:

* não tomam decisões
* não chamam LLM livremente
* não escrevem respostas ao usuário

---

### 4.7 LLM Layer

Responsável por:

* interpretação sob contrato
* geração de texto apenas quando permitido

O LLM nunca decide fluxo nem simula capacidades externas.

---

### 4.8 Answer Pipeline

Responsável por:

* formatação final da resposta
* tom e UX textual
* declaração de origem e confiança

Toda saída ao usuário passa por aqui.

---

## 5. Estrutura Conceitual de Diretórios

```
ORION/
├── runtime/        # boot, lifecycle, startup orchestration
├── routing/        # router, intent resolution, decision logic
├── policies/       # system laws, constraints, security enforcement
├── planning/       # action plan generation
├── execution/      # executor, action execution, results
├── plugins/        # external capabilities
│   ├── web/
│   ├── filesystem/
│   └── ...
├── llm/            # model adapters (Gemini, Groq, etc.)
├── answer/         # answer pipeline & formatting
├── memory/         # memory subsystem (future)
├── devtools/       # debug, inspect, simulate
├── infra/          # deployment, docker, env
├── docs/           # ALL .md live here (source of truth)
└── main.py         # single entrypoint
```

Regras:

* Nenhum arquivo pode existir fora dessa estrutura sem justificativa arquitetural.
* Devtools nunca são importados em runtime de produção.
* Cada arquivo possui responsabilidade única.

---

## 6. Evolução de Capacidades (Habilidades)

As capacidades do ORION são incrementais e **sempre mapeadas a uma camada**.

### Exemplos:

* Web Search → plugins/web
* Voz (TTS / STT) → plugins/voice + answer
* Visão → plugins/vision
* Memória persistente → memory
* UX multimodal → answer + runtime

Nenhuma nova habilidade pode ser adicionada sem:

1. definir sua camada
2. definir seu impacto no fluxo
3. documentar no `CAPABILITIES.md`

---

## 7. Contrato com Implementadores (IA ou Humanos)

Qualquer sistema (incluindo IA como Antigravity) que implemente ORION deve:

* seguir este documento à risca
* não criar atalhos
* não misturar responsabilidades
* não inventar capacidades não documentadas

Violação deste documento invalida a implementação.

---

## 8. Considerações Finais

ORION é um sistema governado por leis, não por prompts.

O código é uma consequência da arquitetura — nunca o contrário.
