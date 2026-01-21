import logging
import re
from datetime import datetime

import httpx

from app.config import settings
from app.models import Cotacao

logger = logging.getLogger(__name__)


class CambioAPIIndisponivelError(Exception):
    """Exceção lançada quando a API de câmbio está indisponível."""

    pass


class CambioService:
    BASE_URL = "https://serpapi.com/search.json"
    ERRO_API_INDISPONIVEL = (
        "A API de cotação de câmbio está indisponível no momento. "
        "Não é possível fornecer o valor da cotação agora. "
        "Por favor, peça ao cliente para tentar novamente em alguns minutos."
    )

    def _tratar_erro_api(self, erro: Exception, tipo_erro: str) -> None:
        logger.error(f"{tipo_erro} ao consultar API de câmbio: {erro}")
        raise CambioAPIIndisponivelError(self.ERRO_API_INDISPONIVEL)

    def _extrair_valor(self, texto: str) -> float | None:
        texto = texto.replace(",", ".")
        match = re.search(r"(\d+\.?\d*)", texto)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None

    def _parse_serpapi_response(self, data: dict) -> float | None:
        valor = None

        if "answer_box" in data:
            answer = data["answer_box"]
            if "result" in answer:
                valor = self._extrair_valor(answer["result"])
            elif "answer" in answer:
                valor = self._extrair_valor(answer["answer"])

        if valor is None and "knowledge_graph" in data:
            kg = data["knowledge_graph"]
            if "description" in kg:
                valor = self._extrair_valor(kg["description"])

        if valor is None and "organic_results" in data and len(data["organic_results"]) > 0:
            snippet = data["organic_results"][0].get("snippet", "")
            valor = self._extrair_valor(snippet)

        return valor

    def obter_cotacao_sync(
        self, moeda_origem: str = "USD", moeda_destino: str = "BRL"
    ) -> Cotacao:
        query = f"1 {moeda_origem} to {moeda_destino}"

        params = {
            "q": query,
            "api_key": settings.serpapi_key,
            "engine": "google",
            "hl": "pt-br",
            "gl": "br",
        }

        try:
            with httpx.Client() as client:
                response = client.get(self.BASE_URL, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                valor = self._parse_serpapi_response(data)

                if valor:
                    return Cotacao(
                        moeda_origem=moeda_origem.upper(),
                        moeda_destino=moeda_destino.upper(),
                        valor=valor,
                        data_consulta=datetime.now(),
                    )

        except httpx.TimeoutException as e:
            self._tratar_erro_api(e, "Timeout")
        except httpx.HTTPError as e:
            self._tratar_erro_api(e, "Erro HTTP")
        except (KeyError, ValueError) as e:
            self._tratar_erro_api(e, "Erro ao processar dados")

        logger.warning("API de câmbio não retornou valor válido")
        raise CambioAPIIndisponivelError(self.ERRO_API_INDISPONIVEL)
