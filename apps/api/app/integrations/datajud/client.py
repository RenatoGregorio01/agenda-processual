from typing import Any

import httpx

from app.core.config import get_settings
from app.integrations.datajud.cnj import alias_do_cnj


class DatajudError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def datajud_url(alias: str) -> str:
    settings = get_settings()
    base = settings.datajud_base_url.rstrip("/")
    return f"{base}/api_publica_{alias}/_search"


async def consultar_processo(numero: str) -> tuple[str, str, dict[str, Any] | None]:
    """Consulta a Datajud. Retorna (digitos, alias, source ou None se sem hits)."""
    settings = get_settings()
    if not settings.datajud_api_key.strip():
        raise DatajudError("DATAJUD_API_KEY não configurada")

    digitos, alias = alias_do_cnj(numero)
    payload = {
        "query": {"match": {"numeroProcesso": digitos}},
        "size": 1,
    }
    headers = {
        "Authorization": f"APIKey {settings.datajud_api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(datajud_url(alias), headers=headers, json=payload)

    if response.status_code == 429:
        raise DatajudError("Limite de consultas da Datajud atingido", status_code=429)
    if response.status_code >= 400:
        raise DatajudError(
            f"Datajud retornou HTTP {response.status_code}",
            status_code=response.status_code,
        )

    body = response.json()
    hits = body.get("hits", {}).get("hits", [])
    if not hits:
        return digitos, alias, None
    source = hits[0].get("_source")
    if not isinstance(source, dict):
        return digitos, alias, None
    return digitos, alias, source
