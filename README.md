# Agenda Processual

MVP de controle de prazos processuais para escritório de advocacia.

Validação inicial: destacar a **data de vencimento** e alertar em 3 / 2 / 1 dia (hoje o fluxo costuma ser olhômetro + memoriômetro).

## Design

Brief para Figma AI/Make: [docs/figma-brief-mvp.md](docs/figma-brief-mvp.md)

## Roadmap

Próximos temas de produto (incluindo compra de acesso e melhoria de UI): [docs/roadmap.md](docs/roadmap.md)

## Stack

- API: FastAPI (Python)
- Web: Next.js + TypeScript
- Banco: PostgreSQL
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
| `main` | Produção / releases estáveis |
| `develop` | Integração da próxima release |
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
| API | http://localhost:8000 |
| Docs OpenAPI | http://localhost:8000/docs |
| Postgres | `localhost:5432` |

Web isolado:

```bash
cd apps/web
cp .env.example .env.local
npm install
npm run dev
```

