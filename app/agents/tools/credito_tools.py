"""Tools para o Agente de Credito."""

import logging

from crewai.tools import tool

from app.agents.tools.context import get_contexto
from app.services.cliente_service import ClienteService
from app.services.credito_service import CreditoService

logger = logging.getLogger(__name__)

_cliente_service = ClienteService()
_credito_service = CreditoService()


@tool("consultar_limite")
def consultar_limite() -> str:
    """
    Consulta o limite de credito atual do cliente autenticado.
    Retorna limite atual, score e limite maximo permitido pelo score.
    """
    logger.info("[TOOL] consultar_limite chamada")

    contexto = get_contexto()
    if not contexto.cliente_autenticado:
        logger.warning("[TOOL] Cliente nao autenticado")
        return "ERRO|Cliente nao autenticado"

    limite_atual = contexto.limite_atual
    score = contexto.score
    limite_maximo = _credito_service.obter_limite_maximo_por_score(score)

    logger.info(
        f"[TOOL] Limite consultado: atual=R$ {limite_atual:.2f}, "
        f"score={score}, maximo=R$ {limite_maximo:.2f}"
    )

    return f"LIMITE|{limite_atual}|{score}|{limite_maximo}"


@tool("solicitar_aumento_limite")
def solicitar_aumento_limite(novo_limite: float) -> str:
    """
    Processa uma solicitacao de aumento de limite de credito.

    Args:
        novo_limite: Valor do novo limite desejado em reais
    """
    logger.info(
        f"[TOOL] solicitar_aumento_limite chamada com novo_limite={novo_limite}"
    )

    contexto = get_contexto()
    if not contexto.cliente_autenticado:
        logger.warning("[TOOL] Cliente nao autenticado")
        return "ERRO|Cliente nao autenticado"

    logger.info(
        f"[TOOL] Processando solicitacao: CPF={contexto.cpf}, "
        f"Limite atual={contexto.limite_atual}, "
        f"Novo limite={novo_limite}, Score={contexto.score}"
    )

    solicitacao = _credito_service.registrar_solicitacao(
        cpf=contexto.cpf,
        limite_atual=contexto.limite_atual,
        novo_limite=novo_limite,
        score=contexto.score,
    )

    if solicitacao.status_pedido.value == "aprovado":
        _cliente_service.atualizar_limite(contexto.cpf, novo_limite)
        contexto.limite_atual = novo_limite
        logger.info(f"[TOOL] Aumento APROVADO: novo limite = R$ {novo_limite:.2f}")
        return f"APROVADO|{novo_limite}"
    else:
        limite_maximo = _credito_service.obter_limite_maximo_por_score(contexto.score)
        logger.info(
            f"[TOOL] Aumento REJEITADO: limite solicitado = R$ {novo_limite:.2f}, "
            f"limite maximo = R$ {limite_maximo:.2f}, score = {contexto.score}"
        )
        return f"REJEITADO|{limite_maximo}|{contexto.score}"


@tool("obter_limite_maximo")
def obter_limite_maximo() -> str:
    """
    Retorna o limite maximo que o cliente pode solicitar com seu score atual.
    """
    logger.info("[TOOL] obter_limite_maximo chamada")

    contexto = get_contexto()
    if not contexto.cliente_autenticado:
        logger.warning("[TOOL] Cliente nao autenticado")
        return "ERRO|Cliente nao autenticado"

    limite_maximo = _credito_service.obter_limite_maximo_por_score(contexto.score)

    logger.info(
        f"[TOOL] Limite maximo obtido: R$ {limite_maximo:.2f} para score {contexto.score}"
    )

    return f"LIMITE_MAXIMO|{limite_maximo}|{contexto.score}"
