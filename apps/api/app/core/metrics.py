from prometheus_client import Counter, Gauge

ALERTAS_CANDIDATOS = Gauge(
    "agenda_alertas_candidatos",
    "Quantidade de candidatos a alerta no último processamento",
)
ALERTAS_ENVIADOS = Counter(
    "agenda_alertas_enviados_total",
    "Total de e-mails de alerta enviados com sucesso",
)
ALERTAS_ERROS = Counter(
    "agenda_alertas_erros_total",
    "Total de falhas ao enviar e-mail de alerta",
)
ALERTAS_IGNORADOS = Counter(
    "agenda_alertas_ignorados_total",
    "Total de alertas ignorados (já enviados)",
)


def record_alertas_result(*, candidatos: int, enviados: int, erros: int, ignorados: int) -> None:
    ALERTAS_CANDIDATOS.set(candidatos)
    if enviados:
        ALERTAS_ENVIADOS.inc(enviados)
    if erros:
        ALERTAS_ERROS.inc(erros)
    if ignorados:
        ALERTAS_IGNORADOS.inc(ignorados)
