# AGENTS.md

Notes for AI coding agents (Claude Code, Cursor, etc.) working on ChatTemplate.

> **If you cloned this as a template:** update the sections below to match your project. The defaults describe the template itself.

## What this is

A FastAPI + Next.js starter for chat apps with streaming, auth and persistent sessions. Mostly built for myself, since I keep rebuilding the same stack.

See [README.md](./README.md) and [TODO.md](./TODO.md).

## Stack

- Backend: Python 3.12 · FastAPI · SQLAlchemy 2 async · Alembic · asyncpg · sse-starlette
- Frontend: Next.js 15 · React 19 · TypeScript · Tailwind v4
- Database: Postgres 16
- Auth: JWT (HS256) + bcrypt
- Tooling: uv · pnpm · Docker · GitHub Actions

## Key paths

- `backend/src/api/main.py` — FastAPI app entry (CORS, lifespan, router includes)
- `backend/src/api/core/` — config, db (async engine), security (JWT, bcrypt), deps
- `backend/src/api/auth/` — register / login / me
- `backend/src/api/chat/` — SSE streaming + LLM provider abstraction (`llm.py`)
- `backend/src/api/sessions/` — chat session CRUD + message persistence
- `backend/migrations/versions/` — Alembic migrations
- `frontend/app/` — Next.js pages (`login`, `chat`)
- `frontend/components/` — `ChatBox`, `Message`
- `frontend/lib/` — `api.ts` (fetch wrapper), `auth.ts` (token storage), `useChatStream.ts` (SSE consumer)

## Commands

With Docker (recommended):

```bash
cp .env.example .env
# fill OPENAI_API_KEY in .env, or leave LLM_PROVIDER=mock to use the canned responses
docker compose up --build
```

Without Docker:

```bash
docker compose up -d db
cd backend && uv sync && uv run alembic upgrade head && uv run uvicorn api.main:app --reload --port 8000
cd ../frontend && pnpm install && pnpm dev
```

Tests:

```bash
cd backend && uv run pytest -q
cd frontend && pnpm typecheck && pnpm lint
```

Migrations:

```bash
cd backend
uv run alembic revision --autogenerate -m "your message"
uv run alembic upgrade head
```

## Conventions

- Commits: lowercase imperative, conventional style (`fix:`, `feat:`, `docs:`)
- Do not include `Co-Authored-By` in commits
- Type hints everywhere in Python; strict TypeScript on the frontend
- Add new LLM providers in `backend/src/api/chat/llm.py` (implement an `async def stream(messages)` method and register in `get_provider`)
- Add new resources as their own folder with `models.py` / `schemas.py` / `service.py` / `router.py` (mirror the auth/sessions/chat pattern)
- SSE wire format is `event: <name>\ndata: <text>\n\n` — don't break it on the backend or the frontend hook breaks

## Don't

- Don't commit `.env`
- Don't bypass the `get_current_user` dependency on routes that should require auth
- Don't change the SSE event names (`token`, `done`) without updating both backend (`chat/router.py`) and frontend (`useChatStream.ts`)

## TODO

See [TODO.md](./TODO.md).
