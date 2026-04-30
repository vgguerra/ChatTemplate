from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.sessions.models import ChatMessage, ChatSession


async def list_for_user(db: AsyncSession, user_id: int) -> list[ChatSession]:
    result = await db.execute(
        select(ChatSession).where(ChatSession.user_id == user_id).order_by(ChatSession.id.desc())
    )
    return list(result.scalars().all())


async def get_for_user(
    db: AsyncSession, session_id: int, user_id: int
) -> ChatSession | None:
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .options(selectinload(ChatSession.messages))
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, user_id: int, title: str) -> ChatSession:
    session = ChatSession(user_id=user_id, title=title)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def append_message(
    db: AsyncSession, session_id: int, role: str, content: str
) -> ChatMessage:
    msg = ChatMessage(session_id=session_id, role=role, content=content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg
