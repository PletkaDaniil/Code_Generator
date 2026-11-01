import logging
from fastapi import APIRouter
from sqlalchemy.exc import IntegrityError
from src.database.crud import create_user, get_user_by_username
from src.database.database import DbSession
from src.utils.schemas.register import RegisterRequest
from src.utils.schemas.user import UserResponse
from src.utils.exceptions import AppError
from src.utils.security import hash_password


register_router = APIRouter(tags=["auth"])
logger = logging.getLogger(__name__)


@register_router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: RegisterRequest, db: DbSession
) -> UserResponse:
    """
        Регистрация нового пользователя
    """
    
    # проверяем, занят ли логин кем-то еще
    if await get_user_by_username(db, data.username):
        logger.warning("Отказ регистрации: логин уже занят")
        raise AppError(409, "Пользователь с таким логином уже существует")

    # хешируем пароль перед сохранением в БД
    hashed = await hash_password(data.password)

    try:
        user = await create_user(db, data.username, hashed)
    except IntegrityError:
        # обрабатываем ситуацию, когда два запроса одновременно создают один логин
        await db.rollback()
        logger.warning("Конфликт регистрации при создании пользователя")
        raise AppError(409, "Пользователь с таким логином уже существует")

    logger.info("Пользователь зарегистрирован: user_id=%s", user.id)

    return UserResponse(id=user.id, username=user.username)
