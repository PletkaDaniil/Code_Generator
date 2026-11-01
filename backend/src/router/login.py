import logging
from fastapi import APIRouter
from src.config.config import settings
from src.database.crud import create_one_time_token, get_user_by_username
from src.database.database import DbSession
from src.utils.schemas.login import LoginRequest
from src.utils.schemas.token import TokenResponse
from src.utils.exceptions import AppError
from src.utils.security import DUMMY_HASH, generate_token, verify_password


login_router = APIRouter(tags=["auth"])
logger = logging.getLogger(__name__)


@login_router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest, db: DbSession
) -> TokenResponse:
    """"
        Авторизация пользователя по логину и паролю
    """
    user = await get_user_by_username(db, data.username)

    # проверяем пароль даже если пользователь не найден
    password_ok = await verify_password(
        data.password, user.hashed_password if user else DUMMY_HASH
    )

    # возвращаем ошибку при неверных учетных данных
    if user is None or not password_ok:
        logger.warning("Неуспешная попытка входа")
        raise AppError(401, "Неверный логин или пароль")

    # генерируем одноразовый токен доступа
    token = generate_token()
    await create_one_time_token(
        db, user.id, token, settings.token.token_ttl_seconds
    )

    logger.info(
        "Вход выполнен; одноразовый токен создан: user_id=%s expires_in=%s",
        user.id,
        settings.token.token_ttl_seconds,
    )

    return TokenResponse(
        token=token,
        expires_in=settings.token.token_ttl_seconds
    )
