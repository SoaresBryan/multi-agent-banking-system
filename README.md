# Multi-Agent Banking System

Sistema multiagente inteligente para operações bancárias utilizando IA, desenvolvido com Python, FastAPI, CrewAI e MongoDB.

## Visão Geral do Projeto

O Multi-Agent Banking System é uma solução inovadora que utiliza múltiplos agentes de IA especializados para atender clientes em diferentes necessidades bancárias. O sistema foi projetado para oferecer uma experiência de atendimento natural e eficiente, onde cada agente possui expertise específica em sua área de atuação (triagem, crédito, análise financeira e câmbio).

O projeto implementa um sistema de orquestração inteligente que gerencia transições transparentes entre agentes, mantendo o contexto da conversa e oferecendo uma experiência fluida ao usuário. A arquitetura é baseada em microserviços, com APIs RESTful, interface web interativa e persistência de dados tanto em arquivos CSV quanto em banco de dados MongoDB para memória de conversações.

**Principais Características:**
- Sistema multiagente com 4 agentes especializados
- Orquestração automática com transições transparentes entre agentes
- Autenticação de clientes com CPF e data de nascimento
- Análise de crédito com cálculo dinâmico de score
- Consulta de câmbio em tempo real
- Interface web interativa desenvolvida com Streamlit
- API REST completa para integração
- Memória persistente de conversações com MongoDB
- Testes automatizados com cobertura completa

## Arquitetura do Sistema

### Visão Geral da Arquitetura

O sistema é composto por camadas bem definidas que seguem princípios de separação de responsabilidades:

