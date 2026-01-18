from enum import Enum

from crewai import Agent, LLM

from app.config import settings


class TipoAgente(str, Enum):
    TRIAGEM = "triagem"
    CREDITO = "credito"
    ENTREVISTA = "entrevista"
    CAMBIO = "cambio"


def get_llm() -> LLM:
    return LLM(
        model=f"openai/{settings.openai_model}",
        api_key=settings.openai_api_key,
        temperature=0.3,
    )


def criar_agente_triagem() -> Agent:
    from app.agents.tools.triagem_tools import (
        autenticar_cliente,
        verificar_autenticacao,
    )

    return Agent(
        role="Assistente Virtual do Banco Agil - Modulo de Autenticacao",
        goal="Autenticar clientes e redirecionar para o agente especializado apropriado",
        backstory="""Voce e a porta de entrada do Banco Agil. Sua funcao e autenticar clientes
usando CPF e data de nascimento, identificar qual servico precisam, e redirecionar IMEDIATAMENTE
para o agente especializado. Seja rapido e eficiente - apenas identifique e redirecione.
As transicoes entre agentes sao invisiveis ao cliente.""",
        tools=[autenticar_cliente, verificar_autenticacao],
        llm=get_llm(),
        verbose=settings.debug,
        allow_delegation=False,
        max_iter=50,
    )


def criar_agente_credito() -> Agent:
    from app.agents.tools.credito_tools import (
        consultar_limite,
        obter_limite_maximo,
        solicitar_aumento_limite,
    )

    return Agent(
        role="Assistente Virtual do Banco Agil - Modulo de Credito",
        goal="Consultar limites, processar solicitacoes de aumento, e oferecer analise de perfil quando necessario",
        backstory="""Voce e o especialista em credito do Banco Agil. Use as ferramentas disponiveis
para consultar limites e processar pedidos de aumento. Quando o cliente informa um valor desejado,
processe imediatamente sem pedir confirmacao. Se a solicitacao for rejeitada, ofereca uma analise
de perfil financeiro para melhorar o score. As transicoes entre agentes sao invisiveis ao cliente.""",
        tools=[consultar_limite, solicitar_aumento_limite, obter_limite_maximo],
        llm=get_llm(),
        verbose=settings.debug,
        allow_delegation=False,
        max_iter=50,
    )


def criar_agente_entrevista() -> Agent:
    from app.agents.tools.entrevista_tools import calcular_novo_score

    return Agent(
        role="Assistente Virtual do Banco Agil - Modulo de Analise Financeira",
        goal="Conduzir entrevista financeira conversacional, coletar 5 informacoes, e calcular novo score",
        backstory="""Voce e o especialista em analise financeira do Banco Agil. Conduza uma entrevista
natural e conversacional, coletando UMA informacao por vez: renda mensal, tipo de emprego (CLT, PJ,
AUTONOMO ou DESEMPREGADO), despesas fixas, numero de dependentes, e dividas. Quando tiver todas as
5 informacoes, calcule o novo score e redirecione para o agente de credito. Seja paciente e natural.
As transicoes entre agentes sao invisiveis ao cliente.""",
        tools=[calcular_novo_score],
        llm=get_llm(),
        verbose=settings.debug,
        allow_delegation=False,
        max_iter=25,
    )


def criar_agente_cambio() -> Agent:
    from app.agents.tools.cambio_tools import (
        consultar_cotacao,
        listar_moedas_disponiveis,
    )

    return Agent(
        role="Assistente Virtual do Banco Agil - Modulo de Cambio",
        goal="Fornecer cotacoes de moedas estrangeiras de forma rapida e objetiva",
        backstory="""Voce e o especialista em cambio do Banco Agil. Forneca cotacoes de moedas
de forma direta e objetiva, sem saudacoes. Use as ferramentas para consultar cotacoes e listar
moedas disponiveis. Apos informar uma cotacao, pergunte se o cliente deseja consultar outra moeda.
As transicoes entre agentes sao invisiveis ao cliente.""",
        tools=[consultar_cotacao, listar_moedas_disponiveis],
        llm=get_llm(),
        verbose=settings.debug,
        allow_delegation=False,
        max_iter=50,
    )
