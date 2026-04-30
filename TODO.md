# TODO

Stuff I want to add when I get to it. Loosely ordered by what I'd reach for next.

## Soon

- [ ] Anthropic provider
- [ ] Ollama provider for local dev
- [ ] Refresh tokens
- [ ] Rate limiting (slowapi)
- [ ] Langfuse traces

## Later

- [ ] LangGraph integration (ReAct loop)
- [ ] Tool-call UI (show tool calls inline in chat)
- [ ] pgvector for RAG
- [ ] Playwright e2e tests
- [ ] Deploy notes (Fly.io / Azure)

## Considered, rejected

- WebSocket instead of SSE — SSE is enough for one-way streaming
- MySQL instead of Postgres — Postgres because of pgvector
- Sync DB layer — async is the point of the stack

## Done

- Initial scaffold (auth, sessions, SSE chat, Docker, CI)
