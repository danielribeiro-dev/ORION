# MEMORY.md

Este documento define **como a memória do ORION funciona**, o que pode ser armazenado, quem decide o armazenamento e como essas informações impactam o comportamento do sistema.

A memória é um **componente estrutural**, não um efeito colateral do LLM.

---

## 1. Princípios Fundamentais

* O LLM **não decide** o que é lembrado
* O LLM **não é a memória**
* O LLM apenas **se comporta de acordo com o estado da memória**

> A memória pertence ao sistema. O LLM apenas a consome.

---

## 2. Tipos de Memória

### 2.1 Memória de Sessão (Curto Prazo)

Escopo:

* Conversa atual
* Contexto temporário

Exemplos:

* Tema atual
* Objetivo imediato

Persistência:

* Não persistente

---

### 2.2 Memória Básica do Usuário (Persistente)

Esta memória **existe desde o início do sistema**.

Armazena:

* Nome do usuário
* Forma preferida de tratamento
* Nome pelo qual o sistema deve ser chamado
* Idioma de comunicação atual (ex: `"pt-BR"`, `"english"`)

Exemplo:

* Usuário: "Dan"
* Sistema: "ORION"
* Nome invocado: "Jarvis"
* Idioma: "english"

> Importante: o nome invocado **não altera a identidade interna do sistema**, apenas sua forma de interação.

Status: **Obrigatória**

---

### 2.3 Memória de Longo Prazo (Evolutiva)

Armazena:

* Decisões arquiteturais
* Preferências persistentes
* Configurações do sistema

Regras:

* Core decide o que persiste
* Tudo deve ser justificável

---

## 3. Identidade vs Invocação

### 3.1 Identidade Interna

* Nome interno do sistema: **ORION**
* Usado em:

  * Logs
  * Arquitetura
  * Código

Imutável.

---

### 3.2 Nome de Invocação (Wake Name)

* Definido pelo usuário
* Pode mudar a qualquer momento
* Pode ser qualquer string válida

Exemplos:

* "Jarvis"
* "Friday"
* "Orion"

Uso:

* Interação textual
* Interação por voz (wake word)

Status: **Essencial**

---

## 4. Integração com Voz

Quando o módulo de voz estiver ativo:

* O nome de invocação será usado como **wake phrase**
* A alteração do nome deve refletir imediatamente na escuta

Exemplo:

> "Jarvis, cria um script em Python"

---

## 5. Fluxo de Decisão de Memória

1. Evento ocorre
2. Core avalia relevância
3. Memory Module valida
4. Persistência (ou não)

O LLM apenas recebe o estado atualizado.

---

## 6. Regra de Ouro

> Se o LLM precisar "decidir lembrar", a arquitetura está errada.

A memória é explícita, controlada e auditável.
