# OBSERVABILITY.md

Este documento define **como o ORION observa a si mesmo**.

Observabilidade não é opcional. É o que garante:

* Confiabilidade
* Debugabilidade
* Auditoria
* Evolução segura

> Um sistema inteligente sem observabilidade é uma caixa-preta perigosa.

---

## 1. Princípios Fundamentais

* Tudo que é importante **deve ser observável**
* Logs não são apenas para erro, mas para **entendimento**
* Nenhuma decisão relevante ocorre sem deixar rastro

---

## 2. Tipos de Observabilidade

### 2.1 Logs

Os logs devem registrar eventos significativos do sistema.

Exemplos:

* Inicialização do sistema
* Seleção de LLM (primário ou fallback)
* Execução de comandos
* Alterações de memória persistente

Requisitos:

* Timestamp
* Módulo de origem
* Nível (INFO | WARN | ERROR | DEBUG)

---

### 2.2 Métricas

As métricas permitem acompanhar o comportamento do sistema ao longo do tempo.

Exemplos:

* Latência de respostas
* Taxa de fallback de LLM
* Número de execuções de código
* Uso de memória

Objetivo:

> Detectar degradação antes de falhas visíveis.

---

### 2.3 Tracing

Tracing conecta eventos entre módulos.

Exemplos:

* Uma solicitação do usuário passando por:

  * Interface → Core → LLM → Memory → Execution

Cada fluxo deve possuir:

* ID único
* Propagação entre módulos

---

### 2.4 Auditoria

Auditoria registra **mudanças sensíveis e irreversíveis**.

Exemplos:

* Alteração de nome de invocação
* Persistência de memória
* Execução de comandos perigosos

Auditoria deve ser:

* Imutável
* Persistente

---

## 3. Níveis de Log

* DEBUG: detalhes internos
* INFO: eventos normais
* WARN: comportamentos inesperados
* ERROR: falhas

O nível deve ser configurável por ambiente.

---

## 4. Integração com Módulos

Cada módulo é responsável por:

* Emitir seus próprios logs
* Propagar IDs de trace

O Core coordena o fluxo.

---

## 5. Segurança e Privacidade

* Dados sensíveis **não devem** aparecer em logs
* Tokens e chaves devem ser mascarados
* Logs devem respeitar o escopo de privacidade do usuário

---

## 6. Persistência

* Logs críticos devem ser persistidos
* Logs temporários podem ser rotativos

Estratégia definida por ambiente:

* Dev
* Prod

---

## 7. Regra de Ouro

> Se você não consegue explicar por que o sistema tomou uma decisão, falta observabilidade.

Este documento garante que o ORION nunca seja uma caixa-preta.
