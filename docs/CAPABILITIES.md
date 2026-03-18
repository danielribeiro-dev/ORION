# ORION — Capabilities

Este documento define **o que o ORION é capaz de fazer** em cada estágio de sua evolução.

Diferente do `ARCHITECTURE.md`, este arquivo **pode crescer ao longo do tempo**, mas **nunca pode violar** as leis arquiteturais já definidas.

Toda nova capacidade deve:

1. estar listada aqui
2. indicar seu status
3. mapear claramente as camadas envolvidas
4. respeitar o fluxo canônico do ORION

---

## 1. Regras Gerais para Capacidades

* Capacidades não criam exceções ao fluxo do sistema.
* Capacidades não alteram responsabilidades das camadas.
* Capacidades são sempre implementadas **dentro de uma ou mais camadas existentes**.
* Se uma capacidade não puder ser mapeada claramente a camadas, ela **não deve ser implementada**.

## 2. Resumo Rápido: O que o ORION Pode e Não Pode Fazer

### ✅ O que o sistema PODE fazer hoje:
* **Conversar:** Bater papo, responder perguntas gerais, formatar textos e atuar como um excelente LLM (via `ChatPlugin`).
* **Memória Básica:** Lembrar seu nome, o nome pelo qual você o chama, e o idioma escolhido (via `MemoryPlugin`).
* **Busca Web:** Pesquisar na internet e trazer os resultados para sustentar conversas sobre fatos recentes (via `WebPlugin`).
* **Autocontrole Institucional:** Declarar de forma rígida (sem LLM) quem é, sua versão corrente e que permissões o usuário atual tem.
* **Proteger Ações:** Bloquear e pedir confirmação interativa para ações sensíveis (nível 2), como mudar nome ou idioma.

### ❌ O que o sistema NÃO PODE fazer hoje:
* **Acessar/Executar Sistemas Locais Arbitrários:** O LLM não pode rodar scripts soltos nem abrir aplicativos do seu computador diretamente. (Embora exista um base Filesystem plugin, ele está severamente restrito/inativo para execução arbitrária sem aprovação no `Executor`).
* **Mexer em Configurações Físicas (.env, senhas):** O sistema não tem autonomia para acessar credenciais locais.
* **Autonomia Sem Fim (Agentes):** O sistema é Reativo. Ele só atua quando você solicita. Ele não vai varrer a internet ou rodar loops invisíveis sozinho sem ter sido explicitamente acionado e passando pelo pipeline determinístico.
* **Aprender Automaticamente Novos Conceitos de Longo Prazo:** Além dos dados básicos de perfil (nomes e idioma), ele não extrai e armazena automaticamente fatos soltos num banco de dados semântico ainda.

---

## 3. Estratégia de Modelos de Linguagem (LLM Strategy)

O ORION **exige obrigatoriamente** uma estratégia de LLM primário e fallback.

### Regras:

* Deve existir **um LLM primário** ativo.
* Deve existir **ao menos um LLM secundário (fallback)**.
* O fallback só pode ser acionado por falha técnica (timeout, indisponibilidade, erro de API).
* O fallback **nunca** altera comportamento, políticas ou capacidades.
* Todo LLM deve falar Português-BR.

### Exemplos de configuração válida:

* Primário: Groq
* Fallback: Gemini

ou

* Primário: OpenAI
* Fallback: Ollama (local)

### Camadas envolvidas:

* runtime
* llm
* policies

> Observação: detalhes de configuração (.env, keys, providers) **não pertencem a este documento** e devem ser tratados em documentação de ambiente.

---

## 3. Capacidades Fundamentais (MVP Inicial)

Estas capacidades são obrigatórias na primeira implementação do ORION.

---

### 3.1 Conversa Estruturada (Sem Ação) e Respostas Institucionais

**Status:** Obrigatória

**Descrição:**
ORION é capaz de responder perguntas conversacionais que **não exigem ações externas**. 
Questões sobre a identidade, versão e permissões do sistema (intents do tipo `SYSTEM`) retornam uma saída estruturada bypassando explicitamente qualquer inferência via LLM.

**Camadas envolvidas:**

* routing
* execution
* policies
* llm
* answer

**Regras específicas:**

* Não pode simular acesso a ferramentas
* Não pode inferir dados temporais
* O LLM é severamente bloqueado de declarar as permissões do usuário
* Sempre responder via Answer Pipeline

---

### 3.2 Detecção de Dados Temporais ou Mutáveis

**Status:** Obrigatória

**Descrição:**
ORION detecta automaticamente quando um pedido envolve informações temporais ou mutáveis (ex: dólar, bitcoin, clima, datas recentes).

**Camadas envolvidas:**

* routing
* decision
* policies

**Regras específicas:**

* A detecção ocorre antes da execução
* Não pode ser ignorada por nenhuma camada posterior

---

### 3.3 Busca Web Obrigatória

**Status:** Obrigatória

**Descrição:**
ORION é capaz de buscar informações na web quando exigido por policy.

**Camadas envolvidas:**

* planning
* execution
* plugins/web
* answer

**Regras específicas:**

* Web é obrigatória para dados temporais
* LLM não pode inferir valores
* Falha de web deve ser explicitada ao usuário

---

### 3.4 Execução de Ferramentas Seguras

**Status:** Obrigatória

**Descrição:**
ORION executa ferramentas controladas por plugins, sempre via Executor.

**Camadas envolvidas:**

* planning
* execution
* plugins

**Regras específicas:**

* Plugins não decidem
* Plugins não escrevem respostas
* Toda execução gera Action Result

---

### 3.5 Resposta com Origem e Confiança

**Status:** Obrigatória

