from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from api.auth import service
from api.auth.schemas import Token, UserCreate, UserRead
from api.core.config import settings
from api.core.deps import CurrentUser, DBSession
from api.core.rate_limit import limiter
from api.core.security import create_access_token

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.rate_limit_auth)
async def register(request: Request, payload: UserCreate, db: DBSession) -> UserRead:
    if await service.get_by_email(db, payload.email):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")
    user = await service.create_user(db, payload)
    return UserRead.model_validate(user)


@router.post("/login", response_model=Token)
@limiter.limit(settings.rate_limit_auth)
async def login(
    request: Request,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSession,
) -> Token:
    user = await service.authenticate(db, form.username, form.password)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return Token(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)
