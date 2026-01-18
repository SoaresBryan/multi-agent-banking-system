import csv
from datetime import datetime
from pathlib import Path

from app.models import SolicitacaoCredito, StatusSolicitacao


class CreditoService:
    def __init__(
        self,
        solicitacoes_path: str | None = None,
        score_limite_path: str | None = None,
    ):
        base_path = Path(__file__).parent.parent / "data"
        self.solicitacoes_path = Path(solicitacoes_path or base_path / "solicitacoes_aumento_limite.csv")
        self.score_limite_path = Path(score_limite_path or base_path / "score_limite.csv")

    def obter_limite_maximo_por_score(self, score: int) -> float:
        try:
            with open(self.score_limite_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    score_min = int(row["score_minimo"])
                    score_max = int(row["score_maximo"])
                    if score_min <= score <= score_max:
                        return float(row["limite_maximo"])
        except FileNotFoundError:
            pass
        return 0.0

    def verificar_elegibilidade(
        self, score: int, limite_solicitado: float
    ) -> tuple[bool, float]:
        limite_maximo = self.obter_limite_maximo_por_score(score)
        elegivel = limite_solicitado <= limite_maximo
        return elegivel, limite_maximo

    def registrar_solicitacao(
        self,
        cpf: str,
        limite_atual: float,
        novo_limite: float,
        score: int,
    ) -> SolicitacaoCredito:
        elegivel, _ = self.verificar_elegibilidade(score, novo_limite)
        status = StatusSolicitacao.APROVADO if elegivel else StatusSolicitacao.REJEITADO

        solicitacao = SolicitacaoCredito(
            cpf_cliente=cpf,
            data_hora_solicitacao=datetime.now(),
            limite_atual=limite_atual,
            novo_limite_solicitado=novo_limite,
            status_pedido=status,
        )

        self._salvar_solicitacao(solicitacao)
        return solicitacao

    def _salvar_solicitacao(self, solicitacao: SolicitacaoCredito) -> None:
        arquivo_existe = self.solicitacoes_path.exists()
        with open(self.solicitacoes_path, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            if not arquivo_existe or self.solicitacoes_path.stat().st_size == 0:
                writer.writerow([
                    "cpf_cliente",
                    "data_hora_solicitacao",
                    "limite_atual",
                    "novo_limite_solicitado",
                    "status_pedido",
                ])
            writer.writerow([
                solicitacao.cpf_cliente,
                solicitacao.data_hora_solicitacao.isoformat(),
                solicitacao.limite_atual,
                solicitacao.novo_limite_solicitado,
                solicitacao.status_pedido.value,
            ])
