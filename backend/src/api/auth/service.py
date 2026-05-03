from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.models import RefreshToken, User
from api.auth.schemas import UserCreate
from api.core.config import settings
from api.core.security import (
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, payload: UserCreate) -> User:
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


async def issue_refresh_token(db: AsyncSession, user_id: int) -> str:
    token, digest = generate_refresh_token()
    expires = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    db.add(RefreshToken(user_id=user_id, token_hash=digest, expires_at=expires))
    await db.commit()
    return token


async def consume_refresh_token(db: AsyncSession, token: str) -> RefreshToken | None:
    """Look up an active refresh token row and mark it revoked. Returns the row or None."""
    digest = hash_refresh_token(token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == digest))
    row = result.scalar_one_or_none()
    if row is None or row.revoked_at is not None:
        return None
    if row.expires_at <= datetime.now(UTC):
        return None
    row.revoked_at = datetime.now(UTC)
    await db.commit()
    return row


async def revoke_refresh_token(db: AsyncSession, token: str) -> None:
    digest = hash_refresh_token(token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == digest))
    row = result.scalar_one_or_none()
    if row is not None and row.revoked_at is None:
        row.revoked_at = datetime.now(UTC)
        await db.commit()
