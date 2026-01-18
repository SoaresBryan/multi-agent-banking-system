"""Testes unitários para SolicitacaoService."""

import pytest
from datetime import datetime

from app.services import SolicitacaoService
from app.models.solicitacao import StatusSolicitacao


class TestSolicitacaoServiceListarTodas:
    """Testes para o método listar_todas."""

    def test_listar_todas_solicitacoes(self, temp_csv_solicitacoes):
        """Deve retornar todas as solicitações do arquivo."""
        service = SolicitacaoService(temp_csv_solicitacoes)
        solicitacoes = service.listar_todas()

        assert len(solicitacoes) == 3
        assert solicitacoes[0].cpf_cliente == "12345678901"
        assert solicitacoes[0].status_pedido == StatusSolicitacao.APROVADO
        assert solicitacoes[1].status_pedido == StatusSolicitacao.REJEITADO
        assert solicitacoes[2].status_pedido == StatusSolicitacao.PENDENTE

    def test_listar_todas_arquivo_inexistente(self):
        """Deve retornar lista vazia quando arquivo não existe."""
        service = SolicitacaoService("/caminho/inexistente.csv")
        solicitacoes = service.listar_todas()

        assert len(solicitacoes) == 0
        assert isinstance(solicitacoes, list)

    def test_listar_todas_verifica_dados(self, temp_csv_solicitacoes):
        """Deve retornar solicitações com dados corretos."""
        service = SolicitacaoService(temp_csv_solicitacoes)
        solicitacoes = service.listar_todas()

        primeira = solicitacoes[0]
        assert primeira.cpf_cliente == "12345678901"
        assert primeira.limite_atual == 5000.0
        assert primeira.novo_limite_solicitado == 10000.0
        assert isinstance(primeira.data_hora_solicitacao, datetime)


class TestSolicitacaoServiceListarPorCpf:
    """Testes para o método listar_por_cpf."""

    def test_listar_por_cpf_existente(self, temp_csv_solicitacoes):
        """Deve retornar solicitações do CPF especificado."""
        service = SolicitacaoService(temp_csv_solicitacoes)
        solicitacoes = service.listar_por_cpf("12345678901")

        assert len(solicitacoes) == 2
        assert all(s.cpf_cliente == "12345678901" for s in solicitacoes)

    def test_listar_por_cpf_unico(self, temp_csv_solicitacoes):
        """Deve retornar solicitações de CPF com apenas uma solicitação."""
        service = SolicitacaoService(temp_csv_solicitacoes)
        solicitacoes = service.listar_por_cpf("98765432100")

        assert len(solicitacoes) == 1
        assert solicitacoes[0].cpf_cliente == "98765432100"

    def test_listar_por_cpf_inexistente(self, temp_csv_solicitacoes):
        """Deve retornar lista vazia para CPF sem solicitações."""
        service = SolicitacaoService(temp_csv_solicitacoes)
        solicitacoes = service.listar_por_cpf("99999999999")

        assert len(solicitacoes) == 0
        assert isinstance(solicitacoes, list)

    def test_listar_por_cpf_formatado(self, temp_csv_solicitacoes):
        """Deve encontrar solicitações mesmo com CPF formatado."""
        service = SolicitacaoService(temp_csv_solicitacoes)
        solicitacoes = service.listar_por_cpf("123.456.789-01")

        assert len(solicitacoes) == 2

    def test_listar_por_cpf_verifica_ordem(self, temp_csv_solicitacoes):
        """Deve manter ordem das solicitações conforme arquivo."""
        service = SolicitacaoService(temp_csv_solicitacoes)
        solicitacoes = service.listar_por_cpf("12345678901")

        assert solicitacoes[0].status_pedido == StatusSolicitacao.APROVADO
        assert solicitacoes[1].status_pedido == StatusSolicitacao.REJEITADO