```
┌─────────────────────────────────────────────────────────┐
│                  CAMADA DE APRESENTAÇÃO                 │
│  ┌─────────────────────┐    ┌─────────────────────┐   │
│  │  Streamlit Frontend │    │   FastAPI REST API  │   │
│  └─────────────────────┘    └─────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│              CAMADA DE ORQUESTRAÇÃO                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Agent Orchestrator                      │  │
│  │  - Gerencia transições entre agentes             │  │
│  │  - Detecta redirecionamentos automáticos         │  │
│  │  - Mantém contexto da conversa                   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                  CAMADA DE AGENTES                      │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────┐│
│  │  Triagem   │ │  Crédito   │ │ Entrevista │ │Câmbio││
│  │   Agent    │ │   Agent    │ │   Agent    │ │Agent ││
│  └────────────┘ └────────────┘ └────────────┘ └──────┘│
│       │              │              │              │    │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────┐│
│  │  Triagem   │ │  Crédito   │ │ Entrevista │ │Câmbio││
│  │   Tools    │ │   Tools    │ │   Tools    │ │Tools ││
│  └────────────┘ └────────────┘ └────────────┘ └──────┘│
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│              CAMADA DE SERVIÇOS                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Cliente  │ │ Crédito  │ │  Score   │ │  Câmbio  │  │
│  │ Service  │ │ Service  │ │ Service  │ │ Service  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│           CAMADA DE DADOS E PERSISTÊNCIA                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   MongoDB    │  │  CSV Files   │  │   Models     │ │
│  │  (Memória)   │  │  (Dados)     │  │  (Pydantic)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Agentes Especializados

O sistema conta com 4 agentes especializados, cada um com role, goal e backstory bem definidos:

#### 1. Agente de Triagem
**Responsabilidade:** Porta de entrada do sistema, responsável por autenticar clientes e identificar suas necessidades.

**Ferramentas (Tools):**
- `autenticar_cliente`: Autentica cliente usando CPF e data de nascimento
- `verificar_autenticacao`: Verifica se o cliente já está autenticado

**Comportamento:**
- Recebe a solicitação inicial do cliente
- Realiza autenticação com até 3 tentativas
- Identifica a necessidade do cliente (crédito, câmbio, etc.)
- Redireciona automaticamente para o agente especializado apropriado

**Redirecionamentos:**
- `[REDIRECIONA_CREDITO]`: Para consultas e solicitações de limite de crédito
- `[REDIRECIONA_CAMBIO]`: Para consultas de câmbio e cotações
- `[REDIRECIONA_ENTREVISTA]`: Para análise de perfil financeiro

#### 2. Agente de Crédito
**Responsabilidade:** Gerencia consultas de limite e processa solicitações de aumento.

**Ferramentas (Tools):**
- `consultar_limite`: Consulta o limite atual e máximo do cliente
- `solicitar_aumento_limite`: Processa solicitação de aumento de limite
- `obter_limite_maximo`: Calcula limite máximo baseado no score

**Comportamento:**
- Consulta informações de limite do cliente
- Processa pedidos de aumento de forma automática
- Avalia se o aumento é possível baseado no score
- Oferece análise de perfil quando solicitação é rejeitada

**Redirecionamentos:**
- `[REDIRECIONA_ENTREVISTA]`: Quando cliente precisa melhorar score para obter mais crédito

#### 3. Agente de Entrevista (Análise Financeira)
**Responsabilidade:** Conduz entrevista financeira para recalcular score do cliente.

**Ferramentas (Tools):**
- `calcular_novo_score`: Calcula novo score baseado nas informações coletadas

**Comportamento:**
- Conduz entrevista conversacional coletando 5 informações:
  1. Renda mensal
  2. Tipo de emprego (formal, autônomo, desempregado)
  3. Despesas fixas mensais
  4. Número de dependentes
  5. Valor total de dívidas
- Coleta UMA informação por vez para manter naturalidade
- Calcula novo score usando algoritmo ponderado
- Atualiza score no sistema
- Redireciona para o agente de crédito com novo score

**Redirecionamentos:**
- `[REDIRECIONA_CREDITO]`: Após calcular e atualizar o score

#### 4. Agente de Câmbio
**Responsabilidade:** Fornece cotações de moedas estrangeiras em tempo real.

**Ferramentas (Tools):**
- `consultar_cotacao`: Consulta cotação de uma moeda específica via SerpAPI
- `listar_moedas_disponiveis`: Lista todas as moedas disponíveis para consulta

**Comportamento:**
- Fornece cotações de forma rápida e objetiva
- Suporta múltiplas moedas (USD, EUR, GBP, ARS, CAD, AUD, JPY, CHF, CNY, BTC)
- Aceita códigos de moeda ou nomes populares (ex: "dólar", "euro")
- Oferece consultas adicionais após fornecer uma cotação

**Redirecionamentos:**
- `[REDIRECIONA_TRIAGEM]`: Para retornar ao menu principal

### Fluxo de Dados e Comunicação entre Agentes

#### 1. Contexto Compartilhado
Todos os agentes compartilham um contexto global (`ContextoConversa`) que contém:
- Histórico completo da conversa
- Estado de autenticação do cliente
- Dados do cliente (CPF, nome, score, limite)
- Tentativas de autenticação
- Dados extras coletados durante entrevistas

#### 2. Mecânica de Redirecionamento
O sistema utiliza tags especiais nas respostas dos agentes para sinalizar transições:
- `[REDIRECIONA_CREDITO]`, `[REDIRECIONA_ENTREVISTA]`, `[REDIRECIONA_CAMBIO]`, `[REDIRECIONA_TRIAGEM]`
- `[ENCERRA_ATENDIMENTO]` para finalizar o atendimento

**Processo de Transição:**
1. Agente processa a mensagem e gera resposta com tag de redirecionamento
2. Orquestrador detecta a tag usando regex patterns
3. Tag é removida da resposta antes de exibir ao usuário
4. Contexto é preservado
5. Novo agente é ativado
6. Sistema reprocessa a mensagem original com o novo agente
7. Transição é **invisível** para o cliente

#### 3. Prompts Dinâmicos
Cada agente recebe um prompt customizado que inclui:
- Template específico do agente (carregado de `app/agents/prompts/`)
- Contexto atual da conversa
- Dados do cliente (nome, score, limite atual, limite máximo)
- Estado de autenticação

### Utilização dos Models (Pydantic)

Os models definidos em [app/models](app/models) são utilizados extensivamente na camada de serviços para garantir validação e tipagem forte:

#### Cliente ([app/models/cliente.py](app/models/cliente.py))
```python
class Cliente(BaseModel):
    cpf: str
    nome: str
    data_nascimento: date
    score: int 
    limite_atual: float
