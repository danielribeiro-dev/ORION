# FLOW

## Visão Geral

O fluxo do Jarvis/ORION define como comandos do usuário percorrem o sistema desde a entrada até a execução final, garantindo previsibilidade, segurança e extensibilidade.

O sistema é orientado a **pipeline**, onde cada etapa tem responsabilidades claras e bem delimitadas.

---

## Fluxo Principal de Execução

### 1. Entrada do Usuário

* O usuário fornece um comando em linguagem natural.
* O comando pode ser:

  * Informativo
  * Operacional
  * Criativo
  * Técnico

Nenhuma execução direta ocorre neste estágio.

---

### 2. Análise Inicial (Intent Parser)

Responsável por:

* Identificar a intenção do comando
* Classificar o tipo de ação
* Detectar se requer:

  * Plugins
  * Sandbox
  * Web
  * Acesso ao filesystem

Saída:

* Estrutura semântica padronizada do pedido

---

### 3. Validação de Segurança e Governança

Antes de qualquer ação, a `GovernanceEngine` garante:

* Checagem de permissões baseada no `ActionLevel`
* Categorização das ações por risco (LEVEL_0, LEVEL_1, LEVEL_2)
* Restrições de ambiente (Dev Mode ON/OFF)
* Bloqueio de ações proibidas
* Verificação de escopo (filesystem, web, sandbox)

Falhas aqui **interrompem o fluxo imediatamente**. Ações classificadas como críticas (LEVEL_2) serão retidas na fase de execução até a `ConsoleUI` coletar a aprovação explícita.

---

### 4. Roteamento de Execução

Com base na análise:

* LLM puro (resposta direta via `ChatPlugin`)
* Plugin específico (ferramentas e filesystem)
* Resposta Institucional Direta (resolvida via pseudo-plugin `system` interceptado estruturalmente no Executor e que ignora requisições LLM)
* Sandbox (criação/modificação de plugins)
* Web como fonte temporal

Pode haver múltiplos caminhos combinados.

---

### 5. Execução

Cada executor é determinístico e atua como validador final:

* **Bypass Estrutural**
  * Intercepta intents do tipo `system`
  * Forma resposta normativa garantindo zero-alucinação.

* **Confirmações Level 2**
  * Exige `ConsoleUI` interativa para mudanças perigosas ou globais.

* **Plugins**

  * Executam apenas sua responsabilidade
  * Não acessam outros plugins diretamente

* **Sandbox**

  * Ambiente controlado
  * Só ativo em Dev Mode ON
  * Gera código, nunca executa diretamente sem validação

* **Web**

  * Coleta dados externos
  * Retorna dados estruturados ao LLM

---

### 6. Pós-processamento

* Consolidação dos resultados
* Normalização de respostas
* Resumo quando necessário
* Preparação da resposta final

---

### 7. Resposta ao Usuário

* Resposta clara e contextual
* Transparência quando usar Web (fontes)
* Logs não sensíveis gerados

---

## Dev Mode

Dev Mode é um **modo explícito de desenvolvimento**, onde:

* O sistema pode criar, editar ou remover plugins
* A Sandbox é habilitada
* Ações perigosas continuam bloqueadas

Dev Mode **não** ignora regras de segurança — apenas amplia capacidades controladas.

---

## Fluxos Especiais

### Criação de Plugins

1. Usuário solicita novo comportamento
2. Intent Parser detecta criação
3. Validação: Dev Mode ON
4. Sandbox gera plugin
5. Plugin passa por validação
6. Plugin é registrado no sistema

---

### Uso do Web Plugin

* Web é obrigatório para dados:

  * Temporais
  * Atualizados
  * Externos

Limites:

* Até 100 fontes por pesquisa
* Web retorna dados, não decisões

---

## Princípios do Fluxo

* Nenhuma execução sem validação
* Nenhum plugin é confiável por padrão
* Web nunca decide, apenas informa
* Sandbox nunca executa diretamente
* Segurança precede funcionalidade
