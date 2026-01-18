"""Tools para o Agente de Entrevista de Credito."""

import logging

from crewai.tools import tool

from app.agents.tools.context import get_contexto
from app.services.cliente_service import ClienteService
from app.services.score_service import ScoreService, TipoEmprego

logger = logging.getLogger(__name__)

_cliente_service = ClienteService()
_score_service = ScoreService()


@tool("calcular_novo_score")
def calcular_novo_score(
    renda_mensal: float,
    tipo_emprego: str,
    despesas_mensais: float,
    num_dependentes: int,
    dividas_atuais: float,
) -> str:
    """
    Calcula o novo score do cliente com base nas informacoes financeiras coletadas.

    Args:
        renda_mensal: Renda mensal do cliente em reais
        tipo_emprego: Tipo de emprego (CLT, FORMAL, PJ, AUTONOMO, DESEMPREGADO)
        despesas_mensais: Total de despesas fixas mensais em reais
        num_dependentes: Numero de dependentes (0, 1, 2, 3 ou mais)
        dividas_atuais: Total de dividas em aberto em reais (0 se nao tiver)

    Returns:
        String formatada com o resultado do calculo
    """
    logger.info(
        f"[TOOL] calcular_novo_score chamada com: "
        f"renda={renda_mensal}, emprego={tipo_emprego}, "
        f"despesas={despesas_mensais}, dependentes={num_dependentes}, "
        f"dividas={dividas_atuais}"
    )

    contexto = get_contexto()

    tipo_upper = tipo_emprego.upper().strip()
    tipos_validos = {
        "CLT": TipoEmprego.FORMAL,
        "FORMAL": TipoEmprego.FORMAL,
        "PJ": TipoEmprego.AUTONOMO,
        "AUTONOMO": TipoEmprego.AUTONOMO,
        "AUTÔNOMO": TipoEmprego.AUTONOMO,
        "DESEMPREGADO": TipoEmprego.DESEMPREGADO,
    }

    if tipo_upper not in tipos_validos:
        logger.warning(f"[TOOL] Tipo de emprego invalido: {tipo_upper}")
        return f"ERRO|Tipo de emprego invalido. Use: CLT, FORMAL, PJ, AUTONOMO ou DESEMPREGADO"

    tipo_emprego_enum = tipos_validos[tipo_upper]

    if renda_mensal <= 0:
        logger.warning(f"[TOOL] Renda invalida: {renda_mensal}")
        return "ERRO|Renda mensal deve ser maior que zero"

    if despesas_mensais < 0:
        logger.warning(f"[TOOL] Despesas invalidas: {despesas_mensais}")
        return "ERRO|Despesas mensais nao podem ser negativas"

    if despesas_mensais > renda_mensal * 1.5:
        logger.warning(
            f"[TOOL] Despesas ({despesas_mensais}) muito altas em relacao a renda ({renda_mensal}). "
            "Isso resultara em score baixo."
        )

    tem_dividas = dividas_atuais > 0

    novo_score = _score_service.calcular_score(
        renda_mensal=renda_mensal,
        tipo_emprego=tipo_emprego_enum,
        despesas_fixas=despesas_mensais,
        num_dependentes=num_dependentes,
        tem_dividas=tem_dividas,
    )

    score_anterior = contexto.score
    limite_atual = contexto.limite_atual

    from app.services.credito_service import CreditoService

    credito_service = CreditoService()
    novo_limite_maximo = credito_service.obter_limite_maximo_por_score(novo_score)
    limite_maximo_anterior = credito_service.obter_limite_maximo_por_score(score_anterior)

    logger.info(
        f"[TOOL] Score calculado: {score_anterior} -> {novo_score}, "
        f"Limite maximo: R$ {limite_maximo_anterior:.2f} -> R$ {novo_limite_maximo:.2f}"
    )

    if novo_score < score_anterior or novo_limite_maximo < limite_atual:
        logger.warning(
            f"[TOOL] VALIDACAO: Novo score ({novo_score}) ou limite maximo ({novo_limite_maximo:.2f}) "
            f"e MENOR que o atual (score: {score_anterior}, limite: {limite_atual:.2f}). "
            f"NAO sera atualizado na base de dados para proteger o cliente."
        )

        return (
            f"ANALISE_CONCLUIDA_SEM_MELHORIA. "
            f"Score mantido em: {score_anterior} pontos. "
            f"Limite maximo atual: R$ {limite_maximo_anterior:.2f}. "
            f"IMPORTANTE: Informe ao cliente que a analise nao resultou em melhoria do limite. "
            f"O limite atual de R$ {limite_atual:.2f} esta mantido. "
            f"Inclua [REDIRECIONA_CREDITO] na resposta."
        )

    contexto.score = novo_score

    if contexto.cpf:
        _cliente_service.atualizar_score(contexto.cpf, novo_score)
        logger.info(f"[TOOL] Score atualizado no CSV: {score_anterior} -> {novo_score}")

    return (
        f"SUCESSO! Calculo finalizado. "
        f"Score anterior: {score_anterior} pontos. "
        f"Novo score: {novo_score} pontos. "
        f"Novo limite maximo: R$ {novo_limite_maximo:.2f}. "
        f"IMPORTANTE: Informe estes resultados ao cliente e inclua [REDIRECIONA_CREDITO] na resposta."
    )
