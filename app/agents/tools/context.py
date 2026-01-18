"""Gerenciador de contexto global para compartilhar estado entre tools."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContextoConversa:
    """Contexto compartilhado entre agentes durante uma conversa."""

    cliente_autenticado: bool = False
    cpf: str | None = None
    nome_cliente: str | None = None
    score: int | None = None
    limite_atual: float | None = None
    tentativas_auth: int = 0
    historico: list[dict[str, str]] = field(default_factory=list)
    dados_extras: dict[str, Any] = field(default_factory=dict)

    def adicionar_mensagem(self, role: str, content: str) -> None:
        self.historico.append({"role": role, "content": content})

    def to_dict(self) -> dict:
        return {
            "cliente_autenticado": self.cliente_autenticado,
            "cpf": self.cpf,
            "nome_cliente": self.nome_cliente,
            "score": self.score,
            "limite_atual": self.limite_atual,
            "tentativas_auth": self.tentativas_auth,
            "dados_extras": self.dados_extras,
        }


_contexto_atual: ContextoConversa | None = None


def set_contexto(contexto: ContextoConversa) -> None:
    global _contexto_atual
    _contexto_atual = contexto


def get_contexto() -> ContextoConversa:
    global _contexto_atual
    if _contexto_atual is None:
        _contexto_atual = ContextoConversa()
    return _contexto_atual


def reset_contexto() -> None:
    global _contexto_atual
    _contexto_atual = ContextoConversa()
