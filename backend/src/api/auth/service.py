from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.models import User
from api.auth.schemas import UserCreate
from api.core.security import hash_password, verify_password


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
