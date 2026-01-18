import csv
from datetime import datetime
from pathlib import Path

from app.models import Cliente


class ClienteService:
    def __init__(self, csv_path: str | None = None, score_limite_path: str | None = None):
        if csv_path is None:
            csv_path = Path(__file__).parent.parent / "data" / "clientes.csv"
        if score_limite_path is None:
            score_limite_path = Path(__file__).parent.parent / "data" / "score_limite.csv"
        self.csv_path = Path(csv_path)
        self.score_limite_path = Path(score_limite_path)

    def buscar_por_cpf(self, cpf: str) -> Cliente | None:
        cpf_limpo = cpf.replace(".", "").replace("-", "")
        try:
            with open(self.csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["cpf"] == cpf_limpo:
                        return Cliente(
                            cpf=row["cpf"],
                            nome=row["nome"],
                            data_nascimento=datetime.strptime(
                                row["data_nascimento"], "%Y-%m-%d"
                            ).date(),
                            score=int(row["score"]),
                            limite_atual=float(row["limite_atual"]),
                        )
        except FileNotFoundError:
            return None
        return None

    def autenticar(self, cpf: str, data_nascimento: str) -> Cliente | None:
        cliente = self.buscar_por_cpf(cpf)
        if cliente is None:
            return None

        try:
            data_input = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
        except ValueError:
            try:
                data_input = datetime.strptime(data_nascimento, "%d/%m/%Y").date()
            except ValueError:
                return None

        if cliente.data_nascimento == data_input:
            return cliente
        return None

    def atualizar_score(self, cpf: str, novo_score: int) -> bool:
        cpf_limpo = cpf.replace(".", "").replace("-", "")
        linhas = []
        encontrado = False

        try:
            with open(self.csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    if row["cpf"] == cpf_limpo:
                        row["score"] = str(novo_score)
                        encontrado = True
                    linhas.append(row)
        except FileNotFoundError:
            return False

        if not encontrado:
            return False

        with open(self.csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(linhas)

        return True

    def atualizar_limite(self, cpf: str, novo_limite: float) -> bool:
        cpf_limpo = cpf.replace(".", "").replace("-", "")
        linhas = []
        encontrado = False

        try:
            with open(self.csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    if row["cpf"] == cpf_limpo:
                        row["limite_atual"] = f"{novo_limite:.2f}"
                        encontrado = True
                    linhas.append(row)
        except FileNotFoundError:
            return False

        if not encontrado:
            return False

        with open(self.csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(linhas)

        return True

    def calcular_limite_por_score(self, score: int) -> float:
        """Calcula o limite máximo baseado no score consultando a tabela score_limite.csv"""
        try:
            with open(self.score_limite_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    score_min = int(row["score_minimo"])
                    score_max = int(row["score_maximo"])
                    if score_min <= score <= score_max:
                        return float(row["limite_maximo"])
        except FileNotFoundError:
            return 0.0
        return 0.0

    def adicionar_cliente(
        self, cpf: str, nome: str, data_nascimento: str, score: int
    ) -> bool:
        """Adiciona um novo cliente ao CSV"""
        cpf_limpo = cpf.replace(".", "").replace("-", "")

        if len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
            return False

        if self.buscar_por_cpf(cpf_limpo):
            return False

        try:
            data_obj = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
        except ValueError:
            try:
                data_obj = datetime.strptime(data_nascimento, "%d/%m/%Y").date()
                data_nascimento = data_obj.strftime("%Y-%m-%d")
            except ValueError:
                return False

        limite = self.calcular_limite_por_score(score)

        try:
            with open(self.csv_path, "a", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "cpf",
                        "nome",
                        "data_nascimento",
                        "score",
                        "limite_atual",
                    ],
                )
                writer.writerow(
                    {
                        "cpf": cpf_limpo,
                        "nome": nome,
                        "data_nascimento": data_nascimento,
                        "score": score,
                        "limite_atual": f"{limite:.2f}",
                    }
                )
            return True
        except Exception:
            return False

    def listar_todos(self) -> list[Cliente]:
        """Lista todos os clientes do CSV"""
        clientes = []
        try:
            with open(self.csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        clientes.append(
                            Cliente(
                                cpf=row["cpf"],
                                nome=row["nome"],
                                data_nascimento=datetime.strptime(
                                    row["data_nascimento"], "%Y-%m-%d"
                                ).date(),
                                score=int(row["score"]),
                                limite_atual=float(row["limite_atual"]),
                            )
                        )
                    except Exception:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(
                            f"Cliente com dados inválidos ignorado: CPF={row.get('cpf', 'N/A')}"
                        )
                        continue
        except FileNotFoundError:
            return []
        return clientes
