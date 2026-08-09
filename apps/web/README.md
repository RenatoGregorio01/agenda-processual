# Web — Agenda Processual

Frontend Next.js + TypeScript (App Router).

## Desenvolvimento

```bash
cd apps/web
cp .env.example .env.local
npm install
npm run dev
```

App: http://localhost:3000  
API esperada: `NEXT_PUBLIC_API_URL` (padrão `http://localhost:8000`)

Login: http://localhost:3000/login  
Usuário seed: `veronica@escritorio.com` / `agenda123`

## Com Docker

```bash
docker compose -f docker/docker-compose.yml up --build
```

Web em http://localhost:3000
