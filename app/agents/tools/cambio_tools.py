"""Tools para o Agente de Cambio."""

from crewai.tools import tool

from app.services.cambio_service import CambioAPIIndisponivelError, CambioService

_cambio_service = CambioService()


@tool("consultar_cotacao")
def consultar_cotacao(moeda: str) -> str:
    """
    Consulta a cotacao atual de uma moeda em relacao ao Real (BRL).

    Args:
        moeda: Codigo da moeda (USD, EUR, GBP, etc) ou nome (dolar, euro, libra)
    """
    mapeamento = {
        "dolar": "USD",
        "dollar": "USD",
        "dolar americano": "USD",
        "euro": "EUR",
        "libra": "GBP",
        "pound": "GBP",
        "libra esterlina": "GBP",
        "peso argentino": "ARS",
        "peso": "ARS",
        "dolar canadense": "CAD",
        "dolar australiano": "AUD",
        "iene": "JPY",
        "yen": "JPY",
        "franco suico": "CHF",
        "franco": "CHF",
        "yuan": "CNY",
        "bitcoin": "BTC",
    }

    codigo = mapeamento.get(moeda.lower().strip(), moeda.upper().strip())

    try:
        cotacao = _cambio_service.obter_cotacao_sync(codigo, "BRL")
        return f"COTACAO|{codigo}|{cotacao.valor:.4f}|{cotacao.data_consulta.strftime('%H:%M')}"
    except CambioAPIIndisponivelError as e:
        return f"API_INDISPONIVEL|{str(e)}"


@tool("listar_moedas_disponiveis")
def listar_moedas_disponiveis() -> str:
    """
    Lista todas as moedas disponiveis para consulta de cotacao.
    """
    moedas = [
        "USD (Dolar Americano)",
        "EUR (Euro)",
        "GBP (Libra Esterlina)",
        "ARS (Peso Argentino)",
        "CAD (Dolar Canadense)",
        "AUD (Dolar Australiano)",
        "JPY (Iene Japones)",
        "CHF (Franco Suico)",
        "CNY (Yuan Chines)",
        "BTC (Bitcoin)",
    ]
    return "MOEDAS|" + "|".join(moedas)
