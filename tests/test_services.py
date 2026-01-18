import pytest
from app.services.cliente_service import ClienteService
from app.services.score_service import ScoreService, TipoEmprego
from app.services.credito_service import CreditoService


class TestScoreService:
    def setup_method(self):
        self.service = ScoreService()

    def test_calcular_score_emprego_formal_sem_dividas(self):
        score = self.service.calcular_score(
            renda_mensal=5000,
            tipo_emprego=TipoEmprego.FORMAL,
            despesas_fixas=2000,
            num_dependentes=1,
            tem_dividas=False,
        )
        # (5000 / 2001) * 30 + 300 + 80 + 100 = ~555
        assert 500 <= score <= 600

    def test_calcular_score_desempregado_com_dividas(self):
        score = self.service.calcular_score(
            renda_mensal=0,
            tipo_emprego=TipoEmprego.DESEMPREGADO,
            despesas_fixas=1000,
            num_dependentes=3,
            tem_dividas=True,
        )
        # 0 + 0 + 30 + (-100) = baixo
        assert score < 100

    def test_score_minimo_zero(self):
        score = self.service.calcular_score(
            renda_mensal=0,
            tipo_emprego=TipoEmprego.DESEMPREGADO,
            despesas_fixas=10000,
            num_dependentes=5,
            tem_dividas=True,
        )
        assert score >= 0

    def test_score_maximo_1000(self):
        score = self.service.calcular_score(
            renda_mensal=100000,
            tipo_emprego=TipoEmprego.FORMAL,
            despesas_fixas=100,
            num_dependentes=0,
            tem_dividas=False,
        )
        assert score <= 1000


class TestClienteService:
    def test_validacao_cpf_formato(self):
        from app.models.cliente import Cliente

        # CPF válido com 11 dígitos
        cliente = Cliente(
            cpf="12345678901",
            nome="Test",
            data_nascimento="1990-01-01",
            score=500,
            limite_atual=1000.0,
        )
        assert cliente.cpf == "12345678901"

    def test_validacao_cpf_invalido(self):
        from app.models.cliente import Cliente

        with pytest.raises(ValueError):
            Cliente(
                cpf="123",  # CPF inválido
                nome="Test",
                data_nascimento="1990-01-01",
            )
