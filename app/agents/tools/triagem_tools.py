"""Tools para o Agente de Triagem."""

from crewai.tools import tool

from app.agents.tools.context import get_contexto
from app.services.cliente_service import ClienteService

_cliente_service = ClienteService()


@tool("autenticar_cliente")
def autenticar_cliente(cpf: str, data_nascimento: str) -> str:
    """
    Autentica o cliente usando CPF e data de nascimento.
    Retorna os dados do cliente se autenticado ou mensagem de erro.

    Args:
        cpf: CPF do cliente (com ou sem formatacao)
        data_nascimento: Data de nascimento (formato: DD/MM/AAAA ou AAAA-MM-DD)
    """
    contexto = get_contexto()
    cliente = _cliente_service.autenticar(cpf, data_nascimento)

    if cliente:
        contexto.cliente_autenticado = True
        contexto.cpf = cliente.cpf
        contexto.nome_cliente = cliente.nome
        contexto.score = cliente.score
        contexto.limite_atual = cliente.limite_atual
        return f"AUTENTICADO|{cliente.nome}|{cliente.score}|{cliente.limite_atual}"
    else:
        contexto.tentativas_auth += 1
        tentativas_restantes = 3 - contexto.tentativas_auth
        if tentativas_restantes > 0:
            return f"FALHA|{tentativas_restantes} tentativa(s) restante(s)"
        else:
            return "BLOQUEADO|Limite de tentativas excedido"


@tool("verificar_autenticacao")
def verificar_autenticacao() -> str:
    """
    Verifica se o cliente ja esta autenticado na sessao atual.
    """
    contexto = get_contexto()
    if contexto.cliente_autenticado:
        return f"AUTENTICADO|{contexto.nome_cliente}"
    return f"NAO_AUTENTICADO|Tentativas: {contexto.tentativas_auth}/3"
