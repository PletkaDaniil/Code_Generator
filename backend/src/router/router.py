import logging
from typing import Annotated
from fastapi import APIRouter, Depends, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.database.crud import consume_one_time_token
from src.database.database import DbSession
from src.utils.schemas.code import CodeResponse
from src.utils.secret_code import generate_code
from src.utils.exceptions import AppError


router = APIRouter(tags=["code"])
logger = logging.getLogger(__name__)

# обрабатываем ошибки самостоятельно
bearer_scheme = HTTPBearer(auto_error=False)


@router.get("/", response_model=CodeResponse)
async def public_code(response: Response) -> CodeResponse:
    """
        Часть 1
        открытый эндпоинт, новый код при каждом запросе
    """

    # без кэширования ответа
    response.headers["Cache-Control"] = "no-store"

    return CodeResponse(code=generate_code())


# выдаём код только по одноразовому токену
@router.get("/secure", response_model=CodeResponse)
async def secure_code(
    response: Response,
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> CodeResponse:
    """
        Часть 2
        код выдаётся только по одноразовому токену, повторно он не работает
    """

    # без кэширования ответа
    response.headers["Cache-Control"] = "no-store"

    user_id = None
    if credentials is not None:
        # проверяем токен и помечаем его использованным
        user_id = await consume_one_time_token(db, credentials.credentials)

    # проверяем, удалось ли получить пользователя по токену
    if user_id is None:
        logger.warning("Отказ в доступе к защищённому коду: токен отсутствует или недействителен")
        raise AppError(401, "Требуется вход: токен отсутствует, просрочен или уже использован")

    logger.info("Защищённый код выдан: user_id=%s", user_id)

    return CodeResponse(code=generate_code())