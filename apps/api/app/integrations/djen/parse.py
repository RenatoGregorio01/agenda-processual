from datetime import date, datetime
from typing import Any

from app.integrations.datajud.cnj import mascarar_cnj, so_digitos


def parse_data(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    text = str(value).strip()[:10]
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def normalize_item(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Normaliza um item da API Comunica. Descarta sem id ou sem número."""
    djen_id = raw.get("id")
    if djen_id is None:
        return None
    numero = so_digitos(
        str(raw.get("numero_processo") or raw.get("numeroprocessocommascara") or "")
    )
    if len(numero) != 20:
        return None

    mascarado = str(raw.get("numeroprocessocommascara") or "").strip()
    if not mascarado:
        mascarado = mascarar_cnj(numero) or numero

    tipo = str(raw.get("tipoComunicacao") or raw.get("tipo_comunicacao") or "Publicação").strip()
    if not tipo:
        tipo = "Publicação"

    motivo = raw.get("motivo_cancelamento") or raw.get("motivoCancelamento")
    motivo_text = str(motivo).strip()[:500] if motivo else None

    hash_value = raw.get("hash")
    return {
        "djen_id": str(djen_id),
        "hash": str(hash_value)[:80] if hash_value else None,
        "numero_processo": mascarado[:64],
        "numero_processo_digitos": numero,
        "tribunal": (
            str(raw.get("siglaTribunal") or raw.get("sigla_tribunal") or "").strip() or None
        ),
        "tipo_comunicacao": tipo[:80],
        "tipo_documento": (
            str(raw.get("tipoDocumento") or raw.get("tipo_documento") or "").strip()[:80] or None
        ),
        "orgao": (str(raw.get("nomeOrgao") or raw.get("nome_orgao") or "").strip()[:255] or None),
        "data_disponibilizacao": parse_data(
            raw.get("data_disponibilizacao") or raw.get("dataDisponibilizacao")
        ),
        "motivo_cancelamento": motivo_text,
    }
