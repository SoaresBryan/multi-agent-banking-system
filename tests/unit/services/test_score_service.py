"""Testes unitários para ScoreService."""

import pytest

from app.services import ScoreService
from app.services.score_service import TipoEmprego


class TestScoreServiceCalcularScore:
    """Testes para o método calcular_score."""

    def test_score_ideal(self):
        """Deve calcular score máximo para condições ideais."""
        service = ScoreService()
        score = service.calcular_score(
            renda_mensal=10000.0,
            tipo_emprego=TipoEmprego.FORMAL,
            despesas_fixas=2000.0,
            num_dependentes=0,
            tem_dividas=False
        )

        assert score == 649

    def test_score_minimo(self):
        """Deve calcular score mínimo (0) para condições ruins."""
        service = ScoreService()
        score = service.calcular_score(
            renda_mensal=1000.0,
            tipo_emprego=TipoEmprego.DESEMPREGADO,
            despesas_fixas=2000.0,
            num_dependentes=3,
            tem_dividas=True
        )

        assert score == 0

    def test_score_com_emprego_formal(self):
        """Deve calcular score corretamente com emprego formal."""
        service = ScoreService()
        score = service.calcular_score(
            renda_mensal=5000.0,
            tipo_emprego=TipoEmprego.FORMAL,
            despesas_fixas=2000.0,
            num_dependentes=1,
            tem_dividas=False
        )

        assert score > 0
        assert score <= 1000

    def test_score_com_emprego_autonomo(self):
        """Deve calcular score com peso menor para emprego autônomo."""
        service = ScoreService()
        score_formal = service.calcular_score(
            renda_mensal=5000.0,
            tipo_emprego=TipoEmprego.FORMAL,
            despesas_fixas=2000.0,
            num_dependentes=1,
            tem_dividas=False
        )
        score_autonomo = service.calcular_score(
            renda_mensal=5000.0,
            tipo_emprego=TipoEmprego.AUTONOMO,
            despesas_fixas=2000.0,
            num_dependentes=1,
            tem_dividas=False
        )

        assert score_autonomo < score_formal

    def test_score_com_dividas(self):
        """Deve reduzir score quando tem dívidas."""
        service = ScoreService()
        score_sem_dividas = service.calcular_score(
            renda_mensal=5000.0,
            tipo_emprego=TipoEmprego.FORMAL,
            despesas_fixas=2000.0,
            num_dependentes=1,
            tem_dividas=False
        )
        score_com_dividas = service.calcular_score(
            renda_mensal=5000.0,
            tipo_emprego=TipoEmprego.FORMAL,
            despesas_fixas=2000.0,
            num_dependentes=1,
            tem_dividas=True
        )

        assert score_com_dividas < score_sem_dividas

    def test_score_com_dependentes(self):
        """Deve reduzir score com mais dependentes."""
        service = ScoreService()
        score_sem_dependentes = service.calcular_score(
            renda_mensal=5000.0,
            tipo_emprego=TipoEmprego.FORMAL,
            despesas_fixas=2000.0,
            num_dependentes=0,
            tem_dividas=False
        )
        score_com_dependentes = service.calcular_score(
            renda_mensal=5000.0,
            tipo_emprego=TipoEmprego.FORMAL,
            despesas_fixas=2000.0,
            num_dependentes=3,
            tem_dividas=False
        )

        assert score_com_dependentes < score_sem_dependentes

    def test_score_alta_renda_baixa_despesa(self):
        """Deve calcular score alto para alta renda e baixas despesas."""
        service = ScoreService()
        score = service.calcular_score(
            renda_mensal=10000.0,
            tipo_emprego=TipoEmprego.FORMAL,
            despesas_fixas=1000.0,
            num_dependentes=0,
            tem_dividas=False
        )

        assert score >= 500

    def test_score_baixa_renda_alta_despesa(self):
        """Deve calcular score baixo para baixa renda e altas despesas."""
        service = ScoreService()
        score = service.calcular_score(
            renda_mensal=2000.0,
            tipo_emprego=TipoEmprego.AUTONOMO,
            despesas_fixas=1800.0,
            num_dependentes=2,
            tem_dividas=True
        )

        assert score < 300

    def test_score_limite_superior(self):
        """Deve limitar score ao máximo de 1000."""
        service = ScoreService()
        score = service.calcular_score(
            renda_mensal=100000.0,
            tipo_emprego=TipoEmprego.FORMAL,
            despesas_fixas=100.0,
            num_dependentes=0,
            tem_dividas=False
        )

        assert score <= 1000

    def test_score_limite_inferior(self):
        """Deve limitar score ao mínimo de 0."""
        service = ScoreService()
        score = service.calcular_score(
            renda_mensal=0.0,
            tipo_emprego=TipoEmprego.DESEMPREGADO,
            despesas_fixas=5000.0,
            num_dependentes=5,
            tem_dividas=True
        )

        assert score >= 0

    def test_score_despesas_maiores_que_renda(self):
        """Deve calcular score quando despesas > renda."""
        service = ScoreService()
        score = service.calcular_score(
            renda_mensal=2000.0,
            tipo_emprego=TipoEmprego.FORMAL,
            despesas_fixas=3000.0,
            num_dependentes=1,
            tem_dividas=False
        )

        assert score == 499

    def test_score_tipo_emprego_clt_alias(self):
        """Deve aceitar alias CLT como emprego formal."""
        service = ScoreService()
        score = service.calcular_score(
            renda_mensal=5000.0,
            tipo_emprego=TipoEmprego.CLT,
            despesas_fixas=2000.0,
            num_dependentes=1,
            tem_dividas=False
        )

        assert score > 0

    def test_score_tipo_emprego_pj_alias(self):
        """Deve aceitar alias PJ como emprego autônomo."""
        service = ScoreService()
        score = service.calcular_score(
            renda_mensal=5000.0,
            tipo_emprego=TipoEmprego.PJ,
            despesas_fixas=2000.0,
            num_dependentes=1,
            tem_dividas=False
        )

        assert score > 0

    def test_score_dependentes_acima_de_3(self):
        """Deve usar peso de 3 dependentes para valores maiores que 3."""
        service = ScoreService()
        score_3_deps = service.calcular_score(
            renda_mensal=5000.0,
            tipo_emprego=TipoEmprego.FORMAL,
            despesas_fixas=2000.0,
            num_dependentes=3,
            tem_dividas=False
        )
        score_5_deps = service.calcular_score(
            renda_mensal=5000.0,
            tipo_emprego=TipoEmprego.FORMAL,
            despesas_fixas=2000.0,
            num_dependentes=5,
            tem_dividas=False
        )

        assert score_3_deps == score_5_deps
