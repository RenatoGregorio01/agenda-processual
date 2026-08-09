from datetime import UTC, datetime


def utc_now() -> datetime:
    """UTC atual sem tzinfo — compatível com as colunas naive do banco."""
    return datetime.now(UTC).replace(tzinfo=None)
