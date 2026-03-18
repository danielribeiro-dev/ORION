# PLUGINS.md

Este documento define **o sistema de plugins do ORION**, incluindo regras de segurança, ciclo de vida, sandbox, Dev Mode e plugins iniciais.

Plugins são a principal forma de **expansão controlada** do ORION.

---

## 1. Princípios Fundamentais

* Plugins **não quebram o Core**
* Plugins operam sob **permissões explícitas**
* Todo plugin é **observável** (logs, métricas, auditoria)
* Nenhum plugin nasce fora de um **Sandbox**

---

## 2. Sandbox

O **Sandbox** é o ambiente isolado onde plugins são:

* Criados
* Testados
* Executados

Objetivos:

* Conter falhas
* Evitar impacto no sistema principal
* Permitir experimentação segura

Regras:

* Sem acesso irrestrito ao sistema operacional
* Acesso apenas às APIs permitidas
* Limites claros de CPU, memória e I/O

Status: **Obrigatório**

---

## 3. Dev Mode

### 3.1 O que é Dev Mode

**Dev Mode** é um estado explícito do sistema que permite:

* Criação de novos plugins
* Modificação de plugins existentes
* Acesso ampliado ao Sandbox

Por padrão:

* Dev Mode = **OFF**

---

### 3.2 Regras do Dev Mode

* Apenas o usuário pode ativar
* Deve ser registrado em auditoria
* Deve ser reversível a qualquer momento

Exemplo:

> "Ativar Dev Mode"

Enquanto ativo:

* O ORION pode criar plugins sob demanda do usuário
* Código gerado fica restrito ao Sandbox

Fora do Dev Mode:

* Plugins apenas executam
* Nenhum código novo é criado

---

## 4. Ciclo de Vida de Plugins

1. Criação (Dev Mode ON)
2. Registro
3. Validação de permissões
4. Execução
5. Observabilidade
6. Atualização ou remoção

---

## 5. Plugins Iniciais (Essenciais)

### 5.1 Filesystem Plugin

Capacidades:

* Ler arquivos
* Criar arquivos
* Editar arquivos
* Mover arquivos
* Excluir arquivos
* Resumir arquivos (texto, PDF, etc.)

Restrições:

* Proibido operar em arquivos do sistema
* Exclusão permitida apenas:

  * Fora de diretórios críticos
  * Até limite configurável (ex: máximo 5 arquivos por operação)

Observação:

* Toda operação destrutiva deve ser auditada

Status: **Obrigatório**

---

### 5.2 Web Plugin

O Web Plugin é uma **fonte essencial de dados temporais**.

Capacidades:

* Pesquisas na web
* Coleta de dados atuais
* Retorno de fontes

Regras:

* Máximo de 100 fontes por consulta
* Fontes devem ser registradas
* O plugin retorna **dados estruturados**, não respostas finais

Fluxo:

1. Web Plugin coleta dados
2. Dados retornam ao Core
3. LLM utiliza dados para completar a resposta

Status: **Obrigatório**

---

## 6. Plugins Planejados / Viáveis Agora

### 6.1 App Launcher Plugin

Capacidades:

* Listar aplicativos disponíveis no sistema
* Abrir aplicativos por comando do usuário

Exemplo:

> "Jarvis, abre o VS Code"

Restrições:

* Apenas apps permitidos
* Sem execução arbitrária

Status: **Viável / Planejado**

---

### 6.2 Automation Plugin

Capacidades:

* Executar fluxos automatizados
* Encadear ações entre plugins

Status: **Planejado**

---

### 6.3 Voice Plugin

Capacidades:

* Wake word
* Speech-to-Text
* Text-to-Speech

Integração:

* Usa o nome de invocação da memória

Status: **Planejado**

---

## 7. Permissões

Cada plugin declara explicitamente:

* O que pode acessar
* O que pode modificar
* O que pode executar

O Core valida antes da execução.

---

## 8. Regra de Ouro

> Se um plugin precisa de acesso total ao sistema, ele não é um plugin — é um risco.

Plugins existem para expandir o ORION **sem comprometer sua segurança**.
