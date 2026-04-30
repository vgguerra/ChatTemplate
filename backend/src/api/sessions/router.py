from fastapi import APIRouter, HTTPException, status

from api.core.deps import CurrentUser, DBSession
from api.sessions import service
from api.sessions.schemas import SessionCreate, SessionDetail, SessionRead

router = APIRouter()


@router.get("/", response_model=list[SessionRead])
async def list_sessions(user: CurrentUser, db: DBSession) -> list[SessionRead]:
    sessions = await service.list_for_user(db, user.id)
    return [SessionRead.model_validate(s) for s in sessions]


@router.post("/", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: SessionCreate, user: CurrentUser, db: DBSession
) -> SessionRead:
    s = await service.create(db, user.id, payload.title)
    return SessionRead.model_validate(s)


@router.get("/{session_id}", response_model=SessionDetail)
async def get_session(session_id: int, user: CurrentUser, db: DBSession) -> SessionDetail:
    s = await service.get_for_user(db, session_id, user.id)
    if s is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found")
    return SessionDetail.model_validate(s)
