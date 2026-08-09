# API — Agenda Processual

FastAPI + SQLModel + PostgreSQL + Alembic.

## Endpoints (skeleton)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/v1/health` | Healthcheck (público) |
| POST | `/api/v1/auth/login` | Login (JWT) |
| GET | `/api/v1/auth/me` | Usuário autenticado |
| GET | `/api/v1/prazos` | Lista prazos (auth) |
| POST | `/api/v1/prazos` | Cria prazo (auth) |
| GET | `/api/v1/prazos/{id}` | Detalhe (auth) |
| PATCH | `/api/v1/prazos/{id}` | Atualiza (auth) |
| POST | `/api/v1/prazos/{id}/cumprir` | Marca cumprido (auth) |
| DELETE | `/api/v1/prazos/{id}` | Soft delete (auth) |
| POST | `/api/v1/prazos/{id}/restaurar` | Restaura (auth) |
| GET | `/api/v1/auditoria` | Auditoria (admin vê tudo; demais só as próprias) |
| GET/POST | `/api/v1/usuarios` | Gestão de usuários (somente admin) |
| PATCH | `/api/v1/usuarios/{id}` | Atualiza usuário/permissões (somente admin) |

Usuário seed (dev): `veronica@escritorio.com` / `agenda123` (admin)

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