```
**Uso:** [ClienteService](app/services/cliente_service.py) utiliza este model para:
- Validar dados ao buscar clientes do CSV
- Garantir consistência nas operações de autenticação
- Validar CPF automaticamente (apenas números, 11 dígitos)
- Validar range do score (0-1000)

#### SolicitacaoCredito ([app/models/solicitacao.py](app/models/solicitacao.py))
```python
class SolicitacaoCredito(BaseModel):
    cpf_cliente: str
    data_hora_solicitacao: datetime
    limite_atual: float
    novo_limite_solicitado: float
    status_pedido: StatusSolicitacao
```
**Uso:** [SolicitacaoService](app/services/solicitacao_service.py) utiliza este model para:
- Registrar solicitações de aumento de limite
- Validar status das solicitações
- Listar histórico de solicitações por cliente

#### Cotacao ([app/models/cotacao.py](app/models/cotacao.py))
```python
class Cotacao(BaseModel):
    moeda_origem: str
    moeda_destino: str
    valor: float
    data_consulta: datetime
```
**Uso:** [CambioService](app/services/cambio_service.py) utiliza este model para:
- Encapsular dados de cotações obtidas via SerpAPI
- Garantir consistência nos dados de câmbio
- Fornecer timestamp das consultas

### Persistência de Dados

O sistema utiliza uma estratégia híbrida de persistência:

**CSV Files ([app/data](app/data)):**
- `clientes.csv`: Base de dados de clientes (CPF, nome, data nascimento, score, limite)
- `score_limite.csv`: Tabela de conversão score → limite máximo
- `solicitacoes_aumento_limite.csv`: Histórico de solicitações

**MongoDB:**
- Database: `banking_agents`
- Collection: `conversations`
- Propósito: Armazenar histórico de conversações para memória de longo prazo
- Estrutura: Mensagens agrupadas por `conversation_id` e `agent_id`
- Índices: Criados automaticamente para otimizar queries por conversation_id

## Funcionalidades Implementadas

### Funcionalidades Core

1. **Autenticação de Clientes**
   - Autenticação via CPF e data de nascimento
   - Até 3 tentativas antes de encerrar atendimento
   - Suporte a múltiplos formatos de data (YYYY-MM-DD, DD/MM/YYYY)
   - Validação automática de CPF

2. **Gestão de Crédito**
   - Consulta de limite atual e limite máximo disponível
   - Solicitação de aumento de limite
   - Aprovação/rejeição automática baseada em score
   - Cálculo dinâmico de limite baseado em tabela score-limite
   - Registro de todas as solicitações com timestamp e status

3. **Análise de Perfil Financeiro**
   - Entrevista conversacional para coleta de dados financeiros
   - Cálculo de novo score baseado em:
     - Renda mensal (peso: 35%)
     - Tipo de emprego - CLT/PJ/AUTÔNOMO/DESEMPREGADO (peso: 25%)
     - Despesas fixas (peso: 20%)
     - Número de dependentes (peso: 10%)
     - Dívidas totais (peso: 10%)
   - Atualização automática do score no sistema
   - Recálculo de limite disponível pós-atualização

4. **Consulta de Câmbio**
   - Cotações em tempo real via SerpAPI (Google Search)
   - Suporte a 10+ moedas principais (USD, EUR, GBP, ARS, CAD, AUD, JPY, CHF, CNY, BTC)
   - Reconhecimento de nomes populares de moedas
   - Listagem de moedas disponíveis

5. **Interface Web (Streamlit)**
   - Chat interativo com agentes
   - Indicador visual do agente atual
   - Status de autenticação em tempo real
   - Painel administrativo com 3 módulos:
     - **Adicionar Cliente**: Cadastro de novos clientes com cálculo automático de limite
     - **Listar Clientes**: Visualização tabular de todos os clientes
     - **Solicitações de Limite**: Dashboard com filtros por status e CPF
   - Botão de "Novo Atendimento" para resetar a sessão

6. **API REST (FastAPI)**
   - **POST /chat**: Endpoint para envio de mensagens
   - **POST /chat/reset**: Reset de conversação
   - **GET /health**: Health check
   - **POST /admin/clientes**: Adicionar novo cliente
   - **GET /admin/clientes**: Listar todos os clientes
   - **GET /admin/solicitacoes**: Listar solicitações de crédito
   - Documentação automática (Swagger/ReDoc)
   - CORS habilitado para integração frontend

7. **Memória Persistente**
   - Armazenamento de conversações no MongoDB
   - Histórico completo de mensagens por sessão
   - Recuperação de contexto em sessões futuras
   - Separação de memória por agente e conversation_id

### Funcionalidades Técnicas

8. **Orquestração Inteligente**
   - Detecção automática de redirecionamentos via regex
   - Transições transparentes entre agentes
   - Preservação de contexto durante transições
   - Logs detalhados de todas as transições

9. **Sistema de Tools (CrewAI)**
   - 9 tools especializadas distribuídas entre os agentes
   - Decorador `@tool` para integração com CrewAI
   - Mensagens de retorno estruturadas para parsing

10. **Testes Automatizados**
    - Testes unitários com pytest
    - Testes de integração de serviços
    - Testes de API com TestClient
    - Fixtures reutilizáveis com conftest.py
    - Cobertura de código com pytest-cov

## Desafios Enfrentados e Como Foram Resolvidos

### 1. Comunicação Entre Agentes e Manutenção de Contexto

**Desafio:**
Inicialmente, os agentes não tinha contexto suficiente sobre os outros agentes e quando um agente redirecionava para outro, o contexto da conversa era perdido. O novo agente não tinha acesso às informações coletadas anteriormente (ex: dados de autenticação, score, preferências), resultando em uma experiência fragmentada onde o cliente precisava repetir informações.

**Solução Implementada:**
- Criação de uma classe `ContextoConversa` ([app/agents/tools/context.py](app/agents/tools/context.py)) que funciona como estado global compartilhado
- Funções `set_contexto()` e `get_contexto()` para acesso centralizado
- Atualização do contexto antes de cada execução de agente
- Serialização de dados críticos no contexto (CPF, nome, score, limite, dados extras)
- Histórico completo de mensagens mantido no contexto e passado via prompt
- Adicionado no contexto de todos os agentes informações sobre os outros agentes para melhorar o redirecionamento

**Resultado:** Transições completamente transparentes, onde o novo agente tem acesso total ao histórico e dados coletados anteriormente.

### 2. Definição Precisa de Cada Agente (Role, Goal, Backstory)

**Desafio:**
Nos primeiros testes, os agentes tinham comportamentos inconsistentes:
- Agente de triagem tentava responder perguntas de crédito ao invés de redirecionar
- Agente de entrevista coletava todas as informações de uma vez, tornando a conversa robótica
- Agente de crédito pedia confirmações múltiplas antes de processar solicitações
- Transições entre agentes eram visíveis ao usuário (ex: "Vou te transferir para o agente de crédito")

**Solução Implementada:**

**a) Refinamento de Role, Goal e Backstory:**
Cada agente recebeu instruções extremamente específicas no backstory.

**b) Engenharia de Prompt Avançada:**
- Criação de arquivos de prompt separados ([app/agents/prompts/](app/agents/prompts/))
- Templates com placeholders dinâmicos: `{contexto}`, `{historico}`, `{mensagem}`, `{nome}`, `{score}`, `{limite_atual}`, `{limite_maximo}`
- Instruções explícitas sobre quando usar cada tag de redirecionamento
- Exemplos de boas e más respostas dentro dos prompts
- Instrução clara: "As transicoes entre agentes sao invisiveis ao cliente"

**Resultado:** Agentes com comportamentos previsíveis, naturais e especializados em suas funções.

### 3. Comportamento Ideal do Agente de Entrevista

**Desafio:**
O agente de entrevista inicialmente fazia perguntas em lote ou pulava etapas, resultando em:
- Experiência não-conversacional ("Qual sua renda, emprego, despesas e dívidas?")
- Coleta incompleta de dados
- Erro no cálculo do score por falta de informações
- Confusão do usuário sobre o que informar

**Solução Implementada:**

**a) Engenharia de Prompt Específica:**
```
"Conduza uma entrevista natural e conversacional, coletando UMA informacao por vez"
"Seja paciente e natural"
"Quando tiver todas as 5 informacoes, calcule o novo score"
```

**b) Controle via Tool:**
A tool `calcular_novo_score` ([app/agents/tools/entrevista_tools.py](app/agents/tools/entrevista_tools.py)) exige **todas** as 5 informações como parâmetros obrigatórios:
- renda_mensal: float
- tipo_emprego: str
- despesas_fixas: float
- num_dependentes: int
- dividas: float

Isso força o agente a coletar todas as informações antes de tentar calcular.

**c) Ajuste de max_iter:**
O agente de entrevista possui `max_iter=25`, forçando-o a ser mais eficiente e direto na coleta.

**Resultado:** Entrevistas naturais, coletando uma informação por vez, com validação automática de completude.

### 4. Parsing de Redirecionamentos e Limpeza de Respostas

**Desafio:**
As tags de redirecionamento (ex: `[REDIRECIONA_CREDITO]`) apareciam na resposta final ao usuário, causando confusão e quebrando a experiência natural.

**Solução Implementada:**
- Sistema de regex patterns no orquestrador ([app/agents/orchestrator.py](app/agents/orchestrator.py)):
```python
REDIRECT_PATTERNS = {
    r"\[REDIRECIONA_CREDITO\]": TipoAgente.CREDITO,
    r"\[REDIRECIONA_ENTREVISTA\]": TipoAgente.ENTREVISTA,
    r"\[REDIRECIONA_CAMBIO\]": TipoAgente.CAMBIO,
    r"\[REDIRECIONA_TRIAGEM\]": TipoAgente.TRIAGEM,
}
```
- Método `_detectar_redirecionamento()` para identificar tags
- Método `_limpar_tags_resposta()` para remover todas as tags antes de retornar ao usuário
- Separação clara entre "resposta bruta" (com tags) e "resposta final" (limpa)

**Resultado:** Experiência totalmente fluida onde o usuário nunca vê tags técnicas.

### 5. Integração com APIs Externas (SerpAPI)

**Desafio:**
Cotações de câmbio precisavam ser em tempo real, mas APIs de câmbio dedicadas são caras ou limitadas. O parsing de resultados do Google via SerpAPI é complexo devido a variações no formato da resposta.

**Solução Implementada:**
- Uso do SerpAPI com engine Google Search para consultas do tipo "1 USD to BRL"
- Método `_parse_serpapi_response()` com múltiplas estratégias de extração:
  1. Tentar `answer_box.result`
  2. Tentar `answer_box.answer`
  3. Tentar `knowledge_graph.description`
  4. Tentar `organic_results[0].snippet`
- Regex robusto para extração de valores: `r"(\d+\.?\d*)"`
- Tratamento de exceções (timeout, HTTP errors, parsing errors)
- Fallback retornando `None` em caso de falha

**Resultado:** Cotações confiáveis em tempo real.

## Escolhas Técnicas e Justificativas

### 1. CrewAI Framework

**Por que escolhemos:**
- **Abstração de Agentes:** CrewAI fornece uma abstração de alto nível para criação de agentes com role, goal e backstory, facilitando a definição de personalidades e comportamentos especializados
- **Sistema de Tools:** Decorador `@tool` simplifica a criação de ferramentas que os agentes podem usar, com documentação automática para o LLM
- **Orquestração com Crew:** Classe `Crew` gerencia execução de tasks e coordenação entre agentes
- **Integração com LLMs:** Suporte nativo a OpenAI, Anthropic e outros provedores via classe `LLM`
- **Process Types:** Suporte a processos sequenciais e hierárquicos

**Como usamos:**
- 4 agentes especializados criados com `Agent()`
- 9 tools customizadas usando decorador `@tool`
- Execução de tasks com `Crew.kickoff()`
- LLM configurável via settings (GPT-4o-mini por padrão)
- `max_iter` ajustado por agente para controlar iterações

**Benefícios obtidos:**
- Código limpo e declarativo
- Fácil adicionar novos agentes e tools
- Logs detalhados de execução (verbose mode)
- Prompts otimizados automaticamente para o LLM

### 2. OpenAI GPT-4o-mini

**Por que escolhemos:**
- **Custo-benefício:** GPT-4o-mini oferece excelente performance a custo reduzido 
- **Velocidade:** Latência baixa, essencial para experiência de chat em tempo real
- **Capacidade:** Suficiente para tasks de classificação, extração de informações e geração de respostas naturais

### 3. MongoDB para Memória

**Por que escolhemos:**
- **Flexibilidade de Schema:** Conversações têm estrutura variável, NoSQL é ideal
- **Performance em Escrita:** Alta taxa de inserts de mensagens
- **Queries Simples:** Buscas por conversation_id são diretas
- **Motor (AsyncIO):** Driver assíncrono nativo para Python, integração perfeita com FastAPI
- **Escalabilidade:** Fácil escalar horizontalmente se necessário


### 4. Streamlit para Frontend

**Por que escolhemos:**
- **Sugerido no Desafio:** Requisito do projeto

**Resultado:** Interface funcional e agradável para demonstração e uso interno.

### 5. FastAPI para Backend

**Por que escolhemos:**
- **Performance:** Um dos frameworks Python mais rápidos, baseado em Starlette e Pydantic
- **Async Nativo:** Suporte total a async/await, ideal para I/O-bound operations (LLM calls, DB)
- **Validação Automática:** Pydantic models integrados para validação de request/response
- **Documentação Automática:** Swagger UI  gerado automaticamente


### 6. Pydantic para Validação de Dados

**Por que escolhemos:**
- **Type Safety:** Validação automática de tipos em runtime
- **Validadores Customizados:** `@field_validator` para lógicas complexas (ex: validação de CPF)
- **Serialização:** Conversão automática para JSON
- **IDE Support:** Autocomplete e type checking
- **Integração:** FastAPI e Pydantic são projetados para trabalhar juntos

### 7. Pytest para Testes

**Por que escolhemos:**
- **Pytest:** Padrão para testes em Python


### 8. SerpAPI para Cotações de Câmbio

**Por que escolhemos:**
- **Dados em Tempo Real:** Usa Google Search para obter cotações atualizadas
- **Sem Rate Limits Agressivos:** Plano gratuito permite 100 searches/mês


### 9. Arquitetura em Camadas

**Por que escolhemos:**
- **Separação de Responsabilidades:** Cada camada tem função bem definida
- **Testabilidade:** Camadas podem ser testadas isoladamente
- **Manutenibilidade:** Mudanças em uma camada têm impacto limitado
- **Escalabilidade:** Camadas podem ser escaladas independentemente

**Camadas Implementadas:**
1. **Presentation:** FastAPI routes + Streamlit UI
2. **Orchestration:** AgentOrchestrator
3. **Agents:** CrewAI agents + tools
4. **Services:** Business logic (ClienteService, CreditoService, etc.)
5. **Data:** MongoDB + CSV + Pydantic models

## Tutorial de Execução e Testes

### Pré-requisitos

- **Python 3.12+** instalado
- **MongoDB 7+** instalado e rodando
- **Git** para clonar o repositório
- **Chave de API da OpenAI** ([obter aqui](https://platform.openai.com/api-keys))
- **Chave de API do SerpAPI** ([obter aqui](https://serpapi.com/manage-api-key))
- **URL de conexão MONGODB** ([obter aqui](https://account.mongodb.com/account/login))

### Instalação

#### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/multi-agent-banking-system.git
cd multi-agent-banking-system
```

