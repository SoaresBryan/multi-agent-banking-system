import csv
from datetime import datetime
from pathlib import Path

from app.models.solicitacao import SolicitacaoCredito, StatusSolicitacao


class SolicitacaoService:
    def __init__(self, csv_path: str | None = None):
        if csv_path is None:
            csv_path = (
                Path(__file__).parent.parent
                / "data"
                / "solicitacoes_aumento_limite.csv"
            )
        self.csv_path = Path(csv_path)

    def listar_todas(self) -> list[SolicitacaoCredito]:
        """Lista todas as solicitações de aumento de limite do CSV"""
        solicitacoes = []
        try:
            with open(self.csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    solicitacoes.append(
                        SolicitacaoCredito(
                            cpf_cliente=row["cpf_cliente"],
                            data_hora_solicitacao=datetime.fromisoformat(
                                row["data_hora_solicitacao"]
                            ),
                            limite_atual=float(row["limite_atual"]),
                            novo_limite_solicitado=float(row["novo_limite_solicitado"]),
                            status_pedido=StatusSolicitacao(row["status_pedido"]),
                        )
                    )
        except FileNotFoundError:
            return []
        return solicitacoes

    def listar_por_cpf(self, cpf: str) -> list[SolicitacaoCredito]:
        """Lista todas as solicitações de um cliente específico"""
        cpf_limpo = cpf.replace(".", "").replace("-", "")
        todas = self.listar_todas()
        return [s for s in todas if s.cpf_cliente == cpf_limpo]