**Descrição:**
ORION declara explicitamente a origem das informações utilizadas e o nível de confiança da resposta.

**Camadas envolvidas:**

* answer
* policies

**Regras específicas:**

* Nunca fingir fonte
* Nunca atribuir conhecimento genérico ao LLM

---

### 3.6 Seleção de Idioma do Sistema

**Status:** Obrigatória

**Descrição:**
O usuário pode configurar o idioma primário no qual o sistema se comunica através da memória persistente de perfil. Esta configuração injeta instruções definitivas no contexto de conversação, forçando a adoção do idioma definido no LLM.

**Camadas envolvidas:**

* memory
* plugins/memory
* plugins/chat
* execution

**Regras específicas:**

* Modificação persistente.
* Considerada uma ação sensível de `ActionLevel.LEVEL_2` e exige confirmação. 

---

## 4. Capacidades Planejadas (Não Implementadas Ainda)

Estas capacidades estão previstas, mas **não fazem parte do MVP inicial**.

---

### 4.1 Memória Persistente

**Status:** Planejada

**Camadas envolvidas:**

* memory
* policies
* execution

---

### 4.2 Voz (STT / TTS)

**Status:** Planejada

**Camadas envolvidas:**

* plugins/voice
* answer
* runtime

---

### 4.3 Visão

**Status:** Planejada

**Camadas envolvidas:**

* plugins/vision
* execution

---

### 4.4 UX Multimodal

**Status:** Planejada

**Camadas envolvidas:**

* answer
* runtime

---

## 5. Regra de Evolução

Nenhuma capacidade pode ser considerada válida se:

* não estiver documentada aqui
* não respeitar o `ARCHITECTURE.md`
* não indicar claramente suas camadas

Capacidades são adicionadas por decisão consciente — nunca por acidente.
# CAPABILITIES.md

Este documento define **o que o ORION sabe fazer** e **o que ele deverá saber fazer ao longo do tempo**. Ele serve como um contrato vivo entre:

* Você (arquitetura e decisões)
* Eu (design, lógica e evolução)
* Antigravity (executor gradual de código e integrações)

A ideia é simples: **tudo que o ORION puder fazer precisa estar explicitado aqui**.

---

## 1. Princípios das Capacidades

* Capacidades são **modulares** e **incrementais**
* Nenhuma capacidade nasce "mágica" — ela sempre depende de:

  * Código
  * Integração
  * Permissões
* O sistema deve conseguir responder:

  * *O que eu sei fazer agora?*
  * *O que ainda não sei, mas está planejado?*

---

## 2. Categorias de Capacidades

As capacidades são organizadas por domínio para facilitar expansão futura (plugins, voz, UX, etc).

### 2.1 Core Cognitivo

Capacidades fundamentais de raciocínio e coordenação:

* Orquestração de tarefas
* Planejamento em múltiplos passos
* Raciocínio lógico estruturado
* Escolha dinâmica de ferramentas
* Delegação entre módulos internos

Status: **Obrigatório desde o início**

---

### 2.2 LLM (Large Language Models)

#### 2.2.1 LLM Primário

O sistema **deve** operar com um LLM principal configurável.

Exemplos suportáveis:

* OpenAI
* Groq
* Gemini

Responsabilidades:

* Raciocínio principal
* Planejamento
* Decisão
* Geração de respostas

#### 2.2.2 LLM Secundário (Fallback)

O sistema **deve** possuir um LLM secundário para fallback automático em casos de:

* Timeout
* Erro de API
* Limite de uso

Regras:

* O fallback deve ser transparente
* Logs devem registrar quando ocorreu fallback

> Observação: a estratégia de fallback pode ser detalhada futuramente em um arquivo específico (ex: `LLM_STRATEGY.md`), mas **a exigência da existência do fallback pertence a este documento**.

---

### 2.3 Memória

Capacidades relacionadas a retenção e recuperação de contexto:

* Memória de curto prazo (contexto de sessão)
* Memória de longo prazo (decisões, arquitetura, preferências)
* Indexação semântica
* Atualização controlada de memória

Status: **Essencial**

---

### 2.4 Execução de Código

* Execução local controlada
* Execução via Antigravity
* Validação antes de executar
* Logs de execução

Restrições:

* Nunca executar código não autorizado
* Sempre validar contexto e impacto

---

### 2.5 Plugins & Extensões

Sistema preparado para capacidades plugáveis:

* Plugins internos
* Plugins externos
* Ativação/desativação dinâmica

Exemplos futuros:

* Plugin de voz
* Plugin de automação
* Plugin de sistemas externos

---

### 2.6 Voz (Voice)

Capacidades relacionadas a interação por voz:

* Speech-to-Text
* Text-to-Speech
* Controle por comandos de voz

Status: **Planejado**

---

### 2.7 UX / Interface

* Interface CLI
* Interface Web
* Feedback visual de estados internos

Status: **Evolutivo**

---

## 3. Capacidades Herdadas do Jarvis

O ORION deve cobrir e superar as capacidades já existentes no Jarvis, incluindo:

* Automação de tarefas
* Execução de scripts
* Auxílio ao desenvolvedor
* Organização de comandos

Diferença-chave:

> No ORION, **toda capacidade é explícita, documentada e evolutiva**.

---

## 4. Roadmap de Capacidades

Cada nova capacidade deve:

1. Ser adicionada neste arquivo
2. Ter status (Planejado | Em Desenvolvimento | Estável)
3. Indicar dependências

---

## 5. Regra de Ouro

> Se uma capacidade não está neste arquivo, **ela não existe oficialmente**.

Este documento é a base para crescimento controlado do ORION.