#### 2. Crie e Ative um Ambiente Virtual

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

#### 4. Configure as Variáveis de Ambiente

Copie o arquivo de exemplo e edite com suas credenciais:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```bash
OPENAI_API_KEY=sk-sua-chave-aqui
OPENAI_MODEL=gpt-4o-mini
SERPAPI_KEY=sua-chave-serpapi-aqui
MONGO_URI=mongodb://localhost:27017
MONGO_DB=banking_agents
DEBUG=false
```


### Executando a Aplicação

#### Opção 1: Interface Web (Streamlit)

```bash
streamlit run app/frontend/chat.py
```
ou
```bash
.\run_chat
```
O Streamlit abrirá automaticamente em [http://localhost:8501](http://localhost:8501)

**Funcionalidades Disponíveis:**
- **Chat com Agente:** Converse com os agentes inteligentes
- **Adicionar Cliente:** Cadastre novos clientes no sistema
- **Listar Clientes:** Visualize todos os clientes cadastrados
- **Solicitações de Limite:** Veja histórico de solicitações de crédito

#### Opção 2: API REST (FastAPI) (Executa somente a api)

**Linux/Mac:**
```bash
uvicorn app.main:app --reload --port 8000
```

**Windows:**
```bash
uvicorn app.main:app --reload --port 8000
```

**Ou use o script fornecido (Windows):**
```bash
.\run
```

A API estará disponível em [http://localhost:8000](http://localhost:8000)

**Documentação Automática:**
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

#### Opção 3: Chat em Linha de Comando

Para usar o chat interativo no terminal:

```bash
python run_chat.bat
```

Ou manualmente:
```bash
streamlit run app/frontend/chat.py --server.headless=true
```

### Executando Testes

#### Executar Todos os Testes

```bash
pytest
```

### Testando a API com curl

#### Health Check

```bash
curl http://localhost:8000/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "app": "Multi-Agent Banking System"
}
```

#### Enviar Mensagem ao Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "mensagem": "Ola, gostaria de consultar meu limite",
    "conversation_id": "test-123"
  }'
```

**Resposta esperada:**
```json
{
  "resposta": "Olá! Para consultar seu limite, preciso autenticar você primeiro. Por favor, me informe seu CPF.",
  "agente_atual": "triagem",
  "atendimento_encerrado": false
}
```

#### Adicionar Novo Cliente

```bash
curl -X POST http://localhost:8000/admin/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "cpf": "12345678901",
    "nome": "João Silva",
    "data_nascimento": "1990-05-15",
    "score": 700
  }'
