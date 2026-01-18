"""Testes unitários para as rotas da API Admin."""

import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models import Cliente
from app.models.solicitacao import SolicitacaoCredito, StatusSolicitacao
from datetime import datetime

client = TestClient(app)


class TestAdicionarClienteAPI:
    """Testes para POST /admin/clientes."""

    @patch("app.api.admin.ClienteService")
    def test_adicionar_cliente_sucesso(self, mock_service_class):
        """Deve adicionar cliente com sucesso."""
        mock_service = MagicMock()
        mock_service.buscar_por_cpf.return_value = None
        mock_service.adicionar_cliente.return_value = True
        mock_service.buscar_por_cpf.side_effect = [
            None,
            Cliente(
                cpf="12345678901",
                nome="João Silva",
                data_nascimento=date(1990, 1, 1),
                score=750,
                limite_atual=15000.00,
            ),
        ]
        mock_service_class.return_value = mock_service

        response = client.post(
            "/admin/clientes",
            json={
                "cpf": "12345678901",
                "nome": "João Silva",
                "data_nascimento": "1990-01-01",
                "score": 750,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Cliente adicionado com sucesso"
        assert data["cliente"]["cpf"] == "12345678901"

    @patch("app.api.admin.ClienteService")
    def test_adicionar_cliente_cpf_invalido_curto(self, mock_service_class):
        """Deve retornar erro para CPF com menos de 11 dígitos."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        response = client.post(
            "/admin/clientes",
            json={
                "cpf": "1234567890",
                "nome": "João Silva",
                "data_nascimento": "1990-01-01",
                "score": 750,
            },
        )

        assert response.status_code == 400
        assert "CPF inválido" in response.json()["detail"]

    @patch("app.api.admin.ClienteService")
    def test_adicionar_cliente_cpf_invalido_longo(self, mock_service_class):
        """Deve retornar erro para CPF com mais de 11 dígitos."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        response = client.post(
            "/admin/clientes",
            json={
                "cpf": "123456789012",
                "nome": "João Silva",
                "data_nascimento": "1990-01-01",
                "score": 750,
            },
        )

        assert response.status_code == 400
        assert "CPF inválido" in response.json()["detail"]

    @patch("app.api.admin.ClienteService")
    def test_adicionar_cliente_cpf_com_letras(self, mock_service_class):
        """Deve retornar erro para CPF com letras."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        response = client.post(
            "/admin/clientes",
            json={
                "cpf": "1234567890A",
                "nome": "João Silva",
                "data_nascimento": "1990-01-01",
                "score": 750,
            },
        )

        assert response.status_code == 400
        assert "CPF inválido" in response.json()["detail"]

    @patch("app.api.admin.ClienteService")
    def test_adicionar_cliente_duplicado(self, mock_service_class):
        """Deve retornar erro ao tentar adicionar cliente duplicado."""
        mock_service = MagicMock()
        mock_service.buscar_por_cpf.return_value = Cliente(
            cpf="12345678901",
            nome="João Silva",
            data_nascimento=date(1990, 1, 1),
            score=750,
            limite_atual=15000.00,
        )
        mock_service_class.return_value = mock_service

        response = client.post(
            "/admin/clientes",
            json={
                "cpf": "12345678901",
                "nome": "João Silva",
                "data_nascimento": "1990-01-01",
                "score": 750,
            },
        )

        assert response.status_code == 400
        assert "já existe" in response.json()["detail"]

    @patch("app.api.admin.ClienteService")
    def test_adicionar_cliente_erro_ao_adicionar(self, mock_service_class):
        """Deve retornar erro quando falha ao adicionar."""
        mock_service = MagicMock()
        mock_service.buscar_por_cpf.return_value = None
        mock_service.adicionar_cliente.return_value = False
        mock_service_class.return_value = mock_service

        response = client.post(
            "/admin/clientes",
            json={
                "cpf": "12345678901",
                "nome": "João Silva",
                "data_nascimento": "1990-01-01",
                "score": 750,
            },
        )

        assert response.status_code == 400
        assert "Erro ao adicionar cliente" in response.json()["detail"]


class TestListarClientesAPI:
    """Testes para GET /admin/clientes."""

    @patch("app.api.admin.ClienteService")
    def test_listar_clientes_sucesso(self, mock_service_class):
        """Deve listar todos os clientes."""
        mock_service = MagicMock()
        mock_service.listar_todos.return_value = [
            Cliente(
                cpf="12345678901",
                nome="João Silva",
                data_nascimento=date(1990, 1, 1),
                score=750,
                limite_atual=15000.00,
            ),
            Cliente(
                cpf="98765432100",
                nome="Maria Santos",
                data_nascimento=date(1985, 5, 15),
                score=450,
                limite_atual=2000.00,
            ),
        ]
        mock_service_class.return_value = mock_service

        response = client.get("/admin/clientes")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["cpf"] == "12345678901"
        assert data[1]["cpf"] == "98765432100"

    @patch("app.api.admin.ClienteService")
    def test_listar_clientes_vazio(self, mock_service_class):
        """Deve retornar lista vazia quando não há clientes."""
        mock_service = MagicMock()
        mock_service.listar_todos.return_value = []
        mock_service_class.return_value = mock_service

        response = client.get("/admin/clientes")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


class TestListarSolicitacoesAPI:
    """Testes para GET /admin/solicitacoes."""

    @patch("app.api.admin.SolicitacaoService")
    def test_listar_solicitacoes_sucesso(self, mock_service_class):
        """Deve listar todas as solicitações."""
        mock_service = MagicMock()
        mock_service.listar_todas.return_value = [
            SolicitacaoCredito(
                cpf_cliente="12345678901",
                data_hora_solicitacao=datetime(2026, 1, 18, 10, 0, 0),
                limite_atual=5000.0,
                novo_limite_solicitado=10000.0,
                status_pedido=StatusSolicitacao.APROVADO,
            ),
            SolicitacaoCredito(
                cpf_cliente="98765432100",
                data_hora_solicitacao=datetime(2026, 1, 18, 11, 0, 0),
                limite_atual=2000.0,
                novo_limite_solicitado=5000.0,
                status_pedido=StatusSolicitacao.PENDENTE,
            ),
        ]
        mock_service_class.return_value = mock_service

        response = client.get("/admin/solicitacoes")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["cpf_cliente"] == "12345678901"
        assert data[0]["status_pedido"] == "aprovado"

    @patch("app.api.admin.SolicitacaoService")
    def test_listar_solicitacoes_vazio(self, mock_service_class):
        """Deve retornar lista vazia quando não há solicitações."""
        mock_service = MagicMock()
        mock_service.listar_todas.return_value = []
        mock_service_class.return_value = mock_service

        response = client.get("/admin/solicitacoes")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


class TestListarSolicitacoesPorCpfAPI:
    """Testes para GET /admin/solicitacoes/{cpf}."""

    @patch("app.api.admin.SolicitacaoService")
    def test_listar_solicitacoes_por_cpf_sucesso(self, mock_service_class):
        """Deve listar solicitações de um CPF específico."""
        mock_service = MagicMock()
        mock_service.listar_por_cpf.return_value = [
            SolicitacaoCredito(
                cpf_cliente="12345678901",
                data_hora_solicitacao=datetime(2026, 1, 18, 10, 0, 0),
                limite_atual=5000.0,
                novo_limite_solicitado=10000.0,
                status_pedido=StatusSolicitacao.APROVADO,
            ),
        ]
        mock_service_class.return_value = mock_service

        response = client.get("/admin/solicitacoes/12345678901")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["cpf_cliente"] == "12345678901"

    @patch("app.api.admin.SolicitacaoService")
    def test_listar_solicitacoes_por_cpf_inexistente(self, mock_service_class):
        """Deve retornar erro 404 quando CPF não tem solicitações."""
        mock_service = MagicMock()
        mock_service.listar_por_cpf.return_value = []
        mock_service_class.return_value = mock_service

        response = client.get("/admin/solicitacoes/99999999999")

        assert response.status_code == 404
        assert "Nenhuma solicitação encontrada" in response.json()["detail"]
