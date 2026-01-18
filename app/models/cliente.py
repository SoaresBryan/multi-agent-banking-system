from datetime import date
from pydantic import BaseModel, field_validator
import re


class Cliente(BaseModel):
    cpf: str
    nome: str
    data_nascimento: date
    score: int = 0
    limite_atual: float = 0.0

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, v: str) -> str:
        cpf = re.sub(r"\D", "", v)
        if len(cpf) != 11:
            raise ValueError("CPF deve ter 11 dígitos")
        return cpf

    @field_validator("score")
    @classmethod
    def validar_score(cls, v: int) -> int:
        if not 0 <= v <= 1000:
            raise ValueError("Score deve estar entre 0 e 1000")
        return v
