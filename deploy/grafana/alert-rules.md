# Alertas recomendados no Grafana (Alerting → New alert rule)
#
# Filtre por `env` (homelab | develop) ou `job` (agenda-api | agenda-api-develop).
# Crie um par de regras (prod + develop) ou use `env=~"homelab|develop"`.

## 1) API down — produção

- Expr: `up{job="agenda-api"} == 0`
- For: 2m
- Summary: Agenda API (prod) indisponível

## 2) API down — develop

- Expr: `up{job="agenda-api-develop"} == 0`
- For: 2m
- Summary: Agenda API (develop) indisponível
- Nota: útil quando a home mostra "API: offline" em develop.agendaprocessual.com.br

## 3) Erros de e-mail de alerta

- Expr: `increase(agenda_alertas_erros_total{env="homelab"}[1h]) > 0`
- Espelho develop: `increase(agenda_alertas_erros_total{env="develop"}[1h]) > 0`
- For: 0m
- Summary: Falha ao enviar alerta de prazo

## 4) Taxa de 5xx alta — produção

- Expr: `sum(rate(http_requests_total{job="agenda-api",status=~"5.."}[5m])) > 0.1`
- For: 5m
- Summary: Erros 5xx na Agenda API (prod)

## 5) Taxa de 5xx alta — develop

- Expr: `sum(rate(http_requests_total{job="agenda-api-develop",status=~"5.."}[5m])) > 0.1`
- For: 5m
- Summary: Erros 5xx na Agenda API (develop)

## 6) DJEN sync com falha — develop

- Expr: `increase(agenda_djen_sync_erros_total{env="develop"}[1h]) > 0`
- For: 15m
- Summary: Falhas de sync DJEN em homologação
