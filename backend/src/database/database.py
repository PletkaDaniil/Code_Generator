from collections.abc import AsyncGenerator
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.config.config import settings


# асинхронно подключаемся к БД
engine = create_async_engine(
    settings.db.database_url,
    echo=False,
    pool_pre_ping=True,
)


# создаем "фабрику" асинхронных сессий
SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


# получаем сессию БД для работы с запросами
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


# создаем короткий тип для роутов
DbSession = Annotated[AsyncSession, Depends(get_db)]