# Deploy no homelab (servidor Ubuntu)

A stack de produção roda no **servidor Ubuntu** (`gregorio-homelab`), não no Mac.

Clone no servidor: `~/agenda-processual`  
Túnel Cloudflare, API, Web, Postgres, Redis e Mailpit sobem juntos via Compose.

Ordem sugerida:

1. Secrets e URLs
2. SMTP real
3. Cloudflare Tunnel (token no servidor)
4. Prometheus scrape + dashboard Grafana
5. CI/CD (runner no Ubuntu)

## 1. Secrets (no servidor)

```bash
ssh homelab-ts
cd ~/agenda-processual
cp docker/homelab.env.example docker/homelab.env
cp docker/smtp.env.example docker/smtp.env   # opcional mas recomendado
# edite ambos (JWT_SECRET, TUNNEL_TOKEN, SMTP_*, URLs)
chmod 600 docker/homelab.env docker/smtp.env
```

Gere um `JWT_SECRET` forte (ex.: `openssl rand -hex 32`).

## 2. SMTP

Siga [smtp-e-acesso.md](smtp-e-acesso.md) (Gmail senha de app ou Resend).
Sem `smtp.env`, a API usa Mailpit (só rede interna — sem porta no host).

## 3. Cloudflare Tunnel

1. Zero Trust → Tunnels → túnel `agenda` → token em `docker/homelab.env`.
2. Public Hostnames (serviço Docker na mesma rede do compose):

| Hostname | URL interna |
|----------|-------------|
| `agendaprocessual.com.br` | `http://web:3000` |
| `api.agendaprocessual.com.br` | `http://api:8000` |

3. Em `homelab.env`:
   - `APP_PUBLIC_URL=https://agendaprocessual.com.br`
   - `NEXT_PUBLIC_API_URL=https://api.agendaprocessual.com.br`
   - `CORS_ORIGINS=https://agendaprocessual.com.br`

### Subir / atualizar

```bash
cd ~/agenda-processual
git pull --ff-only origin main   # ou develop

docker compose \
  --env-file docker/homelab.env \
  --env-file docker/smtp.env \
  -f docker/docker-compose.yml \
  -f docker/compose.homelab.yml \
  -f docker/compose.smtp.yml \
  up -d --build
```

(`smtp.env` / `compose.smtp.yml` só se existirem.)

**Não** publica portas no host para web/api/db/redis (evita conflito com Grafana `:3000` e Postgres do homelab `:5432`). Acesso público só via túnel.

## 4. Observabilidade

- API em `http://agenda-api:8000/metrics` na rede Docker `observability`.
- Job: [`deploy/prometheus/agenda.yml`](../deploy/prometheus/agenda.yml) → `prometheus.yml` do homelab.
- Dashboard: [`deploy/grafana/agenda-dashboard.json`](../deploy/grafana/agenda-dashboard.json).

```bash
curl -s 'http://127.0.0.1:9090/api/v1/targets' | grep agenda
```

## 5. CI/CD (GitHub Actions → Ubuntu)

1. Instale o [self-hosted runner](https://github.com/RenatoGregorio01/agenda-processual/settings/actions/runners/new) **no Ubuntu**, label `homelab`.
2. Variável `HOMELAB_REPO_PATH` = `/home/renato/agenda-processual`
3. Push em `main`/`develop` → `deploy-homelab.yml` faz `git pull` + `compose up -d --build` nesse path.

O runner antigo no Mac pode ser removido (Settings → Runners).

## Mac (só desenvolvimento)

```bash
# Sem túnel / sem produção:
docker compose -f docker/docker-compose.yml up -d --build
```

Não rode `compose.homelab.yml` no Mac se o túnel já estiver ativo no Ubuntu (dois connectors no mesmo tunnel competem).

## Checklist

- [ ] Stack no Ubuntu (`docker ps | grep agenda`)
- [ ] `cloudflared` no Ubuntu com conexões `Registered tunnel connection`
- [ ] https://agendaprocessual.com.br e /api health OK
- [ ] Stack do Mac parada (`compose down`)
- [ ] `HOMELAB_REPO_PATH` aponta para o clone no Ubuntu
- [ ] Prometheus `agenda-api:8000` = UP
- [ ] Backup de `~/agenda-processual/docker/data/postgres`
