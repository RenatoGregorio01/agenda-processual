# Alertas da Agenda Processual

Fonte canônica das expressões: [`deploy/prometheus/alerts.yml`](../prometheus/alerts.yml).

## Provisionar no Prometheus (recomendado)

1. Copie `alerts.yml` para o servidor Ubuntu, ex.:
   `compose/monitoring/prometheus/rules/agenda-alerts.yml`
2. Em `prometheus.yml`:

```yaml
rule_files:
  - /etc/prometheus/rules/*.yml
```

(ajuste o path ao volume do container)

3. Recarregue: `curl -X POST http://localhost:9090/-/reload`
4. Confira em **Status → Rules** e **Alerts**.

## Notificar (Grafana)

1. Grafana → **Alerting → Contact points** (e-mail, Discord, Telegram, etc.)
2. Opções:
   - **Grafana Alerting** lendo o Prometheus (datasources → Manage alerts), **ou**
   - **Alertmanager** no homelab recebendo as regras do Prometheus

Sem contact point / receiver, o alerta só aparece na UI.

## Regras (resumo)

| Alerta | Expr (resumo) | For | Severidade |
|--------|---------------|-----|------------|
| `AgendaApiDown` | `max(up{job="agenda-api"}) == 0` | 2m | critical |
| `AgendaApi5xxHigh` | `sum(rate(...status=~"5.."[5m])) > 0.1` | 5m | warning |
| `AgendaApiErrorRatioHigh` | taxa 5xx / total > 5% | 5m | warning |
| `AgendaApiLatencyHigh` | p95 > 2s | 5m | warning |
| `AgendaAlertasEmailErros` | `increase(agenda_alertas_erros_total[1h]) > 0` | 0m | warning |

## Criar manualmente no Grafana (alternativa)

**Alerting → New alert rule**, datasource Prometheus, cole a `expr` de cada regra em `alerts.yml`, use o mesmo `for` e anexe um contact point.
