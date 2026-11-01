import logging
from fastapi import Request
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


class AppError(Exception):
    """
        Ожидаемая ошибка приложения
    """
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


async def app_error_handler(
    request: Request, exc: AppError
) -> JSONResponse:
    """
        Обрабатываем ожидаемые ошибки приложения
    """
    logger.exception("Ошибка приложения: %s %s", request.method, request.url.path)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
        Обрабатываем остальные ошибки, которые не были предусмотрены
    """
    logger.exception("Необработанная ошибка: %s %s", request.method, request.url.path)

    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"}
    )