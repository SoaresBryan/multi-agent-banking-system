from enum import Enum


class TipoEmprego(str, Enum):
    """Tipos de emprego conforme desafio."""
    FORMAL = "formal"
    AUTONOMO = "autonomo"
    DESEMPREGADO = "desempregado"
    CLT = "formal"
    PJ = "autonomo"


class ScoreService:
    PESO_RENDA = 30
    PESO_EMPREGO = {
        TipoEmprego.FORMAL: 300,
        TipoEmprego.AUTONOMO: 200,
        TipoEmprego.DESEMPREGADO: 0,
    }
    PESO_DEPENDENTES = {
        0: 100,
        1: 80,
        2: 60,
        3: 30,
    }
    PESO_DIVIDAS = {
        True: -100,
        False: 100,
    }

    def calcular_score(
        self,
        renda_mensal: float,
        tipo_emprego: TipoEmprego,
        despesas_fixas: float,
        num_dependentes: int,
        tem_dividas: bool,
    ) -> int:
        if despesas_fixas > renda_mensal:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"[SCORE] Dados suspeitos: despesas (R$ {despesas_fixas:.2f}) > renda (R$ {renda_mensal:.2f}). "
                "Isso resulta em score muito baixo."
            )

        componente_renda = (renda_mensal / (despesas_fixas + 1)) * self.PESO_RENDA

        componente_emprego = self.PESO_EMPREGO.get(tipo_emprego, 0)

        if num_dependentes >= 3:
            componente_dependentes = self.PESO_DEPENDENTES[3]
        else:
            componente_dependentes = self.PESO_DEPENDENTES.get(num_dependentes, 30)

        componente_dividas = self.PESO_DIVIDAS.get(tem_dividas, 0)

        score_calculado = (
            componente_renda
            + componente_emprego
            + componente_dependentes
            + componente_dividas
        )

        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"[SCORE] Calculo detalhado: "
            f"Renda={renda_mensal:.2f}, Despesas={despesas_fixas:.2f}, "
            f"Emprego={tipo_emprego.value}, Dependentes={num_dependentes}, Dividas={tem_dividas} | "
            f"Componentes: renda={componente_renda:.2f}, emprego={componente_emprego}, "
            f"dependentes={componente_dependentes}, dividas={componente_dividas} | "
            f"Score final={int(score_calculado)}"
        )

        return max(0, min(1000, int(score_calculado)))
