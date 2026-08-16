# Alertas recomendados no Grafana (Alerting → New alert rule)
#
# 1) API down
#    Expr:   up{job="agenda-api"} == 0
#    For:    2m
#    Summary: Agenda API indisponível no Prometheus
#
# 2) Erros de e-mail de alerta
#    Expr:   increase(agenda_alertas_erros_total[1h]) > 0
#    For:    0m
#    Summary: Falha ao enviar alerta de prazo
#
# 3) Taxa de 5xx alta
#    Expr:   sum(rate(http_requests_total{job="agenda-api",status=~"5.."}[5m])) > 0.1
#    For:    5m
#    Summary: Erros 5xx na Agenda API
