# SECURITY.md

Este documento define **o modelo de segurança do ORION**.

Segurança não é um recurso isolado — é um **comportamento transversal** que afeta todos os módulos, plugins e fluxos do sistema.

---

## 1. Princípios Fundamentais

* Segurança é **default**, não opcional
* Negação por padrão (deny by default)
* Privilégio mínimo
* Toda ação sensível deve ser rastreável

---

## 2. Modelo de Ameaça (Threat Model)

O ORION deve se proteger contra:

* Execução de código não autorizado
* Acesso indevido ao sistema de arquivos
* Vazamento de segredos (.env)
* Persistência indevida de memória
* Ações irreversíveis sem consentimento

---

## 3. Isolamento de Componentes

### 3.1 LLM

* Não acessa sistema operacional
* Não acessa `.env`
* Não executa código
* Não persiste memória

O LLM apenas recebe **estado filtrado** e retorna **texto**.

---

### 3.2 Core

* Único módulo autorizado a:

  * Coordenar ações
  * Aprovar execuções
  * Persistir memória

---

### 3.3 Execution & Plugins

* Executam apenas via Sandbox
* Permissões explícitas
* Limites de recurso

---

## 4. Sandbox (Reforço de Segurança)

O Sandbox é a **principal barreira de contenção**.

Regras:

* Sem acesso root
* Sem execução fora do escopo permitido
* Sem acesso a diretórios críticos

Qualquer violação:

* Execução abortada
* Evento auditado

---

## 5. Dev Mode (Controle Rígido)

* OFF por padrão
* Ativação manual pelo usuário
* Registro em auditoria
* Escopo limitado ao Sandbox

Dev Mode **não**:

* Remove restrições de segurança
* Permite acesso total ao sistema

---

## 6. Proteção de Segredos

* Segredos vivem apenas em `.env`
* Nunca expostos ao LLM
* Nunca logados
* Nunca persistidos em memória

Exemplos:

* API Keys
* Tokens

---

## 7. Ações Sensíveis

Ações consideradas sensíveis:

* Execução de código
* Exclusão de arquivos
* Persistência de memória
* Alteração de identidade (wake name)

Regras:

* Devem ser auditadas
* Podem exigir confirmação explícita

---

## 8. Logs e Auditoria

* Logs não expõem dados sensíveis
* Auditoria é imutável
* Auditoria registra:

  * Quem solicitou
  * O que foi feito
  * Quando

---

## 9. Falhas e Contenção

Em caso de erro:

* Falhar de forma segura (fail-safe)
* Nenhuma ação parcial
* Nenhuma persistência inconsistente

---

## 10. Regra de Ouro

> Se uma ação não pode ser explicada, auditada e revertida, ela não deve existir.

Este documento garante que o ORION permaneça **seguro, previsível e sob controle humano**.
