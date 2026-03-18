# MODULES.md

Este documento define **os módulos internos do ORION**, suas responsabilidades e como eles se relacionam.

Ele responde a perguntas como:

* Quais partes compõem o sistema?
* Quem é responsável por quê?
* Onde uma nova funcionalidade deve entrar?

> Regra: **nenhuma funcionalidade nasce fora de um módulo**.

---

## 1. Visão Geral

O ORION é composto por módulos independentes, porém coordenados. Cada módulo:

* Tem responsabilidade única (SRP)
* Pode evoluir sem quebrar os outros
* Pode ser substituído

```
ORION
 ├─ Core
 ├─ LLM
 ├─ Memory
 ├─ Execution
 ├─ Plugins
 ├─ Interface
 └─ Observability
```

---

## 2. Core Module

**Responsabilidade:** coordenação central do sistema.

Funções:

* Orquestrar módulos
* Planejar tarefas
* Tomar decisões de alto nível
* Controlar fluxo de execução

Não faz:

* Chamadas diretas a APIs externas
* Execução de código bruto

Dependências:

* LLM
* Memory
* Execution

Status: **Obrigatório**

---

## 3. LLM Module

**Responsabilidade:** abstração de modelos de linguagem.

Funções:

* Gerenciar LLM primário
* Gerenciar LLM secundário (fallback)
* Normalizar respostas
* Controlar prompts

Não faz:

* Decisão de negócio
* Execução de código

Arquivos futuros possíveis:

* LLM_STRATEGY.md

Status: **Obrigatório**

---

## 4. Memory Module

**Responsabilidade:** armazenamento e recuperação de informações.

Funções:

* Memória de curto prazo
* Memória de longo prazo
* Indexação semântica
* Atualização controlada

Regras:

* Nem tudo pode ser salvo
* Core decide o que persiste

Status: **Essencial**

---

## 5. Execution Module

**Responsabilidade:** executar ações no mundo real.

Funções:

* Execução de código
* Chamadas a sistema
* Integração com Antigravity
* Validação pré-execução

Regras:

* Segurança acima de tudo
* Logs obrigatórios

Status: **Essencial**

---

## 6. Plugins Module

**Responsabilidade:** extensibilidade.

Funções:

* Registro de plugins
* Ciclo de vida (load/unload)
* Permissões

Exemplos:

* Plugin de voz
* Plugin de automação

Status: **Evolutivo**

---

## 7. Interface Module

**Responsabilidade:** interação com o usuário.

Funções:

* CLI
* Web UI
* Voz

Observação:

* Interface não contém lógica de negócio

Status: **Evolutivo**

---

## 8. Observability Module

**Responsabilidade:** visibilidade do sistema.

Funções:

* Logs
* Métricas
* Tracing
* Auditoria

Motivação:

> Um sistema inteligente sem observabilidade é uma caixa-preta perigosa.

Status: **Obrigatório**

---

## 9. Regra Final

> Se você não sabe em qual módulo algo entra, a arquitetura ainda não está clara o suficiente.

Este documento deve evoluir junto com o sistema.
