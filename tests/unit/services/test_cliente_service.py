"""Testes unitários para ClienteService."""

import pytest
from unittest.mock import patch, mock_open
from datetime import date

from app.services import ClienteService
from app.models import Cliente


class TestClienteServiceBuscarPorCpf:
    """Testes para o método buscar_por_cpf."""

    def test_buscar_cliente_existente(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve retornar cliente quando CPF existe."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        cliente = service.buscar_por_cpf("12345678901")

        assert cliente is not None
        assert cliente.cpf == "12345678901"
        assert cliente.nome == "João Silva"
        assert cliente.score == 750

    def test_buscar_cliente_com_formatacao(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve encontrar cliente mesmo com CPF formatado."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        cliente = service.buscar_por_cpf("123.456.789-01")

        assert cliente is not None
        assert cliente.cpf == "12345678901"

    def test_buscar_cliente_inexistente(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve retornar None quando CPF não existe."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        cliente = service.buscar_por_cpf("99999999999")

        assert cliente is None

    def test_buscar_cliente_arquivo_inexistente(self, temp_csv_score_limite):
        """Deve retornar None quando arquivo não existe."""
        service = ClienteService("/caminho/inexistente.csv", temp_csv_score_limite)
        cliente = service.buscar_por_cpf("12345678901")

        assert cliente is None


class TestClienteServiceCalcularLimitePorScore:
    """Testes para o método calcular_limite_por_score."""

    def test_score_baixo(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve retornar limite correto para score baixo (0-299)."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        limite = service.calcular_limite_por_score(250)

        assert limite == 500.00

    def test_score_medio_baixo(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve retornar limite correto para score médio-baixo (300-499)."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        limite = service.calcular_limite_por_score(400)

        assert limite == 2000.00

    def test_score_medio(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve retornar limite correto para score médio (500-699)."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        limite = service.calcular_limite_por_score(600)

        assert limite == 5000.00

    def test_score_alto(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve retornar limite correto para score alto (700-849)."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        limite = service.calcular_limite_por_score(750)

        assert limite == 15000.00

    def test_score_muito_alto(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve retornar limite correto para score muito alto (850-1000)."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        limite = service.calcular_limite_por_score(900)

        assert limite == 50000.00

    def test_score_limite_inferior(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve retornar limite correto no limite inferior da faixa."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        limite = service.calcular_limite_por_score(700)

        assert limite == 15000.00

    def test_score_limite_superior(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve retornar limite correto no limite superior da faixa."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        limite = service.calcular_limite_por_score(849)

        assert limite == 15000.00

    def test_arquivo_inexistente(self, temp_csv_clientes):
        """Deve retornar 0.0 quando arquivo não existe."""
        service = ClienteService(temp_csv_clientes, "/caminho/inexistente.csv")
        limite = service.calcular_limite_por_score(750)

        assert limite == 0.0


class TestClienteServiceAdicionarCliente:
    """Testes para o método adicionar_cliente."""

    def test_adicionar_cliente_valido(self, temp_csv_vazio, temp_csv_score_limite):
        """Deve adicionar cliente com dados válidos."""
        service = ClienteService(temp_csv_vazio, temp_csv_score_limite)
        sucesso = service.adicionar_cliente(
            cpf="11122233344",
            nome="Pedro Oliveira",
            data_nascimento="1995-06-20",
            score=800
        )

        assert sucesso is True
        cliente = service.buscar_por_cpf("11122233344")
        assert cliente is not None
        assert cliente.nome == "Pedro Oliveira"
        assert cliente.score == 800
        assert cliente.limite_atual == 15000.00

    def test_adicionar_cliente_cpf_formatado(self, temp_csv_vazio, temp_csv_score_limite):
        """Deve adicionar cliente mesmo com CPF formatado."""
        service = ClienteService(temp_csv_vazio, temp_csv_score_limite)
        sucesso = service.adicionar_cliente(
            cpf="111.222.333-44",
            nome="Pedro Oliveira",
            data_nascimento="1995-06-20",
            score=800
        )

        assert sucesso is True
        cliente = service.buscar_por_cpf("11122233344")
        assert cliente is not None

    def test_adicionar_cliente_data_formato_brasileiro(self, temp_csv_vazio, temp_csv_score_limite):
        """Deve adicionar cliente com data no formato brasileiro (DD/MM/AAAA)."""
        service = ClienteService(temp_csv_vazio, temp_csv_score_limite)
        sucesso = service.adicionar_cliente(
            cpf="11122233344",
            nome="Pedro Oliveira",
            data_nascimento="20/06/1995",
            score=800
        )

        assert sucesso is True
        cliente = service.buscar_por_cpf("11122233344")
        assert cliente is not None
        assert cliente.data_nascimento == date(1995, 6, 20)

    def test_adicionar_cliente_cpf_invalido_curto(self, temp_csv_vazio, temp_csv_score_limite):
        """Deve falhar ao adicionar cliente com CPF inválido (menos de 11 dígitos)."""
        service = ClienteService(temp_csv_vazio, temp_csv_score_limite)
        sucesso = service.adicionar_cliente(
            cpf="1234567890",
            nome="Pedro Oliveira",
            data_nascimento="1995-06-20",
            score=800
        )

        assert sucesso is False

    def test_adicionar_cliente_cpf_invalido_longo(self, temp_csv_vazio, temp_csv_score_limite):
        """Deve falhar ao adicionar cliente com CPF inválido (mais de 11 dígitos)."""
        service = ClienteService(temp_csv_vazio, temp_csv_score_limite)
        sucesso = service.adicionar_cliente(
            cpf="123456789012",
            nome="Pedro Oliveira",
            data_nascimento="1995-06-20",
            score=800
        )

        assert sucesso is False

    def test_adicionar_cliente_cpf_com_letras(self, temp_csv_vazio, temp_csv_score_limite):
        """Deve falhar ao adicionar cliente com CPF contendo letras."""
        service = ClienteService(temp_csv_vazio, temp_csv_score_limite)
        sucesso = service.adicionar_cliente(
            cpf="1234567890A",
            nome="Pedro Oliveira",
            data_nascimento="1995-06-20",
            score=800
        )

        assert sucesso is False

    def test_adicionar_cliente_duplicado(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve falhar ao adicionar cliente com CPF já existente."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        sucesso = service.adicionar_cliente(
            cpf="12345678901",
            nome="João Duplicado",
            data_nascimento="1990-01-01",
            score=750
        )

        assert sucesso is False

    def test_adicionar_cliente_data_invalida(self, temp_csv_vazio, temp_csv_score_limite):
        """Deve falhar ao adicionar cliente com data inválida."""
        service = ClienteService(temp_csv_vazio, temp_csv_score_limite)
        sucesso = service.adicionar_cliente(
            cpf="11122233344",
            nome="Pedro Oliveira",
            data_nascimento="data-invalida",
            score=800
        )

        assert sucesso is False


class TestClienteServiceListarTodos:
    """Testes para o método listar_todos."""

    def test_listar_clientes_existentes(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve retornar lista de todos os clientes."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        clientes = service.listar_todos()

        assert len(clientes) == 2
        assert clientes[0].cpf == "12345678901"
        assert clientes[1].cpf == "98765432100"

    def test_listar_clientes_vazio(self, temp_csv_vazio, temp_csv_score_limite):
        """Deve retornar lista vazia quando não há clientes."""
        service = ClienteService(temp_csv_vazio, temp_csv_score_limite)
        clientes = service.listar_todos()

        assert len(clientes) == 0

    def test_listar_clientes_arquivo_inexistente(self, temp_csv_score_limite):
        """Deve retornar lista vazia quando arquivo não existe."""
        service = ClienteService("/caminho/inexistente.csv", temp_csv_score_limite)
        clientes = service.listar_todos()

        assert len(clientes) == 0

    def test_listar_clientes_ignora_invalidos(self, temp_csv_score_limite, tmp_path):
        """Deve ignorar clientes com dados inválidos."""
        import csv

        temp_file = tmp_path / "clientes_invalidos.csv"
        with open(temp_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["cpf", "nome", "data_nascimento", "score", "limite_atual"])
            writer.writerow(["12345678901", "João Silva", "1990-01-01", "750", "15000.00"])
            writer.writerow(["123", "CPF Inválido", "1990-01-01", "750", "15000.00"])
            writer.writerow(["98765432100", "Maria Santos", "1985-05-15", "450", "2000.00"])

        service = ClienteService(str(temp_file), temp_csv_score_limite)
        clientes = service.listar_todos()

        assert len(clientes) == 2


class TestClienteServiceAtualizarScore:
    """Testes para o método atualizar_score."""

    def test_atualizar_score_sucesso(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve atualizar score do cliente com sucesso."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        sucesso = service.atualizar_score("12345678901", 850)

        assert sucesso is True
        cliente = service.buscar_por_cpf("12345678901")
        assert cliente.score == 850

    def test_atualizar_score_cliente_inexistente(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve falhar ao atualizar score de cliente inexistente."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        sucesso = service.atualizar_score("99999999999", 850)

        assert sucesso is False

    def test_atualizar_score_cpf_formatado(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve atualizar score mesmo com CPF formatado."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        sucesso = service.atualizar_score("123.456.789-01", 850)

        assert sucesso is True


class TestClienteServiceAtualizarLimite:
    """Testes para o método atualizar_limite."""

    def test_atualizar_limite_sucesso(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve atualizar limite do cliente com sucesso."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        sucesso = service.atualizar_limite("12345678901", 20000.00)

        assert sucesso is True
        cliente = service.buscar_por_cpf("12345678901")
        assert cliente.limite_atual == 20000.00

    def test_atualizar_limite_cliente_inexistente(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve falhar ao atualizar limite de cliente inexistente."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        sucesso = service.atualizar_limite("99999999999", 20000.00)

        assert sucesso is False

    def test_atualizar_limite_cpf_formatado(self, temp_csv_clientes, temp_csv_score_limite):
        """Deve atualizar limite mesmo com CPF formatado."""
        service = ClienteService(temp_csv_clientes, temp_csv_score_limite)
        sucesso = service.atualizar_limite("123.456.789-01", 20000.00)

        assert sucesso is True
