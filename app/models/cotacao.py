from datetime import datetime
from pydantic import BaseModel


class Cotacao(BaseModel):
    moeda_origem: str
    moeda_destino: str
    valor: float
    data_consulta: datetime
