from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models import Cliente
from app.models.solicitacao import SolicitacaoCredito
from app.services import ClienteService, SolicitacaoService

router = APIRouter(prefix="/admin", tags=["admin"])


class AdicionarClienteRequest(BaseModel):
    cpf: str
    nome: str
    data_nascimento: str
    score: int


class AdicionarClienteResponse(BaseModel):
    success: bool
    message: str
    cliente: Cliente | None = None


class ClienteResponse(BaseModel):
    cpf: str
    nome: str
    data_nascimento: date
    score: int
    limite_atual: float


@router.post("/clientes", response_model=AdicionarClienteResponse)
async def adicionar_cliente(request: AdicionarClienteRequest):
    """
    Adiciona um novo cliente ao sistema.

    O limite inicial é calculado automaticamente baseado no score do cliente.
    """
    cliente_service = ClienteService()

    cpf_limpo = request.cpf.replace(".", "").replace("-", "").strip()
    if len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
        raise HTTPException(
            status_code=400,
            detail="CPF inválido. O CPF deve conter exatamente 11 dígitos numéricos.",
        )

    if cliente_service.buscar_por_cpf(request.cpf):
        raise HTTPException(status_code=400, detail="Cliente já existe no sistema")

    sucesso = cliente_service.adicionar_cliente(
        cpf=request.cpf,
        nome=request.nome,
        data_nascimento=request.data_nascimento,
        score=request.score,
    )

    if not sucesso:
        raise HTTPException(
            status_code=400,
            detail="Erro ao adicionar cliente. Verifique os dados informados.",
        )

    # Buscar cliente adicionado
    cliente = cliente_service.buscar_por_cpf(request.cpf)

    return AdicionarClienteResponse(
        success=True,
        message="Cliente adicionado com sucesso",
        cliente=cliente,
    )


@router.get("/clientes", response_model=list[ClienteResponse])
async def listar_clientes():
    """
    Lista todos os clientes cadastrados no sistema.
    """
    cliente_service = ClienteService()
    clientes = cliente_service.listar_todos()

    return [
        ClienteResponse(
            cpf=cliente.cpf,
            nome=cliente.nome,
            data_nascimento=cliente.data_nascimento,
            score=cliente.score,
            limite_atual=cliente.limite_atual,
        )
        for cliente in clientes
    ]


@router.get("/solicitacoes", response_model=list[SolicitacaoCredito])
async def listar_solicitacoes():
    """
    Lista todas as solicitações de aumento de limite.
    """
    solicitacao_service = SolicitacaoService()
    return solicitacao_service.listar_todas()


@router.get("/solicitacoes/{cpf}", response_model=list[SolicitacaoCredito])
async def listar_solicitacoes_por_cpf(cpf: str):
    """
    Lista todas as solicitações de aumento de limite de um cliente específico.
    """
    solicitacao_service = SolicitacaoService()
    solicitacoes = solicitacao_service.listar_por_cpf(cpf)

    if not solicitacoes:
        raise HTTPException(
            status_code=404, detail="Nenhuma solicitação encontrada para este CPF"
        )

    return solicitacoes
