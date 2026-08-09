# API — Agenda Processual

FastAPI + SQLModel + PostgreSQL + Alembic.

## Endpoints (skeleton)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/v1/health` | Healthcheck |
| GET | `/api/v1/prazos` | Lista prazos (por vencimento) |
| POST | `/api/v1/prazos` | Cria prazo |
| GET | `/api/v1/prazos/{id}` | Detalhe |
| PATCH | `/api/v1/prazos/{id}` | Atualiza |
| POST | `/api/v1/prazos/{id}/cumprir` | Marca cumprido |
| DELETE | `/api/v1/prazos/{id}` | Exclui |

## Local sem Docker

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

## Migrações

```bash
alembic revision --autogenerate -m "mensagem"
alembic upgrade head
```
