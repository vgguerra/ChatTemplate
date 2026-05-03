from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from api.auth import service
from api.auth.schemas import RefreshRequest, TokenPair, UserCreate, UserRead
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


@router.post("/login", response_model=TokenPair)
@limiter.limit(settings.rate_limit_auth)
async def login(
    request: Request,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSession,
) -> TokenPair:
    user = await service.authenticate(db, form.username, form.password)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    refresh = await service.issue_refresh_token(db, user.id)
    return TokenPair(access_token=create_access_token(str(user.id)), refresh_token=refresh)


@router.post("/refresh", response_model=TokenPair)
@limiter.limit(settings.rate_limit_auth)
async def refresh(request: Request, payload: RefreshRequest, db: DBSession) -> TokenPair:
    row = await service.consume_refresh_token(db, payload.refresh_token)
    if row is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    new_refresh = await service.issue_refresh_token(db, row.user_id)
    return TokenPair(
        access_token=create_access_token(str(row.user_id)),
        refresh_token=new_refresh,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshRequest, db: DBSession) -> Response:
    await service.revoke_refresh_token(db, payload.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)
