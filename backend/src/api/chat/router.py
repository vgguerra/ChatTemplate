from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException, Request, status
from sse_starlette.sse import EventSourceResponse

from api.chat.llm import get_provider
from api.chat.schemas import ChatRequest
from api.core.config import settings
from api.core.deps import CurrentUser, DBSession
from api.core.rate_limit import limiter
from api.sessions import service as sessions_service

router = APIRouter()


@router.post("/{session_id}/stream")
@limiter.limit(settings.rate_limit_chat)
async def stream_chat(
    request: Request,
    session_id: int,
    payload: ChatRequest,
    user: CurrentUser,
    db: DBSession,
) -> EventSourceResponse:
    session = await sessions_service.get_for_user(db, session_id, user.id)
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found")

    history = [{"role": m.role, "content": m.content} for m in session.messages]
    history.append({"role": "user", "content": payload.message})
    await sessions_service.append_message(db, session_id, "user", payload.message)

    provider = get_provider()

    async def event_gen() -> AsyncIterator[dict]:
        buffer: list[str] = []
        async for token in provider.stream(history):
            buffer.append(token)
            yield {"event": "token", "data": token}
        full_reply = "".join(buffer)
        await sessions_service.append_message(db, session_id, "assistant", full_reply)
        yield {"event": "done", "data": ""}

    return EventSourceResponse(event_gen())
