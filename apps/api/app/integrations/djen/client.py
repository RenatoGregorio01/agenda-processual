from datetime import date
from typing import Any

import httpx

from app.core.config import get_settings

PAGE_SIZE = 50
MAX_PAGES = 20
MAX_RETRIES_EMPTY = 2


class DjenError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def djen_comunicacao_url() -> str:
    settings = get_settings()
    return f"{settings.djen_base_url.rstrip('/')}/comunicacao"


async def consultar_comunicacoes(
    *,
    data_inicio: date,
    data_fim: date,
    numero_processo_digitos: str | None = None,
    nome_advogado: str | None = None,
    numero_oab: str | None = None,
    uf_oab: str | None = None,
) -> list[dict[str, Any]]:
    """Consulta publicações do DJEN por CNJ, Nome do Advogado ou OAB numa janela de datas."""
    settings = get_settings()
    if not settings.djen_enabled:
        raise DjenError("Consulta ao DJEN desabilitada")

    if not any([numero_processo_digitos, nome_advogado, numero_oab]):
        raise DjenError(
            "Informe ao menos o processo, nome do advogado ou OAB para consultar o DJEN"
        )

    items: list[dict[str, Any]] = []
    count: int | None = None
    empty_retries = 0
    url = djen_comunicacao_url()

    async with httpx.AsyncClient(timeout=20.0) as client:
        pagina = 1
        while pagina <= MAX_PAGES:
            params: dict[str, Any] = {
                "dataDisponibilizacaoInicio": data_inicio.isoformat(),
                "dataDisponibilizacaoFim": data_fim.isoformat(),
                "pagina": pagina,
                "itensPorPagina": PAGE_SIZE,
            }
            if numero_processo_digitos:
                params["numeroProcesso"] = numero_processo_digitos
            if nome_advogado:
                params["nomeAdvogado"] = nome_advogado
            if numero_oab:
                params["numeroOab"] = numero_oab
            if uf_oab:
                params["ufOab"] = uf_oab

            response = await client.get(
                url,
                params=params,
                headers={"Accept": "application/json"},
            )
            if response.status_code == 429:
                raise DjenError("Limite de consultas do DJEN atingido", status_code=429)
            if response.status_code == 403:
                raise DjenError(
                    "DJEN recusou a consulta (IP fora do Brasil ou bloqueio temporário)",
                    status_code=403,
                )
            if response.status_code >= 400:
                raise DjenError(
                    f"DJEN retornou HTTP {response.status_code}",
                    status_code=response.status_code,
                )

            body = response.json()
            if not isinstance(body, dict):
                raise DjenError("Resposta inválida do DJEN")
            if count is None:
                count = int(body.get("count") or 0)
            page_items = body.get("items") or []
            if not isinstance(page_items, list):
                page_items = []

            if not page_items:
                if count is not None and len(items) >= count:
                    break
                if empty_retries >= MAX_RETRIES_EMPTY:
                    break
                empty_retries += 1
                continue

            empty_retries = 0
            items.extend(item for item in page_items if isinstance(item, dict))
            if count is not None and len(items) >= count:
                break
            pagina += 1

    return items
