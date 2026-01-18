from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class StatusSolicitacao(str, Enum):
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    REJEITADO = "rejeitado"


class SolicitacaoCredito(BaseModel):
    cpf_cliente: str
    data_hora_solicitacao: datetime
    limite_atual: float
    novo_limite_solicitado: float
    status_pedido: StatusSolicitacao = StatusSolicitacao.PENDENTE
