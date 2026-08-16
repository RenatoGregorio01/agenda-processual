# Deploy no homelab (público + Grafana + SMTP)

Ordem sugerida:

1. Secrets e URLs
2. SMTP real
3. Cloudflare Tunnel
4. Prometheus scrape + dashboard Grafana
5. Teste de alerta ponta a ponta

## 1. Secrets

```bash
cp docker/homelab.env.example docker/homelab.env
cp docker/smtp.env.example docker/smtp.env
# edite ambos (JWT_SECRET, TUNNEL_TOKEN, SMTP_*, URLs do domínio)
```

Gere um `JWT_SECRET` forte (ex.: `openssl rand -hex 32`).

## 2. SMTP

Siga [smtp-e-acesso.md](smtp-e-acesso.md) (Gmail senha de app ou Resend).
O job diário (`ALERTAS_CRON_HOUR`, default 8h America/Sao_Paulo) e o
`POST /api/v1/alertas/processar` (admin) usam o mesmo SMTP.

## 3. Cloudflare Tunnel — configurar domínio (passo a passo)

### A) Domínio na Cloudflare

1. Compre/registre um domínio (ex.: Registro.br).
2. Crie conta em [dash.cloudflare.com](https://dash.cloudflare.com).
3. **Add a site** → informe o domínio.
4. Cloudflare mostra 2 nameservers (ex.: `ada.ns.cloudflare.com`). No Registro.br (ou onde comprou), troque os DNS/nameservers para esses.
5. Espere o status ficar **Active** (pode levar minutos a algumas horas).

### B) Túnel nomeado (URL fixa)

1. No menu: **Zero Trust** → **Networks** → **Tunnels** → **Create a tunnel**.
2. Tipo **Cloudflared** → nome `agenda` → **Save**.
3. Em **Install connector**, escolha **Docker** e **copie o token** (`eyJ...`).
4. Cole o token em `docker/homelab.env` como `TUNNEL_TOKEN=...`.
5. Aba **Public Hostname** → **Add** (exemplo com `agendaprocessual.com.br`):

| Subdomain | Domain | Type | URL |
|-----------|--------|------|-----|
| *(vazio = apex)* | agendaprocessual.com.br | HTTP | `http://web:3000` |
| `api` | agendaprocessual.com.br | HTTP | `http://api:8000` |

Use **um túnel** (`agenda`) com os dois hostnames e só `TUNNEL_TOKEN`.

6. Em `homelab.env`:
   - `APP_PUBLIC_URL=https://agendaprocessual.com.br`
   - `NEXT_PUBLIC_API_URL=https://api.agendaprocessual.com.br`
   - `CORS_ORIGINS=https://agendaprocessual.com.br`

7. Suba com `compose.homelab.yml` (comando na seção abaixo).

Acesso: **https://agendaprocessual.com.br**.

### C) Teste rápido sem domínio (já usado)

Quick Tunnel gera URL `*.trycloudflare.com` temporária. Não use para produção.

### D) Subir stack com domínio + SMTP

```bash
docker compose \
  --env-file docker/homelab.env \
  --env-file docker/smtp.env \
  -f docker/docker-compose.yml \
  -f docker/compose.homelab.yml \
  -f docker/compose.smtp.yml \
  up -d --build
```

Não publique no túnel: Postgres, Redis, Mailpit.

## 4. Observabilidade (Grafana do homelab)

A API expõe `GET /metrics` (Prometheus) e `GET /api/v1/health` (DB + Redis).

No servidor Ubuntu (`~/homelab`):

1. **Scrape** via Tailscale do Mac (porta host `8001`) —
   [`deploy/prometheus/agenda.yml`](../deploy/prometheus/agenda.yml) →
   `compose/monitoring/prometheus/prometheus.yml` do repo homelab.
2. **Dashboard** —
   [`deploy/grafana/agenda-dashboard.json`](../deploy/grafana/agenda-dashboard.json)
   → pasta Homelab (`uid: agenda-processual`). Inclui painéis de 5xx/4xx e
   latência **por endpoint** (`handler` + `method`).
3. **Alertas** —
   [`deploy/prometheus/alerts.yml`](../deploy/prometheus/alerts.yml)
   (API down, 5xx, taxa de erro, latência p95, falha de e-mail de prazo).
   Passo a passo e contact points:
   [`deploy/grafana/alert-rules.md`](../deploy/grafana/alert-rules.md).

Validação rápida:

```bash
# Target agenda-api = UP
curl -s 'http://prometheus.homelab/api/v1/query?query=up{job="agenda-api"}'

# Regras carregadas
curl -s 'http://prometheus.homelab/api/v1/rules' | head
```

Se o IP Tailscale do Mac mudar, atualize o `targets` no `prometheus.yml` e rode
`curl -X POST http://localhost:9090/-/reload` no servidor (mesmo comando após
copiar/atualizar `alerts.yml`).

Não publique `/metrics` no túnel Cloudflare sem autenticação (hoje o path
público existe; preferir scrape só pela LAN/Tailscale).

## 5. Teste de e-mail de alerta

1. Login como admin na URL pública.
2. Em Usuários, marque “Receber alertas” no responsável.
3. Crie prazo pendente com vencimento = hoje + N (N nos alertas do prazo, default 3 e 1).
4. Dispare:

```bash
TOKEN=$(curl -s -X POST https://api.agenda.SEUDOMINIO/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"SEU_ADMIN","password":"SUA_SENHA"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

curl -s -X POST https://api.agenda.SEUDOMINIO/api/v1/alertas/processar \
  -H "Authorization: Bearer $TOKEN"
```

5. Confira a caixa de e-mail e o painel Grafana (enviados / erros).
6. O link do e-mail deve apontar para `APP_PUBLIC_URL`, não localhost.

## 6. CI/CD (GitHub Actions → homelab)

Fluxo: **push em `develop`/`main`** → testes API + build Web → deploy no runner local.

### A) Self-hosted runner (uma vez)

1. No Mac do homelab: [GitHub → Settings → Actions → Runners → New self-hosted runner](https://github.com/RenatoGregorio01/agenda-processual/settings/actions/runners/new).
2. Siga as instruções (download + `./config.sh` + `./run.sh`).
3. Labels: deixe `self-hosted` e adicione **`homelab`**.
4. Rode o runner como serviço (`svc.sh install && svc.sh start`) para não depender do terminal aberto.

### B) Variável do repositório

GitHub → **Settings → Secrets and variables → Actions → Variables**:

| Name | Value (exemplo) |
|------|-----------------|
| `HOMELAB_REPO_PATH` | `/Users/renatogregorio/Documents/Projetos/agenda-processual` |

O deploy faz `git pull` **nesse caminho** (mesmo volume Postgres/Redis). Não use o workspace efêmero do Actions.

Secrets (`homelab.env`, `smtp.env`, `TUNNEL_TOKEN`) continuam **só no disco local** — não vá para o GitHub.

### C) Workflows

| Arquivo | Quando |
|---------|--------|
| `api-ci.yml` / `web-ci.yml` | PR e push em feature (validação) |
| `deploy-homelab.yml` | Push em `main`/`develop` ou manual (`workflow_dispatch`) |

Sem runner online, o job **Deploy** fica amarelo/vermelho; API/Web CI na nuvem ainda rodam.

## Checklist

- [ ] Web em **produção** (`next build` / imagem `Dockerfile`, sem `next dev`)
- [ ] `DEBUG=false`, `APP_ENV=production`
- [ ] `JWT_SECRET` único
- [ ] Senha admin forte em `SEED_ADMIN_PASSWORD` (aplicada no boot se a env estiver setada)
- [ ] `APP_PUBLIC_URL` e `NEXT_PUBLIC_API_URL` em HTTPS
- [ ] `COOKIE_SECURE=true` (já no compose.homelab)
- [ ] SMTP real (não Mailpit) — ver [smtp-e-acesso.md](smtp-e-acesso.md)
- [ ] Tunnel só web + api (1 túnel, 2 Public Hostnames)
- [ ] Prometheus scrapando `agenda-api`
- [ ] Backup de `docker/data/postgres`
