from datetime import datetime, timedelta, timezone
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models.models import OneTimeToken, User


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


async def create_one_time_token(
    db: AsyncSession, user_id: int, token: str, ttl_seconds: int
) -> OneTimeToken:
    """
        Создаем одноразовый токен доступа
    """
    now = datetime.now(timezone.utc)

    # удаляем просроченные токены, чтобы таблица не росла
    await db.execute(delete(OneTimeToken).where(OneTimeToken.expires_at <= now))

    one_time_token = OneTimeToken(
        token=token,
        user_id=user_id,
        expires_at=now + timedelta(seconds=ttl_seconds),
    )

    db.add(one_time_token)
    await db.commit()
    return one_time_token


async def consume_one_time_token(db: AsyncSession, token: str) -> int | None:
    """
        Находим непросроченный токен и сразу удаляем его одним запросом.
        Возвращаем user_id или None, если токена нет, он просрочен или уже использован.
        Благодаря атомарному удалению два одновременных запроса не смогут использовать один токен.
    """
    result = await db.execute(
        delete(OneTimeToken)
        .where(
            OneTimeToken.token == token,
            OneTimeToken.expires_at > datetime.now(timezone.utc),
        )
        .returning(OneTimeToken.user_id)
    )

    user_id = result.scalar_one_or_none()
    await db.commit()

    return user_id