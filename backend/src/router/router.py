import logging
from fastapi import APIRouter, Depends, Response
from src.utils.schemas.code import CodeResponse
from src.utils.auth import get_current_user_id
from src.utils.secret_code import generate_code


router = APIRouter(tags=["code"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=CodeResponse)
async def public_code(
    response: Response
) -> CodeResponse:
    """
        Часть 1
        открытый эндпоинт, новый код при каждом запросе
    """

    # без кэширования ответа
    response.headers["Cache-Control"] = "no-store"

    return CodeResponse(code=generate_code())


@router.get(
    "/secure",
    response_model=CodeResponse,
    dependencies=[Depends(get_current_user_id)],
)
async def secure_code(
    response: Response
) -> CodeResponse:
    """
        Часть 2
        выдаем новый 4-х значный код только пока токен действителен
    """

    # без кэширования ответа
    response.headers["Cache-Control"] = "no-store"
    logger.info("Генерация нового кода для авторизованного пользователя")
    
    return CodeResponse(code=generate_code())