```

#### Listar Clientes

```bash
curl http://localhost:8000/admin/clientes
```

### Fluxo de Teste Completo

#### 1. Autenticação e Consulta de Limite

1. Inicie o Streamlit ou acesse a API
2. Envie: "Olá, gostaria de consultar meu limite"
3. Agente responde pedindo CPF
4. Envie: "11111111111" (CPF de teste precisa estar disponivel no CSV)
5. Agente pede data de nascimento
6. Envie: "1990-01-01"
7. Agente autentica e redireciona para agente de crédito
8. Agente de crédito exibe limite atual e máximo

#### 2. Solicitação de Aumento de Limite

Continuando do fluxo anterior:
9. Envie: "Gostaria de aumentar meu limite para 8000"
10. Sistema processa e aprova/rejeita baseado no score
11. Se rejeitado, agente oferece análise de perfil

#### 3. Análise de Perfil Financeiro

Se oferecido:
12. Envie: "Sim, quero fazer a análise"
13. Agente de entrevista pergunta renda mensal
14. Envie: "5000"
15. Agente pergunta tipo de emprego
16. Envie: "CLT"
17. Agente pergunta despesas fixas
18. Envie: "2000"
19. Agente pergunta número de dependentes
20. Envie: "1"
21. Agente pergunta valor de dívidas
22. Envie: "3000"
23. Sistema calcula novo score e redireciona para crédito
24. Agente de crédito informa novo limite disponível

#### 4. Consulta de Câmbio

1. Envie: "Qual a cotação do dólar?"
2. Sistema redireciona para agente de câmbio
3. Agente consulta SerpAPI e retorna cotação atual
4. Agente pergunta se deseja consultar outra moeda


