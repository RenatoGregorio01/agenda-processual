# Agenda Processual

MVP de controle de prazos processuais para escritório de advocacia.

Validação inicial: destacar a **data de vencimento** e alertar em 3 / 2 / 1 dia (hoje o fluxo costuma ser olhômetro + memoriômetro).

## Design

Brief para Figma AI/Make: [docs/figma-brief-mvp.md](docs/figma-brief-mvp.md)  
Brief para Google Stitch (UI das telas): [docs/stitch-brief-ui.md](docs/stitch-brief-ui.md)

## Roadmap

Próximos temas de produto (incluindo compra de acesso e melhoria de UI): [docs/roadmap.md](docs/roadmap.md)

## Stack

- API: FastAPI (Python)
- Web: Next.js + TypeScript
- Banco: PostgreSQL
- Cache: Redis (andamentos Datajud)
- Deploy: Docker no homelab

## Estrutura

```text
apps/
  api/     # FastAPI + SQLAlchemy/SQLModel + Alembic
  web/     # Next.js (frontend)
docker/    # Compose e serviços locais
docs/      # Briefs e documentação de produto
```

## Branches (GitFlow)

| Branch | Uso |
|--------|-----|
| `main` | Produção / releases estáveis (`agendaprocessual.com.br`) |
| `develop` | Integração da próxima release (`develop.agendaprocessual.com.br`) |
| `feature/*` | Features a partir de `develop` |
| `release/*` | Preparação de versão |
| `hotfix/*` | Correção urgente a partir de `main` |

## Desenvolvimento local

Com Docker (API + Postgres + Web):

```bash
docker compose -f docker/docker-compose.yml up --build
```

| Serviço | URL |
|---------|-----|
| Web | http://localhost:3000 |
| API | http://localhost:8001 |
| Docs OpenAPI | http://localhost:8001/docs |
| Mailpit | http://localhost:8025 |
| Postgres | `localhost:5432` |
| Redis | `localhost:6379` |

Homologação no homelab (depois do merge em `develop`): https://develop.agendaprocessual.com.br — ver [docs/homelab-deploy.md](docs/homelab-deploy.md).

SMTP real (Gmail etc.) e como expor na internet: [docs/smtp-e-acesso.md](docs/smtp-e-acesso.md).  
Homelab (produção + homologação `develop`): [docs/homelab-deploy.md](docs/homelab-deploy.md).

Web isolado:

```bash
cd apps/web
cp .env.example .env.local
npm install
npm run dev
```

