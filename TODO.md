# TODO

Stuff I want to add when I get to it. Loosely ordered by what I'd reach for next.

## Soon

- [ ] Anthropic provider
- [ ] Ollama provider for local dev
- [ ] Refresh tokens
- [ ] Rate limiting (slowapi)
- [ ] Langfuse traces
- [ ] Demo GIF or screenshot in the README
- [ ] Architecture diagram (Mermaid) in the README

## Later

- [ ] LangGraph integration (ReAct loop)
- [ ] Tool-call UI (show tool calls inline in chat)
- [ ] pgvector for RAG
- [ ] Playwright e2e tests
- [ ] Deploy notes (Fly.io / Azure)
- [ ] CONTRIBUTING.md and issue templates once the repo gets traction

## Considered, rejected

- WebSocket instead of SSE — SSE is enough for one-way streaming
- MySQL instead of Postgres — Postgres because of pgvector
- Sync DB layer — async is the point of the stack

## Done

- Initial scaffold (auth, sessions, SSE chat, Docker, CI)
- Initial Alembic migration (users, chat_sessions, chat_messages)
- Renamed everything to ChatTemplate
