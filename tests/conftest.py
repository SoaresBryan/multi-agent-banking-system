"""Fixtures compartilhadas para testes."""

import tempfile
from datetime import date
from pathlib import Path

import pytest

from app.models import Cliente
from app.models.solicitacao import SolicitacaoCredito, StatusSolicitacao
from datetime import datetime


@pytest.fixture
def cliente_valido():
    """Cliente válido para testes."""
    return Cliente(
        cpf="12345678901",
        nome="João Silva",
        data_nascimento=date(1990, 1, 1),
        score=750,
        limite_atual=15000.00,
    )


@pytest.fixture
def cliente_score_baixo():
    """Cliente com score baixo para testes."""
    return Cliente(
        cpf="98765432100",
        nome="Maria Santos",
        data_nascimento=date(1985, 5, 15),
        score=450,
        limite_atual=2000.00,
    )


@pytest.fixture
def solicitacao_aprovada():
    """Solicitação aprovada para testes."""
    return SolicitacaoCredito(
        cpf_cliente="12345678901",
        data_hora_solicitacao=datetime(2026, 1, 18, 10, 0, 0),
        limite_atual=5000.0,
        novo_limite_solicitado=10000.0,
        status_pedido=StatusSolicitacao.APROVADO,
    )


@pytest.fixture
def solicitacao_rejeitada():
    """Solicitação rejeitada para testes."""
    return SolicitacaoCredito(
        cpf_cliente="12345678901",
        data_hora_solicitacao=datetime(2026, 1, 18, 11, 0, 0),
        limite_atual=5000.0,
        novo_limite_solicitado=50000.0,
        status_pedido=StatusSolicitacao.REJEITADO,
    )


@pytest.fixture
def temp_csv_clientes():
    """Cria um arquivo CSV temporário para testes de clientes."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", newline="", encoding="utf-8") as f:
        f.write("cpf,nome,data_nascimento,score,limite_atual\n")
        f.write("12345678901,João Silva,1990-01-01,750,15000.00\n")
        f.write("98765432100,Maria Santos,1985-05-15,450,2000.00\n")
        temp_path = f.name

    yield temp_path

    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def temp_csv_score_limite():
    """Cria um arquivo CSV temporário para testes de score-limite."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", newline="", encoding="utf-8") as f:
        f.write("score_minimo,score_maximo,limite_maximo\n")
        f.write("0,299,500.00\n")
        f.write("300,499,2000.00\n")
        f.write("500,699,5000.00\n")
        f.write("700,849,15000.00\n")
        f.write("850,1000,50000.00\n")
        temp_path = f.name

    yield temp_path

    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def temp_csv_solicitacoes():
    """Cria um arquivo CSV temporário para testes de solicitações."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", newline="", encoding="utf-8") as f:
        f.write("cpf_cliente,data_hora_solicitacao,limite_atual,novo_limite_solicitado,status_pedido\n")
        f.write("12345678901,2026-01-18T10:00:00,5000.0,10000.0,aprovado\n")
        f.write("12345678901,2026-01-18T11:00:00,5000.0,50000.0,rejeitado\n")
        f.write("98765432100,2026-01-18T12:00:00,2000.0,5000.0,pendente\n")
        temp_path = f.name

    yield temp_path

    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def temp_csv_vazio():
    """Cria um arquivo CSV temporário vazio para testes."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", newline="", encoding="utf-8") as f:
        f.write("cpf,nome,data_nascimento,score,limite_atual\n")
        temp_path = f.name

    yield temp_path

    Path(temp_path).unlink(missing_ok=True)
