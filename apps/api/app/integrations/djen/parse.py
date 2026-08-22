import re
from datetime import date, datetime
from typing import Any

from app.integrations.datajud.cnj import mascarar_cnj, so_digitos

EXTENSO_MAP = {
    "um": 1,
    "dois": 2,
    "tres": 3,
    "três": 3,
    "quatro": 4,
    "cinco": 5,
    "seis": 6,
    "sete": 7,
    "oito": 8,
    "nove": 9,
    "dez": 10,
    "quinze": 15,
    "vinte": 20,
    "trinta": 30,
}


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


def extrair_dias_prazo(texto: str | None) -> int | None:
    """Extrai quantidade de dias de prazo mencionado na intimação / despacho judicial."""
    if not texto:
        return None
    t = texto.lower()

    # 1. Padrão numérico direto: 'prazo de 15 dias', 'prazo de 15 (quinze) dias', 'em 5 dias'
    m = re.search(
        r"prazo\s+(?:legal\s+)?(?:de\s+)?(\d+)\s*(?:\([a-zçãõáéíóú\s]+\)\s*)?dias?",
        t,
    )
    if m:
        val = int(m.group(1))
        if 1 <= val <= 180:
            return val

    m2 = re.search(
        r"(?:manifestar|manifeste-se|apresentar|apresente|ciência|responder|resposta|impugnar|recorrer|cumprir)\w*\s+(?:no\s+prazo\s+de\s+|em\s+)?(\d+)\s*(?:\([a-zçãõáéíóú\s]+\)\s*)?dias?",
        t,
    )
    if m2:
        val = int(m2.group(1))
        if 1 <= val <= 180:
            return val

    m3 = re.search(r"(?:no\s+prazo\s+de|em)\s+(\d+)\s*dias?", t)
    if m3:
        val = int(m3.group(1))
        if 1 <= val <= 180:
            return val

    # 2. Padrão por extenso: 'prazo de quinze dias', 'em cinco dias'
    for k, v in EXTENSO_MAP.items():
        if re.search(rf"prazo\s+(?:de\s+)?{k}\s+dias?", t) or re.search(rf"em\s+{k}\s+dias?", t):
            return v

    return None


def _format_destinatarios(raw: dict[str, Any]) -> str | None:
    dest_adv = raw.get("destinatarioadvogados") or []
    nomes_adv: list[str] = []
    if isinstance(dest_adv, list):
        for item in dest_adv:
            if isinstance(item, dict):
                adv = item.get("advogado")
                if isinstance(adv, dict):
                    nome = str(adv.get("nome") or "").strip()
                    num_oab = str(adv.get("numero_oab") or "").strip()
                    uf_oab = str(adv.get("uf_oab") or "").strip()
                    if nome:
                        oab_str = f" (OAB/{uf_oab} {num_oab})" if num_oab and uf_oab else ""
                        nomes_adv.append(f"{nome}{oab_str}")

    if nomes_adv:
        return ", ".join(dict.fromkeys(nomes_adv))[:1000]

    dest = raw.get("destinatarios") or []
    nomes_partes: list[str] = []
    if isinstance(dest, list):
        for item in dest:
            if isinstance(item, dict):
                nome = str(item.get("nome") or "").strip()
                if nome:
                    nomes_partes.append(nome)

    if nomes_partes:
        return ", ".join(dict.fromkeys(nomes_partes))[:1000]

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

    texto = str(raw.get("texto") or raw.get("teor") or "").strip() or None
    link = str(raw.get("link") or "").strip()[:500] or None
    nome_classe = (
        str(raw.get("nomeClasse") or raw.get("nome_classe") or "").strip()[:255] or None
    )
    destinatarios = _format_destinatarios(raw)
    dias = extrair_dias_prazo(texto)

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
        "nome_classe": nome_classe,
        "orgao": (str(raw.get("nomeOrgao") or raw.get("nome_orgao") or "").strip()[:255] or None),
        "texto": texto,
        "link": link,
        "destinatarios": destinatarios,
        "dias_identificados": dias,
        "data_disponibilizacao": parse_data(
            raw.get("data_disponibilizacao") or raw.get("dataDisponibilizacao")
        ),
        "motivo_cancelamento": motivo_text,
    }
