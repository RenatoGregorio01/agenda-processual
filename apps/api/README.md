# API — Agenda Processual

FastAPI + SQLModel + PostgreSQL + Alembic.

## Endpoints (skeleton)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/v1/health` | Healthcheck (DB + Redis; 503 se DB cair) |
| GET | `/metrics` | Métricas Prometheus |
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
| POST | `/api/v1/auditoria/purge` | Apaga logs de auditoria fora da retenção (admin) |
| GET/POST | `/api/v1/usuarios` | Gestão de usuários (somente admin) |
| PATCH | `/api/v1/usuarios/{id}` | Atualiza usuário/permissões (somente admin) |
| GET | `/api/v1/djen` | Inbox de publicações DJEN (auth) |
| GET | `/api/v1/djen/resumo` | Contagem de publicações novas (auth) |
| POST | `/api/v1/djen/sync` | Sincroniza DJEN dos processos do escritório (auth) |
| POST | `/api/v1/djen/{id}/ignorar` | Ignora publicação (editor/admin) |
| POST | `/api/v1/processos/{id}/djen/sync` | Sincroniza DJEN de um processo |

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

## Testes

```bash
# unitários + e2e da API
pytest -q

# só e2e (ASGI + SQLite em memória)
pytest tests/e2e -q
```

Os e2e cobrem login, convite por e-mail, prazos e cálculo de dias úteis/feriados.
