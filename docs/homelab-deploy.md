# Deploy no homelab (servidor Ubuntu)

A stack roda no **servidor Ubuntu** (`gregorio-homelab`), não no Mac.

Dois ambientes no mesmo Docker, **clones e túneis separados**:

| Ambiente | Branch | Clone | URL |
|----------|--------|-------|-----|
| Produção | `main` | `~/agenda-processual` | https://agendaprocessual.com.br |
| Homologação | `develop` | `~/agenda-processual-develop` | https://develop.agendaprocessual.com.br |

Não publique `develop` no clone de produção: containers (`agenda-db`, `agenda-api`, …) e o túnel `agenda` são da stack de produção.

## Produção (`main`)

### 1. Secrets

```bash
ssh homelab-ts
cd ~/agenda-processual
cp docker/homelab.env.example docker/homelab.env
cp docker/smtp.env.example docker/smtp.env   # opcional mas recomendado
# edite ambos (JWT_SECRET, TUNNEL_TOKEN, SMTP_*, URLs)
chmod 600 docker/homelab.env docker/smtp.env
```

Gere um `JWT_SECRET` forte (ex.: `openssl rand -hex 32`).

### 2. SMTP

Siga [smtp-e-acesso.md](smtp-e-acesso.md) (Gmail senha de app ou Resend).
Sem `smtp.env`, a API usa Mailpit (só rede interna — sem porta no host).

### 3. Cloudflare Tunnel (`agenda`)

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
git pull --ff-only origin main

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

## Homologação (`develop`)

Ambiente para validar PRs depois do merge em `develop`. Banco, Redis, imagens e túnel **próprios**. Faixa laranja no topo da UI.

### 1. Segundo clone

```bash
ssh homelab-ts
git clone git@github.com:RenatoGregorio01/agenda-processual.git ~/agenda-processual-develop
cd ~/agenda-processual-develop
git checkout develop
cp docker/homelab-develop.env.example docker/homelab-develop.env
# JWT_SECRET e TUNNEL_TOKEN diferentes da produção
chmod 600 docker/homelab-develop.env
```

### 2. Túnel Cloudflare (`agenda-develop`)

Crie um **segundo túnel** (Zero Trust → Tunnels → Create). Não reutilize o token do túnel `agenda`: dois connectors no mesmo túnel competem.

Public Hostnames:

| Hostname | URL interna |
|----------|-------------|
| `develop.agendaprocessual.com.br` | `http://web:3000` |
| `api-develop.agendaprocessual.com.br` | `http://api:8000` |
| `mailpit-develop.agendaprocessual.com.br` (opcional) | `http://mailpit:8025` |

Em `homelab-develop.env`:

- `APP_PUBLIC_URL=https://develop.agendaprocessual.com.br`
- `NEXT_PUBLIC_API_URL=https://api-develop.agendaprocessual.com.br`
- `CORS_ORIGINS=https://develop.agendaprocessual.com.br`

E-mails de convite/alerta desta stack vão para o Mailpit interno (não SMTP real), para não pingar o escritório.

### Subir / atualizar

```bash
cd ~/agenda-processual-develop
git pull --ff-only origin develop

docker compose -p agenda-develop \
  --env-file docker/homelab-develop.env \
  -f docker/docker-compose.yml \
  -f docker/compose.develop.yml \
  up -d --build
```

Login seed: `veronica@escritorio.com` / senha de `SEED_ADMIN_PASSWORD` no env.

### 3. Variável do GitHub Actions

Settings → Variables → `HOMELAB_DEVELOP_REPO_PATH` = `/home/renato/agenda-processual-develop`

(Produção continua em `HOMELAB_REPO_PATH` = `/home/renato/agenda-processual`.)

## Observabilidade

- Produção: `http://agenda-api:8000/metrics` na rede `observability`.
- Homologação: `http://agenda-develop-api:8000/metrics` (mesmo arquivo).
- Job: [`deploy/prometheus/agenda.yml`](../deploy/prometheus/agenda.yml) → `prometheus.yml` do homelab.
- Dashboard: [`deploy/grafana/agenda-dashboard.json`](../deploy/grafana/agenda-dashboard.json).

```bash
curl -s 'http://127.0.0.1:9090/api/v1/targets' | grep agenda
```

Recarregue o Prometheus depois de incluir o job `agenda-api-develop`.

## CI/CD (GitHub Actions → Ubuntu)

1. Instale o [self-hosted runner](https://github.com/RenatoGregorio01/agenda-processual/settings/actions/runners/new) **no Ubuntu**, label `homelab`.
2. `HOMELAB_REPO_PATH` = clone de **produção**.
3. `HOMELAB_DEVELOP_REPO_PATH` = clone de **homologação**.
4. Push em `main` → `deploy-homelab.yml`.
5. Push em `develop` → `deploy-develop.yml`.

O runner antigo no Mac pode ser removido (Settings → Runners).

## Mac (só desenvolvimento)

```bash
# Sem túnel / sem produção / sem homologação:
docker compose -f docker/docker-compose.yml up -d --build
```

Não rode `compose.homelab.yml` nem `compose.develop.yml` no Mac se os túneis já estiverem ativos no Ubuntu.

## Checklist

- [ ] Stack de produção (`docker ps | grep agenda-api`)
- [ ] Stack de homologação (`docker ps | grep agenda-develop`)
- [ ] Dois cloudflared (`agenda` e `agenda-develop`) com `Registered tunnel connection`
- [ ] https://agendaprocessual.com.br e /api health OK
- [ ] https://develop.agendaprocessual.com.br com faixa de homologação
- [ ] Stack do Mac parada (`compose down`)
- [ ] `HOMELAB_REPO_PATH` e `HOMELAB_DEVELOP_REPO_PATH` no GitHub
- [ ] Prometheus `agenda-api:8000` e `agenda-develop-api:8000` = UP
- [ ] Backup diário do Postgres de **produção** (`agenda-db`) via restic no HD externo — ver [homelab/docs/backup.md](https://github.com/RenatoGregorio01/homelab/blob/main/docs/backup.md)
