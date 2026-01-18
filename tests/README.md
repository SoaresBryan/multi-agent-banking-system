# Testes Unitários

Este diretório contém todos os testes unitários da aplicação.

## Estrutura

```
tests/
├── conftest.py                      # Fixtures compartilhadas
├── unit/
│   ├── services/
│   │   ├── test_cliente_service.py   # Testes do ClienteService
│   │   ├── test_solicitacao_service.py  # Testes do SolicitacaoService
│   │   └── test_score_service.py     # Testes do ScoreService
│   └── api/
│       └── test_admin_api.py         # Testes dos endpoints da API Admin
└── README.md
```

## Executar Testes

### Executar todos os testes

```bash
pytest
```

### Executar testes específicos

```bash
# Executar apenas testes de um arquivo
pytest tests/unit/services/test_cliente_service.py

# Executar apenas testes de uma classe
pytest tests/unit/services/test_cliente_service.py::TestClienteServiceBuscarPorCpf

# Executar apenas um teste específico
pytest tests/unit/services/test_cliente_service.py::TestClienteServiceBuscarPorCpf::test_buscar_cliente_existente
```

### Executar testes com output detalhado

```bash
pytest -v
```

#### ClienteService
- ✅ Buscar cliente por CPF (existente, inexistente, com formatação)
- ✅ Calcular limite baseado no score (todas as faixas)
- ✅ Adicionar cliente (válido, CPF inválido, duplicado, data inválida)
- ✅ Listar todos os clientes
- ✅ Atualizar score
- ✅ Atualizar limite

#### SolicitacaoService
- ✅ Listar todas as solicitações
- ✅ Listar solicitações por CPF

#### ScoreService
- ✅ Calcular score com diferentes parâmetros
- ✅ Validar limites mínimo e máximo
- ✅ Testar diferentes tipos de emprego
- ✅ Testar impacto de dívidas e dependentes

### Testes de API

#### Admin API
- ✅ POST /admin/clientes (sucesso, validações, erros)
- ✅ GET /admin/clientes
- ✅ GET /admin/solicitacoes
- ✅ GET /admin/solicitacoes/{cpf}

## Princípios dos Testes

1. **Isolamento**: Todos os testes são isolados e não dependem uns dos outros
2. **Mocks**: Usamos mocks para não fazer requisições reais a APIs, bancos de dados ou LLMs
3. **Arquivos Temporários**: Arquivos CSV são criados temporariamente e deletados após os testes
4. **Nomenclatura Clara**: Nomes descritivos que explicam o que está sendo testado
5. **Cobertura Completa**: Testamos casos de sucesso, falha e edge cases


