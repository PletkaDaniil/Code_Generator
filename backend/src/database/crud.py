import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models.models import AccessToken, User


def hash_token(
    token: str
) -> str:
    """
        Хешируем токен доступа
    """
    return hashlib.sha256(token.encode()).hexdigest()


async def get_user_by_username(
    db: AsyncSession, username: str
) -> User | None:
    """
        Получаем пользователя по имени
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession, username: str, hashed_password: str
) -> User:
    """
        Создаем нового пользователя
    """
    user = User(username=username, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_access_token(
    db: AsyncSession, user_id: int, token: str, ttl_seconds: int
) -> AccessToken:
    """
        Создаем токен доступа для пользователя с указанным временем жизни
    """
    now = datetime.now(timezone.utc)
    
    # удаляем просроченные токены, чтобы таблица не росла
    await db.execute(delete(AccessToken).where(AccessToken.expires_at <= now))

    access_token = AccessToken(
        token=hash_token(token),
        user_id=user_id,
        expires_at=now + timedelta(seconds=ttl_seconds),
    )
    db.add(access_token)
    await db.commit()
    return access_token


async def get_user_id_by_token(
    db: AsyncSession, token: str
) -> int | None:
    """
        Получаем user_id владельца токена
        (если токен существует и не просрочен)
    """
    result = await db.execute(
        select(AccessToken.user_id).where(
            AccessToken.token == hash_token(token),
            AccessToken.expires_at > datetime.now(timezone.utc),
        )
    )
    return result.scalar_one_or_none()


async def delete_access_token(
    db: AsyncSession, token: str
) -> None:
    """
        Удаляем токен доступа из бд
    """
    await db.execute(
        delete(AccessToken).where(AccessToken.token == hash_token(token))
    )
    await db.commit()
