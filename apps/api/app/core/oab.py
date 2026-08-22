import re
import unicodedata

from fastapi import HTTPException, status

_UF_RE = re.compile(r"^[A-Z]{2}$")
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def normalize_oab_numero(value: str | None) -> str | None:
    if value is None:
        return None
    digits = re.sub(r"\D", "", value.strip())
    return digits[:20] or None


def normalize_oab_uf(value: str | None) -> str | None:
    if value is None:
        return None
    uf = value.strip().upper()
    return uf[:2] if uf else None


def validate_advogado_oab(
    *,
    eh_advogado: bool,
    oab_numero: str | None,
    oab_uf: str | None,
) -> tuple[str | None, str | None]:
    numero = normalize_oab_numero(oab_numero)
    uf = normalize_oab_uf(oab_uf)
    if not eh_advogado:
        return None, None
    if not numero or not uf:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Advogado precisa de número da OAB e UF",
        )
    if not _UF_RE.match(uf):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UF da OAB inválida",
        )
    return numero, uf


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = _SLUG_RE.sub("-", ascii_text).strip("-")
    return slug[:80] or "escritorio"
