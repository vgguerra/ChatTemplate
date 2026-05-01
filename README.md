# ChatTemplate

A starter I use when I need to spin up a FastAPI + Next.js app that talks to an LLM. JWT auth, SSE-streamed chat, persistent sessions, Docker compose for local dev.

Mostly built for myself, since I keep rebuilding the same stack. Sharing it in case it's useful to anyone else.

## Use this as a template

Click **Use this template** at the top of the repo on GitHub to spin up a new project with this layout. Then update the names in `backend/pyproject.toml`, `backend/src/api/main.py` and `frontend/app/layout.tsx` to match your project.

## Stack

- Backend: FastAPI · Pydantic · SQLAlchemy 2 async · Alembic · asyncpg
- Frontend: Next.js 15 · React 19 · TypeScript · Tailwind v4
- Database: Postgres 16
- LLM: OpenAI by default; provider is abstracted in `chat/llm.py`, easy to swap
- Auth: JWT (HS256) + bcrypt
- Tooling: uv · pnpm · Docker · GitHub Actions

## Quickstart

### Docker

```bash
cp .env.example .env
# put OPENAI_API_KEY in .env (or leave LLM_PROVIDER=mock)
docker compose up --build
```

- Frontend: http://localhost:3000
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Host

```bash
docker compose up -d db

cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn api.main:app --reload --port 8000

cd ../frontend
pnpm install
pnpm dev
```

## What's in here

- FastAPI app with health endpoint and lifespan
- JWT auth: `/auth/register`, `/auth/login`, `/auth/me`
- SSE chat endpoint: `/chat/{session_id}/stream`
- Persistent sessions: `/sessions` CRUD
- Postgres schema via Alembic
- Mock LLM provider for dev without API keys (`LLM_PROVIDER=mock`)
- docker-compose with db + api + web
- CI (lint, format, test, build)

## TODO

See [TODO.md](./TODO.md).

## License

MIT — see [LICENSE](./LICENSE).
