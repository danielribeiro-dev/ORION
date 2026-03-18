# LLM_STRATEGY.md

Este documento define **como o ORION utiliza modelos de linguagem (LLMs)**, incluindo prioridade, fallback, configuração e regras de segurança.

Ele complementa o `CAPABILITIES.md` e o `MODULES.md`, descrevendo **o comportamento operacional** do cérebro do sistema.

---

## 1. Princípios Fundamentais

* O LLM **não decide regras do sistema**
* O LLM **não possui estado próprio**
* O LLM **não acessa variáveis sensíveis diretamente**

> O LLM é um executor cognitivo, não um controlador.

---

## 2. LLM Primário

O ORION deve operar com **um LLM primário**, responsável pelo raciocínio principal.

Características desejáveis:

* Baixa latência
* Boa capacidade de raciocínio
* Estabilidade

Exemplos:

* Groq
* OpenAI
* Gemini

A escolha do LLM primário **não é hardcoded**.

---

## 3. LLM Secundário (Fallback)

O ORION deve possuir **ao menos um LLM secundário** configurado como fallback automático.

O fallback ocorre em casos de:

* Timeout
* Erro de API
* Rate limit

Regras:

* O fallback deve ser transparente para o usuário
* O evento deve ser registrado no Observability Module

---

## 4. Estratégia de Seleção

A seleção de LLM segue a lógica:

1. Tentar LLM primário
2. Em falha, acionar LLM secundário
3. Retornar resposta normalizada

> O Core controla a estratégia. O LLM Module apenas executa.

---

## 5. Variáveis de Ambiente (.env)

Todas as informações sensíveis **devem** ser carregadas via variáveis de ambiente.

Exemplos obrigatórios:

* Chaves de API de LLMs
* Tokens de serviços externos
* Configurações de ambiente (dev, prod)

Arquivo padrão:

```
.env
```

Este arquivo **não deve** ser versionado no repositório.

---

## 6. Nome do Sistema e Configuração de Identidade

### 6.1 Identidade Interna

* Nome interno do sistema: **ORION**
* Definido em código
* Nunca exposto como variável de ambiente

---

### 6.2 Nome de Invocação (Wake Name)

O nome pelo qual o sistema é chamado:

* É definido pelo usuário
* Pode mudar dinamicamente
* **Não deve** ser fixado em `.env`

Motivo:

> O nome de invocação é uma **preferência de usuário**, não uma configuração de ambiente.

Armazenamento correto:

* Memory Module (memória persistente)

---

## 7. Justificativa Arquitetural

* `.env` é para **segredos e infraestrutura**
* Memória é para **preferências e identidade de interação**

Misturar os dois cria:

* Rigidez
* Risco de inconsistência
* Problemas em multiusuário

---

## 8. Regra de Ouro

> Se mudar de usuário exige mudar `.env`, a arquitetura está errada.

Este documento define o comportamento do cérebro do ORION, não sua personalidade.
